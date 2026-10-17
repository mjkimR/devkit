# Architecture Documentation

The architecture of devkit in arc42 chapters, with C4 diagrams in Mermaid. Each chapter is an ID-bearing document; refer to it by its ID (`ARCH-<NN>-<slug>`).

## 1. Chapters

| NN | arc42 Chapter | Document | Covers |
| :--- | :--- | :--- | :--- |
| 01 | Introduction and Goals | `ARCH-01-introduction-and-goals` | Mission, core modules, agent-first design, quality goals |
| 02 | Architecture Constraints | `ARCH-08-cross-cutting` | Layering, POSIX platforms, Python runtime, standard library boundary |
| 03 | System Scope and Context | `ARCH-03-context` | C4 L1: AI coding agents, Git work trees, package managers, host runtime |
| 04 | Solution Strategy | `ARCH-01-introduction-and-goals` | Single CLI distribution, standard library advisory protocol, opt-in bundles |
| 05 | Building Block View | `ARCH-05-1-containers`, `ARCH-05-2-components` | C4 L2: package topology (`devkit-agt`, `devkit-advisory`, content packages); C4 L3: internal modules |
| 06 | Runtime View | `ARCH-06-runtime-view` | Sync transactions, rule evaluation and fix cycles, workflow execution, worktrees |
| 07 | Deployment View | `ARCH-07-deployment` | Wheel distribution, Git dependency sources, projected agent directory layout |
| 08 | Cross-cutting Concepts | `ARCH-08-cross-cutting` | Agent Advisory Protocol, agent-first output sentinels, resource taxonomy, command plugins |
| 09 | Architecture Decisions | `docs/decisions/` | ADRs |
| 12 | Glossary | [glossary.md](../glossary.md) | Ubiquitous vocabulary |

## 2. Conventions

- Chapter documents are `ARCH-<NN>[-<n>]-<slug>.md`: `<NN>` is the arc42 chapter number (never 09 or 12).
- The frontmatter `id` equals the file stem (`RULE-id-convention`); `summary` is required (`RULE-document-summary`).
