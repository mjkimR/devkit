---
id: SPEC-mcp-tool-execution-classes
title: Two MCP tool execution classes
summary: Narrows McpTool.execution to read_only and bounded_write, derives the read-only hint from it and drops the separate read_only field.
status: in-progress
created: 2026-11-11
related_capabilities:
  - CAP-MCP-runtime-registration
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-mcp-tool-execution-classes] Two MCP tool execution classes

## 1. Problem Statement & Motivation

`devkit_core.base.mcp.McpTool.execution` declares five classes (`read_only`, `preflight`, `interactive` as the
default, `approved_resume`, `bounded_write`), but the runtime in `devkit_mcp` distinguishes only `read_only` from the
rest. `preflight`, `interactive` and `approved_resume` have no producer: they are leftovers of the removed MCP
approval paths. The separate boolean `read_only` field duplicates the classification and can disagree with it, so a
tool could advertise a read-only annotation while the runtime guards it as a write, or the reverse. A tool author
reading the contract sees choices that change nothing. `CAP-MCP-runtime-registration` documents the five classes.

## 2. User Stories

- **US-1**: As an MCP tool author, I want exactly the execution classes the runtime honors, so that a declaration
  says what the runtime does.
- **US-2**: As an MCP client, I want the read-only annotation hint to follow the execution class, so that the
  advertised hint never contradicts how the call is guarded.

## 3. Non-Goals

1. **Scope Excluded**: no change to the guards themselves (loaded-code staleness, execution environment, cloud
   profile filtering), to `destructive` or `open_world`, or to the shared artifact tools' behavior.
2. **Scope Excluded**: no compatibility shim for the removed classes or the `read_only=` keyword; the repository has
   no external producer of `McpTool`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Two execution classes with a write default
- **Given** `devkit_core.base.mcp.McpTool`
- **When** its `execution` field type and default are inspected
- **Then** the type admits exactly `read_only` and `bounded_write`, and a tool constructed without `execution` has
  `execution == "bounded_write"`

### [AC-02] The separate read_only field is gone
- **Given** `McpTool`
- **When** a tool is constructed with the keyword `read_only=True`
- **Then** construction raises `TypeError`, and `McpTool` has no `read_only` field

### [AC-03] Removed classes fail closed at discovery
- **Given** an installed service that declares a tool with `execution` set to `preflight`, `interactive` or
  `approved_resume`
- **When** `load_tools` loads the services
- **Then** it raises `HostMcpError` naming the service ("cannot load"), as for any unknown classification

### [AC-04] The read-only hint follows the execution class
- **Given** a server built from a `read_only` tool and a `bounded_write` tool
- **When** a client lists the tools
- **Then** the `read_only` tool's annotations carry `readOnlyHint` true and the `bounded_write` tool's carry
  `readOnlyHint` false

### [AC-05] Guarding and the shared tools are unchanged
- **Given** the shared artifact tools of `devkit_dist.features.shared.mcp`
- **When** they are declared and served
- **Then** `shared_put` is `bounded_write` and `shared_get`/`shared_list` are `read_only`; the existing stale-runtime,
  cloud-profile and owning-workspace tests pass unchanged except for replacing the removed `preflight` fixture class
  with `bounded_write`

### [AC-06] The capability states the two classes
- **Given** `CAP-MCP-runtime-registration`
- **When** a reader looks up the execution classification
- **Then** it names only `read_only` and `bounded_write`, the `bounded_write` default and the derived read-only hint,
  and no longer mentions `preflight`, `interactive` or `approved_resume` as classes

## 5. Assumptions

1. A tool that omits `execution` is guarded as a write (`bounded_write`), the same guarding the former
   `interactive` default received, so failing closed is preserved.
2. Removed classes need no dedicated error code: discovery already refuses any classification outside the declared
   type, so the narrowed type alone rejects them.

## 6. Source feedback

- Finding SM-2 of the review-refactor code pass (`docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`).
