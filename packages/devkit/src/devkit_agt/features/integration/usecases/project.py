"""Independent project readiness for adaptive-dev session integration."""

from __future__ import annotations

import json
from pathlib import Path

from devkit_dist.features.project import development_approach
from devkit_dist.features.project.repositories.project import commit_config

from devkit_agt.features.integration.models.contracts import Evidence, IntegrationContext, Readiness
from devkit_agt.features.integration.models.errors import ApproachMismatchError, LifecycleValidationRequiredError
from devkit_agt.features.integration.repositories.snapshots import build_snapshot
from devkit_agt.features.rules import Phase, committed_anchors, run_project_rules, touched_owners

DISCLOSURE = "CI rules run on the result; review, tests and lint are explicit source verification claims"


def touched_workflow_units(context: IntegrationContext) -> tuple[str, ...]:
    root = Path(context.finish.base)
    snap = build_snapshot(root, context.finish.source_sha, context.finish.target_sha, context.result_sha)
    anchors = committed_anchors(root, snap.base) | committed_anchors(root, snap.tree)
    return touched_owners(anchors, snap.changed + snap.deleted)


def _passed(value: object) -> bool:
    return value is True or (
        isinstance(value, str)
        and (value.strip().upper() in ("PASS", "PASSED") or value.strip().upper().startswith("PASS "))
    )


def check(context: IntegrationContext) -> Readiness:
    root = Path(context.finish.base)
    target = development_approach(commit_config(root, context.finish.target_sha) or {}).approach
    proposed = development_approach(commit_config(root, context.result_sha or context.finish.source_sha) or {}).approach
    if target != "adaptive-dev":
        raise ApproachMismatchError("project readiness requires committed adaptive-dev target policy")
    units = touched_workflow_units(context)
    if context.task.kind != "session" or units:
        raise LifecycleValidationRequiredError("project readiness cannot validate retained workflow Units", *units)
    reasons: list[str] = []
    evidence = [
        Evidence("DEVELOPMENT_APPROACH", json.dumps({"target": target, "proposed": proposed}, sort_keys=True)),
        Evidence("LIFECYCLE", "omitted:adaptive-dev"),
    ]
    try:
        claims = json.loads(context.task.claims_json)
    except (ValueError, TypeError):
        claims = None
    if not isinstance(claims, dict) or not all(_passed(claims.get(k)) for k in ("review", "tests", "lint")):
        evidence.append(Evidence("SESSION_CLAIMS_INVALID", "review, tests and lint require explicit passing results"))
        reasons.append("missing or failed independent verification claims")
    else:
        evidence.append(
            Evidence(
                "VERIFICATION_CLAIMS", json.dumps({k: claims[k] for k in ("review", "tests", "lint")}, sort_keys=True)
            )
        )
    snap = build_snapshot(root, context.finish.source_sha, context.finish.target_sha, context.result_sha)
    run = run_project_rules(root, snapshot=snap, phase=Phase.LINTER)
    reasons.extend(f"{e.code}: {e.message}" for e in run.errors)
    reasons.extend(f"{v.rule_id}: {v.file}: {v.message}" for v in run.blocking_violations)
    evidence.extend(
        [
            Evidence("CI_RULES", "pass" if run.ok else "fail"),
            Evidence("SOURCE_SHA", context.finish.source_sha),
            Evidence("TARGET_SHA", context.finish.target_sha),
        ]
    )
    if run.result.omissions:
        evidence.append(
            Evidence("RULE_OMISSIONS", json.dumps([o.to_dict() for o in run.result.omissions], sort_keys=True))
        )
    if context.result_sha:
        evidence.append(Evidence("RESULT_SHA", context.result_sha))
    return Readiness(
        context.finish.source_sha,
        context.finish.target_sha,
        tuple(evidence),
        tuple(reasons),
        context.result_sha,
        ("TARGET_SHA", "RESULT_SHA"),
        DISCLOSURE,
        "uv run devkit rules check",
    )
