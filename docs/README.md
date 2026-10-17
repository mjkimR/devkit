# Documentation Guide

This project manages its documentation based on **Spec-Driven Development (SDD)** and the **arc42 + C4 Model** architectural frameworks.

---

## 1. Documentation Directory Map

| Directory | Focus Area | Description |
| :--- | :--- | :--- |
| **`architecture/`** | System Architecture | System blueprints (C4 L1-L3, runtime sequences, deployment infrastructure, cross-cutting concepts) |
| **`capabilities/`** | System Capabilities (Living Spec) | Permanent functional capabilities and contracts partitioned by area (`CAP-<AREA>-<slug>`) |
| **`decisions/`** | Architecture Decisions (ADR) | Context and rationale for critical technology selection and structural decisions (`ADR-<slug>`) |
| **`stories/`** | User Stories | User-centric journeys, actor value flows, acceptance criteria (`US-<slug>`) |
| **`materials/`** | Reference & Spikes | Technical spikes, benchmarks, external libraries, competitor analysis reports |
| **`proposals/`** | Proposals | Pre-spec proposals incubating uncertain work (`PROP-<slug>`) |
| **`development/`** | Development & Collaboration | Local environment setup, Git workflow, commit/PR conventions, CI/CD pipelines |
| **`glossary.md`** | Ubiquitous Glossary | Core domain business and technical ubiquitous terminology definitions |

---

## 2. Interaction Principles Between Documents

1. **Orthogonal M:N Relationship Between Capabilities and Stories**:
   - A user story may traverse multiple functional capability areas.
   - `capabilities/` and `stories/` cross-reference each other via Markdown Frontmatter (`stories:` and `capabilities:`).
2. **Separation of Durable Backbone (`docs/`) and Ephemeral Task Specs (`specs/`)**:
   - `docs/` is the permanent Living Spec maintained throughout the system lifecycle.
   - Sprint/ticket task specifications reside in `specs/` and are archived/cleaned upon completion.
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
