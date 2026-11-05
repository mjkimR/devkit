---
id: PROP-deep-research-practical-orchestration-target
title: Target Living Spec for practical deep-research orchestration
status: draft
proposal: SPEC-deep-research-practical-orchestration
created_at: 2026-11-05
targets:
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
  - file: docs/decisions/2026-11/20261105-deliverable-driven-research.md
---

# Planned source and Living Spec reflection

This is a Planning target list for `SPEC-deep-research-practical-orchestration`; it describes proposed behavior.
No source or current contract changes are made by this Planning turn. The prospective ADR path assumes handoff
on 2026-11-05; use the actual promoted path if handoff occurs on another date.

## Source paths

| Path | Expected change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md` | Frame the requested deliverable and intended use before allocation; check usefulness before retaining the result. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/orchestration.md` | Add assignment contribution, selective source reopening, optional usefulness criticism and retrieval classification within the existing bound. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/synthesis.md` | Retain the requested artifact and relevant next action; distinguish optional research from prerequisites and respect declined validation work. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/roles/research-investigator.md` | Report inspected evidence and limits; permit ordinary retrieval recovery without bypassing refusal. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/roles/direction-explorer.md` | Apply the same retrieval distinction and contribute the assigned output under user constraints. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/roles/discovery-critic.md` | Check supplied deliverable/use constraints alongside consequential evidence and assumption problems; allow zero findings. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/roles/discovery-planner.md` | Draft proportionate requested artifacts and conditional follow-up without unwanted prerequisites. |
| `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` | Adjust focused instruction-contract checks only where changed text requires it; preserve explicit-only selection, local roles, optional support and material ownership checks. |
| `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py` | Run the existing consumer smoke; change only if the selected source contract makes a focused installed check necessary. |

The manifest and workspace allocation reference are expected to remain unchanged. No runtime feature dependency is
added. Development may omit a listed file when the settled instruction change does not require it; explain that
choice in its plan and review evidence.

## Contract targets

- `CAP-DLV-deep-research`: retain the existing explicit invocation, approach neutrality, source qualification,
  optional role, research authority and material-retention rules. Extend its behavior rules with requested
  deliverable/intended use, coordinator usefulness check, selective verification and bounded retrieval recovery.
- `UC-research-an-idea-and-shape-a-roadmap`: reflect output framing in step 3 and selective checking in steps 5–7.
  Add extensions and acceptance scenarios for a practical repository-reference request, a declined validation
  program, a supported role return, ordinary retrieval failure, permission refusal and ambiguous authorization.
- `ADR-deliverable-driven-research`: promote through handoff to the decision under `docs/decisions/`; no existing
  ADR decision is replaced. The exact promoted document belongs to the Development reconciliation targets.

## Semantic review examples

1. A request for reusable agent configurations returns repository/file references, what to borrow or omit and a
   starting composition. It does not stop at evidence about whether agent teams work.
2. A user declines comparative validation. The recommendation names uncertainty and a usable starting point;
   a same-task comparison is not an adoption prerequisite.
3. A decisive investigator claim has an identified primary source and relevant inspected passage. The coordinator
   reviews that evidence and reopens only a consequential gap, contradiction or suspect claim.
4. A public-source timeout without access refusal can receive a retry or another permitted primary source within
   the original bound. Record what failed and what was actually inspected. An alternate source that does not
   support the original claim leaves it unverified.
5. A sandbox/trust/permission refusal stops that resource. Ambiguous authorization also stops that resource;
   neither case permits another tool, identity, process or path to obtain denied access.
6. A small request finishes inline; no critic, fixed issue count or effectiveness experiment is required.

Distribution tests prove packaging and explicit boundaries. Review checks these instruction examples; it does not
establish aesthetic quality, team superiority, token savings or empirical research effectiveness.
