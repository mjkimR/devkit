---
id: ADR-dist-foundation-ownership
title: Distribution standalone scope and foundation ownership
summary: Defines standalone distribution features and assigns the shared foundation and sole devkit CLI entry point to devkit-dist, with harness engines supplied by devkit-agt.
proposal: SPEC-devkit-dist-package-separation
status: accepted
created_at: 2026-10-18
---

# [ADR-dist-foundation-ownership] Distribution standalone scope and foundation ownership

- **Status**: Accepted
- **Date**: 2026-10-18

---

## 1. Context & Problem Statement

`devkit.distribution` currently depends on shared core services, playbook search, and native host hook support housed in `devkit-agt`. Moving the distribution directory alone would leave a dependency on the harness package and would not provide a standalone command line.

## 2. Decision Drivers

- Asset consumers can install and operate distribution without the rules, workflow, or gate engines.
- A single package owns the `devkit` executable when distribution and harness are installed together.
- Dependency direction follows the foundation-to-engine layering.

## 3. Considered Options

- Extract only the distribution directory while retaining shared services and CLI ownership in `devkit-agt`.
- Move distribution, its required shared foundation, and CLI ownership into `devkit-dist`, with harness engines supplied by `devkit-agt`.

## 4. Decision Outcome

Choose the second option as the preliminary direction for Planning.

- Installing `devkit-dist` alone MUST provide distribution commands, native hook support, context loading, and playbook functionality without installing `devkit-agt`.
- `devkit-dist` MUST own the shared foundation needed for that standalone scope and the sole `devkit` console entry point.
- `devkit-agt` MUST depend on `devkit-dist` and supply the higher-level harness engines. `devkit-dist` MUST NOT depend on `devkit-agt`.
- Planning determines the exact split of shared core, search, and host modules, the Python namespace, command registration, schema ownership, and bundled content. These implementation choices are not settled by this decision.

This preliminary decision does not constitute acceptance of the complete proposal or authorization to begin implementation.

## 5. Consequences

- The change covers shared modules, CLI composition, packaging and release wiring, and affected contracts and guides in addition to `devkit.distribution`.
- Verification must exercise distribution in an environment without `devkit-agt`, and distribution plus harness together, including command discovery and a single executable owner.
- Optional search and host integrations must be accounted for when defining standalone dependencies and extras.
