"""The role contracts' bodies are the subagents' prompts; caller guidance lives in ``spec-delegate``."""

from __future__ import annotations

import tomllib
from typing import Any

import pytest
import yaml
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection
from distsupport.guidance import assert_rule, states_rule
from spec_support.bundle_text import BUNDLE, flat, raw, text

WORKERS = ("development-worker", "planning-worker")
BACKLOG_ROLES = ("triage", "decomposer")
ROLES = (
    "challenger",
    "reconcile-reviewer",
    "code-reviewer",
    "ux-reviewer",
    "scout",
    *BACKLOG_ROLES,
    *WORKERS,
    "git-operator",
)
DELEGATE = BUNDLE / "skills/spec-delegate/SKILL.md"
WORKER_RESULTS = BUNDLE / "skills/spec-delegate/references/worker.md"
ORCHESTRATE = BUNDLE / "skills/spec-orchestrate/SKILL.md"
TASKS = BUNDLE / "skills/spec-tasks/SKILL.md"
PLANNING = BUNDLE / "skills/spec/references/planning.md"


def _contract(role: str) -> tuple[dict[str, Any], str]:
    _, frontmatter, body = raw(f"subagents/{role}.md").split("---\n", 2)
    return yaml.safe_load(frontmatter), body


@pytest.mark.parametrize("role", ROLES)
def test_explicit_role_levels_and_other_roles_inherit(role: str) -> None:
    metadata, _ = _contract(role)
    assert "x-model-profile" not in metadata
    if role == "scout":
        assert metadata["level"] == "compact"
    elif role == "git-operator":
        assert metadata["level"] == "lean"
    else:
        assert "level" not in metadata
    for host in metadata["hosts"].values():
        assert not {"model", "effort", "model_reasoning_effort", "reasoning_effort"} & host.keys()


def test_every_shipped_role_is_checked_for_inheritance() -> None:
    assert {
        path.name.removesuffix(".jinja").removesuffix(".md") for path in (BUNDLE / "subagents").glob("*.md*")
    } == set(ROLES)


@pytest.mark.parametrize("role", ("scout", "challenger"))
def test_a_subagent_only_procedure_lives_in_the_contract(role: str) -> None:
    metadata, body = _contract(role)
    assert "skill" not in metadata
    assert "\n## Procedure\n" in body and "\n## Return\n" in body
    assert not (BUNDLE / f"skills/spec-{role}").exists()


@pytest.mark.parametrize("role", ROLES)
def test_a_contract_body_holds_only_the_role_prompt(role: str) -> None:
    body = flat(_contract(role)[1])
    assert "## Host projection notes" not in body
    assert "## Safety conditions" not in body
    assert "the Developer records them" not in body


def test_reviewer_and_reconciler_keep_the_skills_the_main_session_shares() -> None:
    assert _contract("code-reviewer")[0]["skill"] == "spec-review"
    assert _contract("reconcile-reviewer")[0]["skill"] == "spec-sync"


def test_the_ux_reviewer_is_an_isolated_read_only_role_bound_to_its_skill() -> None:
    # ADR-ux-review-before-code: a fresh, read-only context; optional, never a stage; no severity.
    metadata, body = _contract("ux-reviewer")
    assert metadata["skill"] == "spec-ux-review"
    assert (metadata["x-execution"], metadata["x-invocation"], metadata["x-git-actions"]) == (
        "isolated",
        "optional",
        ["read"],
    )
    hosts = metadata["hosts"]
    assert hosts["claude-code"]["disallowedTools"] == ["Write", "Edit"]
    assert hosts["codex"]["sandbox_mode"] == "read-only"
    assert hosts["antigravity"]["commandExecutionPolicy"] == "sandbox"
    assert_rule(body, "modify", "stage", "commit nothing")
    assert_rule(body, "no finding", "severity")
    assert_rule(body, "read", "`.devkit/managed/spec/skills/spec-ux-review/SKILL.md`")
    assert_rule(body, "follow", "Steps", "Inputs", "payload")
    skill = raw("skills/spec-ux-review/SKILL.md")
    for tokens in (
        ("actor", "try", "right thing"),
        ("actor", "notice", "control", "available"),
        ("actor", "connect", "control", "goal"),
        ("actor", "progress", "goal"),
        ("each screen", "0, 1 or 2"),
        ("`link check (reviewer judgment)`", "out of the rubric"),
        ("findings", "no severity"),
        ("at most two rounds", "unit"),
        ("`resolution: resolved`", "`resolution: waived`", "`waiver`"),
        ("`ux-reviewer`", "optional", "never a stage"),
    ):
        assert_rule(skill, *tokens)
    exact = flat(skill)
    for identifier in (
        "**R1 task fit**",
        "**R2 one primary region**",
        "**R3 states**",
        "**R4 feedback**",
        "**R5 terms**",
        "**R6 objects**",
        "--kind ux-review",
    ):
        assert identifier in exact, identifier
    assert "severity:" not in exact


