---
id: PROP-multi-runtime-project-harness-target
title: Target Living Spec Structure for PROP-multi-runtime-project-harness
status: draft
proposal: PROP-multi-runtime-project-harness
created_at: 2026-11-04
targets:
  - file: docs/architecture/ARCH-05-2-components.md
---

# [Blueprint] PROP-multi-runtime-project-harness: Target Living Spec Structure for Multi-Runtime Project Harness and Verification Adapters

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-multi-runtime-project-harness is accepted.

---

## 1. System Capabilities Plan (docs/capabilities/)

- **CAP-HARN-multi-runtime-adapters (proposed)**:
  - Defines the runtime adapter specification (`detect`, `toolchain_check`, `recommended_verify_commands`).
  - Catalogs built-in adapters: Python, Node.js, Go, Rust, Godot.
- **CAP-GATE-external-rule-runner (proposed)**:
  - Specifies JSON stdio protocol for non-Python custom rule linters.
  - Defines error handling, timeout boundaries, and diagnostic reporting.

---

## 2. Use Cases Plan (docs/usecases/)

- **UC-configure-multi-runtime-harness (proposed)**:
  - **Goal**: Seamlessly bootstrap and verify devkit gates in non-Python or polyglot repositories.
  - **Scenario 1**: Auto-detecting Node/TypeScript workspace and generating ESLint/Vitest verification gates.
  - **Scenario 2**: Auto-detecting Godot project and wiring headless test runner and gdtoolkit checks.
  - **Scenario 3**: Executing external linter rule and capturing stdout JSON findings.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-2-components`:
  - Adds runtime adapter module and external rule executor components.
- **Candidate ADR**:
  - PADR-runtime-adapter-boundary: devkit does not package runtimes; it discovers, verifies, and orchestrates them.
  - PADR-external-rule-json-protocol: Stdio JSON schema for external linter plugins.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Expands `.devkit/config.toml` with `[[rules.external]]` and `[harness.runtime]`.

---

## 5. System Before & After Comparison (Before & After)

### As-Is
```
User has a Godot, Node, or Rust project
  ↳ devkit assumes Python environment everywhere
  ↳ Must manually figure out how to wire pre-commit verify commands
  ↳ Cannot write custom project rules in project's primary language
```

### To-Be
```
User runs devkit in Godot/Node/Rust project
  ↳ devkit auto-detects project runtime
  ↳ Suggests and configures native verification gates
  ↳ Supports custom rules written in TypeScript/Go/Rust via JSON stdio protocol
  ↳ devkit doctor validates native toolchain health
```
