"""Registration, real host projection and authority/recovery boundaries of git-operator.

These are asset contracts, not model execution or mutation-reliability evidence.
"""

from __future__ import annotations

import tomllib

import pytest
import yaml
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection
from devkit_dist.features.distribution.services.subagents import parse_subagents, resolve_settings
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw

ROLE = "subagents/git-operator.md"
DISPATCH = "skills/spec-orchestrate/references/git-operator-dispatch.md"
OPERATIONS = "skills/spec-orchestrate/references/git-operator-operations.md"


def test_operator_is_registered_and_has_bounded_lifecycle_access() -> None:
    metadata = yaml.safe_load(raw(ROLE).split("---\n", 2)[1])
    manifest = tomllib.loads(raw("bundle.toml"))
    assert {"id": "git-operator", "kind": "subagent", "source": ROLE} in manifest["assets"]
    assert "git-operator" in manifest["presets"]["core"]["assets"]
    assert metadata["level"] == "lean"
    assert metadata["x-git-actions"] == ["read", "lifecycle"]
    assert metadata["hosts"]["codex"] == {"status": "emulated", "sandbox_mode": "workspace-write"}
    assert metadata["hosts"]["antigravity"]["status"] == "unverified"
    for host in metadata["hosts"].values():
        assert not {"model", "effort", "model_reasoning_effort"} & host.keys()


@pytest.mark.parametrize(
    ("host", "model", "effort_key", "effort"),
    [
        ("claude-code", "sonnet", "effort", "medium"),
        ("codex", "gpt-6.1-terra", "model_reasoning_effort", "medium"),
        ("antigravity", "flash", "effort", None),
    ],
)
def test_real_operator_projects_the_selected_lean_default(host, model, effort_key, effort) -> None:
    contract = read_contract(raw(ROLE).encode(), ROLE)
    projection = render_projection(host, contract, f".devkit/managed/spec/{ROLE}")
    assert projection is not None
    parsed = tomllib.loads(projection.decode()) if host == "codex" else yaml.safe_load(projection.split(b"---\n", 2)[1])
    assert parsed["model"] == model
    assert parsed.get(effort_key) == effort
    if host == "antigravity":
        assert "effort" not in parsed and "model_reasoning_effort" not in parsed
    assert contract.body.encode().rstrip() in projection


def test_project_override_still_wins_over_role_level() -> None:
    contract = read_contract(raw(ROLE).encode(), ROLE)
    policy = parse_subagents({"roles": {"spec:git-operator": {"level": "deep"}}})
    settings = resolve_settings(policy, "spec:git-operator", contract.level, "codex")
    projection = render_projection("codex", contract, ROLE, settings=settings)
    assert projection is not None
    assert tomllib.loads(projection.decode())["model"] == "gpt-6-astra"


def test_dispatch_reuses_identity_but_never_authority_and_keeps_decisions_in_host() -> None:
    dispatch = raw(DISPATCH)
    for tokens in (
        ("first lifecycle job", "conversation and repository"),
        ("Reuse", "exact agent identity", "native continuation"),
        ("identity or continuation", "fresh instance", "current job authority"),
        ("every job", "same operator"),
        ("Host keeps user decisions", "scheduling", "acceptance", "semantic"),
        ("Planning/Development workers remain one-shot",),
        ("quiesce writers", "no two writers"),
        ("Serialize conflicting jobs", "without promising", "global"),
        ("Normal integration already includes cleanup", "no redundant cleanup job"),
    ):
        assert_rule(dispatch, *tokens)


def test_role_refreshes_identity_and_preserves_authority_and_permission_boundaries() -> None:
    role = raw(ROLE)
    for tokens in (
        ("Each job repeats", "source_ref", "target_ref", "authority", "allowed_boundaries"),
        ("previous job grants no authority",),
        ("Refresh", "before mutation", "changed refs/scope", "dirty resources", "active writers"),
        ("No raw force operations", "production-source authoring", "semantic conflict resolution"),
        ("Publication requires separate current authority",),
        ("separate approval for each operation", "operation, target and reason"),
        ("refused or unavailable approval", "stop", "preserve state", "never reroute"),
        ("Never ask the user directly", "Host owns decisions"),
    ):
        assert_rule(role, *tokens)


def test_partial_result_mapping_requires_observed_complete_effects_not_zero_exit() -> None:
    role = raw(ROLE)
    for tokens in (
        ("partial or unknown effects", "inspect live CLI/Git state", "only a verified supported"),
        ("Preserve recovery identity", "completed effects"),
        ("original CLI status, exit code and effects separate from role status",),
        ("completed", "only after all requested effects", "expected checks", "verified complete"),
        ("needs_input", "Host decision", "failed", "execution failure"),
        ("zero-exit CLI result", "remaining requested effects", "cannot be", "completed"),
        ("no CLI ran", "null CLI status/exit code"),
    ):
        assert_rule(role, *tokens)
    operations = raw(OPERATIONS)
    assert_rule(operations, "If merge landed", "do not repeat integration", "only supported remaining cleanup")
    assert_rule(operations, "INTEGRATION_CLEANUP_INCOMPLETE", "zero exit", "incomplete")


@pytest.mark.parametrize(
    "operation",
    ["prepare-worktree", "handoff", "prepare-integration", "execute-integration", "cleanup", "inspect-recovery"],
)
def test_each_operation_has_a_guarded_existing_cli_procedure(operation) -> None:
    assert f"| `{operation}` |" in raw(OPERATIONS)
