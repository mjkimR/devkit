---
id: PLAN-test-host-preflight
spec: SPEC-test-host-preflight
---

# Technical Plan: `SPEC-test-host-preflight`

## 1. Constitution & Invariant Review

No architecture or accepted decision changes. `ARCH-05-2-components` keeps script integration tests under package
ownership. Existing caller-owned approval/retry and full-suite fallback remain intact.

## 2. Architecture Overview & Impact

`module.sh` supplies repeated `--test-path` options with effective test selections to its existing preflight.
The preflight compares paths against the two known viewer HTTP test files, checks an ephemeral IPv4 loopback
bind/listen only when a selection covers one, and closes the socket. No application feature or dependency edge changes.

## 3. Component & Interface Design

`check_test_environment.py [--test-path PATH]... -- COMMAND...` keeps the command after `--` solely for its retry
advisory. No paths means full-suite requirements. Paths are normalized relative to the script's repository root,
with pytest node suffixes removed. A selected directory requires loopback if it contains a known consumer.
`TEST_LOOPBACK_BLOCKED` exits 2 and carries actor=user, retry=after_fix. Socketpair failures take precedence.
For `all`, leading positional selectors are forwarded; option-only or opaque selections conservatively mean full.
For single modules, resolved selectors or their default test roots are forwarded; e2e defaults use e2e roots.

## 5. Error Handling & Edge Cases

Check IPv4 127.0.0.1 port 0, bind then listen, without network traffic or accepted connections. A denial stops the
recipe before pytest. `-k` does not weaken directory requirements. Existing retry argument quoting is preserved.
Cold-cache wheel dependency downloads are documented; cache state is not probed and network is never mandatory
when cached dependencies suffice.

## 6. Verification & Test Plan

AC-01/03: injected bind/listen denial and live permitted bind; exact advisory and cleanup assertions.
AC-02: selected safe/viewer files, ancestors, node IDs, module-relative resolution and e2e defaults.
AC-04: affected-runner routing regressions and unchanged full fallback; inspect prerequisite wording.
Compare controlled bind denial against input code loaded through Git without checking out the base.
Run focused script integration/e2e tests, Ruff, script Pyright, `just test-affected --base e91c47ba`, and cumulative
CI rules against 700c339b. No wheel source changes require a package build; compile script syntax instead.
