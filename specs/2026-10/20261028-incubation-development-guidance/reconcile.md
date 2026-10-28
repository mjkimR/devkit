---
reconcile_id: REC-incubation-development-guidance
status: pending
targets:
- file: docs/capabilities/delivery/CAP-DLV-idea-incubation.md
  resolution: modified
- file: docs/usecases/delivery/UC-incubate-an-idea.md
  resolution: modified
- file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  resolution: modified
- file: docs/architecture/ARCH-05-2-components.md
  resolution: modified
- file: docs/architecture/ARCH-07-deployment.md
  resolution: modified
- file: docs/decisions/2026-10/20261028-keep-incubation-guidance-opt-in-and-current-state-based.md
  resolution: modified
- file: docs/steering/glossary.md
  resolution: modified
- file: guides/INSTALL_GUIDE.md
  resolution: modified
- file: guides/install/bundle-recommendations.md
  resolution: modified
- file: guides/install/new-repository.md
  resolution: modified
- file: guides/install/existing-repository.md
  resolution: modified
---

# Reconciliation

The catalog-owned entry, optional role contracts and mutable project context match the capability/usecase,
approach-aware agent guidance, architecture ownership, glossary and installation instructions.
`materials/semantic-exercises.md` separates synthetic input/choices from actual usage and resume observations.

## Scope and deferred work

Shared runtime applicability is implemented by `SPEC-incubation-lifecycle-policy`; this feature consumes it without
changing runtime code. Optional baseline readiness/activation remains `PROP-incubation-sdd-baseline`, whose accepted
work is tracked separately. No milestone completion is claimed. Existing SDD history and project checks remain
protected. The independent reviewer verifies these targets before this record becomes resolved.

## Feedback

`FB-usecase-parser-affected-selection` records the observed selector gap; the source selector is outside this
feature and remains unchanged. The explicit usecase parser regression is included in final verification.

## Entrypoint review

Derivation proposed broad catalog, guide and architecture-config paths; these were rejected because they are not
behavior doorways. The existing capability doorway remains `incubate/SKILL.md`; the same exact source is added to
the new usecase and the incubation portion of agent guidance while preserving its existing SDD doorway.
