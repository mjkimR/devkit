---
sources:
  CAP-COLL-shared-artifacts: d000f00d3b8d672ea0473d3c6f01dafafe3b8f70
  CAP-HOST-lifecycle-observation: bae2e546b3e578a9a4e3f3094cb304851174520b
  CAP-INT-mcp-services: 41636553f0fe6331719d5d0cfaad2965deda6eb1
  CAP-MCP-runtime-registration: 6dd9d3d5cf7a915a18d80f1adae375cf73823c1a
  UC-drive-development-to-integration: bc214c7d80b401cf5b2ba5027c9144673d104393
title: MCP
---

# MCP

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

`devkit-mcp` is an optional package that serves devkit's tools to an agent host over the Model Context Protocol
(stdio), and keeps the project's local MCP registration in step (`CAP-MCP-runtime-registration`). You do not need it to
use devkit: every lifecycle operation, including integration, runs through the CLI. In this release its main use is
the shared-artifact tools (see [Collaboration](collaboration.md)).

For the role of the Host and of approvals in the workflow, see [Concepts](../concepts.md) and the journey
[Drive development to integration](../journeys/drive-development-to-integration.md).

## Install and register

Install `devkit-mcp` into a retained runtime: the base checkout's environment or a tool installation, never a task
worktree's `.venv` or an editable linked-worktree source. Then let sync register it, or do it explicitly:

| You want to | Run |
| --- | --- |
| Check which runtime would be used | `devkit mcp status --descriptor --format json` |
| Register the project entry | `devkit mcp setup [--host codex\|claude\|antigravity]` |
| See desired, recorded and project registration | `devkit mcp status --format json` |
| Remove devkit's own entry | `devkit mcp remove` |

With the runtime installed, ordinary `devkit sync` reconciles the devkit entry of each selected agent's project file:
`.codex/config.toml` for Codex, `.mcp.json` for Claude Code, and `.agents/mcp_config.json` for Antigravity. Set
`[mcp] register = false` to opt out. New task worktrees get their entry through `devkit sync --registrations-only`
right after locked asset restoration (see [Worktree](worktree.md)). The step-by-step host setup is the guide
[MCP setup](https://github.com/mjkimR/devkit/blob/v0.1.4/guides/install/mcp.md).

## What registration will and will not touch

Registration is careful about files that are not its own:

- It writes only to untracked files, and only to entries recorded as devkit's in the ignored ledger
  `.devkit/transient/mcp/registrations.json`. Tracked files and visible foreign files stay unchanged.
- An absent destination needs an existing ignore rule, or devkit adds one narrow clone-local exclusion after checking
  every linked worktree for files it would hide.
- A missing, edited or duplicated owned entry is a conflict (`MCP_REGISTRATION_CONFLICT`); an identical entry devkit
  does not own is never adopted.
- Host trust, permissions and global settings stay with the host. Same-name declarations in user or managed settings
  are reported as collisions, read-only.
- An interrupted change is recovered before the next one. `--dry-run` and `--check` plan without writing; locked sync
  validates without changing host files.

Registered does not mean connected: status reports the effective connection, form support, trust and permission as
unknown.

## How the server protects you

`devkit mcp serve` binds every call to three locations: the retained runtime, the executor checkout and the owning
configuration workspace (the checkout whose configuration applies). Tool input cannot change the workspace.

- **Execution classes.** Each tool declares itself `read_only`, `bounded_write`, `preflight`, `interactive` or
  `approved_resume`; an undeclared tool counts as `interactive`. A native confirmation counts only when you both
  accept and approve; a decline, cancel, disconnect or a host without form support grants nothing.
- **Cloud environments** expose only read-only tools and refuse forms and writes. Guards repeat after waits and
  before effects.
- **Stale code.** The server records a hash of the devkit code it loaded. If that code changed on disk, every
  non-read-only call is refused with `MCP_RUNTIME_STALE`: restart or reconnect the service. Read-only tools keep
  working.
- **Lost workspace.** A missing or malformed owning workspace fails closed (`MCP_WORKSPACE_UNAVAILABLE`).

## Business approval stays in the conversation

Lifecycle mutations (integration, cleanup) are not MCP tools. The Host checks the work, shows you the exact report,
target and effects, takes your decision under `ask`, and then calls the CLI (`CAP-INT-mcp-services`, see
[Integration](integration.md)). Host trust, tool and sandbox prompts are a separate matter from that decision.

When form text is shown, its language follows the owning workspace's preference; that never changes a guard or a
registration.

## Shared artifact tools

The shared-artifact service offers `shared_put` (a bounded write that needs no approval form) and the read-only
`shared_get` and `shared_list`. They follow the same identity, retention and adapter rules as the
`devkit shared` CLI (`CAP-COLL-shared-artifacts`). In a cloud environment the write tool is neither listed nor
accepted.

## Common codes

| Code | What to do |
| --- | --- |
| `MCP_RUNTIME_UNAVAILABLE` | Install or select a retained runtime with matching service packages, then reconcile. |
| `MCP_RUNTIME_STALE` | Restart or reconnect the service, then call again. |
| `MCP_REGISTRATION_CONFLICT` | Inspect edited or unowned entries; restore exact ownership before syncing. |
| `MCP_REGISTRATION_UNAVAILABLE` | Leave host files alone; use host setup or the CLI route. |
| `MCP_INTERACTIVE_UNAVAILABLE` | Use a local interactive Host or the CLI route. |

## Sources

- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/mcp/CAP-MCP-runtime-registration.md):
  runtime contract, registration, Host workflow and shared artifact services.
- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/host/CAP-HOST-lifecycle-observation.md)
  (project MCP registration boundary) and the
  [host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/host.md#mcp-services).
- Related: [Host](host.md), [Collaboration](collaboration.md), [Integration](integration.md).
