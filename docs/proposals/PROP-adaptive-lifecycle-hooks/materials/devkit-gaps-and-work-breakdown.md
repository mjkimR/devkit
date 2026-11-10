# devkit gaps and work breakdown for PROP-adaptive-lifecycle-hooks

Scope: what devkit lacks for `Stop`, `SubagentStop` and `SessionStart` gates (spike question Q3 of
`PROP-adaptive-lifecycle-hooks`), the work items that would provide it with their sizes, and the delivery options
compared (Q7). Paths are relative to the repository root; `host/` abbreviates
`packages/devkit-dist/src/devkit_dist/features/host/`.

## 1. Evidence boundary

- Read: the host feature, its callers in the distribution and project features, its tests and the documents that
  state its contract, at commit `79156358`. `envelopes/scout-02.yaml` records the inbound-reference search.
- Not run: no test, no sync and no host. Sizes are estimates from the code read, not from a prototype.
- Host facts are those of `host-capability-matrix.md`, with its evidence classes.
- Sizes use the proposal template's scale: S a single fix, M one or two sessions, L a complex module.

## 2. The hook path today

| Fact | Evidence |
| --- | --- |
| The host feature's hook code is about 630 lines in eight modules; `usecases/registrations.py` (740 lines) is MCP registration | `wc -l` over `host/` |
| One adapter exists and the lookup returns it for every supported host | `host/services/configuration.py:17-20`; `host/models/hooks/model.py:15` |
| A handler returns `HookResponse(additional_context: str \| None)` and nothing else | `host/models/hooks/model.py:38-42` |
| Registration planning, the receipt record and status are written per host and loop over hosts | `distribution/services/installation/host_hooks.py:15-35`; `project/models/receipt.py:88-98`; `distribution/usecases/status.py:404-409` |
| One caller hard-codes the Codex file | `distribution/usecases/sync.py:730` |
| The only registered handler is the built-in `observe`; no bundle in the repository ships a hook asset | `packages/devkit-dist/pyproject.toml:37-38`; no `kind = "hook"` in any `bundle.toml` under `packages/` |
| The contract is pinned by 19 test functions in one file, with synthetic events | `packages/devkit-dist/tests/integration/features/host/test_hooks.py` |
| No delivery of a registered hook by a host is recorded | `host-capability-matrix.md` §1 |

An adaptive handler would be the first production consumer of the hook path and the first handler outside
`devkit-dist`.

## 3. Gaps by component