# SPEC-backlog-subagent-roles: read-only, a message return, the challenger host matrix, the cited procedure.
BACKLOG_PROCEDURES = {
    "triage": ".devkit/managed/spec/playbooks/feedback-hygiene/SKILL.md",
    "decomposer": ".devkit/managed/spec/skills/spec/references/backlog.md",
}


@pytest.mark.parametrize("role", BACKLOG_ROLES)
def test_a_backlog_role_is_isolated_read_only_and_cites_its_procedure(role: str) -> None:
    metadata, body = _contract(role)
    assert metadata["role"] == role and "skill" not in metadata
    assert (metadata["x-execution"], metadata["x-invocation"], metadata["x-git-actions"]) == (
        "isolated",
        "optional",
        ["read"],
    )
    hosts = metadata["hosts"]
    assert hosts["claude-code"]["status"] == "native"
    assert hosts["claude-code"]["tools"] == ["Read", "Grep", "Glob", "Bash"]
    assert hosts["claude-code"]["disallowedTools"] == ["Write", "Edit"]
    assert (hosts["codex"]["status"], hosts["codex"]["sandbox_mode"]) == ("emulated", "read-only")
    assert hosts["antigravity"] == {
        "status": "native",
        "tools": ["view_file", "grep_search", "run_command"],
        "commandExecutionPolicy": "sandbox",
    }
    assert_rule(body, "`uv run devkit get-context spec`", "once")
    assert_rule(body, "modify", "stage", "commit nothing")
    exact = flat(body)
    assert f"`{BACKLOG_PROCEDURES[role]}`" in exact
    assert "`diff_scope.head`" in exact and "`failure_condition`" in exact
    bundle = tomllib.loads(raw("bundle.toml"))
    assert {"id": role, "kind": "subagent", "source": f"subagents/{role}.md"} in bundle["assets"]
    assert role in bundle["presets"]["core"]["assets"]


def test_triage_returns_groups_and_never_changes_a_status() -> None:
    body = _contract("triage")[1]
    for tokens in (
        ("Step 1", "group by target"),
        ("Step 2", "one recommended destination", "reason"),
        ("duplicate", "dismissal candidate", "Evidence"),
        ("never", "Step 3", "Host"),
        ("`issue`", "FB IDs", "target", "ownership"),
    ):
        assert_rule(body, *tokens)


def test_the_decomposer_returns_children_edges_and_an_exit_without_feedback_assignment() -> None:
    body = _contract("decomposer")[1]
    assert "`uv run devkit docs refs PROP-<slug> --direction in -n 0`" in flat(body)
    assert "`incoming_edges`" in flat(body)
    for tokens in (
        ("does not divide", "`needs_input`", "reason"),
        ("every child", "below `size: XL`"),
        ("`slug`", "`devkit docs resolve PROP-<slug>`", "does not find", "`title`", "English `summary`", "`scope`"),
        ("`planning_effort`", "`dev_effort`", "afresh", "`boundaries`", "nearest existing parent", "`depends_on`"),
        ("parent PADRs", "answers", "materials", "inherits"),
        ("`exit`", "`split`", "`promote`", "reason"),
        ("`feedback`", "never", "assign", "copy", "child"),
    ):
        assert_rule(body, *tokens)


