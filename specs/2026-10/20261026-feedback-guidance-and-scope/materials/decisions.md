# Decided feedback items

The user compared the options for three open feedback items and chose the recommended one for each (2026-10-26).
Four decision-free documentation items and one mode check from the Living Spec consistency sweep travel with them.

## Decided

1. `FB-fixture-removal-denied` (specs/2026-10/20261026-review-refactor/feedback/fixture-removal-denied.md).
   Decision: do not ask workers to delete scratch files. Authored scratch files stay in an ignored path inside the
   task worktree and are removed with the worktree (`devkit worktree finish` / integration cleanup). Payloads never
   ask a worker to create-then-delete a scratch fixture. Rejected: widening host permissions for recursive removal
   (host-local, brittle path matching, destructive), and forcing every exploratory fixture into a pytest test.
   Targets: the development-worker role contract (rule 8) and the spec-delegate payload reference; mirror wording in
   any planning-worker or worktree guidance that says the same.

2. `FB-merge-conflict-guardrail-action`
   (specs/2026-10/20261026-merge-proposal-materials-at-handoff/feedback/merge-conflict-guardrail-action.md).
   Decision: keep the code `SPEC_PROPOSAL_TARGET_EXISTS` and the error class (the ADR keeps both), but a materials
   merge conflict is raised without the guardrail so its directive is `INTERACTION` (stop and ask the user; `[FIX]`
   is the reconciliation for once they agree). An existing handoff target (spec directory, ADR file) stays
   `BLOCKED`. Rejected: keeping `BLOCKED` with a report-only fix (misstates a data collision as a rule), and an
   agent-fixable mode (renames materials without the user). Targets: `ProposalTargetExistsError` construction in
   the handoff use case (`_refuse_merge`), its tests, and `CAP-DLV-proposal-incubation` (plus the error table).

3. `FB-scope-external-feedback-target`
   (specs/2026-10/20261024-canonical-libyaml-only/feedback/scope-external-feedback-target.md).
   Decision: an exact path declared in a task `_Boundary` that names a feedback file of another spec bundle
   (`specs/**/feedback/*.md`) is collected as a file scope, so overlap detection covers two units resolving the same
   feedback. Every other path inside another spec bundle stays `excluded-tree`; globs and directories do not get the
   exception. Rejected: an informational reason without a scope (no overlap detection), and moving feedback closure
   to the Host (contradicts spec-sync). Targets: scope input collection and entrypoint derivation's tree exclusion,
   tests, and the scope contract in `docs/capabilities/delivery/`.

## Decision-free, from the consistency sweep (specs/2026-10/20261026-living-spec-consistency-sweep/feedback/)

4. `FB-handoff-error-modes-documented-differently`: the handoff errors emit `MAINTENANCE` while the error table
   documents `BLOCKED` and `INPUT_ERROR`. Settle it by the shipped mode unless the shipped mode is a defect (a
   refusal the user caused rendered as a tool failure); record a defect as feedback rather than redesigning modes,
   except where item 2 already changes the mode.
5. `FB-spec-readme-and-mcp-guide-native-handoff`: remove the native-handoff claim and the devkit-mcp dependency from
   `packages/devkit-spec/README.md` and `guides/install/mcp.md`.
6. `FB-integration-mcp-glossary-and-actor-row`: update the glossary "Integration MCP" entry and the
   `ARCH-04-1-ecosystem-boundaries` actor row to the shipped state.
7. `FB-worktree-module-layout-stale`: align the `CAP-WT-task-worktrees` §7 module list with the package.
8. `FB-sync-config-template-example-stale`: align the `CAP-DIST-sync-and-transactions` template example with the
   shipped `[tool.spec] worktree` setting.

Out of this unit: `FB-plain-handoff-skips-proposal-handoff-policy` (needs a design decision) and
`FB-config-template-reports-unchanged-after-writing` (a separate bugfix).
