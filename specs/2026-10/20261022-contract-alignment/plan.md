---
id: PLAN-contract-alignment
spec: SPEC-contract-alignment
---

# Technical Plan: `SPEC-contract-alignment` Align ADRs and alias wording with the shipped contracts

## 1. Constitution & Invariant Review

- Changing what an accepted ADR decides needs a new ADR (`ADR-immutable-decisions-editable-records`): both changes
  are new ADRs with `supersedes`, and the replaced ADRs get `status: superseded` and `superseded_by`.
- The review loop rule change was decided by the user (the bundle rule holds), so the ADR records an existing
  decision; `review-loop.md` is not edited.
- `CAP-DOCS-document-model` section 3.5 rule 6 already defines the alias rule across contracts; the alias wording
  restates it per contract and adds no behavior.

## 2. Architecture Overview & Impact

| Area | Change |
| --- | --- |
| `docs/decisions/2026-10/20261022-foundation-and-mcp-package-ownership.md` | New ADR-foundation-and-mcp-package-ownership, superseding `ADR-dist-foundation-ownership` (AC-01). |
| `docs/decisions/2026-10/20261022-host-owned-review-loop-recovery.md` | New ADR-host-owned-review-loop-recovery, superseding `ADR-bounded-high-effort-review-loop` (AC-02). |
| The two superseded ADRs | `status: superseded`, `superseded_by`, the status line; no other edit. |
| `CAP-DLV-delivery-workflows` | Rule 7 states the Host-owned `problem` and recovery round; rule 15 cites the successor (AC-03). |
| `CAP-DLV-spec-bundles`, `CAP-TRACE-code-entrypoints`, `CAP-DIST-manifest-spec` | Alias wording (AC-04). |
| devkit bundle `instructions/consumption.md`, then `devkit sync` | Playbook get by a declared alias (AC-04). |
| `docs/glossary.md` | `Alias` row (AC-04). |
| Link repair | `ARCH-05-1-containers`, `CAP-DIST-content-packages`, `ADR-configuration-language-and-rendering`, `ADR-package-split-and-namespaces` (to the foundation successor); `ARCH-04-delivery-strategy`, `ADR-review-and-reconcile-verification` (to the review loop successor) (AC-05). |

Facts verified before writing:

- `packages/devkit-core/pyproject.toml`: `devkit-core` depends on `devkit-advisory` and `pyyaml` only;
  `src/devkit_core/` holds `base/` and `core/`; `tests/integration/test_package.py` checks its imports.
- `packages/devkit/pyproject.toml` (`devkit-agt`): `mcp = ["devkit-mcp==<version>"]`,
  `search = ["devkit-dist[search]"]`; `packages/devkit-dist/pyproject.toml` declares only the `search` extra and the
  `devkit` script; `packages/devkit-mcp/pyproject.toml` depends on `devkit-core`, `devkit-dist` and `mcp`.
  `packages/devkit/tests/integration/package/test_lockstep.py` pins the `devkit-agt` extras.
- `features/proposals/usecases/specs.py` refuses a slug through `index.declares` (ID or alias);
  `features/entrypoints/usecases/derive.py` resolves `--target` IDs through `index.resolve` (ID or alias;
  `DuplicateIdError` for an ambiguous one); `services/bundles/manifest.py` `_check_playbook_aliases` refuses an alias
  equal to a playbook asset ID of the bundle or declared twice; `usecases/playbook_get.py` resolves an alias when
  exactly one effective header declares it and reports the canonical `id` and the `alias`.

Choices:

- ADR slugs name the decision: foundation and `mcp` extra ownership; Host-owned recovery in the review loop.
- The review loop successor restates the whole loop (rounds, minor fixes, severity, recurrence, count, cap) and the
  carried-over `ADR-medium-review-delegation` rules, because it replaces a whole ADR.
- `ADR-configuration-language-and-rendering` keeps its driver text: project configuration stays in the
  distribution's project feature (`ADR-package-split-and-namespaces`), so only the citation is repointed.

## 3. Verification & Test Plan

- `uv run devkit rules check` (document references, summaries, superseded links).
- `uv run devkit sync` after the `consumption` edit, then `uv run devkit sync --check`.
- `just test-affected` for the bundle instruction change.
- `git diff --check`.
- `rg` over `docs/` for the superseded IDs and for "waiver citing" to confirm AC-03 and AC-05.