def test_support_roles_shell_access() -> None:
    scout = _contract("scout")[0]["hosts"]
    assert "Bash" in scout["claude-code"]["tools"]
    assert "run_command" in scout["antigravity"]["tools"]
    assert scout["antigravity"]["commandExecutionPolicy"] == "sandbox"
    challenger = _contract("challenger")[0]["hosts"]
    assert "Bash" in challenger["claude-code"]["tools"]
    assert challenger["claude-code"]["disallowedTools"] == ["Write", "Edit"]
    assert "run_command" in challenger["antigravity"]["tools"]
    assert challenger["antigravity"]["commandExecutionPolicy"] == "sandbox"
    reconciler = _contract("reconcile-reviewer")[0]["hosts"]
    assert reconciler["claude-code"]["tools"] == ["Read", "Grep", "Glob", "Bash"]
    assert reconciler["claude-code"]["disallowedTools"] == ["Write", "Edit"]
    assert reconciler["codex"]["sandbox_mode"] == "read-only"
    assert "run_command" in reconciler["antigravity"]["tools"]
    assert reconciler["antigravity"]["commandExecutionPolicy"] == "sandbox"


@pytest.mark.parametrize("role", WORKERS)
def test_a_worker_commits_its_result_and_records_in_its_worktree(role: str) -> None:
    # ADR-worker-delivers-committed-result; 01 §4.1-4.2: one-shot workers write their own records and commit.
    metadata, body = _contract(role)
    assert metadata["x-git-actions"] == ["read", "commit"]
    hosts = metadata["hosts"]
    assert hosts["claude-code"]["status"] == "native"
    # Role subagents run nested: Host -> worker -> role.
    assert {"Write", "Edit", "Bash", "Agent"} <= set(hosts["claude-code"]["tools"])
    assert hosts["codex"] == {"status": "emulated", "sandbox_mode": "workspace-write"}
    assert hosts["antigravity"]["status"] == "unverified"
    assert_rule(body, "absolute paths", "`git -C <worktree>`")
    assert_rule(body, "Git", "commit only", "never", "push", "merge", "rebase", "reset", "amend", "stash", "check out")
    assert_rule(body, "`worker` envelope", "worker-records.md")
    assert_rule(body, "`final_head`", "`git -C <worktree> rev-parse HEAD`", "after", "adds the envelope")
    assert "do not write envelope files" not in flat(body)


def test_the_development_worker_commits_at_stage_boundaries_and_on_a_problem() -> None:
    body = _contract("development-worker")[1]
    for tokens in (
        ("commit", "every stage boundary", "write-scope paths only"),
        ("emergency commit", "only", "`--no-verify`"),
        ("one path outside the write scope", "rejects", "whole result"),
        ("problem", "emergency commit"),
        (
            "do not",
            "split units",
            "push",
            "merge",
            "integrate",
            "revert",
            "close",
            "raise the planning depth",
            "shrink",
        ),
        ("implementation choices", "agreed", "goal", "scope", "contract", "record the reason"),
    ):
        assert_rule(body, *tokens)


def test_the_development_worker_result_is_self_contained() -> None:
    body = _contract("development-worker")[1]
    for tokens in (
        ("check off", "`devkit rules fix <unit>/spec.md`"),
        ("scratch", "ignored path", "inside the worktree"),
        ("`tmp_path`", "system temporary directory"),
        ("`--basetemp`", "command line", "not", "`PYTEST_ADDOPTS`"),
        ("Denied", "everything else", "pytest-managed fixtures"),
        # activity-effort decides the nested roles; the reconcile reviewer only verifies.
        ("`code-reviewer`", "`reconcile-reviewer`", "nested subagents"),
        ("Living Spec", "`reconcile.md`", "yourself"),
    ):
        assert_rule(body, *tokens)


# Planning steps an executor runs in either mode, moved out of the contract
# (ADR-executor-neutral-planning-steps-in-a-spec-reference): each phrase must be gone from the contract, and the
# reference must still state its rule (the tokens). Recording answers is stated once, in worker-records.md §2,
# which the reference points to (``MOVED_ANSWER_PHRASES``).
MOVED_PLANNING_PHRASES = {
    "Collect every question for the user in one round": ("every question", "one round"),
    "status: reviewing": ("first turn", "status: reviewing"),
    "needs_decompose: true": ("needs_decompose: true", "status: draft"),
    "--questions-file": ("`worker` envelope", "--questions-file"),
    "check `dev_effort` in `proposal.md`": ("before the final work commit", "`dev_effort`", "`proposal.md`"),
    "[planning run coverage]": ("[planning run coverage]",),
}
MOVED_ANSWER_PHRASES = {
    "as a commit of their own": ("records them first in a commit of its own", "separate commit"),
    "envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>": (
        "devkit workflow envelope answer --unit <dir>",
        "--answers-to worker-NN.yaml",
    ),
}


