---
sources:
  CAP-COLL-shared-artifacts: 83dfa43f60f67f8a6eab85414d90c95ba27e2982
  CAP-HOST-lifecycle-observation: ae687191311536ae259168b69a18e389f35997ac
  CAP-INT-mcp-services: ee8088a63e89abb3519c1744c540c41e95352ea2
  CAP-MCP-runtime-registration: ca1255fabbc01ec9870ba8e18410df23ab554d0c
  UC-drive-development-to-integration: ede0ca1f9647c2e9e1a520d97818d09fa7bcb5e4
title: MCP
---

# MCP

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
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
| Check which runtime would be used | `devkit mcp status --descriptor [--executable <python>] --format json` |
| Register the project entries | `devkit mcp setup [--executable <python>] [--host codex\|claude\|antigravity ...]` |
| See desired, recorded and project registration | `devkit mcp status --format json` |
| Remove devkit's own entry | `devkit mcp remove` |

With the runtime installed, ordinary `devkit sync` reconciles the devkit entry of each selected agent's project file:
`.codex/config.toml` for Codex, `.mcp.json` for Claude Code, and `.agents/mcp_config.json` for Antigravity. Set
`[mcp] register = false` to opt out. New task worktrees get their entry through `devkit sync --registrations-only`
right after locked asset restoration (see [Worktree](worktree.md)).

`mcp setup` refuses with `MCP_RUNTIME_UNAVAILABLE` before writing anything when no verified runtime exists; after an
ordinary sync the same code is only a warning. `--host` (repeatable) limits registration to the named hosts, and
because setup reconciles the whole project, owned entries of every other host are removed; a later run without
`--host` registers the configured agents again.

`devkit status` does not inspect MCP registration at all. When locked sync holds back a registration write it would
have made, it reports `MCP_REGISTRATION_PENDING` with `uv run devkit sync --registrations-only` as the fix; `devkit mcp
status`, `mcp setup` and the two sync modes are where real registration plans are diagnosed. The step-by-step host setup is the guide
[MCP setup](https://github.com/mjkimR/devkit/blob/v0.1.5/guides/install/mcp.md).

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
- An interrupted change is recovered before the next one (`MCP_REGISTRATION_INTERRUPTED`, fixed by `uv run devkit
  sync`). `--dry-run` and `--check` plan without writing; locked sync validates without changing host files.
- When devkit removes its last owned entry, it reports the narrow exclusions it keeps once
  (`MCP_EXCLUSIONS_RETAINED`); remove them by hand if you no longer want them.

Registered does not mean connected: `devkit mcp status` reports the effective connection, trust and permission as
unknown (in JSON); its text prints one `[MCP: ...]` line and one `[MCP_HOST: ...]` line per host.

## How the server protects you

`devkit mcp serve` binds every call to three locations: the retained runtime, the executor checkout and the owning
configuration workspace (the checkout whose configuration applies). Tool input cannot change the workspace.

- **Execution classes.** Each tool declares itself `read_only`, `bounded_write`, `preflight`, `interactive` or
  `approved_resume`; an undeclared tool counts as `interactive`. The transport asks for no confirmation form and
  grants no business authority: approval belongs to the Host-authorized CLI.
- **Cloud environments** expose only read-only tools and refuse writes. Guards repeat after lock waits and before
  effects.
- **Stale code.** The server records a hash of the devkit code it loaded. If that code changed on disk, every
  non-read-only call is refused with `MCP_RUNTIME_STALE`: restart or reconnect the service. Read-only tools keep
  working.
- **Lost workspace.** A missing or malformed owning workspace fails closed (`MCP_WORKSPACE_UNAVAILABLE`).

## Business approval stays in the conversation

Lifecycle mutations (integration, cleanup) are not MCP tools. The Host checks the work, shows you the exact report,
target and effects, takes your decision under `ask`, and then calls the CLI (`CAP-INT-mcp-services`, see
[Integration](integration.md)). Host trust, tool and sandbox prompts are a separate matter from that decision.

Domain text a tool returns follows the owning workspace's language preference; no tool argument selects a language
or workspace, and the preference never changes a guard or a registration.

## Shared artifact tools

The shared-artifact service offers `shared_put` (a bounded write that needs no approval) and the read-only
`shared_get` and `shared_list`. They follow the same identity, retention and adapter rules as the
`devkit shared` CLI (`CAP-COLL-shared-artifacts`). In a cloud environment the write tool is neither listed nor
accepted.

## Common codes

| Code | What to do |
| --- | --- |
| `MCP_RUNTIME_UNAVAILABLE` | Install or select a retained runtime with matching service packages, then reconcile. |
| `MCP_RUNTIME_STALE` | Restart or reconnect the service, then call again. |
| `MCP_REGISTRATION_CONFLICT` | You decide how to restore the named file (edited, malformed or unowned entries), then sync. |
| `MCP_REGISTRATION_UNAVAILABLE` | The destination is tracked, visible or would hide foreign files; leave it alone and use host setup. |
| `MCP_REGISTRATION_INTERRUPTED`, `MCP_LEDGER_UNIGNORED` | Run `uv run devkit sync`. |
| `MCP_REGISTRATION_PENDING` | Locked sync held back a write; run `uv run devkit sync --registrations-only`. |
| `MCP_HOST_UNSUPPORTED`, `MCP_REGISTRATION_SHADOWED` | A selected host has no adapter, or a user or managed entry of the same name shadows the project one; resolve it with the host's own tools. |
| `MCP_CHECKOUT_REQUIRED` | Point `--workspace-root` at the top level of a Git checkout that holds `.devkit/`. |
| `MCP_INTERACTIVE_UNAVAILABLE` | Use a local interactive Host or the CLI route. |

## Sources

- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/mcp/CAP-MCP-runtime-registration.md):
  runtime contract, registration, Host workflow and shared artifact services.
- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/host/CAP-HOST-lifecycle-observation.md)
  (project MCP registration boundary) and the
  [host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/host.md#mcp-services).
- Related: [Host](host.md), [Collaboration](collaboration.md), [Integration](integration.md).
