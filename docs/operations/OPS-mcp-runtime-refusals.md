---
id: OPS-mcp-runtime-refusals
title: "MCP runtime refusal and registration diagnosis and routing"
status: active
summary: "Routes devkit MCP tools that partly refuse, or a project registration that is not active, to existing owners by comparing the tool-call result, sync or setup notices and the mcp status runtime facts; host connection, trust and permissions stay outside devkit evidence."
related_capabilities:
  - CAP-MCP-runtime-registration
related_operations:
  - OPS-distribution-sync
---

# [OPS-mcp-runtime-refusals] MCP runtime refusal and registration diagnosis and routing

Some devkit MCP tools run while others refuse, or the host shows no devkit tools at all. Three surfaces each see
part of the cause. The tool-call result comes from the serving process, sync and setup notices come from the
registration plan, and the `mcp status` runtime field describes the runtime installed now. A serving process can
refuse calls while `mcp status` reports `runtime` `available`, so one surface alone misroutes the case. This entry
routes symptoms that only a comparison of these surfaces separates.

## Routing

A refused tool call returns `{"error": {...}}` with the advisory `code` as structured content and marks the result as
an error. `uv run devkit mcp status --format json` reports `package`, `runtime` (`absent`, `unknown`, `unavailable` or
`available`), per-host `project` `state` and `collisions`, and refused plans under `errors`; text prints
`[MCP: action=status package=<package> runtime=<runtime>]` and one `[MCP_HOST: ...]` line per host. `devkit sync`, `devkit sync
--registrations-only` and `devkit mcp setup` report registration advisories under `notices`.