def test_the_planning_steps_live_in_the_spec_reference_for_any_executor() -> None:
    reference = raw(PLANNING)
    body = _contract("planning-worker")[1]
    for phrase, tokens in MOVED_PLANNING_PHRASES.items():
        assert_rule(reference, *tokens)
        assert phrase not in flat(body), phrase
    records = raw("skills/spec/references/worker-records.md")
    for phrase, tokens in MOVED_ANSWER_PHRASES.items():
        assert_rule(records, *tokens)
        assert phrase not in flat(body), phrase
    assert_rule(reference, "answers", "record them first", "[worker records](worker-records.md) §2", "then fold")
    assert_rule(reference, "runner", "`direct`", "`planning-worker`")
    assert "[planning](references/planning.md)" in text("skills/spec/SKILL.md")
    assert_rule(body, "follow", "`.devkit/managed/spec/skills/spec/references/planning.md`")


def test_the_planning_worker_keeps_its_worker_obligations() -> None:
    body = _contract("planning-worker")[1]
    for tokens in (
        ("`scout`", "`challenger`", "nested subagent"),
        ("wait", "every nested role", "before", "end the turn"),
        ("waiting for answers", "`needs_input`", "not a problem"),
        ("temporary probes", "only", "ignored path"),
    ):
        assert_rule(body, *tokens)


@pytest.mark.parametrize("role", [r for r in ROLES if r not in (*WORKERS, "git-operator")])
def test_every_other_role_stays_read_only(role: str) -> None:
    assert _contract(role)[0]["x-git-actions"] == ["read"]


def test_the_reconciler_verifies_and_never_drafts() -> None:
    metadata, body = _contract("reconcile-reviewer")
    assert "Write" not in metadata["hosts"]["claude-code"]["tools"]
    assert_rule(body, "fixing the reflection", "stay with the implementer")
    assert_rule(body, "fields", "`reconcile-check` envelope")  # recorded at living-spec-draft, whose exit reads it


def test_the_code_reviewer_leaves_reconcile_verification_to_its_own_role() -> None:
    body = _contract("code-reviewer")[1]
    assert_rule(body, "reconcile verification", "`reconcile-reviewer`")
    assert "`reconcile-check`" not in flat(body)
    assert_rule(body, "fields", "`review` envelope")


def test_spec_delegate_passes_only_the_payload_to_a_projected_role() -> None:
    delegate = raw(DELEGATE)
    assert_rule(delegate, "contract frontmatter", "first", "`x-git-actions`")
    assert_rule(delegate, "projected role", "only the payload")
    assert_rule(delegate, "`unsupported`", "main session", "contract body yourself")
    assert "Pass the role contract body" not in flat(delegate)
    assert "[payload](references/payload.md)" in flat(delegate)
    payload = raw(DELEGATE.parent / "references/payload.md")
    for role in ROLES:
        assert f"| `{role}` |" in payload, role


def test_tasks_name_the_docs_a_worker_must_write() -> None:
    assert_rule(raw(TASKS), "`development-worker`", "names the `docs/` paths", "write scope")


def test_the_host_validates_the_committed_range_and_blocks_a_failure() -> None:
    delegate = raw(DELEGATE)
    assert_rule(delegate, "worker", "commits only", "activity branch")
    assert_rule(delegate, "for a worker", "validate the committed range", "[worker](references/worker.md)")
    results = raw(WORKER_RESULTS)
    for tokens in (
        ("range", "`<accepted>`", "`<returned>`", "passes when"),
        ("`<accepted>`", "`diff_scope.head`", "ancestors of `<returned>`"),
        ("diff --name-only <accepted> <returned>`", "write scope"),
        ("`<returned>` adds this turn's `worker` envelope", "absent at `<accepted>`"),
        ("worktree's HEAD is `<returned>`",),
        ("the worktree is clean",),
        ("envelopes you committed", "exempt only while unchanged"),
        ("record the violation", "`worker` envelope"),
        ("never reset or amend", "pull request", "blocked"),
        ("validate again", "same last accepted head"),
        ("blocked:", "head its blocked range started from", "never the current HEAD"),
        ("unaccountable after context loss", "merge base", "base branch"),
    ):
        assert_rule(results, *tokens)
    assert "envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem" in flat(results)
    assert "`validation`" not in flat(results)
    records = raw("skills/spec/references/worker-records.md")
    assert_rule(records, "`[BLOCKED: ...]`", "no `resolution`")
    assert_rule(records, "`[BLOCKED: ...]`", "handoff", "`devkit worktree finish --merge`")
    assert_rule(records, "only a `resolution`", "clears")


