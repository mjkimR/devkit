---
id: PROP-adaptive-package-extraction-target
title: Target Living Spec Structure for PROP-adaptive-package-extraction
status: draft
proposal: PROP-adaptive-package-extraction
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/architecture/ARCH-07-deployment.md
---

# [Blueprint] PROP-adaptive-package-extraction: Target Living Spec Structure for Extract adaptive development into a devkit-adaptive distribution

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-adaptive-package-extraction is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-DLV-adaptive-development`: the bundle's owner changes from the catalog to the `devkit-adaptive` distribution.
  Entrypoint paths, the independent-installation rule and its test paths follow the move. The "new wheel" exclusion
  is removed; the runtime scheduler, agent bus and model routing exclusions stay.

---

## 2. Use Cases Plan (docs/usecases/)

No use case changes: the move changes no agent or user flow.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-2-components`: add the `devkit-adaptive` package and its layout; remove `adaptive-dev` from the
  content-only catalog's ownership sentence.
- `ARCH-07-deployment`: add the distribution to the release inventory description.
- Candidate decision: a packaging decision that supersedes the runtime-and-wheel clause of
  `ADR-adaptive-development-and-research`, leaving its approach, current-context and research-material clauses.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Root `AGENTS.md` package table, `packages/devkit-catalog/README.md`, a new package README and `guides/install/`
  name the new distribution.
- `.devkit/architecture.toml` moves the `adaptive_dev` data root.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Owner of the `adaptive-dev` bundle | `devkit-catalog` (content only) | `devkit-adaptive` |
| Python code beside the bundle | None | Package skeleton; commands arrive with `PROP-adaptive-assignment-cli` |
| Bundle name, presets, asset IDs | `adaptive-dev`, `core`, `agents`, `import` | Unchanged |
| Requires `devkit-spec` | No | No |