| # | Component | What it needs | Rule or sentence the change touches |
| --- | --- | --- | --- |
| G1 | `HookResponse` | A stop decision with a reason, valid for `Stop` and `SubagentStop` only, exclusive with context, with a length limit | `CAP-HOST-lifecycle-observation` §4: "It MUST return `HookResponse()`, or context of at most 4096 characters for ..." and "Other events accept an empty response only" (`:124-128`); the class docstring "grants no execution authority" stays true and is restated for a continuation request |
| G2 | Codex adapter, response | Render the decision as `{"decision":"block","reason":...}` for the two events; refuse it elsewhere | `host/repositories/adapters/codex.py:45-51`; `ARCH-08-2-resource-taxonomy` output column "Bounded native context response" (`:276`); `docs/development/reference/host.md:8` |
| G3 | Advisory rule | Keep every failure a release: a failed dispatch still prints `{}` and exits `0`. State that a stop decision grants no approval or permission | `CAP-HOST-lifecycle-observation` §4 `:131`, `:133-135`; `ARCH-08-1-agent-output` `:35-38`. No sentence is contradicted when failures keep releasing |
| G4 | Event set | `SubagentStop` in the Codex adapter's events, with its matcher rule | `CAP-HOST-lifecycle-observation` §2 `:63-64` (event list); `CAP-DIST-manifest-spec` `:63-65`; `codex.py:16-18` |
| G5 | Adapter layer | A lookup from host name to adapter; `SUPPORTED_HOSTS` with a second entry; the host key `claude-code`, because inventory compares the hook's host with the selected agent name (`inventory.py:214-223`) while MCP registration maps it to `claude` (`registrations.py:189-191`) | `CAP-HOST-lifecycle-observation` §1 "Other hosts are unsupported" (`:35`), §2 "Only `codex` is supported" (`:62`) |
| G6 | Claude Code adapter | Its registration file, event list, matcher and timeout rules, command and response rendering. The matcher-group shape and the response fields equal Codex's (`documented`), so `parse_config`, `plan_config` and the response renderer are reusable | New module beside `codex.py`; `CAP-HOST-lifecycle-observation` §3 "For Codex, sync MUST update only receipt-recorded matcher groups in `.codex/hooks.json`" (`:76-80`), §4 generated command (`:101-104`) |
| G7 | Host configuration boundary | A second shared file under management. `.claude/settings.json` and `.claude/settings.local.json` also hold permission and environment settings, and Claude Code rewrites the local file itself. The decision is which file, and that only the owned groups under `hooks` are written | `CAP-DIST-agent-projections`, host configuration boundary: "manage only their receipt-recorded matcher groups in `.codex/hooks.json` ... devkit never touches other host settings" (`:65-69`); `CAP-DIST-workspace-ownership` §2 (`:44-47`); `CAP-HOST-lifecycle-observation` §3 "permission settings remain host-owned" (`:95`). `CAP-MCP-runtime-registration` (`:59-60`) already reconciles Claude Code's `.mcp.json`, so the sentence is narrower than the code today |
| G8 | Registration planning | The locked-restore condition generalized from `.codex/hooks.json` to each adapter's file. A hook definition names one host, so a bundle that targets two hosts ships one asset per event and host, and each gives one `unprojected` report per other selected agent | `sync.py:730`; `CAP-DIST-sync-and-transactions` `:495-496`; `CAP-HOST-lifecycle-observation` §2 (`:67-69`) |
| G9 | Receipt and removal | No new field: a `host_hooks` record already holds `host`, `asset`, `event`, `handler`, `command`, `matcher`, `timeout`, and validation goes through the adapter. The removal rule ("remove only its exact owned group; an empty `hooks` object and the file container remain") applies unchanged to a second file. A new record field would change the reader's strict key set, so an older devkit would refuse the newer receipt | `project/repositories/receipt.py:282-310` (strict keys at `:287`); `distribution/services/installation/receipt.py:86-99`; `CAP-DIST-sync-and-transactions` `:99-101`; `CAP-HOST-lifecycle-observation` §3 (`:82-93`) |
| G10 | `devkit host status` | The `--host` option accepts the second host. For a gate, status cannot show that the hook ever ran: only the `observe` handler writes `last_received`. Needed: the runner records the same metadata for every dispatched handler | `host/cli.py:48-57`; `host/usecases/status.py:43-79`; `CAP-HOST-lifecycle-observation` §5 "The built-in `observe` handler MUST store only ..." (`:142-145`) |
| G11 | Handler-owned state | A loop breaker that survives between hook calls needs a store. The observer's files hold no session identity by rule; the handler's package keeps its own record with a hash of the session identity | `CAP-HOST-lifecycle-observation` §4 "Handlers MUST NOT ... log sensitive event content" (`:131`), §5 (`:142-145`) |
| G12 | Launch environment | The generated command is `devkit host hook ...`, resolved through the host's PATH. A host started without the project environment on PATH runs no hook and reports nothing to devkit | `CAP-HOST-lifecycle-observation` §4 (`:101-104`); `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` (`:23-25`) |
| G13 | Handler package | A feature edge from the adaptive handler's feature to `devkit_dist.features.host` (the facade exports `HookEvent` and `HookResponse`; `models.hooks` is not a public module) and to the assignment feature; an entry point in `devkit.host.handlers` | `.devkit/architecture.toml:28-60`; `RULE-architecture`; `host/usecases/runner.py:21-37` |
| G14 | Bundle source snapshots | A snapshot refuses a hook whose handler is not `observe` | `distribution/services/snapshots/support.py:114-122` |
| G15 | Document drift in the sections above | The capability names the handler group `devkit_dist.features.host.handlers` at `:26` and `devkit.host.handlers` at `:113` (the code uses the second); its boundary list names module paths that moved; the reference page names `dispatch` and `inspect_host`, which the facade exports as `DispatchHostHook` and `InspectHost` | `CAP-HOST-lifecycle-observation` `:24-32`; `docs/development/reference/host.md:14-16` |

Earlier records, none of which rejects a stop gate:

- `docs/materials/evaluations/agent-hooks.md` (2026-10-14) did not adopt runtime hooks because "no consumer needs
  them yet". It names the three ownership models for a host hook file that G7 has to choose from: a projected file
  devkit owns, a narrowly owned entry inside a settings file, or a printed snippet the user installs.
- `SPEC-hook-driven-integration-cleanup` deferred hook adapters for hosts other than Codex, and
  `SPEC-claude-terminal-mcp-approval` excluded a Claude Code `PreToolUse` approval hook. Both concern approval, not a
  stop gate.

