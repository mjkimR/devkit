---
id: OPS-host-hook-dispatch-routing
title: "Host hook dispatch diagnosis and routing"
status: active
summary: "Routes a configured host hook that shows no visible warning and no observation to its existing owner through host status validity, the last observation and the sync journal; host trust, permissions and launch environment stay outside devkit evidence."
related_capabilities:
  - CAP-HOST-lifecycle-observation
related_operations:
  - OPS-distribution-sync
---

# [OPS-host-hook-dispatch-routing] Host hook dispatch diagnosis and routing

A configured host hook can leave no warning in the host session and no observation in devkit. Dispatch failures
are warnings on the hook's stderr while the host operation continues, and whether the host displays that stream is
host-defined (`CAP-HOST-lifecycle-observation` §4). Silence alone therefore cannot tell an invalid registration, an
interrupted sync, a handler that failed during the call and a hook the host never ran apart.

## Routing

`uv run devkit host status --format json` lists one `hooks` entry per receipt-recorded registration, with `state`
(`ok` or `invalid`) and `last_received` (`null`, or the latest observation carrying its UTC `received_at`); text
output prints `[HOST_HOOK: <asset> event=<event> state=<state> observed=yes|no]`. `uv run devkit status --format json`
reports `pending_journal`. Only the built-in `observe` handler writes an observation (`CAP-HOST-lifecycle-observation`
§5), so `last_received` stays `null` for a registration bound to another handler even after a successful dispatch.

| Symptom or state | Discriminating evidence | Next useful owner |
| --- | --- | --- |
| Hook not registered | `host status` lists no entry for the `bundle:id`: the receipt records no `host_hooks` row for it, for example because its bundle or the `codex` agent is not selected | `CAP-HOST-lifecycle-observation` §2 owns which hooks sync registers; `CAP-DIST-sync-and-transactions` Readiness Gate owns whether the checkout is synchronized. |
| Shared host configuration unreadable | `host status` reports `HOST_CONFIG_INVALID` instead of per-hook results | The `HOST_CONFIG_INVALID` row of the [host code table](../development/reference/host.md); `CAP-HOST-lifecycle-observation` §3 owns the configuration rules. |
| Invalid registration | The entry has `state` `invalid`, and `errors` carries `HOST_HOOK_MISSING` (no host file) or `HOST_HOOK_CONFLICT` (owned group missing, edited or duplicated in `.codex/hooks.json`) | That code's row of the [host code table](../development/reference/host.md); `CAP-HOST-lifecycle-observation` §3 owns ownership and conflict rules. |
| Invalid definition or handler installation | The entry has `state` `invalid`, and `errors` carries `HOST_HOOK_DISPATCH_FAILED`: definition and receipt differ, the handler entry point is missing, duplicated or unloadable, or the observation metadata is malformed | The `HOST_HOOK_DISPATCH_FAILED` row of the [host code table](../development/reference/host.md); `CAP-HOST-lifecycle-observation` §4 owns the handler contract. |
| Interrupted sync | The entry can stay `state` `ok`, while `devkit status` reports `pending_journal: true` with `TRANSACTION_PENDING`; dispatch refuses every hook with `HOST_HOOK_DISPATCH_FAILED` before reading the receipt while the sync journal exists | `OPS-distribution-sync` routes the pending journal; `CAP-HOST-lifecycle-observation` §4 owns the dispatch refusal. |
| Handler failed during the call | The entry has `state` `ok` and no journal is pending; the only devkit evidence is the hook's stderr warning `HOST_HOOK_DISPATCH_FAILED` naming the handler and its exception type or a result that is not a `HookResponse`, where the host exposes hook stderr | The service package that registers the handler, under `CAP-HOST-lifecycle-observation` §4; the [host code table](../development/reference/host.md) maps the code. |
| Host did not run the hook | devkit reports `unknown`: `trust` and `execution_permissions` are always `unknown`, and `runtime_on_path` describes only the inspecting process, not the PATH of the host process; the entry has `state` `ok`, no journal is pending, no warning is reachable and an `observe` registration's `last_received` does not advance | The agent host application, which owns hook trust, execution permissions, its launch PATH, timeouts and the display of hook stderr (`CAP-HOST-lifecycle-observation` §3, §5). |

Start with `host status`, because an `invalid` entry already names its code. Consult `devkit status` before reading
an `ok` entry as healthy, because `host status` does not inspect the sync journal. For evidence that matches no row,
take the code reported by `host status` or by the hook warning to its row in the
[host code table](../development/reference/host.md) and its actual advisory.

## Normal-state observation

After the owner's action, `host status` reports `ok: true` and every entry has `state` `ok`; the text form prints
`[HOST_STATUS: codex hooks=<n> ok=yes trust=unknown]`. `devkit status` reports `pending_journal: false`, and
`CAP-DIST-sync-and-transactions` Readiness Gate owns the synchronized-checkout criterion. For an `observe`
registration, `last_received.received_at` advances after the host delivers the next matching event
(`CAP-HOST-lifecycle-observation` §5). Neither status command establishes effective host enablement; only an
observation from a real host session shows that a hook ran (`CAP-HOST-lifecycle-observation` §1, §5).

## Authority boundary

The evidence cannot establish that the host trusted, enabled or invoked a hook, the PATH of the host process, or a
delivery count: concurrent observations overwrite the latest timestamp (`CAP-HOST-lifecycle-observation` §5). For a
handler other than `observe`, a missing observation proves nothing.

## Update triggers

- `CAP-HOST-lifecycle-observation` §2 to §5 change.
- The `host status` fields `state`, `last_received`, `trust`, `execution_permissions` or `runtime_on_path` change.
- The dispatch checks in
  [runner.py](../../packages/devkit-dist/src/devkit_dist/features/host/usecases/runner.py) change order.
- A host other than `codex` gains an adapter.
