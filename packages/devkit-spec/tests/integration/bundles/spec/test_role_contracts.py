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
    assert (
        "# The reasoning effort is preset per role (ADR-role-effort-presets); the model is left to the runtime." in text
    )


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
    assert "Do not push, merge, rebase, reset, amend, stash or check out (`MUST NOT`)" in body
    assert "devkit workflow envelope worker" in body and "`worker` envelope" in body
    assert "`head` set to your last work commit" in body and "`final_head`" in body
    assert "do not write envelope files" not in body


def test_the_development_worker_commits_at_stage_boundaries_and_on_a_problem() -> None:
    body = " ".join(_contract("development-worker")[1].split())
    assert "Commit at every stage boundary" in body
    assert "with write-scope paths only, then `git -C <worktree> commit` on the unit branch" in body
    assert "never bypassed (`--no-verify`), except in the emergency commit of a problem (below)" in body
    assert "this commit alone may use `git -C <worktree> commit --no-verify`" in body
    assert "One path outside the write scope rejects the whole result" in body
    assert "emergency commit" in body and "what you tried and the recovery you recommend" in body
    assert "Do not revert, close, raise the depth or narrow the scope yourself" in body
    assert "with your recommended option and record the reason" in body


def test_the_development_worker_result_is_self_contained() -> None:
    body = _contract("development-worker")[1]
    assert "run `devkit rules fix <unit>/spec.md`" in body
    assert "Authored scratch files go in an ignored path inside the worktree" in body
    assert "Pytest-managed temporary fixtures (`tmp_path`, `tmp_path_factory`" in body
    assert "MAY use an isolated system temporary directory outside the worktree" in body
    assert "does not override sandbox permissions" in body
    assert "pass a custom `--basetemp` on the parent command line rather than through `PYTEST_ADDOPTS`" in body
    assert "except the pytest-managed temporary fixtures described above" in body
    # activity-effort decides the nested roles; the reconcile reviewer only verifies.
    assert "a separate `reconcile-reviewer` nested subagent that verifies" in body


# Planning steps an executor runs in either mode, moved out of the contract
# (ADR-executor-neutral-planning-steps-in-a-spec-reference).
MOVED_PLANNING_PHRASES = (
    "Collect the questions for the user in one round, never stopping at the first",
    "as a commit of their own",
    "status: reviewing",
    "needs_decompose: true",
    "never into a file of their own",
    "envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>",
    "--questions-file",
    "check `dev_effort` in `proposal.md`",
    "run the enabled `collect-feedback` sweep",
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
    assert "as a nested subagent (Host -> worker -> role)" in body
    assert "never end the turn while one is still running" in body
    assert "Waiting for the user's answers is not a problem" in body
    assert "Scratch files go in an ignored path inside the worktree" in body


@pytest.mark.parametrize("role", [r for r in ROLES if r not in WORKERS])
def test_every_other_role_stays_read_only(role: str) -> None:
    assert _contract(role)[0]["x-git-actions"] == ["read"]


def test_the_reconciler_verifies_and_never_drafts() -> None:
    metadata, body = _contract("reconcile-reviewer")
    assert "Write" not in metadata["hosts"]["claude-code"]["tools"]
    assert "You do not draft documents" in body
    assert "kind `reconcile-check`" in body  # the caller records it at living-spec-draft, whose exit reads it


def test_the_code_reviewer_leaves_reconcile_verification_to_its_own_role() -> None:
    _, body = _contract("code-reviewer")
    assert "separate `reconcile-reviewer` role" in body
    assert "kind `reconcile-check`" not in body
    assert "kind `review`" in body


def test_spec_delegate_passes_only_the_payload_to_a_projected_role() -> None:
    text = DELEGATE.read_text(encoding="utf-8")
    assert "Read the contract frontmatter first" in text
    assert "With a projected file, pass only the payload" in text
    assert "When the main session substitutes, follow the contract body yourself" in text
    assert "Pass the role contract body" not in text
    assert "[payload](references/payload.md)" in text
    payload = _rendered(DELEGATE.parent / "references/payload.md")
    for role in ROLES:
        assert f"| `{role}` |" in payload, role


def test_tasks_name_the_docs_a_worker_must_write() -> None:
    text = " ".join(TASKS.read_text(encoding="utf-8").split())
    assert "a task a `development-worker` builds names the `docs/` paths its checks require" in text


def test_the_host_validates_the_committed_range_and_blocks_a_failure() -> None:
    delegate = DELEGATE.read_text(encoding="utf-8")
    assert "except a worker, which commits on its activity branch ([worker](references/worker.md))" in delegate
    assert "a range you block is a problem in your own `worker` envelope" in delegate
    text = " ".join(WORKER_RESULTS.read_text(encoding="utf-8").split())
    assert "From the last accepted head to the worker's *final HEAD* (`<returned>`" in text
    assert "merge-base --is-ancestor <diff_scope.head> <returned>" in text
    assert "merge-base --is-ancestor <accepted> <returned>" in text
    assert "diff --name-only <accepted> <returned>` is in the write scope" in text
    assert "`git -C <worktree> status --short` is empty" in text
    assert "--problem" in text and "never reset or amend" in text
    assert "a pull request stays open and blocked" in text
    assert "A blocked unit goes to no review and no integration" in text
    assert "validate the cumulative range again from the same last accepted head" in text
    assert "the base checkout's status and HEAD are as recorded" in text
    assert "except the records you wrote under `<unit>/envelopes/` since `<accepted>`" in text
    assert "`validation`" not in text
    assert "envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem" in text
    assert "Never pass a blocked unit's current HEAD as the base" in text
    assert "`build-verify`, or `fix-verify` in `sdd-spec-bugfix`" in text
    assert "A unit is blocked while any problem, a worker's or yours, has no resolution that names it" in text
    assert "a later commit or a successful `worker` envelope clears nothing" in text
    assert "validate the whole branch: from its merge base" in text
    assert "A comment or a rerun request alone resolves nothing" in text


def test_orchestration_follows_the_committed_result_contract() -> None:
    text = " ".join(_rendered(ORCHESTRATE).split())
    assert (
        "commits at every stage boundary through the commit gate, writes its own records and returns its head" in text
    )
    assert "the committed range from the last accepted head" in text
    assert "A failing range is blocked, never discarded" in text
    assert "a blocked unit goes no further" in text
    assert "A `session`-depth task never becomes a unit" in text
    assert "This scheduling choice requires no additional business approval" in text
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
    assert "never into a file of their own" in planning
    development = _contract("development-worker")[1]
    assert (
        "exactly one `worker` envelope" in development and "envelope resolution --unit <unit> --resolves" in development
    )


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
    assert "## Procedure" in prompt and "## Codex execution and permissions" in prompt
    assert "## On a problem" in prompt


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
        "Every command MUST set cwd to the absolute assigned worktree, including verification and permission requests",
        "every Git command MUST use `git -C <worktree>`",
        "Nested-role read scopes and contract paths MUST be absolute",
        "naming its startup skill and instruction paths (such as `response-style`)",
        "separate command-scoped approval for each necessary operation",
        "sibling-worktree writes, shared Git index/commits, scope registry writes",
        "verification requiring unavailable network access",
        "Use no broad persistent prefix",
        "preflight or approved command grants no later access",
        "`workspace-write` is not worker-specific path confinement",
    ):
        assert requirement in body, (role, requirement)


