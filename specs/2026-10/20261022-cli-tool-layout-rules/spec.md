---
id: SPEC-cli-tool-layout-rules
title: Feature layout and layer rules for cli-tool
summary: Adds RULE-cli-tool-layout and RULE-cli-tool-layers to the cli-tool bundle so agent-facing CLI tools keep the feature layout, confine click to CLI modules and import layers in one direction.
status: planned
created: 2026-10-22
related_capabilities:
  - CAP-CLI-agent-cli-toolkit
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-cli-tool-layout-rules] Feature layout and layer rules for cli-tool

## 1. Problem Statement & Motivation

The `cli-tool` bundle (`CAP-CLI-agent-cli-toolkit`) describes a tool's package layout in its instruction but checks
only the output contract. Agents still invent layouts: a flat package that has to be rebuilt when a second feature
arrives, commands in a `commands.py` the existing rules never read (they select CLI modules by path), and command
functions that call repositories directly. The layout is deterministic enough to check: a fixed set of package-level
modules, `features/<feature>/` with fixed layer names, click confined to CLI modules, and imports that go one way.

## 2. User Stories

- **US-1**: As the user, I want every new CLI tool to have the same feature layout from the first command, so that
  adding a feature never means restructuring the tool.
- **US-2**: As an agent building a tool, I want the layout and the layer directions checked by `devkit rules check`,
  so that a misplaced module or import is reported with its fix while I work.

## 3. Non-Goals

1. **Scope Excluded**: a playbook or command that creates a new tool's skeleton; the instruction remains the starting
   point.
   - **When to Reconsider**: agents repeatedly fix layout violations one by one when creating a tool.
2. **Scope Excluded**: a flat package layout (`src/<package>/usecases.py` beside `cli.py`); it is reported, never
   configurable as an alternative layout.
3. **Scope Excluded**: checking what a command function does beyond its imports (length, logic).
4. **Scope Excluded**: changes to the three existing rules or to `devkit-cli`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Package-level modules outside the fixed set are reported
- **Given** `RULE-cli-tool-layout` with default settings and a tool `src/pkg/` holding `__init__.py`, `cli.py`,
  `errors.py`, `features/scan/cli.py` and `usecases.py`
- **When** the rule runs
- **Then** it reports exactly one `error` violation, at `src/pkg/usecases.py` line 1, and none for the other files

### [AC-02] Feature modules outside the fixed layers are reported
- **Given** `src/pkg/features/scan/` holding `cli.py`, `mcp.py`, `usecases/run.py`, `services.py`, `repositories.py`,
  `models.py`, `errors.py`, `__init__.py` and `helpers.py`, and a module `src/pkg/features/run.py`
- **When** `RULE-cli-tool-layout` runs
- **Then** it reports `src/pkg/features/scan/helpers.py` and `src/pkg/features/run.py`, and nothing else

### [AC-03] click and devkit_cli are confined to CLI modules
- **Given** `RULE-cli-tool-layers` with default settings
- **When** `src/pkg/features/scan/services.py` imports `click` and `src/pkg/features/scan/usecases.py` imports
  `devkit_cli`, while `src/pkg/features/scan/cli.py` and `src/pkg/cli.py` import both
- **Then** it reports the two imports in `services.py` and `usecases.py`, and none in the CLI modules

### [AC-04] Layers import downward only
- **Given** `src/pkg/features/scan/` with `models.py` importing `pkg.features.scan.services`,
  `repositories.py` importing `..models`, `services.py` importing `pkg.features.scan.repositories`, and
  `usecases.py` importing `pkg.features.other.cli`
- **When** `RULE-cli-tool-layers` runs
- **Then** it reports the import in `models.py` and the import in `usecases.py`, and not the other two

### [AC-05] Transports reach only use cases, models and errors
- **Given** `src/pkg/features/scan/cli.py` importing `pkg.features.scan.usecases`, `pkg.features.scan.models`,
  `pkg.features.scan.errors` and `pkg.features.scan.repositories`
- **When** `RULE-cli-tool-layers` runs
- **Then** it reports only the `repositories` import

### [AC-06] The root group loads features lazily
- **Given** `src/pkg/cli.py` importing `pkg.features.scan.cli` at module level and `pkg.errors` at module level, and
  `pkg.features.report.cli` inside a function
- **When** `RULE-cli-tool-layers` runs
- **Then** it reports only the module-level `pkg.features.scan.cli` import

### [AC-07] Shared package modules stay below features
- **Given** `src/pkg/base/contracts.py` importing `pkg.features.scan.models` and `src/pkg/utils/paths.py` importing
  `pkg.base.contracts`
- **When** `RULE-cli-tool-layers` runs
- **Then** it reports only the import in `base/contracts.py`

### [AC-08] The bundle deploys the two rules with the others
- **Given** `devkit-catalog` installed
- **When** a project runs `devkit add cli-tool`
- **Then** the managed rules are the five `RULE-cli-tool-*` rules, and `devkit add cli-tool:guide` deploys none

## 5. Assumptions

- A tool's package is the directory directly below the last `src` segment; every rule reads files under `include`
  (default `**/src/**`) and skips the test patterns.
- Package-level modules: `__init__`, `__main__`, `cli`, `errors`, `base`, `utils` and `features`. Feature modules:
  `__init__`, `cli`, `mcp`, `usecases`, `services`, `repositories`, `models` and `errors`, each a module or a
  directory. `mcp` is allowed so a tool can add an MCP transport without restructuring.
- Layer ranks for imports between features' modules: `models` and `errors` lowest, then `repositories`, `services`,
  `usecases`, and the transports `cli` and `mcp`. A module imports its own rank or lower, across features too;
  transports import only `usecases`, `models` and `errors`. `base` and `utils` import no feature; anything may import
  them. A feature's `__init__.py` is package management and is not checked for direction.
- Imports under `if TYPE_CHECKING:` are not checked (annotations only).
- Both settings lists can be extended per project (`extra_root_modules`, `extra_feature_modules`) for a justified
  exception, as the other bundle rules allow overrides.
