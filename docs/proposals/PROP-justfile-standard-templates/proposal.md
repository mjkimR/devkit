---
id: PROP-justfile-standard-templates
title: Standard Justfile Scaffolding and Verification Recipes
summary: Provides standard justfile templates and verification recipes (test, fix, verify) for consumer repositories adopting devkit.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: harness/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high
dev_effort: medium                    # low | medium | high
boundaries:
  owns:
    - packages/devkit-starter/src/devkit_starter/
    - packages/devkit-cli/src/devkit_cli/
    - docs/capabilities/harness/
    - docs/usecases/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-justfile-standard-templates] Standard Justfile Scaffolding and Verification Recipes

## 1. Background & Hypothesis

devkit provides rigorous rule validation, pre-commit gates, and spec workflows. However, human developers and AI coding agents interact with repositories primarily through task runners like `just`.

In consumer repositories adopting devkit, there is significant friction when setting up the command interface:
1. `justfile` recipes are authored inconsistently across repositories (`just check`, `just test`, `just lint`, `just all`).
2. Agents struggle when guessing the verification command or rely on slow trial-and-error discovery.
3. Pre-commit gates (`[gates.settings.verify-commands]`) require a fast, unified verification recipe, but bootstrapping this recipe is currently an undocumented manual chore.

**Hypothesis**:
devkit should offer a standard `devkit scaffold justfile` command (and brownfield adoption playbook support) that generates a clean, concise, standard English `justfile` containing the 3 canonical recipes:
- `test`: Run project unit and integration tests.
- `fix`: Run code formatters and `devkit rules fix`.
- `verify`: Run code format check, linting, tests, and `devkit rules check`.

## 2. Technical Spike Questions

- **Q1 — Recipe Customization vs Standardization**: How to support diverse project tech stacks without bloated recipes?
  - *Approach*: Scaffold produces clean, unbloated boilerplate with detected commands based on project files (e.g. `uv run pytest`, `cargo test`, `npm test`, or Godot runner) and appends `devkit rules check`.
- **Q2 — Safe Non-Destructive Scaffolding**: How to handle existing justfiles?
  - *Approach*: If `justfile` already exists, `devkit scaffold justfile` will not overwrite. It can output a recommended diff, append missing recipes, or write to a target file like `justfile.template`.
- **Q3 — Language of Comments**:
  - *Approach*: Follow workbench/devkit standard: English for all code and command declarations. Comments are concise and imperative.

## 3. Proposed Design & Impact

1. **CLI Scaffolding Command**:
   - `devkit scaffold justfile [--runtime <python|node|rust|go|godot>]`
   - Automatically detects runtime if flag omitted.
2. **Canonical Recipe Schema**:
   ```just
   # Run all automated tests
   test:
       {{ test_command }}

   # Format code and apply deterministic rule repairs
   fix:
       {{ format_command }}
       uv run devkit rules fix

   # Run complete verification (lint, format check, tests, rules)
   verify:
       {{ lint_command }}
       @just test
       uv run devkit rules check
   ```
3. **Integration with Pre-Commit Gates**:
   - `[gates.settings.verify-commands]` defaults to `["just verify"]` when a justfile is present.

## 4. Lifecycle & Retirement Criteria

- Acceptance: Consensus through SDD proposal review.
- Testing: Golden template generation tests for each supported tech stack.
