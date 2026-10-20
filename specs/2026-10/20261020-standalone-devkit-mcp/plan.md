---
id: PLAN-standalone-devkit-mcp
spec: SPEC-standalone-devkit-mcp
---

# Technical Plan: `SPEC-standalone-devkit-mcp`

## 1. Constitution & Invariant Review

`ADR-independent-mcp-runtime-with-project-registration-and-environment-guards` authorizes the narrow MCP
ownership changes to `ADR-dist-module-split`, `ADR-dist-command-composition` and host project settings.
The current core resolver is integrated and supplies `read_effective_config(root).values` and
`resolve_execution_environment(root).environment/source`. Existing service factories accept an executor root;
retain that interface and carry a process-local invocation context through core contracts to bind the separate
configuration workspace without importing the SDK into domain packages.

## 2. Architecture Overview & Impact

- `devkit.core.mcp`: dependency-free tool/confirmation contracts and explicit execution context guard.
- `devkit_mcp`: command plugin, service discovery, SDK transport, retained runtime descriptor provider.
- `devkit.host`: narrow registration provider discovery and exact project-entry reconciliation.
- Distribution sync: ordinary reconciliation and read-only planning/locked verification, separate from receipts.
- Integration and handoff: guards before form, after reply/locks and at mutation boundaries.
- Package, test-selector, release and installation matrices include the optional wheel.

The new wheel requires the same-version dist wheel, `mcp>=1.30,<2` and directly imported `jsonschema`.
No compatibility reader, command alias or global setup writer is retained.

## 3. Component & Interface Design

The provider returns a launch descriptor with executable, executor root, configuration workspace and profile.
Only retained base/tool-installed imports with the same installed domain providers qualify. Explicit setup may
choose a verified executable. Configuration identity binds resolved checkout and common Git directory; tool
arguments cannot override it. A context guard resolves the local environment on every protected boundary.
Execution classifications are read_only, preflight, interactive and approved_resume; cloud profiles list only
read_only services. Transport and domain layers both enforce restrictions.

Registration discovers providers without a hard runtime import. Codex TOML and Claude JSON entries preserve
foreign configuration. Plan all destinations before any write; reject duplicate keys, unsafe paths, tracked or
visible foreign destinations and edited/unowned entries. Lock common Git state before the checkout project lock.
An ignored local ledger stores exact entries and owned exclusion lines. A recoverable journal records previous
and desired file bytes/modes; recovery refuses foreign edits. Recheck Git eligibility and file identity before
writes. Existing user/ancestor/managed collisions remain untouched and effective host behavior stays unknown.

## 4. Failure Modes

Missing provider removes only exact owned project entries. Provider load errors fail closed. Missing retained
runtime leaves new registration absent with a deterministic advisory. Explicit opt-out uses the same ownership
checks. Exclusions stay local after removal with manual cleanup guidance. Cloud transition stops the next mutation
and preserves completed effects as a partial result. Only a same-call, final captured cleanup context can survive
intentional deletion of its exact configuration checkout; later calls and resume fail closed.

## 5. Verification & Test Plan

AC-01: isolated built-wheel combinations, module/path overlap checks, dist-only and command discovery.
AC-02: existing transport tests moved to the runtime wheel plus SDK capability/protocol cases.
AC-03: isolated Git repositories, linked worktrees, ignored/tracked/foreign files, byte/mode preservation,
provider failures, collisions, journal recovery and dry-run/locked sync tests.
AC-04/05: independent workspace overlays, cloud transitions at form/lock/mutation boundaries, deleted workspace,
retained executable/import source and process-local authority tests.
AC-06: record available host version evidence; actual native UI remains explicitly unverified if unavailable.
Run relevant lint/types, `just test-affected`, dist-only, wheel smoke, release validation without publication,
and cumulative governance. Medium review uses an independent code reviewer and separate reconcile reviewer.

The Host expanded the write boundary narrowly to worktree lifecycle start/prepare and related tests. A trusted
before-step callback rechecks environment before creation, local copy, setup and sync; handoff records partial
recovery when a guard refuses after creation. This closes the setup-to-sync transition without adding MCP imports
to worktree lifecycle or changing ordinary CLI authorization.


## Review decisions

Recovery revalidates Git eligibility before mutation and each host write. Installed clone-local exclusions are
retained across rollback, with a revised durable rollback target preserving their ledger ownership. Runtime probing
includes advisory and every imported dependency module to reject editable sources under removable worktrees.

A fresh checkout has no existing registration to validate. Locked sync restores assets without writing host files;
a separate dist-owned `sync --registrations-only` invocation initializes optional registrations afterward. This
keeps worktree independent of runtime/host imports and uses the same selected interpreter, local opt-out and cloud
profile. The trusted before-step callback guards that additional mutation boundary. Existing changed registrations
still refuse locked sync. This narrow lifecycle expansion was authorized by the Host.

Entrypoint derivation was reviewed: broad package, tooling and documentation candidates are rejected as unrelated
joins. Existing focused host, runtime/core binding, integration, handoff and lifecycle paths remain the useful
capability entrypoints; no package-wide entrypoints are added automatically.
