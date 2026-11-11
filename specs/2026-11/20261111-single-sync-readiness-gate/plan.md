---
id: PLAN-single-sync-readiness-gate
spec: SPEC-single-sync-readiness-gate
---

# Technical Plan: `SPEC-single-sync-readiness-gate` One readiness gate for a synchronized checkout

## 1. Constitution & Invariant Review

None. The change documents how two existing commands are used and changes no command contract, so no ADR is
needed. It agrees with `CAP-DIST-sync-and-transactions` ("`sync --check` remains the general synchronization
gate"; "`sync --check` stays the read-only check for a workspace that is already synchronized") and with
`ADR-mcp-runtime-and-shared-artifacts` (general `devkit status` emits no `MCP_REGISTRATION_PENDING`), which the
current `devkit status` help contradicts. Bundle text follows the authoring bundle's self-containment rule: no
document ID of this repository in the changed bundle files.

## 2. Architecture Overview & Impact

Documentation, bundle text and one CLI help string; no detection code, exit code, JSON field or feature edge.

| Component | Change | Serves |
| --- | --- | --- |
| `CAP-DIST-sync-and-transactions` | new `### Readiness Gate` subsection after "Locked Synchronization": the criterion, what `status` does not detect, the MCP registration rule and the step order | AC-01 |
| `docs/development/reference/distribution.md` | the closing sentence of the `devkit status` section names the gate and the report | AC-02 |
| devkit bundle `instructions/consumption.md`, `instructions/in-repo-bundle.md` | completion criteria become `uv run devkit sync --check` exits `0` | AC-03, AC-07 |
| adaptive-dev `agent-asset-conversion/references/project-bundle.md` | Completion: `sync --check` exits `0`; the bundle's selection is read from `uv run devkit list` as a fact | AC-03, AC-07 |
| `UC-import-third-party-agent-assets` Scenario 7 | Then clause ends with `uv run devkit sync --check` exits `0` | AC-03 |
| `guides/INSTALL_GUIDE.md` Step 5, `guides/install/existing-repository.md` "Already installed" | `sync --check` is the readiness check, `status` the diagnosis, in the order of `guides/install/mcp.md` | AC-04 |
| `devkit_dist.features.distribution.cli.selection.status` docstring (the `--help` text) | names `sync --check` as the readiness gate; drops "MCP registration still to set up" | AC-05 |
| `test_cli_contract.py` (distribution integration tests) | one test on `status --help` | AC-05 |

The devkit bundle is selected by this repository, so `uv run devkit sync` rewrites the tracked receipt
`.devkit/installation.json` (hashes of the two changed instructions); it is committed as sync output. The
adaptive-dev bundle is not selected here, so its change produces no sync output.

## 3. Component & Interface Design

The help text after the change (normative wording of the last sentences of the `status` docstring):

```text
Warnings and notices (override drift under the default "warn", a package the
project does not deploy that fails to load) are listed under notices. Output is
JSON only: nothing is repeated on stderr. This is a diagnostic report, not the
readiness gate: `devkit sync --check` exiting 0 says the checkout is synchronized.
```

## 4. Error Handling & Edge Cases

- `sync --check` exits `2` on a refusal (conflict, unsafe path, pending journal, invalid selection); every criterion
  says "exits `0`", so exit `1` and `2` are both not ready and need no separate wording.
- A clone using MCP after `sync --locked` keeps `sync --check` at exit `1` until `sync --registrations-only`; the
  capability and "Already installed" order the steps so the check runs last.

## 6. Verification & Test Plan

- AC-01, AC-02, AC-03, AC-04: read the changed sections; `rg -n "devkit status.{0,60}exit" packages/*/src/*/bundles guides docs/usecases`
  and `rg -n "remains the check that says whether a sync is needed" docs/` find nothing.
- AC-05: `uv run pytest packages/devkit-dist/tests/integration/features/distribution/test_cli_contract.py`.
- AC-06: `git diff --stat 2fcff57d -- packages/devkit-dist/src/devkit_dist/features/distribution/usecases/` is empty;
  `just test-dist`; `just test-affected` (with its `mode=full` fallback).
- AC-07: `uv run devkit bundle validate` on the devkit and adaptive-dev bundle directories; the agent-asset ID search
  of the authoring bundle on the changed files; `uv run devkit rules check --ci --base main`.
- Also: `just lint`, the type check of `docs/development/setup.md`, `uv run devkit sync --check` after the sync.
