---
id: PROP-multi-runtime-project-harness
title: Multi-Runtime Project Harness and Verification Adapters
summary: Extends devkit verification gates, toolchains, and environment detection to seamlessly support Node, Go, Rust, Godot, and hybrid projects.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: harness/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high
dev_effort: high                      # low | medium | high
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/src/devkit_agt/features/gate/
    - packages/devkit-cli/src/devkit_cli/
    - docs/capabilities/harness/
    - docs/capabilities/gate/
    - docs/usecases/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-multi-runtime-project-harness] Multi-Runtime Project Harness and Verification Adapters

## 1. Background & Hypothesis

devkit was initially designed and implemented in Python, leveraging `uv` for dependency isolation and CLI execution. However, software projects adopting devkit span diverse runtime environments:
- Game engines: Godot (GDScript, C#)
- Web/Backend: Node.js/TypeScript, Go, Rust
- Polyglot monorepos: Hybrid Python + TypeScript or Go + Rust services

Currently, when devkit is used in a non-Python repository, significant friction occurs:
1. **Toolchain Discovery & Doctor**: devkit has no built-in knowledge of non-Python toolchains (e.g., verifying whether Node, pnpm, Go, Cargo, or Godot headless binary are installed).
2. **Verification Gates**: The `verify-commands` pre-commit gate requires manual hardcoding of commands in `.devkit/config.toml`, without runtime-aware templates or environment health checks.
3. **Custom Rule Plugins**: Rule extensions are limited to Python modules in `.devkit/rules`. Non-Python teams cannot write custom domain linters in TypeScript, Go, or shell scripts without wrapping them in Python harnesses.

**Hypothesis**:
devkit should define an extensible **Runtime Adapter** interface that detects project runtime(s) (Node, Go, Rust, Godot, Python, Generic), wires environment verification commands, and supports external JSON-based rule execution. This makes devkit a first-class companion for polyglot software engineering while keeping the core devkit CLI lightweight and consistent.

## 2. Technical Spike Questions

- **Q1 — Scope of Runtime Management**: Should devkit install non-Python language toolchains (e.g. download Node or Cargo)?
  - *Decision*: **No**. Installing compilers and runtimes belongs to Host/OS package managers or project bootstrap scripts (e.g. `setup.sh`). devkit's role is detection, diagnostic reporting (`devkit doctor`), and orchestration.
- **Q2 — Extensible Rule IPC Schema**: How should non-Python custom rules communicate with `devkit rules check`?
  - *Approach*: Define a lightweight JSON-over-stdio protocol:
    ```json
    // Input to rule executable (stdin):
    {"files": ["src/main.ts"], "workspace_root": "/path/to/repo"}

    // Output from rule executable (stdout):
    [{"rule_id": "RULE-custom-ts", "file": "src/main.ts", "line": 12, "severity": "error", "message": "..."}]
    ```
- **Q3 — Hybrid/Multi-Runtime Repositories**: How to handle monorepos with multiple languages?
  - *Approach*: Composite adapter pattern. `detect()` can identify multiple runtimes in separate subdirectories or combined (e.g. Rust backend + TypeScript frontend).

## 3. Proposed Design & Impact

1. **Runtime Adapter Architecture**:
   - `RuntimeAdapter` ABC:
     - `detect(workspace: Path) -> bool`
     - `name: str`
     - `recommended_verify_commands() -> list[str]`
     - `check_toolchain() -> list[Diagnostic]`
   - Built-in adapters: `PythonAdapter` (`uv`, `ruff`, `pytest`), `NodeAdapter` (`npm`/`pnpm`/`yarn`, `eslint`, `vitest`), `RustAdapter` (`cargo clippy`, `cargo test`), `GoAdapter` (`go vet`, `go test`), `GodotAdapter` (`godot`, `gdlint`, `gdformat`).
2. **External Rule Plugin Provider**:
   - Allows configuring command-line linters in `.devkit/config.toml`:
     ```toml
     [[rules.external]]
     id = "RULE-eslint"
     command = ["npx", "eslint", "--format=json"]
     extensions = [".ts", ".tsx", ".js"]
     adapter = "eslint-json"
     ```
3. **Enhanced Diagnostics**:
   - `devkit doctor` reports toolchain status across all detected project runtimes.

## 4. Lifecycle & Retirement Criteria

- Acceptance: SDD proposal review and alignment with workbench multi-repo ecosystem.
- Success Metrics: Seamless execution of `devkit rules check` and `just verify` across Godot, Node, and Go projects without Python-specific boilerplate.