@pytest.mark.parametrize("role", WORKERS)
def test_worker_refusal_and_failed_emergency_preservation_are_truthful(role: str) -> None:
    body = " ".join(_contract(role)[1].split())
    for requirement in (
        "On unavailable or denied approval, stop that operation and preserve partial state",
        "Do not evade refusal through another tool, path, process, broader request or settings edit",
        "only after its cause/input changes and authorization permits it",
        "only through still-permitted, separately scoped operations",
        "Only ordinary commit-gate refusal permits the emergency `--no-verify` exception",
        "sandbox or approval denial never does",
        "If the record or emergency commit also cannot run, return `failed`",
        "actual last commit SHA, dirty paths and which record/commit is absent or uncommitted",
        "never invent a committed envelope or clean tree",
        "Host, which owns the subsequent recovery run and its records",
    ):
        assert requirement in body, (role, requirement)


def test_named_and_generic_native_invocation_respect_trust_and_effective_contract() -> None:
    hosts = " ".join(_rendered(DELEGATE.parent / "references/hosts.md").split())
    for requirement in (
        "Prefer the projected named role and pass only the payload",
        "role absence alone does not prove the root is untrusted",
        "Diagnose availability separately from trust",
        "effective managed/override contract by absolute path",
        "only when host project-instruction loading is permitted",
        "explicitly report emulation",
        "Never replace an override with the upstream contract during fallback",
        "An explicit host trust restriction MUST stop this fallback",
        "Do not use a generic role, another tool/process/path, or host configuration edits to bypass it",
        "Before starting a worker",
        "native spawning, required nested roles and the approval capability",
        "the Host runs the unit in `direct` when allowed; `required` isolation stops with `needs_input`",
        "Capability availability is not a promise that an approval will be granted",
    ):
        assert requirement in hosts, requirement
    assert "stop and ask the user to register the root" not in hosts
    payload = " ".join(_rendered(DELEGATE.parent / "references/payload.md").split())
    assert "every nested-role read scope explicitly" in payload
    assert "names the assigned worktree's absolute startup skill and instruction paths" in payload
    assert "reports any read from another checkout as a boundary exception" in payload
    assert "Every command, including verification and approvals, sets absolute worktree cwd" in payload
    orchestrate = " ".join(_rendered(ORCHESTRATE).split())
    assert "Before spawning, check native spawning, required nested roles" in orchestrate
    assert "`needs_input` for required isolation; no worker starts" in orchestrate


def test_callers_block_permission_failures_without_fabricated_worker_records() -> None:
    results = " ".join(WORKER_RESULTS.read_text().split())
    records = " ".join(_rendered(BUNDLE / "skills/spec/references/worker-records.md").split())
    assert (
        "The Host MUST block a failed dirty or uncommitted return, even when no worker envelope could be written"
        in results
    )
    assert "Inspect actual HEAD/status and the cumulative allowed paths" in results
    assert "never impersonate the worker's missing record" in results
    for text in (results, records):
        assert "actual last" in text and "dirty paths" in text and "absent/uncommitted" in text
        assert "ordinary commit-gate refusal" in text
        assert "never for sandbox or approval denial" in text or "never sandbox or approval denial" in text
    assert "The exactly-one committed worker-record requirement cannot be satisfied in this failure branch" in records
    assert "owns a subsequent recovery run and its records when permitted" in records


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
    assert "may list it under `[DONE]` before any review ran: that is not Planning evidence" in planning
    assert "`[DONE: ... spike]` is not Planning evidence" in signals
    for text in (planning, signals):
        assert "`scout` and `challenger` envelopes and their `reverify` recorded at `spike`" in text
