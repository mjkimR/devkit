---
reconcile_id: REC-superseded-reference-cleanup
status: resolved
targets:
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-configuration-language-and-rendering.md
    resolution: modified
---

# Reconciliation

No production code or behavior changed. The Living Spec changes are the two targets above; the other changes are a
package metadata comment, a test docstring, a test assertion and the `reconcile-reviewer` role contract of the `spec`
bundle with its regenerated projections.

`UC-drive-development-to-integration` gains extensions 7f and 7g and scenarios 17 and 18, and its Extensions section
states that the coded executor refusals it does not name, with their recoveries, are listed in
`CAP-INT-mcp-services`. Each extension restates its capability's directive without command syntax:

- 7f, `INTEGRATION_RECEIPT_READER_CHANGED`: `CAP-INT-mcp-services` section on the receipt case says the refusal comes
  before every provider run, prepare included, that restarting does not help and that the directive is the CLI route
  run from the source's code under separately granted authority, never an automatic route change. The extension keys
  to step 7 and resumes at step 9, like 7d; `docs/development/reference/integration.md` gives the same recovery.
- 7g, `MCP_RUNTIME_STALE`: `CAP-MCP-runtime-registration` says every call other than a read-only one is refused before
  execution guards and the tool run, naming the stale modules, with the directive to restart or reconnect the retained
  service, and read-only tools keep running; `CAP-INT-mcp-services` section 6 says the same. The extension keys to step
  7 and resumes there.

The use case cites `CAP-MCP-runtime-registration` in 7g without adding it to `capabilities:`, because the trace link
needs the capability's `usecases` list, outside this unit's write scope; recorded as
`FB-runtime-registration-usecase-link`. Neither capability changes.

`ADR-configuration-language-and-rendering`: one decision driver reworded as an editorial edit under
`ADR-immutable-decisions-editable-records`. "The foundation belongs to devkit-dist and cannot import the harness,
following `ADR-dist-foundation-ownership`" becomes "Project configuration belongs to devkit-dist, which cannot import
the harness (`ADR-foundation-and-mcp-package-ownership`)". The driver's weight is unchanged (the configuration code
cannot import the harness); the cited outcome of `ADR-foundation-and-mcp-package-ownership` keeps project
configuration, receipts and execution binding in the distribution's project feature and forbids `devkit-dist` to
depend on `devkit-agt`.

No other Living Spec impact:

- The `reconcile-reviewer` stays read-only (`x-git-actions: [read]`, Write and Edit disallowed, read-only or sandboxed
  shell), so `ARCH-04-1-ecosystem-boundaries` ("Read-only inspection") and the "distinct read-only" statements of
  `ADR-host-owned-review-loop-recovery` and `ADR-medium-review-delegation` still hold. No capability states the role's
  tool set (`rg` over `docs/capabilities`: only an unrelated projection example in `CAP-DIST-agent-projections`).
- The `spec-delegate` payload reference states no missing shell for the reconcile reviewer; its stale note on the
  `challenger` row is out of scope and recorded as `FB-payload-challenger-no-shell-note`.
- The pyproject comment and the test docstring are not Living Spec documents.

## Source feedback

- `FB-agt-pyproject-foundation-comment`: resolved; the `devkit-dist` requirement comment reads "the devkit executable
  and distribution, released in lockstep from the same tag" (AC-01).
- `FB-configuration-adr-foundation-driver`: resolved by the driver edit above (AC-02).
- `FB-effort-test-cites-superseded-adr`: resolved; the module docstring cites `ADR-host-owned-review-loop-recovery`
  (AC-03).
- `FB-integration-usecase-coded-extensions`: resolved by extensions 7f and 7g, scenarios 17 and 18 and the delegation
  sentence (AC-04).
- `FB-reconcile-reviewer-diff-access`: resolved; the role contract has the `challenger` host settings, its body runs
  `git diff <base> <head>` for `diff_scope` and compares `git rev-parse HEAD` with the `diff_scope` head, the contract
  test asserts the host settings, and `devkit sync` regenerated the claude-code, codex and antigravity projections
  (AC-05).

Verification for all five: the `rg` commands of AC-01 to AC-03, `just test-affected` (mode=full, 4664 passed, 14
skipped), `just lint devkit-spec`, `devkit rules check --ci --base 8801eb6a` (0 errors), `devkit sync --check`
(matches) and the review envelope `review-01` (self-review at `low`, no findings).

## Deferred work

Out of scope and recorded as feedback in this bundle: `FB-payload-challenger-no-shell-note` and
`FB-runtime-registration-usecase-link`.

## Entrypoints

`devkit spec entrypoints derive` was reviewed (`spec-entrypoints`): the only candidates were for
`UC-drive-development-to-integration` (the `reconcile-reviewer` contract and its projections, the sync receipt, two
tests and the `devkit-agt` pyproject), none a doorway of the integration behavior the use case describes, and the ADR
is not entrypoint-bearing, so no entrypoint was applied.