def test_worker_validation_records_and_compares_no_base_checkout() -> None:
    # ADR-drop-the-base-checkout-equality-from-worker-validation: base advances never block a worker's range.
    results = raw(WORKER_RESULTS)
    payload = raw(DELEGATE.parent / "references/payload.md")
    for document in (results, payload):
        assert not states_rule(document, "base checkout", "before spawning")
        assert not states_rule(document, "base checkout", "status and HEAD")
    assert_rule(results, "base advances", "never block the range", "no base merge")
    assert_rule(results, "accepted residual", "base branch", "passes every condition")


def test_orchestration_follows_the_committed_result_contract() -> None:
    orchestrate = raw(ORCHESTRATE)
    for tokens in (
        ("**Validate**", "committed range", "`spec-delegate`", "worker reference"),
        ("failing range", "blocked", "never discarded"),
        ("every unit", "integrated", "blocked with its problem recorded"),
        ("`session`-depth task", "never becomes a unit"),
        ("`local-orchestrated`", "changes no gate", "no approval"),
        ("`local-orchestrated`", "preserve an explicit user preference"),
    ):
        assert_rule(orchestrate, *tokens)


def test_a_run_records_its_questions_and_problem_in_one_worker_envelope() -> None:
    records = raw("skills/spec/references/worker-records.md")
    assert_rule(records, "one run", "one `worker` envelope")
    assert_rule(records, "no separate", "question or problem kind")
    assert "--answers-to worker-NN.yaml" in flat(records) and "--resolves worker-NN.yaml" in flat(records)
    planning = text(PLANNING)
    assert "--questions-file" in planning and "[worker records](worker-records.md) §2" in planning
    development = _contract("development-worker")[1]
    assert_rule(development, "end the turn", "exactly one `worker` envelope")
    assert_rule(development, "recovery request", '"Problems and resolutions"', "`worker-records.md`")


@pytest.mark.parametrize("role", WORKERS)
def test_real_worker_projects_complete_emulated_codex_toml(role: str) -> None:
    source = BUNDLE / f"subagents/{role}.md"
    contract = read_contract(raw(source).encode(), str(source))
    rendered = render_projection("codex", contract, f".devkit/managed/spec/subagents/{role}.md")
    assert rendered is not None
    projection = tomllib.loads(rendered.decode())
    assert set(projection) == {"name", "description", "sandbox_mode", "developer_instructions"}
    assert projection["name"] == role
    assert projection["sandbox_mode"] == "workspace-write"
    prompt = projection["developer_instructions"]
    assert prompt.endswith(contract.body.rstrip("\n") + "\n")
    prose = flat(prompt)
    assert "Host projection: emulated." in prose
    assert "The host does not enforce the contract's boundaries itself" in prose
    assert "## Procedure" in prose and "## Write boundaries" in prose
    assert_rule(prompt, "Codex", "`workspace-write`", "confines no path")


@pytest.mark.parametrize("role", WORKERS)
def test_worker_other_host_settings_are_preserved(role: str) -> None:
    hosts = _contract(role)[0]["hosts"]
    assert hosts["claude-code"] == {
        "status": "native",
        "tools": ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent"],
    }
    assert hosts["antigravity"] == {
        "status": "unverified",
        "tools": ["view_file", "grep_search", "replace_file_content", "run_command"],
        "commandExecutionPolicy": "sandbox",
    }


@pytest.mark.parametrize("role", WORKERS)
def test_worker_requires_explicit_paths_and_each_operation_approval(role: str) -> None:
    body = _contract(role)[1]
    for tokens in (
        ("every command's cwd", "`git -C <worktree>`"),
        ("nested", "absolute read scopes", "contract paths", "pass on any read"),
        ("Codex", "`workspace-write` confines no path"),
        ("separate approval for each operation", "operation, target and reason"),
        ("sibling-worktree writes", "shared Git", "network"),
        ("no broad persistent prefix", "no earlier grant"),
    ):
        assert_rule(body, *tokens)


