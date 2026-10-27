---
id: FB-reverify-after-workflow-return
title: Explain review evidence after returning to build verification
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/SKILL.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-25
---

# [FB-reverify-after-workflow-return] Explain review evidence after returning to build verification

## 1. Friction / Question

- **Context**: Closing an initial independent code review finding after returning to build-verify for its fix.
- **Expectation**: spec-review says to close the round after fixes with envelope reverify; the workflow also offers
  a build-verify return for defects. Combining those steps should have an explicit evidence rule.
- **Actual**: Reverify accepted the old review and resolved its finding, but workflow next still reported
  envelope-review-passed unmet with no review envelope. The return had invalidated the underlying review evidence.
- **Workaround**: The independent reviewer checked the fixed range again; a new review envelope then passed the stage.
- **Suggestion**: Explain that a return invalidates the old review for stage passage and requires a fresh review
  record, or make a post-return reverify carry enough current-stage review evidence. Preserve gate invalidation.

## Diagnostic Details

- **Reproduction**: Record review with a finding; return to build-verify; commit the fix; record a completed
  reverify from the earlier review with resolve all; run workflow next.
- **Expected / Actual**: Finding closure accepted; stage passage still unmet with no review envelope.
- **Versions**: Implementation at d66c3f73 and fix at 10572438; workflow/skills unchanged by this feature.
- **Conditions**: sdd-spec-feature, medium effort, one initial isolated review and a return after a P1 finding.
- **Workarounds Attempted**: A post-fix independent review and new review envelope passed.
- **Related Assets**: spec-review skill, spec/references/review-loop.md, workflow return and envelope reverify.

## Evidence

```text
ENVELOPE reverify-01 status=completed open_findings=0
STAGE review-refine
UNMET envelope-review-passed
CHECK detail="no review envelope"
```
