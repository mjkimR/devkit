# Documentation Guide

This project manages its documentation based on **Spec-Driven Development (SDD)** and the **arc42 + C4 Model** architectural frameworks.

---

## 1. Documentation Directory Map

| Directory | Focus Area | Description |
| :--- | :--- | :--- |
| **`architecture/`** | System Architecture | System blueprints (C4 L1-L3, runtime sequences, deployment infrastructure, cross-cutting concepts) |
| **`capabilities/`** | System Capabilities (Living Spec) | Permanent functional capabilities and contracts partitioned by area (`CAP-<AREA>-<slug>`) |
| **`decisions/`** | Architecture Decisions (ADR) | Context and rationale for critical technology selection and structural decisions (`ADR-<slug>`) |
| **`usecases/`** | Use Cases | How each actor reaches a goal: main success scenario, extensions, postconditions, acceptance criteria (`UC-<slug>`) |
| **`ux/`** | UX Documents | What a person sees and operates: one screen, modal or panel per document, linked from the use case steps it serves (`UX-<slug>`) |
| **`materials/`** | Reference & Spikes | Technical spikes, benchmarks, external libraries, competitor analysis reports |
| **`proposals/`** | Proposals | Pre-spec proposals that plan uncertain work (`PROP-<slug>`) |
| **`development/`** | Development & Collaboration | Local environment setup, Git workflow, commit/PR conventions, CI/CD pipelines, and CLI/API quick references in `development/reference/` |
| **`steering/`** | Steering Documents | Project-wide background read on demand, one ID-free file per topic with `title` and `summary` frontmatter: `glossary.md` (ubiquitous terminology) and `glossary.yaml` (search synonyms); `devkit get-context spec` lists them in every agent context |

---

## 2. Interaction Principles Between Documents

1. **Orthogonal M:N Relationship Between Capabilities and Use Cases**:
   - A use case may traverse multiple functional capability areas.
   - `capabilities/` and `usecases/` cross-reference each other via Markdown Frontmatter (`usecases:` and `capabilities:`).
2. **Separation of Durable Backbone (`docs/`) and Ephemeral Task Specs (`specs/`)**:
   - `docs/` is the permanent Living Spec maintained throughout the system lifecycle.
   - Sprint/ticket task specifications reside in `specs/`; completed bundles remain in place as work history.
   - Completed work reconciles changed core architecture and rules back into `docs/` (Reconciliation).

---

## 3. Harness Collaboration & Living Spec Governance

1. **AI Agent Collaboration via Skills**:
   - When `devkit-spec` is installed, use `/spec <intent>` to route engineering tasks, `/spec-next` for orientation, and `/spec-feedback` for capturing friction or improvement observations.
2. **On-Demand Guidance Loading**:
   - Project-wide coding standards, domain constraints, and architectural guidelines are instructions, listed with their read conditions by `devkit get-context <bundle>`.
   - Deterministic checks are rules (`devkit rules check`), occasional procedures are playbooks (`devkit playbook search`).
3. **Living Spec Reconciliation**:
   - `docs/` is the durable source of truth. Temporary sprint checklists and PR task lists belong in `specs/`.
   - Upon task completion, all changes to contracts, capabilities, and system behaviors must be reconciled into `docs/`.

## 4. Finding Module Documentation

- Behavior and contracts: `capabilities/<area>/CAP-<AREA>-<slug>.md`.
- Component structure, dependencies, and runtime flows: `architecture/ARCH-*.md`.
- CLI usage, configuration, error codes, and library examples: [Module References](development/reference/README.md).

Module references point to the durable capability and architecture documents; maintain each contract there once.
Refer to ID-bearing documents by full ID; use ordinary links for quick references and other documents without IDs.
