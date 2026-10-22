---
id: PLAN-feedback-quick-fixes
spec: SPEC-feedback-quick-fixes
---

# Technical Plan: `SPEC-feedback-quick-fixes` Feedback Quick Fixes

## 1. Architecture Overview & Impact

- Target Area: `devkit-dist` project configuration (`features/project`), the workspace module scripts, and the
  `spec` bundle's delegation and Planning guidance.
- No new modules, codes or dependencies. `validate_runtime_tables` is the one validator both the shared readers
  (`read_effective_config`, the distribution configuration reader) and the local reader (`read_local_config`) call,
  so one check there covers every entry point.

## 2. Component Breakdown & Interface Contracts

- `local_config.py`: `PRESENTATION_LANGUAGES = ("auto", "en", "ko")`; `validate_runtime_tables` raises
  `ConfigError` (`CONFIG_INVALID`) for any other string, with a fix naming the accepted values.
- `presentation.py`: `resolve_language` returns the validated value as requested and resolved, `fallback=False`.
- `scripts/_lib.sh`: one `module_short_names` table (`short full` pairs, adding `agt`) drives `resolve_module` and a
  `Module short names:` line in `validate_module`'s refusal. The README module paragraph lists the short names.
- `spec-delegate/references/payload.md` and the two worker contracts: the nested-role read scope includes the
  assigned worktree's absolute startup skill and instruction paths; a read from another checkout is a reported
  boundary exception.
- `spec/references/planning.md` and `spec-next/references/workflow-signals.md.jinja`: `spike` under `[DONE]` is not
  Planning evidence; the support-role envelopes recorded at `spike` are.
- Capabilities: `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership`, `CAP-INT-mcp-services` and
  `CAP-DLV-proposal-incubation` (refusal instead of fallback); `CAP-DLV-delivery-workflows` (nested-role skill
  paths, spike evidence).
- After the bundle edits, `uv run devkit sync` re-projects `.claude/`, `.agents/`, `.codex/`, `.devkit/managed/` and
  `.devkit/installation.json`.

## 3. Verification & Test Plan

- `test_presentation.py`: supported values resolve; unsupported values raise `CONFIG_INVALID` with the fix, in both
  the shared and the local file.
- `distribution/test_local_config.py`: the sync scenario expects the refusal for an unsupported value instead of an
  English render.
- `devkit-spec` `test_role_contracts.py`: assert the payload, worker-contract and Planning wording.
- Manual: `just lint-check agt`; `bash scripts/module.sh lint-check nope` prints the short-name line and exits 1.
- `just lint` and `just check` for `devkit-dist` and `devkit-spec`, `just test-affected`,
  `uv run devkit rules check --staged`, `uv run devkit status` after sync.
