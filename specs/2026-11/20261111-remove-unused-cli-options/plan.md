---
id: PLAN-remove-unused-cli-options
spec: SPEC-remove-unused-cli-options
---

# Technical Plan: `SPEC-remove-unused-cli-options` Remove unused CLI options

## 1. Constitution & Invariant Review

- **ADR required before implementation.** `ADR-single-local-landing-route` decides that `--local-only` "stays
  accepted" and lists retiring it as a follow-up. A new ADR, `ADR-remove-unused-cli-options-without-shims`
  (`docs/decisions/2026-11/20261111-remove-unused-cli-options-without-shims.md`), records the no-shim removal of the
  six options and supersedes in part only that clause and that follow-up; the earlier ADR stays `accepted` with a
  `Superseded in part by` pointer (`decision-writing`, Supersession).
- No other accepted ADR or architecture document states a removed option (searched `docs/decisions`,
  `docs/architecture`, `docs/usecases`, `guides/` and `docs/steering` for each flag).
- Capability contracts that state a removed option and are rewritten: `CAP-WT-task-worktrees` §3 (`--local-only`),
  `CAP-DLV-cli-and-output` §1 synopsis and the `[BOUND_ELSEWHERE]` row, `CAP-DLV-workflow-definitions` (binding
  section: `next --workflow <path>`), `CAP-DLV-workflow-orchestration` (unit resolution: `--workflow` on `next`), `CAP-DOCS-document-lookup` (`--query`), plus the mentions in
  `CAP-INT-mcp-services`, `CAP-COLL-work-scope-registry` and `CAP-DLV-delivery-workflows`.
- No new feature edge; `.devkit/architecture.toml` is untouched.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `devkit_agt.features.worktree.cli` | `finish` loses `--local-only` and its parameter; the docstring sentence about it goes |
| `devkit_dist.features.host.cli` | `status` loses `--host` and its `ARGUMENT_INVALID` branch; it inspects `SUPPORTED_HOSTS[0]` |
| `devkit_agt.features.rules.cli.commands` | `_summary_option`, `RunRequest.summary_only` and the `summary_only` parameters go |
| `devkit_agt.features.rules.cli.output` | `print_violations` loses `summary_only` and its `[RULE_COUNTS]` branch; module docstring follows |
| `devkit_agt.features.workflow.cli.run` | `next` loses `--workflow`; `handoff` loses `--date` (and its `parse_date` import, still used by `new`) |
| `devkit_agt.features.workflow.usecases.operations` | `EvaluateUnitUseCase.execute` loses `workflow`; `HandoffWorkflowUseCase.execute` loses `when` and calls `apply_handoff` without it, so the history takes today |
| `devkit_docs.features.documents` | `list` loses `--query`; `ListDocumentsUseCase.execute` loses `query` and its filter term |
| Spec bundle text | `spec-integrate/SKILL.md.jinja`, `spec/references/worktree.md.jinja`, `spec-orchestrate/references/git-operator-operations.md` name `devkit worktree finish <branch>`; `devkit sync` outputs committed |
| Living Spec and references | the capability documents above and `docs/development/reference/{integration,worktree,host,rules}.md` |

Unchanged on purpose: `Workspace.resolve_unit(unit, workflow)` (used by `bind`), `apply_handoff(when=...)` (library
API in the workflow reference), the `[BOUND_ELSEWHERE]` renderer, `host hook --host`, `integration_local_only` (an
extension attribute, not the flag), the release handbook.

## 3. Component & Interface Design

```text
devkit worktree finish BRANCH [--discard] [-w DIR] [--format text|json]
devkit host status [-w DIR] [--format text|json]
devkit rules check [-w DIR] [-p linter|hygiene] [--rules-dir DIR] [--format text|json] [--staged|--ci [--base REF]] [TARGETS]...
devkit rules fix [-w DIR] [-p linter|hygiene] [--rules-dir DIR] [--dry-run] [--format text|json] [TARGETS]...
devkit workflow next --unit DIR [--anchor FILE] [--given NAME]... [--view next|requests] [--no-lint] [--format text|json]
devkit workflow handoff --unit DIR [--anchor FILE] [--workflow ID] [--by NAME] [--given NAME]... [--no-lint] [--format text|json]
devkit docs list [KIND]... [--status S] [--area TEXT] [--history] [--where F=V] [--file PATH] [...]
```

```python
class EvaluateUnitUseCase(BaseUseCase):
    def execute(self, unit: str, *, anchor: str | None = None, given: Sequence[str] = (), lint: bool = True) -> UnitEvaluation: ...

class HandoffWorkflowUseCase(BaseUseCase):
    def execute(self, unit: str, workflow: str | None = None, *, anchor: str | None = None, by: str = "",
                given: Sequence[str] = (), lint: bool = True) -> HandoffOutcome: ...
```

## 5. Error Handling & Edge Cases

- A removed option is a click usage error (exit `2`, `No such option` on stderr) raised before the command body, so
  nothing is read or written.
- `next` in a directory with two anchors keeps `ANCHOR_AMBIGUOUS` and its `--anchor` fix; the `--workflow` route to
  disambiguate is gone, `--anchor` remains.

## 6. Verification & Test Plan

- Tests that passed a removed option are rewritten to assert the usage error (one per option) and to cover the
  behavior that remains: `bind --workflow` for anchor resolution and `WORKFLOW_NOT_BINDABLE`, the library for
  `[BOUND_ELSEWHERE]`, today's date for the handoff history, `host status` without `--host`.
- Per task: `just test <module> <paths>`; then `just lint-check`, `just check`, `just test-affected --base main`,
  `just test-affected --base main --tier e2e`, `uv run devkit rules check --ci --base main`,
  `uv run devkit sync --check` and the AC-02 `git grep`.
- Baseline: the head with the options present is `425d8e46`; the before/after outcome is the option count accepted by
  the six commands (six before, zero after), read from `--help` on each side of the change.
