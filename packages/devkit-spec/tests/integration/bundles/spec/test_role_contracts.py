"""The role contracts' bodies are the subagents' prompts; caller guidance lives in ``spec-delegate``."""

from __future__ import annotations

import tomllib
from typing import Any

import pytest
import yaml
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection
from spec_support.bundle_text import BUNDLE, flat, raw, text

WORKERS = ("development-worker", "planning-worker")
BACKLOG_ROLES = ("triage", "decomposer")
ROLES = ("challenger", "reconcile-reviewer", "code-reviewer", "ux-reviewer", "scout", *BACKLOG_ROLES, *WORKERS)
DELEGATE = BUNDLE / "skills/spec-delegate/SKILL.md"
WORKER_RESULTS = BUNDLE / "skills/spec-delegate/references/worker.md"
ORCHESTRATE = BUNDLE / "skills/spec-orchestrate/SKILL.md"
TASKS = BUNDLE / "skills/spec-tasks/SKILL.md"
PLANNING = BUNDLE / "skills/spec/references/planning.md"


def _contract(role: str) -> tuple[dict[str, Any], str]:
    _, frontmatter, body = raw(f"subagents/{role}.md").split("---\n", 2)
    return yaml.safe_load(frontmatter), body


@pytest.mark.parametrize("role", ROLES)
def test_scout_is_compact_and_other_roles_inherit(role: str) -> None:
    metadata, _ = _contract(role)
    assert "x-model-profile" not in metadata
    if role == "scout":
        assert metadata["level"] == "compact"
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
    body = flat(body)
    assert "Modify, stage and commit nothing" in body and "Give no finding a severity" in body
    skill = text("skills/spec-ux-review/SKILL.md")
    for phrase in (
        "Will the actor try to do the right thing here?",
        "Will the actor notice that the control for it is available?",
        "Will the actor connect the control with the goal?",
        "will the actor see progress toward the goal?",
        "Score each screen 0, 1 or 2",
        "**R1 task fit**",
        "**R2 one primary region**",
        "**R3 states**",
        "**R4 feedback**",
        "**R5 terms**",
        "**R6 objects**",
        "`link check (reviewer judgment)`",
        "keep it out of the rubric",
        "Findings carry no severity",
        "--kind ux-review",
        "At most two rounds per unit",
        "`resolution: resolved`, or `resolution: waived` and a `waiver` reason",
        "never a stage",
    ):
        assert phrase in skill, phrase
    assert "severity:" not in skill


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
    body = flat(body)
    assert "Run `uv run devkit get-context spec` once" in body
    assert f"`{BACKLOG_PROCEDURES[role]}`" in body
    assert "Modify, stage and commit nothing" in body
    assert "`diff_scope.head`" in body and "`failure_condition`" in body
    bundle = tomllib.loads(raw("bundle.toml"))
    assert {"id": role, "kind": "subagent", "source": f"subagents/{role}.md"} in bundle["assets"]
    assert role in bundle["presets"]["core"]["assets"]


def test_triage_returns_groups_and_never_changes_a_status() -> None:
    body = flat(_contract("triage")[1])
    for phrase in (
        "Apply its Step 1",
        "Apply its Step 2 table to each group: one recommended destination with its reason",
        "duplicate",
        "dismissal candidate",
        "never run Step 3",
        "the group's FB IDs, its target and its confirmed ownership",
    ):
        assert phrase in body, phrase


def test_the_decomposer_returns_children_edges_and_an_exit_without_feedback_assignment() -> None:
    body = flat(_contract("decomposer")[1])
    for phrase in (
        "`uv run devkit docs refs PROP-<slug> --direction in -n 0`",
        "return `needs_input` with the reason",
        "every child is below `size: XL`",
        "a proposed `slug` (one that `devkit docs resolve PROP-<slug>` does not find), `title`, English `summary`, `scope`",
        "`planning_effort` and `dev_effort` chosen afresh, `boundaries` by nearest existing parent, `depends_on` edges",
        "the parent PADRs, answers and materials it inherits, or none",
        "`incoming_edges`",
        "`exit`: `split` or `promote` with the reason",
        "never assign or copy an item to a child",
    ):
        assert phrase in body, phrase


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
    body = flat(body)
    assert "git -C <worktree>" in body and "absolute" in body
    assert "Git: commit only; never push, merge, rebase, reset, amend, stash or check out." in body
    assert "`worker` envelope" in body and "worker-records.md" in body
    assert "`final_head`: `git -C <worktree> rev-parse HEAD` after the commit that adds the envelope" in body
    assert "do not write envelope files" not in body


def test_the_development_worker_commits_at_stage_boundaries_and_on_a_problem() -> None:
    body = flat(_contract("development-worker")[1])
    assert "Commit at every stage boundary with write-scope paths only" in body
    assert "only that commit may use `--no-verify`" in body
    assert "One path outside the write scope rejects the whole result" in body
    assert "make the emergency commit" in body
    assert "You do not split units, push, merge, integrate, revert, close, raise the planning depth or shrink" in body
    assert "Decide implementation choices inside the agreed goal, scope and contract and record the reason" in body


