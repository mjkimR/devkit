---
reconcile_id: REC-terminology-authoring-guidance
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconciliation: SPEC-terminology-authoring-guidance

## Reflected

- `CAP-HARN-agent-guidance`: the summary names the terminology guidance and the five-column glossary; the section 4.3
  `living-spec-writing` row names terminology and the glossary, the eight rules and their boundary (they enforce
  nothing and do not authorize renaming code, APIs or schemas), citing
  `ADR-terminology-guidance-lives-in-living-spec-writing`; section 4.7 describes the seeded columns, the "Avoided
  Generic Nouns" section, the pointer to the instruction and the older-glossary fallback, citing
  `ADR-seeded-glossary-columns`.
- `CAP-DLV-delivery-workflows`: business rule 9 states that the Living Spec reflection includes `docs/glossary.md`
  when a change introduces or renames a domain term (`spec-sync` Step 1).
- `docs/glossary.md`: migrated to `Term | Definition | Owner | Avoid | Code identifiers` (AC-07, Task 4); its lead
  names the five columns, and every `Owner` cell resolves (`CAP-ADV-agent-advisory-protocol` and
  `CAP-HOST-lifecycle-observation` replace two IDs that resolved to no document).

## No impact

- Stories: `US-keep-the-living-spec-consistent` and the other stories do not name the glossary or its columns, so no
  acceptance criterion changes.
- `CAP-DOCS-document-search`: unchanged. Avoid entries enter `docs/glossary.yaml` as ordinary synonyms under its
  existing `terms: [{primary, synonyms}]` schema; no schema or expansion change (`ADR-seeded-glossary-columns`).
- Architecture and decisions: no structural change; the two ADRs were promoted at handoff and are not edited.
- Entrypoints: the `CAP-HARN-agent-guidance` entrypoints already cover `bundle/instructions/`, `bundle/skills/` and
  `bundle/seed/`; no other capability gains a code path.
- `docs/development/reference/`: no quick reference mirrors the spec bundle's instructions or seeds.

## Deferred work

None retained. The hygiene rule for generic or avoided terms is a Non-Goal with a reconsider trigger (repeated
violations observed), not work this scope keeps for later.
