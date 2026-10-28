---
id: FB-contract-scan-misses-helper-built-fixes
title: The output contract test does not see fixes built by helpers
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit/tests/integration/package/test_agent_output_contract.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-27
---

# [FB-contract-scan-misses-helper-built-fixes] The output contract test does not see fixes built by helpers

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `test_agent_output_contract` reads `fix=`/`what_to_report=` string literals, f-strings and
  `+` concatenations, plus class-level `fix` values. Fixes returned by helper functions, chosen in conditional
  expressions or built inside f-string fields are read as `{}` or skipped. The review of the output-contract pass
  found five live placeholders this way (`gate run commit-msg <file>`, `<low|medium|high>`, `<the user's reason>`,
  `--workflow <id>`, a bare `devkit workflow answer` in an `IfExp`); all are fixed, but only by review.
- **Proposed Procedure**: render fixes at runtime instead of scanning source: collect every `AdvisoryError` raised by
  the CLI e2e and integration suites (a pytest plugin or a conftest hook around `AdvisoryError.__init__` in tests)
  and apply the same placeholder, `uv run devkit` and retry-verb checks to the rendered `fix`, `details` and
  `what_to_report`.
- **Expected Benefit**: helper-built fixes are checked on every path the suites already exercise.
- **Cost & Risk**: a test-session hook; failures surface in unrelated tests unless reported in one summary test.
- **Attempted**: not attempted.

## Diagnostic Details

- **Reproduction**: `rg "<[a-z|' ]+>" packages/*/src` against fix builders.
- **Expected / Actual**: expected the contract test to fail on a placeholder fix; actual it passes for helper-built
  strings.
- **Versions**: branch `dev-output-contract`.
- **Conditions**: fixes built outside literal `fix=` arguments.
- **Workarounds Attempted**: review found and fixed the current instances.
- **Related Assets**: `CAP-ADV-agent-advisory-protocol` §8, `ARCH-08-1-agent-output`.

## Evidence

```text
Missed by the scan, found by review: gate/models/contracts.py, native_plan_accept.py, native_handoff.py,
base/errors.py acceptance_unrecorded_fix, proposals/usecases/binding.py, workflow/usecases/handoff.py.
```

## Disposition

- **Disposition**: `packages/devkit/tests/integration/package/test_rendered_advisory_contract.py` and
  `packages/devkit/tests/support/testsupport/advisory_contract.py`: resolved through the user-selected session
  scope of explicit constructed-advisory regression tests plus the existing AST scan. Gate commit-message paths,
  conditional handoff choices, proposal acceptance and zero/one/several unbound workflow helpers share placeholder,
  invocation-prefix and retry-directive checks. Invalid computed-field fixtures verify detection. The targeted
  contract suites pass; unexecuted dynamic paths remain outside this coverage, and no global collection hook was added.
