"""The role contracts' bodies are the subagents' prompts; caller guidance lives in ``spec-delegate``."""

from __future__ import annotations

import copy
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml
from devkit_dist.features.distribution.services.bundles.subagents import read_contract, render_projection

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
WORKERS = ("development-worker", "planning-worker")
ROLES = ("challenger", "reconcile-reviewer", "code-reviewer", "scout", *WORKERS)
DELEGATE = BUNDLE / "skills/spec-delegate/SKILL.md"
WORKER_RESULTS = BUNDLE / "skills/spec-delegate/references/worker.md"
ORCHESTRATE = BUNDLE / "skills/spec-orchestrate/SKILL.md"
TASKS = BUNDLE / "skills/spec-tasks/SKILL.md"
PLANNING = BUNDLE / "skills/spec/references/planning.md"
# ADR-role-effort-presets: role -> (x-model-profile, reasoning effort preset). The workers set none and run at the
# session's effort; Antigravity has no effort key; no contract names a model.
EFFORT_PRESETS: dict[str, tuple[str, str | None]] = {
    "scout": ("light-medium", "medium"),
    "reconcile-reviewer": ("light-medium", "medium"),
    "code-reviewer": ("general-high", "high"),
    "challenger": ("high-reasoning", "high"),
    "planning-worker": ("general-high", None),
    "development-worker": ("general-high", None),
}


def _contract(role: str) -> tuple[dict[str, Any], str]:
    _, frontmatter, body = _rendered(BUNDLE / f"subagents/{role}.md").split("---\n", 2)
    return yaml.safe_load(frontmatter), body


def _preset_violations(role: str, metadata: dict[str, Any]) -> list[str]:
    profile, preset = EFFORT_PRESETS[role]
    hosts = metadata["hosts"]
    violations = []
    if metadata.get("x-model-profile") != profile:
        violations.append(f"x-model-profile is {metadata.get('x-model-profile')!r}, expected {profile!r}")
    if hosts["claude-code"].get("effort") != preset:
        violations.append(f"claude-code effort is {hosts['claude-code'].get('effort')!r}, expected {preset!r}")
    codex_preset = None if hosts["codex"]["status"] == "unsupported" else preset
    if hosts["codex"].get("model_reasoning_effort") != codex_preset:
        violations.append(
            f"codex model_reasoning_effort is {hosts['codex'].get('model_reasoning_effort')!r}, expected {codex_preset!r}"
        )
    violations += [f"antigravity sets {key}" for key in hosts["antigravity"] if "effort" in key]
    violations += [f"{host} names a model" for host, block in hosts.items() if "model" in block]
    return violations


def test_every_role_contract_has_an_effort_preset_entry() -> None:
    assert {
        path.name.removesuffix(".jinja").removesuffix(".md") for path in (BUNDLE / "subagents").glob("*.md*")
    } == set(EFFORT_PRESETS)
    assert set(ROLES) == set(EFFORT_PRESETS)


@pytest.mark.parametrize("role", sorted(EFFORT_PRESETS))
def test_a_role_presets_the_reasoning_effort_of_its_profile(role: str) -> None:
    assert _preset_violations(role, _contract(role)[0]) == []


@pytest.mark.parametrize(
    ("role", "host", "key", "value"),
    [
        ("code-reviewer", None, "x-model-profile", "light-medium"),
        ("code-reviewer", "claude-code", "effort", "medium"),
        ("scout", "codex", "model_reasoning_effort", "high"),
        ("development-worker", "claude-code", "effort", "high"),
        ("challenger", "antigravity", "reasoning_effort", "high"),
        ("reconcile-reviewer", "claude-code", "model", "some-model"),
    ],
)
def test_a_drifted_preset_is_a_violation(role: str, host: str | None, key: str, value: str) -> None:
    metadata = copy.deepcopy(_contract(role)[0])
    (metadata if host is None else metadata["hosts"][host])[key] = value
    assert _preset_violations(role, metadata)


def test_the_challenger_leaves_the_model_to_the_runtime() -> None:
    text = _rendered(BUNDLE / "subagents/challenger.md")
    assert "Choose a high-reasoning model at invocation time" not in text
    assert "# The reasoning effort is preset per role; the model is left to the runtime." in text


@pytest.mark.parametrize("role", ("scout", "challenger"))
def test_a_subagent_only_procedure_lives_in_the_contract(role: str) -> None:
    metadata, body = _contract(role)
    assert "skill" not in metadata
    assert "\n## Procedure\n" in body and "\n## Return\n" in body
    assert not (BUNDLE / f"skills/spec-{role}").exists()


@pytest.mark.parametrize("role", ROLES)
def test_a_contract_body_holds_only_the_role_prompt(role: str) -> None:
    _, body = _contract(role)
    assert "## Host projection notes" not in body
    assert "## Safety conditions" not in body
    assert "the Developer records them" not in body


