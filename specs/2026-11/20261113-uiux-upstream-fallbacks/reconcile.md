---
reconcile_id: REC-uiux-upstream-fallbacks
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
---

# Reconcile: `SPEC-uiux-upstream-fallbacks`

## Retained behavior

- `CAP-DLV-uiux-improvement` rules 23–26 and interface routing reflect the new direct conditional reference:
  advisory negative detection with actual target/code/build evidence; observed capability and stop-condition
  briefing; an unavailable required autonomy probe remaining unsatisfied; supported-interface-first persistence
  with report-only fallback. Existing route, native loading, every-answer, permission, ownership and acceptance
  boundaries remain unchanged. The summary includes these limits without claiming an upstream runtime fix.
- `UC-improve-an-interface-and-user-flow` extensions 5g–5i and scenarios 24–26 reflect the same outcomes at the
  delegation step; its summary and rule mapping include the retained behavior. It gains no new workflow or authority.
- No architecture, ADR, glossary or additional capability area changed: there is no runtime, dependency, feature
  edge, new term or lasting authority decision. The human bundle guide reflects the same troubleshooting outcomes.

## Verification and entrypoints

Initial independent medium code-reviewer PASS is in review-01.yaml. Its 11-path range ended at
7b18b6f51e79f494dd8f321b34936f45a9133439. Caller pre/post complete-tree snapshots both equal
203afcb1ab977fc137c467b159f7d5ee8d868b4a and HEAD stayed unchanged. Reviewer reported no reads outside the worktree.

Medium reconcile self-verification applies: only the app_uiux_improve catalog bundle and delivery capability area
change. Both exact existing contract targets are identified above; each changed statement maps directly to the
new reference, with no cross-component choice or interpretive contract change. The author verifies the reflection
separately from code review and records the result in reconcile-check-01.yaml. Native tests cover instructions and
distribution, not model obedience or upstream runtime behavior. Native upstream trials were not performed and are
not a completion gate.

Before/after explicit failure-case instruction coverage is 0/3 at accepted head
5cab6156a60de1a2a2845e38fc19bda92961c90e and 3/3 at the implementation head, measured by git-show source inspection
and semantic instruction assertions, without checking out the base. Sync outputs: none.

Entrypoint derivation returned the existing SKILL.md doorway for both documents, with no missing declaration.
Rejected new candidates: README.md is the human guide, impeccable-limits.md is a conditional helper reference, and
both test files are verification rather than code doorways. The existing entrypoint remains sufficient; no apply
was needed. Targeted document/Unit rules and diff whitespace checks passed with zero violations.

Author semantic comparison: AC-01 maps reference Negative visual detection to capability rule23 and use case
5g/scenario24; AC-02 maps Prepare the brief/Unavailable autonomy probe to rules24–25 and 5h/scenario25; AC-03 maps
Unsupported audit persistence to rule26 and 5i/scenario26; AC-04 keeps existing authority rules and declares the
entry's new conditional read; AC-05 matches the three terminal local-mitigation Dispositions below. No required
contract mismatch or waiver remains.

## Source feedback outcomes

- `FB-impeccable-context-target-no-visual-implementation`: promoted to completed local detector-evidence guidance;
  focused integration 16 and installed-consumer 1 passed. Upstream runtime was not fixed.
- `FB-impeccable-autonomy-probe-in-subagent`: promoted to completed local capability/stop-condition and unsatisfied
  probe guidance with authorized continuation; the same checks passed. Upstream runtime was not fixed.
- `FB-impeccable-audit-storage-write-missing`: promoted to completed local supported-interface/report-only
  persistence guidance; the same checks passed. Upstream runtime was not fixed.

Their Dispositions also record catalog lint/types and affected 182 passing tests. The user selected useful local
compensation, with no retained upstream backlog or external submission. No required work was deferred and no new
follow-up destination is needed; none was created.
