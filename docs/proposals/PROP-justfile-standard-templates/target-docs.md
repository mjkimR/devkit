---
id: PROP-justfile-standard-templates-target
title: Target Living Spec Structure for PROP-justfile-standard-templates
status: draft
proposal: PROP-justfile-standard-templates
created_at: 2026-11-04
targets:
  - file: docs/architecture/ARCH-05-3-command-plugins.md
---

# [Blueprint] PROP-justfile-standard-templates: Target Living Spec Structure for Standard Justfile Scaffolding and Verification Recipes

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-justfile-standard-templates is accepted.

---

## 1. System Capabilities Plan (docs/capabilities/)

- **CAP-HARN-standard-justfile-recipes (proposed)**:
  - Defines the 3 standard recipe contracts (`test`, `fix`, `verify`).
  - Specifies runtime detection logic and template variables for `justfile` rendering.
  - Documents integration with devkit pre-commit verify-commands gate.

---

## 2. Use Cases Plan (docs/usecases/)

- **UC-scaffold-standard-justfile (proposed)**:
  - **Goal**: Allow developers to quickly generate an idiomatic `justfile` wired to devkit.
  - **Scenario 1**: User runs `devkit scaffold justfile` in a new repository; creates standard justfile.
  - **Scenario 2**: User runs command when `justfile` already exists; warns and presents non-destructive merge diff.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-3-command-plugins`:
  - Adds scaffolding utilities under CLI command plugins.
- **Candidate ADR**:
  - PADR-canonical-justfile-recipes: Standardization on 3 core recipes (`test`, `fix`, `verify`).

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Updates brownfield adoption playbook to guide initial justfile generation.

---

## 5. System Before & After Comparison (Before & After)

### As-Is
```
User installs devkit
  ↳ Manually writes justfile
  ↳ Recipe names differ across repos (test vs check vs qa)
  ↳ Missing `devkit rules check` or `devkit rules fix`
```

### To-Be
```
User runs devkit scaffold justfile
  ↳ Inspects project root (detects Godot, Python, Rust, etc.)
  ↳ Emits clean standard justfile with test, fix, verify
  ↳ Seamlessly connects to devkit rules and pre-commit gates
```
