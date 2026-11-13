---
id: FB-envelope-commit-companion-files
title: envelope commit refuses when any other path is pending, even the files the envelope reports on
scope: repo
kind: suggestion
category: other
target: devkit workflow envelope commit
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-envelope-commit-companion-files] envelope commit refuses when any other path is pending, even the files the envelope reports on

Category other: commit ergonomics of workflow records.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit workflow envelope commit` commits exactly one authored envelope; "Other dirty paths
  require a manual combined commit." A consumer spec worker who wrote an envelope together with the `spec.md` or
  feedback edits it records had to fall back to a hand-written `git commit`, choosing its own message.
- **Proposed Procedure**: Accept repeatable `--with <path>` for files inside the same Unit (for example `spec.md`,
  `reconcile.md`, `feedback/*.md`), committed with the same deterministic message; keep the refusal for paths outside
  the Unit.
- **Expected Benefit**: One command and one message form for each envelope-bearing commit; fewer hand-written
  workflow commit messages.
- **Cost & Risk**: Widens a guarded command; hook failures with several files need the same retry contract.
- **Attempted**: Hypothesis; the refusal and manual fallback were observed.

## Diagnostic Details

- **Reproduction**: Write an envelope and edit `spec.md` in the same Unit, then run `devkit workflow envelope commit
  --unit <dir> --file envelopes/<kind>-NN.yaml`.
- **Expected / Actual**: Expected a combined record commit; actual `ENVELOPE_COMMIT_STATE`-class refusal.
- **Versions**: devkit `569379a06` (help text checked); consumer revision unknown.
- **Conditions**: consumer `sdd-spec-feature` Unit.
- **Workarounds Attempted**: manual `git commit` of both files.
- **Related Assets**: `devkit workflow envelope commit --help`, the `spec` skill's `references/envelope.md` section 5.

## Evidence

```text
devkit workflow envelope commit --help: "Commit exactly one authored new envelope ... Other dirty paths require a
manual combined commit."
```
