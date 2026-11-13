---
reconcile_id: REC-idea-discovery
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-idea-discovery.md
    resolution: modified
  - file: docs/usecases/delivery/UC-discover-and-refine-an-idea.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
---

# Reconciliation: `SPEC-idea-discovery`

## Contract reflection

- `CAP-DLV-idea-discovery` owns the additive entry, minimum interview, bounded independent exploration, concrete
  proposals, uncertainty routing, conversation default, optional retention and no delivery authority (AC-01–AC-06).
- `UC-discover-and-refine-an-idea` covers the main path, consequential initial question, missing delegation,
  factual/experiential uncertainty, rejection, requested retention and refused access.
- `CAP-DLV-deep-research` names the second entry's distinct owner while retaining all existing research rules;
  its source skill, references and role files are unchanged from the base.
- `CAP-HARN-agent-guidance` reflects explicit discovery's intake exemption and ordinary later implementation intake.
- The glossary registers idea discovery with its boundary from research, mandatory reports and implementation.
- Package README and install guides describe the same bundle selection, explicit invocation and next-step behavior.

## Structure and decisions

No runtime, package, feature edge, shared role module or dependency was added. Content remains inside the existing
catalog bundle and projection mechanisms, so `ARCH-05-2-components` needs no structural change. Existing research
contracts and accepted decisions are preserved; no superseding ADR is required. Bundle renaming and changes to the
separate design-explore bundle were excluded, not committed follow-up work. No required criteria are deferred.

## Entrypoints

Keep the discovery SKILL.md as the doorway for the new capability and use case. Keep the research doorway for its
wording-only clarification and existing spec-bundle doorway for agent guidance. Reject manifest, tests, README,
other bundle directories and role helpers as new doorways for these documents.

## Verification limits

Native lint, types, 1883 affected tests, one installed-wheel E2E, skill validation and exact-head rules passed.
An independent code-reviewer passed all criteria with no findings. The forward exercise verified one inline
conversation without web, file retention or implementation; it did not establish actual role-team effectiveness,
external retrieval or retained-material resume. Distribution tests exercise real projection and upgrade boundaries.
