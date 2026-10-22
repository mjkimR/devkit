---
reconcile_id: REC-writing-guidance-layers
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-layered-writing-guidance.md
    resolution: modified
  - file: docs/decisions/README.md
    resolution: modified
---

# Reconcile: `SPEC-writing-guidance-layers`

- `CAP-HARN-agent-guidance`: the spec bundle's instruction set (seven instructions) in scope, the asset table and the
  section 4.3 rows for `document-writing`, `decision-writing`, `capability-writing`, `story-writing` and
  `architecture-writing`.
- `CAP-DIST-content-packages`: the `authoring` row names the `agent-asset-writing` instruction.
- `CAP-DLV-proposal-incubation`: the PADR placeholder summary is a Y-statement and the body ends with Confirmation.
- `ARCH-08-2-resource-taxonomy`: the `skill-authoring` preset adds the `agent-asset-writing` instruction.
- `ADR-layered-writing-guidance`: new; records the layering and the header budget.
- `docs/decisions/README.md`: the frontmatter example summary is a Y-statement and the section list ends with
  Confirmation.
- Reference documents outside the Living Spec IDs were updated in step: `docs/development/reference/rules.md`,
  `docs/development/reference/distribution.md`, `guides/install/bundle-recommendations.md`,
  `packages/devkit/README.md`.
- Stories: none changed; the change adds guidance assets, not a new user outcome.
- Glossary: no new domain term; Y-statement, EARS, Example Mapping and fitness function keep their established
  meaning (`living-spec-writing` Glossary rule 5).

## Deferred Work

- Rollout of the guidance to the remaining bundle assets (Non-Goal 1): `FB-writing-guidance-rollout`.
- Mechanical style rules (Non-Goal 2): `FB-writing-style-rules`, restarting after the rollout.