def test_reviewer_and_reconciler_keep_the_skills_the_main_session_shares() -> None:
    assert _contract("code-reviewer")[0]["skill"] == "spec-review"
    assert _contract("reconcile-reviewer")[0]["skill"] == "spec-sync"


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
    assert "git -C <worktree>" in body and "absolute" in body
    assert "Git: commit only; never push, merge, rebase, reset, amend, stash or check out." in body
    assert "`worker` envelope" in body and "worker-records.md" in body
    assert "`final_head`: `git -C <worktree> rev-parse HEAD` after the commit that adds the envelope" in body
    assert "do not write envelope files" not in body


def test_the_development_worker_commits_at_stage_boundaries_and_on_a_problem() -> None:
    body = " ".join(_contract("development-worker")[1].split())
    assert "Commit at every stage boundary with write-scope paths only" in body
    assert "only that commit may use `--no-verify`" in body
    assert "One path outside the write scope rejects the whole result" in body
    assert "make the emergency commit" in body
    assert "You do not split units, push, merge, integrate, revert, close, raise the planning depth or shrink" in body
    assert "Decide implementation choices inside the agreed goal, scope and contract and record the reason" in body


def test_the_development_worker_result_is_self_contained() -> None:
    body = " ".join(_contract("development-worker")[1].split())
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
    reference = " ".join(PLANNING.read_text(encoding="utf-8").split())
    body = " ".join(_contract("planning-worker")[1].split())
    for phrase in MOVED_PLANNING_PHRASES:
        assert phrase in reference, phrase
        assert phrase not in body, phrase
    assert "the Host in `direct` mode or a `planning-worker`" in reference
    assert "[planning](references/planning.md)" in _rendered(BUNDLE / "skills/spec/SKILL.md")
    assert "Follow `.devkit/managed/spec/skills/spec/references/planning.md`" in body


def test_the_planning_worker_keeps_its_worker_obligations() -> None:
    body = " ".join(_contract("planning-worker")[1].split())
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
    assert "Writing and fixing the reflection stay with the implementer" in body
    assert "The fields of a `reconcile-check` envelope" in body  # recorded at living-spec-draft, whose exit reads it


def test_the_code_reviewer_leaves_reconcile_verification_to_its_own_role() -> None:
    _, body = _contract("code-reviewer")
    assert "Reconcile verification belongs to `reconcile-reviewer`" in body
    assert "`reconcile-check`" not in body
    assert "The fields of the `review` envelope" in body


def test_spec_delegate_passes_only_the_payload_to_a_projected_role() -> None:
    text = DELEGATE.read_text(encoding="utf-8")
    assert "Read the contract frontmatter first" in text
    assert "Give a projected role only the payload" in text
    assert "substitute in the main session and follow the contract body yourself" in text
    assert "Pass the role contract body" not in text
    assert "[payload](references/payload.md)" in text
    payload = _rendered(DELEGATE.parent / "references/payload.md")
    for role in ROLES:
        assert f"| `{role}` |" in payload, role


def test_tasks_name_the_docs_a_worker_must_write() -> None:
    text = " ".join(TASKS.read_text(encoding="utf-8").split())
    assert "A task a `development-worker` builds also names the `docs/` paths its checks require" in text


def test_the_host_validates_the_committed_range_and_blocks_a_failure() -> None:
    delegate = " ".join(DELEGATE.read_text(encoding="utf-8").split())
    assert "a worker commits only on its activity branch" in delegate
    assert "For a worker, validate the committed range per [worker](references/worker.md)" in delegate
    text = " ".join(WORKER_RESULTS.read_text(encoding="utf-8").split())
    assert "The range from `<accepted>` to the returned final HEAD `<returned>`" in text
    assert "`<accepted>` and the envelope's `diff_scope.head` are ancestors of `<returned>`" in text
    assert "diff --name-only <accepted> <returned>` is in the write scope" in text
    assert "The worktree is clean" in text
    assert "the base checkout's status and HEAD match what you recorded before spawning" in text
    assert "envelopes you committed since `<accepted>` are exempt only while unchanged since your commit" in text
    assert "`validation`" not in text
    assert "Record the violation as your own `worker` envelope" in text
    assert "envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem" in text
    assert "Never reset or amend; keep a pull request open and blocked" in text
    assert "Validate again from the same last accepted head" in text
    assert "Blocked: the head its blocked range started from, never the current HEAD" in text
    assert "Unaccountable after context loss: the branch's merge base with the base branch" in text
    records = " ".join(_rendered(BUNDLE / "skills/spec/references/worker-records.md").split())
    assert "`[BLOCKED: ...]` means a problem has no `resolution` naming it" in records
    assert "the handoff and `devkit worktree finish --merge`" in records
    assert "Only a `resolution` clears it" in records


