---
reconcile_id: REC-formal-document-templates
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-transactions/design.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md
    resolution: modified
  - file: docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md
    resolution: modified
  - file: docs/domain/delivery/DOMAIN-delivery-relationships.md
    resolution: modified
  - file: docs/operations/OPS-distribution-sync.md
    resolution: modified
---

# Formal document templates reconciliation

## Authoring contract

`ADR-problem-first-formal-document-openings` records the decision; `CAP-DOCS-documentation-ownership` §3.3 item 2
now restates its three outcome clauses: the scoping step (settle the one reader question, split or drop a document
without one), the problem opening per kind with no question section or label, and the closing authority boundary
with maintenance trigger and next useful action. §4 describes the template shape (problem lead, guidance in HTML
comments, `## Authority boundary` and `## Maintenance and next action`) and no longer names the compatibility
pointer. The implementation is the docs bundle's `templates/{design,domain,operations}.md` and
`instructions/{design,domain,operations}-writing.md`; each statement was compared with those files at the reviewed
head.

`ADR-linked-domain-relationship-views` already carries the "Superseded in part" pointer from the handoff commit; its
`§3.4` traces stay as history (spec Non-Goal 5). `ADR-documentation-ownership-and-linked-design-entries` traces a
clause about question-specific owner links to §3.3, which still holds, so it needs no change.

## Template inventory

`CAP-DOCS-document-model` (§3.2 closing paragraph and "Document asset distribution") states eight templates with no
compatibility pointer, matching the bundle's `templates/` directory, the `test_distribution.py` stem set, the
installed `.devkit/managed/docs/templates/` and the receipt `.devkit/installation.json`. `packages/devkit-docs/README.md`
states the same count as a derived reference.

| Removed path | Replacement | Check |
| :--- | :--- | :--- |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design-template.md` | none, by Planning decision Q4: `templates/design.md` | `rg -n design-template docs/capabilities docs/architecture docs/development packages` exit 1; `devkit sync --check` OK; the receipt no longer lists it |

## Formal documents

The five delivered documents are reorganized to their kind's revised template; no file moved, no ID, owner, link,
`§` reference or advisory code was removed (compared against the base `93e72152c` versions). Design, domain and
operations impact is form only: no mechanism, concept or routing statement changed owner, and the
`DESIGN-distribution-file-directory-replacement` entrypoint is unchanged.

| Document | Opening | Body | Closing |
| :--- | :--- | :--- | :--- |
| `DESIGN-distribution-transactions` | label removed; lead states the change-set problem | `## Ordering and rollback detail` | authority prose under `## Authority boundary`; maintenance touchpoints and the next read under `## Maintenance and next action` |
| `DESIGN-distribution-file-directory-replacement` | label removed; lead states the ordering and evidence problem | topic headings unchanged | capability ownership and "not a rollback procedure" under `## Authority boundary`; maintenance seam and the Recovery pointer under `## Maintenance and next action` |
| `DOMAIN-bundle-selection-and-installation` | `## Question` replaced by the confused concepts | `## Relationship overview` table in `Concept or relationship \| Distinction \| Authoritative owner` | split into authority boundary and maintenance with owner pointers |
| `DOMAIN-delivery-relationships` | `## Question` replaced by the confused concepts | table re-columned, owner separated from distinction; walkthrough kept | split into authority boundary and maintenance with owner pointers |
| `OPS-distribution-sync` | lead unchanged | `## Routing` with the skeleton columns; `## Normal-state observation` | `## Authority boundary`; unmatched-evidence guidance moved under `## Maintenance and next action` with a review trigger |

No inbound link targeted a renamed heading anchor (`rg` over the repository outside specs and materials). No use
case, architecture section, UX document or glossary term is affected: the change adds no behavior, component or
term.

## Entrypoints

No DESIGN entrypoint changed; the only declared one, `transaction.py`, is untouched.

## Source feedback

`FB-scout-lacks-web-search` (repo) concerns the scout role contract in the spec bundle, which this spec does not
touch; it stays open for Backlog triage.
