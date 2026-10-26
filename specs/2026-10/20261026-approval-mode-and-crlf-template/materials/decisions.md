# Agreed feedback items

The user asked to resolve these three decision-free feedback items in one unit (2026-10-26). Each follows its
feedback file's suggestion.

1. `FB-approval-refusals-emit-maintenance` (specs/2026-10/20261026-handoff-modes-and-template-report/feedback/approval-refusals-emit-maintenance.md).
   `ProposalApprovalNotReadyError` (`PROPOSAL_APPROVAL_NOT_READY`) renders `BLOCKED` (`guardrail = True`), like
   `SPEC_HANDOFF_NOT_READY`. Check the other `PROPOSAL_APPROVAL_*` errors and give each the mode its cause needs
   (caller-fixable input: `INPUT_ERROR`; prerequisite: `BLOCKED`; a real tool failure stays `MAINTENANCE`).
   Document the modes in the `PROPOSAL_APPROVAL_*` rows of `CAP-DLV-proposal-incubation` and pin them in tests;
   reproduce with a failing test first.
2. `FB-completion-guidance-report-uri` (specs/2026-10/20261026-handoff-modes-and-template-report/feedback/completion-guidance-report-uri.md).
   Drop "or report" and "report URI" from the stale-recovery line of the spec skill's completion reference
   (`completion.md.jinja`); it preserves the source SHA, authority and recovery state. Run `devkit sync`.
3. `FB-config-template-rewrites-crlf-line-endings` (specs/2026-10/20261026-handoff-modes-and-template-report/feedback/config-template-rewrites-crlf-line-endings.md).
   `devkit config template` reads without newline translation and writes added lines in the file's own line ending,
   so existing lines keep their bytes. Reproduce with a failing CRLF regression test first. The contract already
   says no line is changed; add a line-ending sentence only if it is missing.