@pytest.mark.parametrize("role", WORKERS)
def test_worker_refusal_and_failed_emergency_preservation_are_truthful(role: str) -> None:
    body = _contract(role)[1]
    for tokens in (
        ("refused or unavailable approval", "stop that operation", "preserve the state"),
        ("refused or unavailable approval", "never reroute", "tool", "path", "process", "setting"),
        ("emergency commit", "worker-records.md", "Host decides"),
    ):
        assert_rule(body, *tokens)
    records = raw("skills/spec/references/worker-records.md")
    for tokens in (
        ("only this commit", "`git commit --no-verify`", "ordinary commit-gate refusal"),
        ("--no-verify", "never for sandbox or approval denial"),
        ("refused or unavailable approval", "stop that operation", "preserve the state", "never reroute"),
        ("record or commit itself is denied", "preserve the state", "`failed`"),
        ("`failed`", "actual last commit", "dirty paths", "absent/uncommitted"),
        ("record or commit itself is denied", "never invent a committed envelope"),
    ):
        assert_rule(records, *tokens)


def test_named_and_generic_native_invocation_respect_trust_and_effective_contract() -> None:
    hosts = raw(DELEGATE.parent / "references/hosts.md")
    for tokens in (
        ("projected named role", "only the payload"),
        ("missing role", "does not prove", "untrusted"),
        ("availability separately from trust",),
        ("cannot load", "project-instruction loading is permitted", "generic native subagent"),
        ("effective managed/override contract", "absolute path", "report the emulation"),
        ("never substitute the upstream contract", "override"),
        ("explicit host trust restriction", "stops", "do not bypass", "role", "tool", "path", "host setting"),
        ("start a worker only when", "native spawning", "nested roles", "approval capability"),
        ("`direct` when allowed", "`needs_input`", "isolation is required"),
        ("availability", "does not promise", "approval"),
    ):
        assert_rule(hosts, *tokens)
    assert "stop and ask the user to register the root" not in flat(hosts)
    payload = raw(DELEGATE.parent / "references/payload.md")
    assert_rule(payload, "absolute paths", "nested-role reads", "startup skills", "effective role contract")


def test_callers_block_permission_failures_without_fabricated_worker_records() -> None:
    results = raw(WORKER_RESULTS)
    records = raw("skills/spec/references/worker-records.md")
    assert_rule(results, "never write", "worker's records")
    for tokens in (
        ("**Failed without a committed envelope**", "dirty or uncommitted", "block it"),
        ("**Failed without a committed envelope**", "inspect the actual HEAD and status", "scope"),
        ("**Failed without a committed envelope**", "never commit its dirty paths as your own"),
        ("**Failed without a committed envelope**", "record the failure in your own envelope", "when permitted"),
    ):
        assert_rule(results, *tokens)
    assert_rule(records, "actual last", "dirty paths", "absent/uncommitted")
    assert_rule(records, "ordinary commit-gate refusal", "never for sandbox or approval denial")


def test_a_condition_free_spike_completion_is_not_planning_evidence() -> None:
    planning = raw(PLANNING)
    signals = raw("skills/spec-next/references/workflow-signals.md")
    assert_rule(planning, "`devkit workflow next`", "`spike`", "done before any review")
    assert_rule(planning, "only the recorded", "`scout`", "`challenger`", "`reverify`", "Planning evidence")
    assert_rule(signals, "`[DONE: ... spike]`", "not Planning evidence")
    assert_rule(signals, "`scout`", "`challenger`", "`reverify`", "recorded at `spike`")


@pytest.mark.parametrize(
    "host,expected_model", [("claude-code", "haiku"), ("codex", "gpt-6-luna"), ("antigravity", "flash")]
)
def test_scout_projection_selects_lightweight_family_and_omits_effort(host: str, expected_model: str) -> None:
    contract = read_contract(raw("subagents/scout.md").encode(), "scout", "scout")
    rendered = render_projection(host, contract, "contract.md")
    assert rendered is not None
    metadata = (
        tomllib.loads(rendered.decode()) if host == "codex" else yaml.safe_load(rendered.decode().split("---\n")[1])
    )
    assert metadata["model"] == expected_model
    assert not {"effort", "model_reasoning_effort", "level"} & metadata.keys()
