---
id: PLAN-feedback-quick-fixes
spec: SPEC-feedback-quick-fixes
---

# Technical Plan: `SPEC-feedback-quick-fixes` Feedback Quick Fixes

## 1. Architecture Overview & Impact

- Target Area: `devkit-dist` project configuration (`features/project`), the workspace module scripts, and the
  `spec` bundle's delegation and Planning guidance.
- No new modules or dependencies; one new warning code, `PRESENTATION_LANGUAGE_UNSUPPORTED`. The English fallback of
  `ADR-shared-language-preference-with-bounded-approval-content` is kept; `resolve_language` already marks it with
  `fallback=true`, and one helper turns that into returned warnings for the three commands that read the preference.

## 2. Component Breakdown & Interface Contracts

- `project/models/presentation.py`: `PRESENTATION_LANGUAGES = ("auto", "en", "ko")` and
  `PresentationLanguageUnsupportedNotice` (`PRESENTATION_LANGUAGE_UNSUPPORTED`, `WARNING`, never raised) whose
  `[FIX]` names the accepted values and the source file.
- `project/services/presentation.py`: `resolve_language` keeps the ADR fallback (`resolved="en"`, `fallback=true`);
  `language_notices(root)` checks the effective and the shared-only value and returns one warning per source file.
- `devkit sync` (`commit_locked` planning notices), `devkit status` (`ProjectStatus.notices`) and
  `devkit config show` (a new `ConfigurationReport` result with `notices`, printed through `echo_notices` and
  `exit_on_warnings`) return the warning; `validate_runtime_tables` is unchanged from the base.
- `scripts/_lib.sh`: one `module_short_names` table (`short full` pairs, adding `agt`) drives `resolve_module` and a
  `Module short names:` line in `validate_module`'s refusal. The README module paragraph lists the short names.
- `spec-delegate/references/payload.md` and the two worker contracts: the nested-role read scope includes the
  assigned worktree's absolute startup skill and instruction paths; a read from another checkout is a reported
  boundary exception.
- `spec/references/planning.md` and `spec-next/references/workflow-signals.md.jinja`: `spike` under `[DONE]` is not
  Planning evidence; the support-role envelopes recorded at `spike` are.
- Capabilities: `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership`, `CAP-INT-mcp-services` and
  `CAP-DLV-proposal-incubation` (the fallback is a visible warning); `CAP-DLV-delivery-workflows` (nested-role skill
  paths, spike evidence).
- After the bundle edits, `uv run devkit sync` re-projects `.claude/`, `.agents/`, `.codex/`, `.devkit/managed/` and
  `.devkit/installation.json`.

## 3. Verification & Test Plan

- `test_presentation.py`: supported values resolve; unsupported values fall back to `en`; `language_notices` returns
  one warning per falling-back file (shared, local or both) with the fix naming the accepted values.
- `distribution/test_local_config.py`: the sync scenario renders English for an unsupported value and expects the
  warning from `sync_project`, `config show` (exit 0, exit 1 under `--strict`), `status`, and `devkit sync` stderr.
- `devkit-spec` `test_role_contracts.py`: assert the payload, worker-contract and Planning wording.
- Manual: `just lint-check agt`; `bash scripts/module.sh lint-check nope` prints the short-name line and exits 1.
- `just lint` and `just check` for `devkit-dist` and `devkit-spec`, `just test-affected`,
  `uv run devkit rules check --staged`, `uv run devkit status` after sync.