| Symptom or state | Discriminating evidence | Next useful owner |
| --- | --- | --- |
| Read-only tools run; other tools refuse after the installed devkit code changed | Calls other than `read_only` return `MCP_RUNTIME_STALE` naming stale modules; `mcp status` reports `runtime` `available` and sync shows no MCP notice, because the field describes the installed runtime, not the code the serving process loaded | [`host.md` MCP row for `MCP_RUNTIME_STALE`](../development/reference/host.md#mcp-services); `CAP-MCP-runtime-registration` Runtime contract |
| Read-only tools run; other tools refuse in a cloud environment | Calls other than `read_only` return `MCP_INTERACTIVE_UNAVAILABLE`; `mcp status` reports `runtime` `available`, while `mcp status --descriptor` prints `profile=read-only`, the profile the owning workspace's environment now selects | [`host.md` MCP row for `MCP_INTERACTIVE_UNAVAILABLE`](../development/reference/host.md#mcp-services); `CAP-MCP-runtime-registration` Runtime contract |
| Only read-only tools are listed | The host lists no tool other than `read_only` ones, and no call returns an error; `mcp status --descriptor` prints `profile=read-only`, the registration profile of a cloud environment | `CAP-MCP-runtime-registration` Runtime contract (cloud registration profile) |
| Every tool refuses, read-only ones included | Calls return `MCP_WORKSPACE_UNAVAILABLE`, which unlike `MCP_RUNTIME_STALE` and `MCP_INTERACTIVE_UNAVAILABLE` also reaches read-only tools; `mcp status` reports the installed runtime and not the serving process's workspace identity | [`host.md` MCP row for `MCP_WORKSPACE_UNAVAILABLE`](../development/reference/host.md#mcp-services); `CAP-MCP-runtime-registration` Runtime contract |
| A tool fails while the runtime looks available | A call returns `HOST_MCP_FAILED`; `mcp status` reports `runtime` `available` | [`host.md` MCP row for `HOST_MCP_FAILED`](../development/reference/host.md#mcp-services) |
| No devkit tools; no verified runtime | Sync or setup reports `MCP_RUNTIME_UNAVAILABLE`, and `mcp status` reports `runtime` `unavailable` | [`host.md` MCP row for `MCP_RUNTIME_UNAVAILABLE`](../development/reference/host.md#mcp-services) |
| No devkit tools; no runtime package | `mcp status` reports `package` `absent` and `runtime` `absent`; sync reports no MCP notice | `CAP-MCP-runtime-registration` Registration contract (optional provider discovery) |
| No devkit tools; registration plan refused | `mcp status` reports `runtime` `unknown` and lists `MCP_REGISTRATION_CONFLICT` or `MCP_REGISTRATION_INTERRUPTED` under `errors`; a sync or setup that cannot recover or reconcile the registration refuses with `MCP_REGISTRATION_CONFLICT` | `host.md` MCP row for that code ([MCP services](../development/reference/host.md#mcp-services)) |
| No devkit tools after locked sync | Locked sync reports `MCP_REGISTRATION_PENDING`; `mcp status` shows the host with `desired=yes recorded=no state=absent` | `CAP-MCP-runtime-registration` Registration contract (withheld registration writes); `CAP-DIST-sync-and-transactions` Readiness Gate |
| No devkit tools for one host | Sync or setup warns `MCP_REGISTRATION_SHADOWED`, `MCP_HOST_UNSUPPORTED` or `MCP_REGISTRATION_UNAVAILABLE`; `mcp status` shows that host with nonempty `collisions`, `state=unsupported` or no owned entry respectively | `host.md` MCP row for that code ([MCP services](../development/reference/host.md#mcp-services)) |
| No devkit tools, registration facts clean | `mcp status` reports `runtime` `available`, each selected host `state=owned` with `collisions=none`, and no notice or error; `effective`, `connection`, `trust` and `permissions` are `unknown` | The agent host application, which owns connection, effective selection, trust and permissions (`CAP-MCP-runtime-registration` Registration contract; `CAP-HOST-lifecycle-observation` §6) |

`MCP_REGISTRATION_INTERRUPTED` names the registration journal `.devkit/transient/mcp/journal.json`, not the sync
journal that `OPS-distribution-sync` routes. General `devkit status` carries no MCP registration diagnosis by design
(`CAP-MCP-runtime-registration` Registration contract, general status boundary), so read `mcp status` instead.

## Normal-state observation

After the owner's action, `mcp status` reports `runtime` `available` and empty `errors`, and each selected host shows
`state=owned desired=yes recorded=yes collisions=none`. Sync reports no MCP notice, and a call other than
`read_only` returns a result without `error`. `CAP-MCP-runtime-registration` owns these facts, and
`CAP-DIST-sync-and-transactions` Readiness Gate counts planned registration writes toward checkout readiness.
Registration facts do not prove connectivity (`CAP-HOST-lifecycle-observation` §6).

## Authority boundary

This entry classifies evidence and owns no recovery. `CAP-MCP-runtime-registration` owns the runtime refusals,
registration profiles, registration reconciliation and the `mcp status` facts. `ADR-mcp-runtime-and-shared-artifacts`
owns the rationale for the optional runtime, guarded registration and the general status boundary.
`CAP-DIST-sync-and-transactions` owns locked sync and readiness, and `OPS-distribution-sync` routes sync journal
symptoms. The code rows under [MCP services](../development/reference/host.md#mcp-services) map each code to its
recovery, and the actual advisory retains its fix. The agent host application owns connection, effective
selection, trust and permissions.

The evidence cannot establish which runtime a host process launched, whether a serving process has reloaded, or
whether the host connected to or enabled the registered server.

## Maintenance and next action

Review the routing when the Runtime or Registration contract of `CAP-MCP-runtime-registration` changes, when the
`mcp status` fields `package`, `runtime`, `project` or `collisions` change, or when the call order in
[server.py](../../packages/devkit-mcp/src/devkit_mcp/features/runtime/mcp/server.py) changes which refusals reach
read-only tools. For evidence that matches no row, take the reported code to its row under
[MCP services](../development/reference/host.md#mcp-services) and its actual advisory.
