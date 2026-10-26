---
id: PLAN-approval-mode-and-crlf-template
spec: SPEC-approval-mode-and-crlf-template
---

# Technical Plan: `SPEC-approval-mode-and-crlf-template` Approval refusal mode, completion report wording and CRLF-preserving config template

## 1. Constitution & Invariant Review

None. `CAP-ADV-agent-advisory-protocol` derives the mode from the error fields (input error, then guardrail, then
actor), so the approval errors reach their modes through class attributes alone, as the handoff errors of
`SPEC-handoff-modes-and-template-report` do. `CAP-DIST-sync-and-transactions` already says no line is changed; the
template fix makes the code meet it. No `MUST` of `docs/architecture/` changes, and no ADR is needed.

## 2. Architecture Overview & Impact

- **Approval errors** (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`):
  `ProposalApprovalNotReadyError` gets `guardrail = True` (`BLOCKED`). A new `ProposalApprovalReplyError`
  (`PROPOSAL_APPROVAL_REPLY_INVALID`, `input_error = True`, `INPUT_ERROR`) with the fix "Rerun with --mode
  accept_only, or --mode accept_and_handoff with --effort low, medium or high" replaces `ProposalApprovalNotReadyError`
  at the six raises that refuse a mode or effort: `_Acceptance.select` (two), `PlanAcceptUseCase.execute` (two),
  `PlanAcceptUseCase._remaining` and `PlanAcceptUseCase.execute_native` (spec assumption 1).
  `ProposalApprovalStaleError` keeps `MAINTENANCE`. Docstrings name the modes (AC-01 to AC-03).
- **Error table** (`CAP-DLV-proposal-incubation`, "Proposal review briefings and combined acceptance"): the table
  gains a `Mode` column for the `PROPOSAL_APPROVAL_*` rows and the `PROPOSAL_APPROVAL_REPLY_INVALID` row (AC-04).
- **Completion reference** (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`):
  the stale-recovery line drops "or report" and "report URI" (AC-05). `devkit sync` refreshes the projections under
  `.devkit/managed/` and `.claude/` (ignored) and any tracked output `devkit sync --check` names.
- **config template** (`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`):
  `_template` reads `path.read_bytes().decode("utf-8")` (no newline translation) and, when every `\n` of the file
  follows a `\r`, converts the bare `\n` endings of the rendered result to `\r\n`. Rendering on the untranslated text
  keeps every existing byte (tomlkit round-trips the text); only the added lines are bare `\n`, so the conversion
  touches only them. `_write` stays unchanged: it writes the text's bytes as given (AC-06, AC-07).

## 3. Error Handling & Edge Cases

- A decode failure of the bytes raises `UnicodeDecodeError`; `read_config` runs first and already refuses an
  unreadable or invalid file with `CONFIG_INVALID`, so the template step never sees one.
- A file without any newline (`schema = 1`) is LF: nothing to convert.
- A mixed file is rendered on its untranslated text: existing bytes stay, added lines are LF (spec assumption 3).
- `preview_config_template` returns the same converted text, so `--print` agrees with the write.
- A file created by `devkit config template` starts from `schema = 1\n` and stays LF.

## 4. Verification & Test Plan

- Red first for AC-01 and AC-02: `packages/devkit-spec/tests/integration/features/delivery/test_approval_error_modes.py`
  pins code, mode and `guardrail`/`input_error` of the three errors, and runs `PlanAcceptUseCase.execute` with an
  invalid mode and with `accept_and_handoff` without an effort, which refuse before any Git access. It fails on the
  base (`MAINTENANCE`, no `PROPOSAL_APPROVAL_REPLY_INVALID`).
- Red first for AC-06: a CRLF regression test in
  `packages/devkit-dist/tests/integration/features/distribution/test_config_template.py` runs the CLI on a CRLF file,
  reads the bytes and checks the original lines, the absence of a bare `\n`, the second run and `--print`. It fails on
  the base (every line rewritten to LF). AC-07 adds an LF and a mixed-ending case.
- AC-04 and AC-05: `rg` checks named in the tasks; `uv run devkit sync --check`.
- Module checks: `just lint`/`just lint-check` and `just check` for devkit-spec and devkit-dist, `just test-affected`,
  `just test-dist`, `uv run devkit rules check --ci --base 8190b1d3`, then `uv run devkit sync` and
  `uv run devkit sync --check`.
