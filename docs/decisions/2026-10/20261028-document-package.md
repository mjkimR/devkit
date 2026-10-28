---
id: ADR-document-package
title: Separate the document system into devkit-docs
summary: "For delivery processes beyond SDD, we move the document model, lookup, namespaces and document rules into a devkit-docs wheel that devkit-spec depends on, to keep the document system free of any delivery process, accepting renamed commands, codes and config."
status: accepted
created_at: 2026-10-28
---

# [ADR-document-package] Separate the document system into devkit-docs

## 1. Context & Problem Statement

devkit-spec held two kinds of feature in one wheel. The document system serves any repository that keeps devkit
documents: the document model, lookup and search, namespaces and the document rules. The SDD delivery process is
the other kind: proposals, spec bundles, workflows, scope, workers and the lifecycle rules. The document code
imported the delivery process. It read Planning branches to show draft proposals as `reviewing` and read
namespaces through the `[tool.spec]` policy reader. It also shared error, layout and helper modules with lifecycle
code. Another delivery process, such as idea incubation, could not build on the documents without SDD. The coupling
survey `docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md` lists the seams.

## 2. Decision Drivers

- The document system depends on no delivery process; a delivery process plugs in without editing it.
- Repositories that keep SDD observe the same behavior.
- Ownership stays explicit: one regular package per wheel and one owner per `[tool.<name>]` table.
- No external consumer exists yet, so interfaces change in place without shims (AGENTS.md Compatibility).

## 3. Considered Options

- Keep one package and control lifecycle features through presets: the cheapest change, but the coupling inside one
  package has no import boundary to enforce.
- A second regular package inside the devkit-spec wheel: separates imports, but one wheel would hold two packages,
  against `ADR-package-split-and-namespaces`.
- A separate devkit-docs wheel that devkit-spec depends on: one owner per package and an enforceable boundary,
  at the cost of one more wheel to release.

## 4. Decision Outcome

Adopt the separate devkit-docs wheel.

1. **Package**: `devkit-docs` with the regular package `devkit_docs` owns `features/documents`, the document rules'
   implementations and services (`features/governance`), the entrypoint path contract, the `DOCS_` errors and the
   document layout vocabulary. Its version follows root `VERSION` (`ADR-single-release-version`). devkit-spec
   depends on it at the same version and keeps the delivery process and the lifecycle rules. This extends the
   wheel list of `ADR-package-split-and-namespaces`.
2. **Kind vocabulary**: every document kind, the delivery kinds included, stays in the document package's kind
   table (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`). The formats and path grammars of proposals,
   spec bundles, feedback and milestones are document structure. What a delivery process does with them stays in
   that process.
3. **Extension point**: a delivery process changes how `devkit docs list` shows documents through the entry-point
   group `devkit.docs.status_overlay`; devkit-spec registers the Planning display of draft proposals. Other
   lifecycle behavior moves only when a seam requires it.
4. **Configuration**: document namespaces move from `[[tool.spec.namespaces]]` to `[[tool.docs.namespaces]]`,
   owned and read by devkit-docs. This supersedes the namespaces part of `[tool.spec]` in
   `ADR-spec-package-on-devkit`.
5. **Commands and codes**: `devkit docs resolve|refs|list|search` replace the `devkit spec` forms. The document
   codes move from `SPEC_` to `DOCS_`, and `DOCS_CONFIG_INVALID` reports a malformed `[tool.docs]`.
6. **Scanner**: the document model keeps using devkit-agt's Markdown scanner; moving it to devkit-core is unrelated
   to this boundary.
7. **Distribution**: the spec bundle keeps shipping every rule asset, and the document rules' wrappers import
   devkit_docs. A document-only installation is separate work (`PROP-document-bundle-split`).

## 5. Consequences

- **Positive**: the document layer has no import edge to the delivery process, and the architecture declaration
  enforces that. Idea incubation or another process can reuse the document system.
- **Negative / Risks**: agents and guidance must use the renamed commands and codes. Projects with
  `[[tool.spec.namespaces]]` must move them to `[[tool.docs.namespaces]]`; a leftover entry is rejected as an
  unknown key. Releases build one more wheel.
- **Follow-ups**: `PROP-document-bundle-split` provides a document-only installation. The viewer hard-codes kind
  prefixes and layout; a change to the kind table must be mirrored there.

## 6. Confirmation

`RULE-architecture` checks the `devkit_docs` and `devkit_spec` declarations in `.devkit/architecture.toml`.
`packages/devkit-docs/tests` covers the commands, codes, `[tool.docs]` and its template. The status overlay is
covered by `packages/devkit-spec/tests/integration/features/proposals/test_backlog_guard.py`. Each package's
`tests/integration/package/test_documented_codes.py` requires every code to be documented.
