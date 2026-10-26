# Documentation Guide

This project manages its documentation based on **Spec-Driven Development (SDD)** and the **arc42 + C4 Model** architectural frameworks.

---

## 1. Documentation Directory Map

| Directory | Focus Area | Description |
| :--- | :--- | :--- |
| **`architecture/`** | System Architecture | System blueprints (C4 L1-L3, runtime sequences, deployment infrastructure, cross-cutting concepts) |
| **`decisions/`** | Architecture Decisions (ADR) | Context and rationale for critical technology selection and structural decisions |
| **`capabilities/`** | System Capabilities (WBS) | Permanent functional capabilities and business rules partitioned by area |
| **`usecases/`** | Use Cases | How each actor reaches a goal: main success scenario, extensions, postconditions, acceptance criteria (Given-When-Then) |
| **`ux/`** | UX Documents | What a person sees and operates: one screen, modal or panel per document, linked from the use case steps it serves |
| **`materials/`** | Reference & Spikes | Technical spikes, benchmarks, external libraries, competitor analysis reports |
| **`development/`** | Development & Collaboration | Local environment setup, Git workflow, commit/PR conventions, CI/CD pipelines |
| **`steering/`** | Steering Documents | Project-wide background read on demand: `glossary.md` (ubiquitous terminology), `glossary.yaml` (search synonyms) and one Markdown file per further topic (product, style) |

---

## 2. Interaction Principles Between Documents

1. **Orthogonal M:N Relationship Between Capabilities and Use Cases**:
   - A use case may traverse multiple functional capability areas.
   - `capabilities/` and `usecases/` cross-reference each other via Markdown Frontmatter (`usecases:` and `capabilities:`).
2. **Separation of Durable Backbone (`docs/`) and Ephemeral Task Specs (`specs/`)**:
   - `docs/` is the permanent Living Spec maintained throughout the system lifecycle.
   - Sprint/ticket task specifications reside in `specs/` and stay in place as work history once completed.
   - Completed work reconciles changed core architecture and rules back into `docs/` (Reconciliation).

---

## 3. Harness Collaboration & Living Spec Governance

1. **AI Agent Collaboration via Skills (`MUST`)**:
   - Use `/spec <intent>` to route engineering tasks, `/spec-next` for orientation, and `/spec-feedback` for capturing friction or improvement observations.
   - Interactive collaboration and multi-step governance workflows are orchestrated via the skill layer.
2. **On-Demand Guidance Loading**:
   - Project-wide coding standards, domain constraints, and architectural guidelines are instructions, listed with their read conditions by `devkit get-context <bundle>` (the spec bundle's own by `devkit get-context spec`).
   - Steering documents in `steering/` carry only `title` and `summary` frontmatter; `devkit get-context spec` lists them in every agent context, and an agent reads a body when a decision concerns its summary.
   - Deterministic checks are rules (`devkit rules check`), occasional procedures are playbooks (the `devkit-playbook` skill, or a one-line offer at `/spec` intake that the user confirms).
3. **Living Spec Reconciliation (`MUST`)**:
   - `docs/` is the durable source of truth. Temporary sprint checklists and PR task lists belong in `specs/`.
   - Upon task completion, all changes to contracts, capabilities, and system behaviors must be reconciled into `docs/` via the `spec-sync` skill.

---

## 4. Authoring Guidelines

Read the `contract-authoring` instruction for normative wording and measurable contracts, and the `living-spec-writing`
instruction for current-state writing, ID references and history placement.