## 4. Work items

| # | Item | Modules | Tests | Documents | Depends on | Risk | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | Stop decision in the handler contract, rendered for Codex (G1 to G3) | `host/models/hooks/model.py`, `host/repositories/adapters/codex.py`, `host/usecases/runner.py` | About 4 new cases in `test_hooks.py` | `CAP-HOST-lifecycle-observation` §4, `ARCH-08-2-resource-taxonomy`, `docs/development/reference/host.md` | None | Low in code. Codex's behavior on a block, a timeout and a failed hook is unobserved (probes CX-3, CX-6, CX-7) | S |
| W2 | `SubagentStop` event for Codex (G4) | `codex.py` | About 2 cases | `CAP-HOST-lifecycle-observation` §2, `CAP-DIST-manifest-spec` | W1 for a decision on it | Low. The matcher rule for the event needs the vendor page read again | S |
| W3 | Dispatch observation for every handler (G10) | `host/usecases/runner.py`, `host/services/observation.py` | About 2 cases | `CAP-HOST-lifecycle-observation` §5 | None | Low | S |
| W4 | Claude Code hook adapter (G5 to G9, G12, G15) | New adapter module; `host/services/configuration.py`, `host/models/hooks/model.py`, `host/cli.py`, `distribution/usecases/sync.py`; optionally the hook definition for several hosts | 15 to 20 cases parallel to the Codex set, plus `test_cli.py`, `test_workspace_safety.py` and locked-sync cases | `CAP-HOST-lifecycle-observation` §1 to §5, `CAP-DIST-agent-projections`, `CAP-DIST-workspace-ownership`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions`, both reference pages, the installation guides, and one decision on the settings file and what stays host-owned in it | Probes CC-1 to CC-9 | Medium to high: devkit writes a file that holds permission settings and that the host rewrites; a host launched without the project environment runs no hook; first adapter for a second host | L |
| W5 | Antigravity hook adapter | New adapter; the runner's `cwd` and event-name checks, because the input carries `workspacePaths` and no documented event name; another registration shape and response shape | A full parallel set | The same documents as W4 | Probe AG | High: failure and timeout behavior undocumented; no subagent event | L |
| W6 | Ledger additions (N2, N3, N8 of `gate-behavior-and-measurement.md`) | The assignment feature of `devkit-adaptive`: one recorded field on `new`, a list read without observation, Git environment scrubbing | Unit and integration cases in that feature | The assignment capability that `PROP-adaptive-assignment-cli` creates | `PROP-adaptive-assignment-cli`; the change belongs to that unit or to a follow-up | Low. Records written before the field exists belong to no checkout | S |
| W7 | Session-start handler and hook preset | A new feature in `devkit-adaptive` with a handler entry point; hook assets and a preset in the `adaptive-dev` bundle; `.devkit/architecture.toml` | Unit cases for the text and its truncation; an integration case through `devkit host hook` on a temporary repository; the bundle preset tests; one installed-consumer case | `CAP-DLV-adaptive-development` rule 1 and §4, the assignment capability, one guidance sentence in the bundle | W6, the delivered commands, `PROP-adaptive-package-extraction` | Low: nothing is blocked | M |
| W8 | Host `Stop` gate handler | The feature of W7: the decision table of `gate-behavior-and-measurement.md` §3.1, a per-session record under `.devkit/transient/` (G11), the reason text | Unit cases per row of the decision table; integration cases for block, repeated stop, unchanged set and unreadable ledger | The same capability with the decision table and the wrong-block statement; one guidance sentence | W1, W6, W7 | Medium: the behavior is the risk, not the code. A wrong block costs a turn and can push an agent to close assignments to pass | M |
| W9 | `SubagentStop` gate | A change to the assignment feature first: a mapping from a subagent to its assignment and a check before the return (N5, N6); then W2 and a handler | Both features | The assignment capability and its command decision, which states that the commands "block no session" and that an assignee runs none | W1, W2, W8, and an accepted design change in the assignment feature | High: it reverses choices the assignment design made on purpose | L |
| W10 | Probes and measurement | None | None | The results, recorded as material | The delivered commands for the measurement; nothing for the probes | None to the code; it costs host sessions: about nine steps per host for the probes, ten observed runs and fifteen scenario runs per host for the measurement | Not a spec |

## 5. Delivery options

| Option | Items | Specs | Prevents | Does not prevent | Unverified before delivery |
| --- | --- | --- | --- | --- | --- |
| (a) Codex only: blocking `Stop` and session start, no new host | W1, W3, W6, W7, W8 | 1 (size L), plus W6 in the assignment unit | F1 and F2 in Host sessions on Codex | Anything on Claude Code or Antigravity; F3 | Every Codex cell of the matrix: delivery, the review step, `Stop` inside subagent threads, timeout behavior |
| (b) Codex and Claude Code: blocking `Stop` and session start | (a) plus W4 | 2: the host hook contract with the Claude Code adapter (L), and the adaptive gates (L) | F1 and F2 on both hosts | Antigravity; F3 | The same, plus the Claude Code probes and the settings-file decision |
| (c) Session-start injection only | Codex: W6, W7. Both hosts: plus W4 | 1 (size M) on Codex; 2 with Claude Code | F2 | F1, F3 | `SessionStart` delivery and the visible context on each host |
| (d) No delivery | None | 0 | Nothing beyond the commands and guidance | F1, F2 and F3 keep the cost they have without a gate | Nothing |
| (e) Decide after the measurement | W10 now; then one of (a) to (d) by the criteria of `gate-behavior-and-measurement.md` §4.4 | 0 now | Nothing until the decision | Nothing is lost that (a) to (c) could deliver earlier: none of them can start before the commands exist | The effect itself, which is what the wait measures |

The `SubagentStop` gate (W2, W9) is in no option. It adds one more spec to (a) or (b) and needs the assignment
design changed first.

Observations that bear on the choice:

1. **No option can start now.** Every item but W1 to W5 depends on commands that are still in Planning, in a package
   that does not exist yet. W1 to W5 alone deliver a contract without a consumer, which
   `docs/materials/evaluations/agent-hooks.md` declined for that reason.
2. **The cost is concentrated in the second host.** Without W4 the whole delivery is one spec whose host-feature part
   is two small changes. With W4 it is two specs and a change to the host configuration boundary.
3. **Which host matters is not in the repository.** The project selects `antigravity`, `claude-code` and `codex`
   (`.devkit/installation.json`). If adaptive Host sessions run on Claude Code, option (a) prevents nothing there.
4. **Session-start injection on Codex needs no change to the hook contract.** The existing context response covers
   it. It is the smallest delivery and would give the first live observation of the hook path.
5. **The gate's value is the difference between F1 with and without it, minus its wrong blocks.** Neither term is
   known.

## 6. Decomposition (Q7)

- Options (a), (c) on Codex and (d) are at most one spec. The proposal keeps a single size under them.
- Option (b), and (c) with Claude Code, are two specs with different capability areas and independent acceptance:
  the host adapter is usable by any bundle and testable with a test handler, and the adaptive gates are testable on
  Codex without it. Under either, this proposal is returned for decomposition with these children:

| Child | Content | Area | Size | Depends on |
| --- | --- | --- | --- | --- |
| Host hook stop decision and Claude Code adapter | W1, W2, W3, W4 | `capabilities/host/` | L | The Claude Code probes |
| Adaptive lifecycle gates | W7, W8, and the measurement after delivery | `capabilities/delivery/` | L | The first child for W1; `PROP-adaptive-assignment-cli` with W6 |

- The candidate design the draft listed (a blocking response, `SubagentStop`, a second host adapter and adaptive
  handlers for all three events) is three specs: the two children above and W9 with its assignment change.

Which case applies depends on the option the user carries forward (question q1), so the split is not made in this
run.

## 7. Documents each change would edit

Living documents only; each also has specs and reconcile records among its inbound references, which stay as
history. Counts are the inbound references `devkit docs refs <ID> --direction in -n 0` listed.

| Document | Inbound | Edited by |
| --- | --- | --- |
| `CAP-HOST-lifecycle-observation` | 26 | W1, W2, W3, W4 |
| `CAP-DIST-agent-projections` | 26 | W4 |
| `CAP-DIST-workspace-ownership` | 31 | W4 |
| `CAP-DIST-manifest-spec` | 40 | W2, W4 |
| `CAP-DIST-sync-and-transactions` | 75 | W4 |
| `ARCH-08-2-resource-taxonomy` | not listed | W1 |
| `CAP-DLV-adaptive-development` | 39 | W7, W8 |
| The assignment capability of `PROP-adaptive-assignment-cli` | not created yet | W6, W7, W8, W9 |

`ADR-mcp-runtime-and-shared-artifacts` (`:142-144`) limits host files to project files: it refuses to modify global
host configuration or trust. W4 stays inside that limit.