def test_orchestration_follows_the_committed_result_contract() -> None:
    text = " ".join(_rendered(ORCHESTRATE).split())
    assert "**Validate** the committed range through `spec-delegate`'s worker reference" in text
    assert "A failing range is blocked, never discarded" in text
    assert "blocked with its problem recorded" in text
    assert "A `session`-depth task never becomes a unit" in text
    assert "The mode changes no gate, policy or authority, needs no approval" in text
    assert "preserve an explicit user preference" in text


def test_a_run_records_its_questions_and_problem_in_one_worker_envelope() -> None:
    records = " ".join(_rendered(BUNDLE / "skills/spec/references/worker-records.md").split())
    assert "one run leaves one `worker` envelope" in records
    assert "--answers-to worker-NN.yaml" in records and "--resolves worker-NN.yaml" in records
    assert "There is no separate question or problem kind" in records
    planning = " ".join(PLANNING.read_text(encoding="utf-8").split())
    assert (
        "--questions-file" in planning
        and "envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>" in planning
    )
    development = " ".join(_contract("development-worker")[1].split())
    assert "exactly one `worker` envelope" in development
    assert 'follow "Problems and resolutions" in `worker-records.md`' in development


@pytest.mark.parametrize("role", WORKERS)
def test_real_worker_projects_complete_emulated_codex_toml(role: str) -> None:
    source = BUNDLE / f"subagents/{role}.md"
    contract = read_contract(_rendered(source).encode(), str(source))
    rendered = render_projection("codex", contract, f".devkit/managed/spec/subagents/{role}.md")
    assert rendered is not None
    projection = tomllib.loads(rendered.decode())
    assert set(projection) == {"name", "description", "sandbox_mode", "developer_instructions"}
    assert projection["name"] == role
    assert projection["sandbox_mode"] == "workspace-write"
    prompt = projection["developer_instructions"]
    assert "Host projection: emulated." in prompt
    assert "The host does not enforce the contract's boundaries itself" in prompt
    assert prompt.endswith(contract.body.rstrip("\n") + "\n")
    assert "## Procedure" in prompt and "On Codex, `workspace-write` confines no path" in prompt
    assert "## Write boundaries" in prompt


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
    body = " ".join(_contract(role)[1].split())
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
    body = " ".join(_contract(role)[1].split())
    for requirement in (
        "On a refused or unavailable approval, stop that operation and preserve the state",
        "never reroute through another tool, path, process or setting",
        "emergency commit",
        "worker-records.md",
        "Host decides",
    ):
        assert requirement in body, (role, requirement)
    records = " ".join(_rendered(BUNDLE / "skills/spec/references/worker-records.md").split())
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
    hosts = " ".join(_rendered(DELEGATE.parent / "references/hosts.md").split())
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
    payload = " ".join(_rendered(DELEGATE.parent / "references/payload.md").split())
    assert "Name absolute paths for nested-role reads" in payload
    assert "the worktree's own startup skills and instructions and the effective role contract" in payload


def test_callers_block_permission_failures_without_fabricated_worker_records() -> None:
    results = " ".join(WORKER_RESULTS.read_text().split())
    records = " ".join(_rendered(BUNDLE / "skills/spec/references/worker-records.md").split())
    assert "Never write a worker's records for it" in results
    assert "**Failed without a committed envelope** (dirty or uncommitted" in results and "block it" in results
    assert "Inspect the actual HEAD and status against the scope" in results
    assert "never commit its dirty paths as your own" in results
    assert "record the failure in your own envelope when permitted" in results
    assert "actual last" in records and "dirty paths" in records and "absent/uncommitted" in records
    assert "ordinary commit-gate refusal" in records and "never for sandbox or approval denial" in records


def _rendered(path: Path) -> str:
    from devkit_dist.features.distribution.services.bundles.templates import render_template

    if path.name.endswith(".md.jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment="local").decode()
    if path.exists():
        return path.read_text(encoding="utf-8")
    source = path.with_name(path.name + ".jinja")
    return render_template(source.read_bytes(), {}, str(source), environment="local").decode()


def test_a_condition_free_spike_completion_is_not_planning_evidence() -> None:
    planning = " ".join(PLANNING.read_text(encoding="utf-8").split())
    signals = " ".join(_rendered(BUNDLE / "skills/spec-next/references/workflow-signals.md").split())
    assert "`devkit workflow next` may list `spike` as done before any review ran" in planning
    assert "only the recorded `scout`, `challenger` and `reverify` envelopes are Planning evidence" in planning
    assert "`[DONE: ... spike]` is not Planning evidence" in signals
    assert "`scout` and `challenger` envelopes and their `reverify` recorded at `spike`" in signals
