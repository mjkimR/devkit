---
id: ADR-nightly-ci-verification
title: Affected tests locally and complete CI overnight and at release
summary: "Local integration reuses affected-test results for the final merged content; changed-head nightly CI and release CI provide full workspace coverage."
status: accepted
created_at: 2026-10-19
---

# [ADR-nightly-ci-verification] Affected tests locally and complete CI overnight and at release

## Context

Repeated complete workspace runs delay development as the suite grows. Static affected-test selection covers most
local changes but cannot detect every dependency, subprocess or entry-point relationship.

## Decision

Development, review and integration use `just test-affected` without a separate mandatory local full-suite run.
Its existing full-suite fallback and frontend instructions still apply. Lint, type and governance checks remain.
The final integration content is verified after incorporating a moved base or resolving conflicts; merging the
same verified content does not trigger another test run.

Full CI runs at 04:17 Asia/Seoul when the scheduled default-branch head differs from the latest successful nightly
wrapper head, or no success exists. Failed and cancelled runs do not advance that baseline; API failures fail the
gate. Manual wrapper runs always perform full CI. Existing manual CI and release CI always perform full checks,
and publication still depends on release CI success.

The nightly wrapper reuses the existing complete CI rather than duplicating its checks. Repository-specific timing
belongs in the repository docs; shipped delivery skills follow each consuming repository's verification policy.

## Alternatives and Consequences

Keeping a mandatory full suite per integration discovers selection misses earlier but repeats costly work.
Checking only commits from the last 24 hours could permanently miss a failed head; a successful-head baseline
retries it. The chosen policy allows an undetected failure on main until a later complete CI; GitHub scheduling
can be delayed or dropped. Release CI prevents publishing a head whose required full checks fail.
