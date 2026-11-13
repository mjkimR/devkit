---
id: FB-envelope-round-reviewer-identity
title: Review envelopes carry round and reviewer identity only as summary prose
scope: repo
kind: suggestion
category: missing-capability
target: devkit workflow envelope new
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-11-13
---

# [FB-envelope-round-reviewer-identity] Review envelopes carry round and reviewer identity only as summary prose

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit workflow envelope new` has no round or reviewer field. The review loop asks each
  round's summary to start with `round <N>;` (and `closes reconcile-check-<NN>;`), and nothing records which actor
  (independent reviewer, implementer, Host) wrote the envelope.
- **Proposed Procedure**: Add optional `--round <N>` and `--closes <file>` options that write the prefix (or
  structured fields that counting reads), and an optional reviewer-role field such as `--by reviewer|implementer|host`.
- **Expected Benefit**: Consumer spec workers writing `ux-review`, `review` and `reconcile-check` envelopes did not
  know the summary convention and asked where round and reviewer identity go; a flag makes the convention discoverable
  from `--help` and checkable.
- **Cost & Risk**: Two sources of truth if the summary prefix stays; counting would need to read one of them.
- **Attempted**: Hypothesis; observed only the workers' question.

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: Expected an identity slot; actual summary-prefix convention only.
- **Versions**: devkit `569379a06` (option list checked).
- **Conditions**: a consumer `sdd-spec-feature` Unit with two ux-review rounds and two reconcile-check rounds.
- **Workarounds Attempted**: identity written in the summary text.
- **Related Assets**: `devkit workflow envelope new --help`, the `spec` skill's `references/review-loop.md` (Count row).

## Evidence

```text
review-loop.md Count: "Each round's summary starts with `round <N>;` ... a reconcile check closing an earlier one adds
`closes reconcile-check-<NN>;`."
envelope new options: --kind --unit --anchor --stage --summary --assume --unverified --status --check --base ...
(no round or reviewer option)
```

- **Disposition**: Dismissed on the user's hygiene decision. The documented round prefix and role evidence remain sufficient; no failed round count or lost provenance was demonstrated. Additional fields and flags are not requested.
