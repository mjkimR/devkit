---
id: PLAN-lifecycle-feedback-fixes
spec: SPEC-lifecycle-feedback-fixes
---

# Technical Plan: `SPEC-lifecycle-feedback-fixes` Fix four lifecycle feedback items

## 1. Constitution & Invariant Review

None. Every change keeps the agent output contract (`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol`): a
fix is a runnable command or a concrete edit, names devkit as `uv run devkit`, and every refusal keeps a stable code.
The stage check follows `CAP-DLV-workflow-envelopes`' rule that recording never depends on a valid definition, by
falling back when the definition cannot be loaded. No ADR is needed.

## 2. Architecture Overview & Impact

| Item | Component | Change |
| --- | --- | --- |
| AC-01 | `devkit_agt.features.workflow.services.envelope.commit.commit_message` | The unsupported-anchor `fix` becomes a concrete action without a placeholder. |
| AC-02 | `devkit_dist.features.distribution.services.installation.local_render.LocalRenderStaleError` | The class `fix` names `uv run devkit sync --locked` first and a plain sync only after `RECEIPT_STALE`. |
| AC-03, AC-04 | `devkit_agt.features.workflow.usecases.envelopes.WriteEnvelopeUseCase` | For kind `worker`, load the bound definition and refuse a stage it does not declare, before composing or writing. |
| AC-05 | `CAP-DIST-context-and-playbooks`, `docs/development/reference/distribution.md`, `CAP-DLV-workflow-envelopes` | Error tables and the authoring paragraph state the new fixes and the check. |
| AC-06 | `CAP-DOCS-document-model` 3.5 item 5; spec bundle `templates/proposal.md` | State the reference writes of a rename and comment the `excludes` example; `devkit sync` redeploys the template. |

No new dependency, code or command.

## 3. Component & Interface Design

**AC-01.** `commit_message` keeps its signature and refusal; only the fix changes:

```python
fix="Commit the [TARGET] envelope with a manual git commit: explicit envelope commit supports only SPEC and PROP"
" anchor ids"
```

The use case already sets `[TARGET]` to the workspace-relative envelope path when the error carries none.

**AC-02.** `LocalRenderStaleError.fix`:

```python
fix = (
    f"Run `{AGENT_INVOCATION} sync --locked` in this workspace to refresh personal rendering evidence; it changes no"
    f" committed file. Only if it reports RECEIPT_STALE run a plain `{AGENT_INVOCATION} sync`, which also rewrites"
    " committed files, and commit what it changes"
)
```

**AC-03, AC-04.** A helper in `usecases/envelopes.py`, called by `WriteEnvelopeUseCase.execute` for `kind == "worker"`
before the authoring or skeleton branch:

```python
def _require_declared_stage(ws: Workspace, scope: UnitScope, stage: str) -> None:
    """Refuse a worker --stage the unit's workflow does not declare; skip when the definition cannot be loaded."""
```

It loads `ws.load_definition(scope.binding.workflow or ws.config.default or "")` as `_carried_from` does. On an
`AdvisoryError`, or when the loaded id differs from `scope.workflow`, it returns. Otherwise a stage outside
`{s.id for s in doc.stages}` (an empty value and `-` included) raises
`EnvelopeFlagError(..., target_files=["--stage"], fix=...)` with the fix
`Pass --stage the stage `uv run devkit workflow next --unit <rel>` names; workflow <id> declares: <ids>` (all values
filled in). The refusal precedes `write_envelope`, so nothing is written.

## 4. Error Handling & Edge Cases

- `--stage -` on the authoring path is refused by the new check first, with the same code and target as before.
- An exception stage (`exception: true`) is in `doc.stages`, so a worker in recovery can record it.
- A unit bound to a missing workflow id (`WorkflowNotFoundError`) or an unreadable definition (`DefinitionError`)
  keeps the lenient path.
- Tests that write worker envelopes with stages their fixture workflow does not declare must use declared stages or
  fixtures without a loadable definition; an existing test is never weakened.

## 5. Storage & State Management

`devkit sync` after the template edit updates the ignored `.devkit/managed/spec/templates/proposal.md` and the tracked
`.devkit/installation.json` hash; both are committed with the change.

## 6. Verification & Test Plan

- AC-01: `just test devkit tests/integration/package/test_agent_output_contract.py` and the commit policy unit test
  asserting the fix text.
- AC-02: a `devkit-dist` integration test in `test_local_config.py` asserting the fix and that a locked sync clears the
  staleness with tracked files unchanged.
- AC-03, AC-04: CLI tests in `packages/devkit/tests/integration/features/workflow/` for an undeclared stage (authoring
  and skeleton, no file written, code, target, fix), `-`, a declared and an exception stage, and a missing definition.
- AC-05, AC-06: `just rules-check`, `uv run devkit sync --check` and a read of the edited passages.
- Whole change: `just lint-check` and `just check` for `devkit`, `devkit-dist` and `devkit-spec`; `just test-affected`
  (its `mode=full` fallback when selected).