def test_the_development_worker_result_is_self_contained() -> None:
    body = flat(_contract("development-worker")[1])
    assert "run `devkit rules fix <unit>/spec.md`" in body
    assert "Keep authored scratch files in an ignored path inside the worktree" in body
    assert "Pytest-managed fixtures (`tmp_path`) may use an isolated system temporary directory" in body
    assert "pass `--basetemp` on the command line, not through `PYTEST_ADDOPTS`" in body
    assert "Denied: everything else except pytest-managed fixtures" in body
    # activity-effort decides the nested roles; the reconcile reviewer only verifies.
    assert "Run `code-reviewer` and `reconcile-reviewer` as nested subagents" in body
    assert "Write and fix the Living Spec changes and `reconcile.md` yourself" in body


# Planning steps an executor runs in either mode, moved out of the contract
# (ADR-executor-neutral-planning-steps-in-a-spec-reference).
MOVED_PLANNING_PHRASES = (
    "Collect every question for the user in one round",
    "as a commit of their own",
    "status: reviewing",
    "needs_decompose: true",
    "envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>",
    "--questions-file",
    "check `dev_effort` in `proposal.md`",
    "[planning run coverage]",
)


def test_the_planning_steps_live_in_the_spec_reference_for_any_executor() -> None:
    reference = text(PLANNING)
    body = flat(_contract("planning-worker")[1])
    for phrase in MOVED_PLANNING_PHRASES:
        assert phrase in reference, phrase
        assert phrase not in body, phrase
    assert "the Host in `direct` mode or a `planning-worker`" in reference
    assert "[planning](references/planning.md)" in text("skills/spec/SKILL.md")
    assert "Follow `.devkit/managed/spec/skills/spec/references/planning.md`" in body


def test_the_planning_worker_keeps_its_worker_obligations() -> None:
    body = flat(_contract("planning-worker")[1])
    assert "Start each `scout` or `challenger` as a nested subagent" in body
    assert "Wait for every nested role before you rely on its result or end the turn" in body
    assert "Waiting for answers is `needs_input`, not a problem" in body
    assert "Temporary probes: only the ignored path the payload names" in body


@pytest.mark.parametrize("role", [r for r in ROLES if r not in WORKERS])
def test_every_other_role_stays_read_only(role: str) -> None:
    assert _contract(role)[0]["x-git-actions"] == ["read"]


def test_the_reconciler_verifies_and_never_drafts() -> None:
    metadata, body = _contract("reconcile-reviewer")
    assert "Write" not in metadata["hosts"]["claude-code"]["tools"]
    body = flat(body)
    assert "Writing and fixing the reflection stay with the implementer" in body
    assert "The fields of a `reconcile-check` envelope" in body  # recorded at living-spec-draft, whose exit reads it


def test_the_code_reviewer_leaves_reconcile_verification_to_its_own_role() -> None:
    body = flat(_contract("code-reviewer")[1])
    assert "Reconcile verification belongs to `reconcile-reviewer`" in body
    assert "`reconcile-check`" not in body
    assert "The fields of the `review` envelope" in body


def test_spec_delegate_passes_only_the_payload_to_a_projected_role() -> None:
    delegate = text(DELEGATE)
    assert "Read the contract frontmatter first" in delegate
    assert "Give a projected role only the payload" in delegate
    assert "substitute in the main session and follow the contract body yourself" in delegate
    assert "Pass the role contract body" not in delegate
    assert "[payload](references/payload.md)" in delegate
    payload = raw(DELEGATE.parent / "references/payload.md")
    for role in ROLES:
        assert f"| `{role}` |" in payload, role


def test_tasks_name_the_docs_a_worker_must_write() -> None:
    assert "A task a `development-worker` builds also names the `docs/` paths its checks require" in text(TASKS)


def test_the_host_validates_the_committed_range_and_blocks_a_failure() -> None:
    delegate = text(DELEGATE)
    assert "a worker commits only on its activity branch" in delegate
    assert "For a worker, validate the committed range per [worker](references/worker.md)" in delegate
    results = text(WORKER_RESULTS)
    assert "The range from `<accepted>` to the returned final HEAD `<returned>`" in results
    assert "`<accepted>` and the envelope's `diff_scope.head` are ancestors of `<returned>`" in results
    assert "diff --name-only <accepted> <returned>` is in the write scope" in results
    assert "The worktree is clean" in results
    assert "the base checkout's status and HEAD match what you recorded before spawning" in results
    assert "envelopes you committed since `<accepted>` are exempt only while unchanged since your commit" in results
    assert "`validation`" not in results
    assert "Record the violation as your own `worker` envelope" in results
    assert "envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem" in results
    assert "Never reset or amend; keep a pull request open and blocked" in results
    assert "Validate again from the same last accepted head" in results
    assert "Blocked: the head its blocked range started from, never the current HEAD" in results
    assert "Unaccountable after context loss: the branch's merge base with the base branch" in results
    records = text("skills/spec/references/worker-records.md")
    assert "`[BLOCKED: ...]` means a problem has no `resolution` naming it" in records
    assert "the handoff and `devkit worktree finish --merge`" in records
    assert "Only a `resolution` clears it" in records


