---
sources:
  CAP-HOST-lifecycle-observation: ae687191311536ae259168b69a18e389f35997ac
  CAP-INT-mcp-services: ee8088a63e89abb3519c1744c540c41e95352ea2
  CAP-MCP-runtime-registration: ca1255fabbc01ec9870ba8e18410df23ab554d0c
title: Host
---

# Host

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
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
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The host area connects devkit to the agent host you work in (the coding agent's own runtime, such as Codex CLI). It
covers three things (`CAP-HOST-lifecycle-observation`):

- **Native hooks**: a bundle can register a handler for a host lifecycle event (session start, prompt submit, tool
  use, stop), and devkit dispatches the event to an installed Python handler.
- **Project MCP registration**: when the optional MCP runtime is installed, `devkit sync` keeps the project's local
  MCP entry for devkit in step. The rules for that live in the [MCP](mcp.md) area (`CAP-MCP-runtime-registration`).
- **Read-only diagnostics**: `devkit host status` shows what is installed and what the observer last saw.

Hooks and registrations are deployed by `devkit sync` like any other bundle asset; see [Concepts](../concepts.md) for
bundles, sync and the receipt. The host module ships with `devkit-dist`, so hooks work without `devkit-agt`.

## What hooks are, and what they are not

A hook is advisory. Its handler can add context to the agent's turn; it cannot approve anything, grant permission or
enforce a security boundary. When input, configuration or the handler fails, the hook prints a warning on stderr,
returns an empty native response and exits `0`, so a broken hook never stops your session. Domain services still
check readiness and authorization themselves when they change something.

Only Codex CLI command hooks on POSIX are supported in this release. A configured hook is also not proof that the host
trusts or runs it: confirm that in a real Codex session.

## Add a hook to a bundle

A bundle declares one `hook` asset per handler registration, pointing at a small TOML file:

```toml
[[assets]]
id = "trace-tools"
kind = "hook"
source = "hooks/trace-tools.toml"
```

```toml
host = "codex"
event = "PreToolUse"
handler = "observe"
matcher = "^Bash$"
timeout = 10
```

`host`, `event` and `handler` are required. The supported events are `SessionStart`, `UserPromptSubmit`,
`PreToolUse`, `PostToolUse`, `Stop` and `SessionEnd`; `SessionEnd` needs an explicit timeout of at most 3 seconds, and
`UserPromptSubmit` and `Stop` take no matcher. The matcher is a regular expression the host interprets as written.
Unknown fields are errors.

A hook is registered only when both its bundle and the Codex agent are selected. You can override it like any other
asset, and sync validates the effective definition before it touches host configuration.

## Let sync manage host configuration

`devkit bundle plan` lists the generated registrations under `host_hooks`, and `devkit sync --dry-run` or
`--check` include them. Sync then edits `.codex/hooks.json` narrowly:

- it changes only the matcher groups the receipt records as devkit's, and preserves everything else (foreign events,
  foreign groups, their order, top-level metadata);
- removing a hook, deselecting its bundle or dropping Codex removes only that exact group;
- an owned group that is missing, edited or duplicated is `HOST_HOOK_CONFLICT`, raised before anything is written.

To resolve a conflict, review your local edit, restore the recorded group from `.devkit/installation.json`, then run
sync again. There is deliberately no force or adopt mode. `sync --locked` never edits an existing host file; a
changed selection or definition there is `RECEIPT_STALE`. Avoid editing host configuration by hand while sync runs.

Credentials, project and hook trust, user settings and permission settings always stay with the host.

## Make sure the hook can run

The generated command is `devkit host hook --host codex --asset <bundle:id>`. The Codex process needs the installed
`devkit` on its PATH; for a project-local installation, launch Codex with the project's `.venv/bin` first on PATH.
The hook installs nothing and makes no network call. It finds the devkit project from the event's working directory,
verifies the event against the receipt, and invokes exactly one handler. An interrupted sync prevents dispatch.

## Write a handler

A service package registers a callable under the `devkit.host.handlers` entry-point group:

```toml
[project.entry-points."devkit.host.handlers"]
my-context = "my_package.host:context"
```

```python
from devkit_dist.features.host import HookEvent, HookResponse

def context(event: HookEvent) -> HookResponse:
    return HookResponse(additional_context="Read the repository's delivery contract.")
```

The handler receives the host, the native event name, the project root, the qualified asset and the native payload.
It returns an empty response, or up to 4096 characters of context for `SessionStart`, `UserPromptSubmit`,
`PreToolUse` or `PostToolUse`. Keep handlers quiet: printed output is discarded, and they must not log sensitive
event content, spawn background work or treat event input as approval. Missing, duplicate or failing handlers are
reported as `HOST_HOOK_DISPATCH_FAILED`. Changing an override to another handler needs a sync before it dispatches.

## Inspect what is installed

The built-in `observe` handler records only the host, asset, event and UTC time of the latest event, under
`.devkit/transient/host/`. It stores no prompts, commands or session content, and it is not an audit log.

```sh
devkit host status --format json
```

reports each registration, whether its source and handler are valid, and the last observation. Trust and execution
permission are always `unknown`, and `runtime_on_path` describes only the inspecting process. `devkit status` also
lists hook installation problems. Neither command proves the host has enabled a hook.

Unlike other commands, `devkit host hook` writes the host's native response on stdout, without result sentinels;
`devkit host status` follows the normal agent output contract.

## Approvals are separate

Business approvals, such as integrating a task, are not hooks and are not host prompts. Under the `ask` policy the
Host carries your conversational decision to the integration CLI (`CAP-INT-mcp-services`, see
[Integration](integration.md)). Host trust, tool and sandbox prompts remain independent of that decision, and a hook
never stands in for either.

## Sources

- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/host/CAP-HOST-lifecycle-observation.md):
  hook assets, shared configuration ownership, dispatch, observer and status.
- [Host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/host.md): commands and
  codes, including MCP services.
- Related: [MCP](mcp.md) (`CAP-MCP-runtime-registration`), [Integration](integration.md).
