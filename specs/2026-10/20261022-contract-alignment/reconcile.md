---
reconcile_id: REC-contract-alignment
feature: SPEC-contract-alignment
status: resolved
targets:
  - file: docs/decisions/2026-10/20261022-foundation-and-mcp-package-ownership.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-dist-foundation-ownership.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-host-owned-review-loop-recovery.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-bounded-high-effort-review-loop.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-review-and-reconcile-verification.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-04-delivery-strategy.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconciliation

The change is the Living Spec reflection itself; no code or bundle behavior changed.

`ADR-foundation-and-mcp-package-ownership` supersedes `ADR-dist-foundation-ownership` (now `status: superseded`,
`superseded_by`): `devkit-core` owns the foundation, `devkit-agt` declares the `mcp` extra requiring `devkit-mcp`,
`devkit-dist` declares none; the standalone-scope, executable and dependency-direction rules are carried over.
Verified against the `pyproject.toml` files of `devkit-core`, `devkit-dist`, `devkit-agt` and `devkit-mcp`.
`ARCH-05-1-containers` and `CAP-DIST-content-packages` cite the successor. `ADR-package-split-and-namespaces` (context)
and `ADR-configuration-language-and-rendering` (a decision driver) keep citing the superseded ADR as decision-time
reasoning; the driver's stale "foundation belongs to devkit-dist" wording is recorded as
`FB-configuration-adr-foundation-driver`.

`ADR-host-owned-review-loop-recovery` supersedes `ADR-bounded-high-effort-review-loop` (now `status: superseded`,
`superseded_by`) with the rule of the `spec` bundle's `review-loop.md` section 4: a contested P1 still asserted after
one more round is a `worker` `problem`, the Host owns recovery within the authorized goal, scope and constraints with
no user approval gate, a contested P1 closes only with evidence under the agreed contract, and changing an acceptance
criterion or waiving an agreed constraint needs the user's decision. The rounds, minor-fix, severity, recurrence,
count and cap rules and the carried `ADR-medium-review-delegation` effort rules are carried over.
`CAP-DLV-delivery-workflows` rule 7 states the same hand-over and recovery; rule 15, `ARCH-04-delivery-strategy` and
`ADR-review-and-reconcile-verification` cite the successor. `ADR-medium-review-delegation` keeps
`superseded_by: ADR-bounded-high-effort-review-loop`, which is its actual successor.

Alias wording, each checked against the code: `CAP-DLV-spec-bundles` rule 3 and the `SPEC_EXISTS` row (an ID or
alias declaration takes the slug: `index.declares` in `features/proposals/usecases/specs.py`);
`CAP-TRACE-code-entrypoints` `--target` and its `SPEC_ENTRYPOINTS_TARGET_UNKNOWN` and `SPEC_ID_DUPLICATE` rows
(`index.resolve` in `features/entrypoints/usecases/derive.py`; `DocumentIndex.lookup` raises `DuplicateIdError` for an
alias several documents declare when none has it as its ID); `CAP-DIST-manifest-spec` playbook kind and a
**Playbook aliases** validation rule (`_check_playbook_aliases` in `services/bundles/manifest.py`, `BUNDLE_INVALID`);
the devkit bundle `consumption` instruction (`playbook get` by asset ID or declared alias, canonical `id` and `alias`
in the result, `PLAYBOOK_ALIAS_AMBIGUOUS`: `usecases/playbook_get.py`), synchronized with `devkit sync`; and a
`docs/glossary.md` `Alias` row owned by `CAP-DOCS-document-model` with "search keyword" under Avoid. Each restates
`CAP-DOCS-document-model` section 3.5 rule 6.

No use case changes: `UC-drive-development-to-integration` extension 3c names the cap and recurrence stops only and
stays correct.

## Source feedback

- `FB-package-ownership-adrs-lag-code`: resolved by `ADR-foundation-and-mcp-package-ownership`.
- `FB-review-loop-adr-disagrees-with-bundle`: resolved by `ADR-host-owned-review-loop-recovery` and
  `CAP-DLV-delivery-workflows` rule 7.
- `FB-alias-wording-outside-scope`: resolved by the alias wording above.

Verification for all three: `devkit rules check --ci --base 88f8a0fd` (0 errors), `devkit sync --check` (matches),
`just test-affected` (145 passed) and the review envelope `review-01` (self-review at `low`, no findings).

## Deferred work

Out of scope and recorded as feedback in this bundle: `FB-configuration-adr-foundation-driver`,
`FB-agt-pyproject-foundation-comment` (a `devkit-agt` dependency comment still calls `devkit-dist` the shared
foundation) and `FB-effort-test-cites-superseded-adr` (a test docstring cites the superseded review loop ADR).

## Entrypoints

`devkit spec entrypoints derive` was reviewed (`spec-entrypoints`): the only candidates were the sync outputs
(`.devkit/installation.json`, `.devkit/managed/devkit`) and the `consumption` instruction, none a doorway of the
touched capabilities, which were edited for wording only, so no entrypoint was applied.
