---
reconcile_id: REC-deep-research-bundle
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-idea-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-an-idea.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-split-deep-research-bundle.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-retain-research-as-cited-materials.md
    resolution: modified
---

# Reconciliation

`CAP-DLV-deep-research` is the new contract of the research entry: explicit selection, installation without
devkit-spec, explicit-only invocation with no suggestion, approach neutrality, the SDD intake exemption, research
authority with no commit, the carried research rules (bounded evidence, truthful verification, optional support,
role boundaries, independent alternatives, provenance, optional criticism, initial synthesis, bounded partial
result, completion, workspace, selective promotion), the retention, collision, resume and citation conventions,
material preservation, the four-role table and the workspace path. Each checked rule names its test.

`CAP-DLV-idea-incubation` keeps product iteration only: the research rules 17 to 23, 25 and 26 left for the new
capability, rule 24 (useful alternatives) stays as rule 17 and links a research material by its MAT ID, the role
table keeps three roles, §1 and §4 drop the research entry, and `UC-research-an-idea-and-shape-a-roadmap` left its
`usecases`. Its ADR citations move to `ADR-split-deep-research-bundle` and `ADR-retain-research-as-cited-materials`.

`UC-research-an-idea-and-shape-a-roadmap` keeps its ID and links `CAP-DLV-deep-research`: step 2 recovers goals
without an approach check, extensions 2a and 2b now cover SDD and adaptive consumers, 2c a resumed partial material,
7b a material ID collision; Scenario 2 runs under either approach, Scenario 9 hands the material to later work, and
Scenarios 12 and 13 cover 2c and 7b. Its Rules line drops approach inspection and adaptive clarification.
`UC-incubate-an-idea` drops extension 4b and its scenario, and gains 3b (Scenario 8): retained research is read by
its ID and never started or suggested. `UC-route-development-intent` gains 1e (Scenario 2c), the SDD intake
exemption. `CAP-HARN-agent-guidance` states the exemption under the approach-aware SDD entry, describes the
incubation bundle with three roles and adds a Deep research entry section.

`ARCH-05-2-components` names both catalog bundles and their independence; `ARCH-07-deployment` adds the entry point
and the new installed-consumer test. The glossary registers **Deep research**. The two promoted ADRs change only
their body header from "Supersedes on promotion" to "Supersedes"; their `supersedes` fields already name the
superseded ADRs.

## Entrypoints

`CAP-DLV-deep-research` starts with the deep-research skill as its doorway. The dead `incubate-research` entrypoint
was removed from `CAP-DLV-idea-incubation` and replaced by the deep-research skill in `CAP-HARN-agent-guidance` and
`UC-research-an-idea-and-shape-a-roadmap`. Derived candidates for the bundle directories, tests, guides, README,
`pyproject.toml`, `.devkit/architecture.toml`, the spec skill and the smoke script are not behavior doorways and were
rejected.

## Scope and follow-up

- Not changed, outside the write scope: the superseded ADRs `ADR-extend-incubation-with-optional-discovery-teams`
  and `ADR-keep-discovery-plans-distinct-from-delivery-commitments` keep `status: accepted` without
  `superseded_by` (the repository has superseded ADRs in both forms); the release handbook (`handbook/`) does
  not yet describe the deep-research bundle until the release handbook procedure refreshes it.
- `docs/materials/2026-10/20261029-incubation-discovery-teams/` and completed specs keep their historical mentions;
  migrating earlier materials is a Non-Goal.
- No deferred work: every acceptance criterion is in this Unit. `PROP-rename-incubation-to-adaptive-dev` already
  depends on this spec and renames the remaining incubation bundle.
