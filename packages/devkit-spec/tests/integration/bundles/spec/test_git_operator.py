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


# SPEC-git-operator-result-readiness AC-05
def test_worker_input_readiness_comes_from_git_observation_not_the_exit_code() -> None:
    role = raw(ROLE)
    assert "checks: {worker_input: {head: sha, dirty_paths: []}}" in role
    for tokens in (
        ("`prepare-worktree` and `handoff`", "`checks.worker_input`", "rev-parse HEAD", "status --porcelain"),
        ("Each dirty path is also a `remaining_effects` entry", "`needs_input`", "never", "`completed`"),
        ("zero-exit CLI result with dirty paths", "neither a failed CLI operation nor ready input"),
        ("Every result", "returns to the Host", "next action", "`remaining_effects`"),
    ):
        assert_rule(role, *tokens)
    assert_rule(raw(DISPATCH), "Before starting a worker", "`checks.worker_input`", "your own", "exit code alone never")
    # The Host's own post-handoff link-fix commit may follow the reported head (AC-08).
    assert_rule(raw(DISPATCH), "clean HEAD", "`checks.worker_input.head` or a descendant", "your own commits")
    operations = raw(OPERATIONS)
    for row in ("prepare-worktree", "handoff"):
        line = next(line for line in operations.splitlines() if line.startswith(f"| `{row}` |"))
        assert "`checks.worker_input`" in line
    handoff = next(line for line in operations.splitlines() if line.startswith("| `handoff` |"))
    assert "the handoff `commit`" in handoff
    assert_rule(handoff, "SPEC_HANDOFF_COMMIT_REFUSED", "to the Host", "never commit or rerun")


# SPEC-git-operator-result-readiness AC-06 (GOP-06: this unit owns the wording; siblings only regress on it)
def test_operator_returns_production_edits_and_broader_authority_to_the_host() -> None:
    authority = raw(ROLE).split("## Authority and boundaries", 1)[1].split("## Return", 1)[0]
    assert_rule(
        authority,
        "Return production",
        "edits, semantic conflict resolution and authority beyond the job to the Host",
        "perform no such mutation",
    )


# SPEC-git-operator-result-readiness AC-07
def test_evidence_kinds_and_host_permission_stay_separate() -> None:
    role = raw(ROLE)
    for tokens in (
        ("original CLI result", "role status", "Git observations", "host emulation", "remaining work"),
        ("host refusal before dispatch", "blocker code", "null CLI result"),
        ("CLI readiness or `auto`", "never host permission"),
        ("isolated fixtures, replays and untested cases",),
        ("never report unmeasured cost or latency as an", "improvement"),
    ):
        assert_rule(role, *tokens)


PAYLOAD = "skills/spec-delegate/references/payload.md"


def _section(markdown: str, heading: str) -> str:
    return markdown.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


# SPEC-git-operator-batch-preparation AC-01
def test_only_prepare_worktree_forms_a_finite_list_with_full_fields_per_item() -> None:
    contract_input = _section(raw(ROLE), "Input")
    for tokens in (
        ("MAY carry a finite, exact preparation list of `prepare-worktree` items",),
        ("Each item", "repeats every job field", "own branch, worktree path and Unit"),
        ("same retained base", "base ref"),
        ("Every other operation stays one job per dispatch",),
    ):
        assert_rule(contract_input, *tokens)


# SPEC-git-operator-batch-preparation AC-02
def test_list_items_run_serially_and_stop_at_the_first_incomplete_item() -> None:
    procedure = _section(raw(ROLE), "Procedure")
    for tokens in (
        ("For a preparation list", "one at a time in the listed order", "own refresh", "own approval request"),
        ("Before each item", "retained base HEAD", "dispatched base ref"),
        (
            "Stop at the",
            "first item that is not completed",
            "a refusal, a failure, a zero-exit setup or sync warning, a moved base ref",
            "refused or unavailable host approval",
            "later item as not attempted",
        ),
    ):
        assert_rule(procedure, *tokens)


# SPEC-git-operator-batch-preparation AC-03
def test_list_return_wraps_the_single_job_return_per_item() -> None:
    contract_return = _section(raw(ROLE), "Return")
    assert "items: []" in contract_return
    assert "not_attempted: []" in contract_return
    assert "cli_result: {status: null, exit_code: null, effects: []}" in contract_return
    for tokens in (
        (
            "Each `items` entry is the single-job return unchanged",
            "original `cli_result`",
            "`completed_effects`",
            "`remaining_effects`",
            "`checks.worker_input`",
            "`blocker_codes`",
            "add no field",
        ),
        ("refused or", "unavailable host approval", "host-permission blocker code", "null CLI result"),
        ("moved base", "ref is `needs_input`", "changed-ref blocker", "null CLI result"),
        ("Each `not_attempted` entry", "identity and intended effects", "null CLI result"),
        (
            "list status is `completed` only when every listed item is `completed`",
            "`needs_input` when any attempted",
            "else `failed`",
            "no `partial` status",
        ),
        ("non-error notice", "`WORKTREE_REMOTE_UNCHECKED`", "only when its `checks.worker_input` and effects"),
    ):
        assert_rule(contract_return, *tokens)


# SPEC-git-operator-batch-preparation AC-04
def test_host_retries_only_inspected_authorized_remainders_and_owns_setup_repair() -> None:
    dispatch = raw(DISPATCH)
    for tokens in (
        ("stops a preparation list", "first item that is not completed", "`not_attempted`"),
        ("Verify each `items` entry", "your own CLI/Git observation", "`inspect-recovery`"),
        ("new list naming only the remaining items you still", "authorize", "current refs"),
        ("never repeat a completed item",),
        ("setup or sync remainder is", "yours", "supported operation", "runs no setup `[FIX]`, sync or"),
    ):
        assert_rule(dispatch, *tokens)
    procedure = _section(raw(ROLE), "Procedure")
    assert_rule(
        procedure, "setup or sync remainder", "returns to the Host", "no setup `[FIX]`, sync or registration repair"
    )


# SPEC-git-operator-batch-preparation AC-05 (GOP-06 stays the regression test above)
def test_list_authority_covers_only_its_listed_items() -> None:
    authority = _section(raw(ROLE), "Authority and boundaries")
    assert_rule(authority, "preparation list's authority covers only its listed `prepare-worktree` items")
    assert_rule(raw(DISPATCH), "list's authority covers only its listed items", "every other operation")


# SPEC-git-operator-batch-preparation AC-06
def test_operations_and_payload_carry_the_list_form() -> None:
    operations = raw(OPERATIONS)
    row = next(line for line in operations.splitlines() if line.startswith("| `prepare-worktree` |"))
    for token in ("preparation list", "listed order", "dispatched base ref", "first item that is not completed"):
        assert token in row
    payload = next(line for line in raw(PAYLOAD).splitlines() if line.startswith("| `git-operator` |"))
    assert "preparation list of `prepare-worktree` items repeats every field per item" in payload