def test_orchestration_follows_the_committed_result_contract() -> None:
    orchestrate = text(ORCHESTRATE)
    assert "**Validate** the committed range through `spec-delegate`'s worker reference" in orchestrate
    assert "A failing range is blocked, never discarded" in orchestrate
    assert "blocked with its problem recorded" in orchestrate
    assert "A `session`-depth task never becomes a unit" in orchestrate
    assert "The mode changes no gate, policy or authority, needs no approval" in orchestrate
    assert "preserve an explicit user preference" in orchestrate


def test_a_run_records_its_questions_and_problem_in_one_worker_envelope() -> None:
    records = text("skills/spec/references/worker-records.md")
    assert "one run leaves one `worker` envelope" in records
    assert "--answers-to worker-NN.yaml" in records and "--resolves worker-NN.yaml" in records
    assert "There is no separate question or problem kind" in records
    planning = text(PLANNING)
    assert (
        "--questions-file" in planning
        and "envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>" in planning
    )
    development = flat(_contract("development-worker")[1])
    assert "exactly one `worker` envelope" in development
    assert 'follow "Problems and resolutions" in `worker-records.md`' in development


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
    assert "## Procedure" in prose and "On Codex, `workspace-write` confines no path" in prose
    assert "## Write boundaries" in prose


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
    body = flat(_contract(role)[1])
    for requirement in (
        "every command's cwd set to",
        "`git -C <worktree>` for Git",
        "with absolute read scopes and contract paths in this worktree",
        "pass on any read",
        "`workspace-write` confines no path",
        "Request a separate approval for each operation outside sandbox access, naming the operation, target and reason",
        "(sibling-worktree writes, shared Git, network for verification)",
        "use no broad persistent prefix and treat no earlier grant as later permission",
    ):
        assert requirement in body, (role, requirement)


@pytest.mark.parametrize("role", WORKERS)
def test_worker_refusal_and_failed_emergency_preservation_are_truthful(role: str) -> None:
    body = flat(_contract(role)[1])
    for requirement in (
        "On a refused or unavailable approval, stop that operation and preserve the state",
        "never reroute through another tool, path, process or setting",
        "emergency commit",
        "worker-records.md",
        "Host decides",
    ):
        assert requirement in body, (role, requirement)
    records = text("skills/spec/references/worker-records.md")
    for requirement in (
        "Only this commit may use `git commit --no-verify`, and only on ordinary commit-gate refusal",
        "never for sandbox or approval denial",
        "stop that operation and preserve the state; never reroute through another tool, path, process",
        "If the record or commit itself is denied, stop, preserve the state and return `failed`",
        "the actual last commit, dirty paths and the absent/uncommitted record or commit",
        "never invent a committed envelope",
    ):
        assert requirement in records, requirement


def test_named_and_generic_native_invocation_respect_trust_and_effective_contract() -> None:
    hosts = text(DELEGATE.parent / "references/hosts.md")
    for requirement in (
        "Give a projected named role only the payload",
        "A missing role does not prove the root is untrusted",
        "diagnose availability separately from trust",
        "effective managed/override contract by absolute path",
        "host project-instruction loading is permitted",
        "report the emulation",
        "Never substitute the upstream contract for an override",
        "An explicit host trust restriction stops this fallback",
        "do not bypass it with another role, tool, path or host setting",
        "Start a worker only when native spawning, its nested roles and the approval capability",
        "run the unit in `direct` when allowed, or stop with `needs_input` when isolation is required",
        "Availability does not promise an approval",
    ):
        assert requirement in hosts, requirement
    assert "stop and ask the user to register the root" not in hosts
    payload = text(DELEGATE.parent / "references/payload.md")
    assert "Name absolute paths for nested-role reads" in payload
    assert "the worktree's own startup skills and instructions and the effective role contract" in payload


def test_callers_block_permission_failures_without_fabricated_worker_records() -> None:
    results = text(WORKER_RESULTS)
    records = text("skills/spec/references/worker-records.md")
    assert "Never write a worker's records for it" in results
    assert "**Failed without a committed envelope** (dirty or uncommitted" in results and "block it" in results
    assert "Inspect the actual HEAD and status against the scope" in results
    assert "never commit its dirty paths as your own" in results
    assert "record the failure in your own envelope when permitted" in results
    assert "actual last" in records and "dirty paths" in records and "absent/uncommitted" in records
    assert "ordinary commit-gate refusal" in records and "never for sandbox or approval denial" in records


def test_a_condition_free_spike_completion_is_not_planning_evidence() -> None:
    planning = text(PLANNING)
    signals = text("skills/spec-next/references/workflow-signals.md")
    assert "`devkit workflow next` may list `spike` as done before any review ran" in planning
    assert "only the recorded `scout`, `challenger` and `reverify` envelopes are Planning evidence" in planning
    assert "`[DONE: ... spike]` is not Planning evidence" in signals
    assert "`scout` and `challenger` envelopes and their `reverify` recorded at `spike`" in signals


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
