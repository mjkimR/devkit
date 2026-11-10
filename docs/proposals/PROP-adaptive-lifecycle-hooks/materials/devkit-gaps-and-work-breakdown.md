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
| Codex delivered project-registered `SessionStart` and `Stop` hooks to a prototype logger once (codex-cli 0.163.0, 2026-10-17). No run of devkit's generated command by a host is recorded | `docs/materials/2026-10/20261017-hook-driven-integration-cleanup/codex-spike-evidence.md:17`, `:38-47`; `host-capability-matrix.md` §1 |

An adaptive handler would be the first production consumer of the hook path and the first handler outside
`devkit-dist`.

## 3. Gaps by component

| # | Component | What it needs | Rule or sentence the change touches |
| --- | --- | --- | --- |
| G1 | `HookResponse` | A stop decision with a reason, valid for `Stop` and `SubagentStop` only, exclusive with context, with a length limit | `CAP-HOST-lifecycle-observation` §4: "It MUST return `HookResponse()`, or context of at most 4096 characters for ..." and "Other events accept an empty response only" (`:124-128`); the class docstring "grants no execution authority" stays true and is restated for a continuation request. The change alters a MUST, so it carries one decision record |
| G2 | Codex adapter, response | Render the decision as `{"decision":"block","reason":...}` for the two events; refuse it elsewhere | `host/repositories/adapters/codex.py:45-51`; `ARCH-08-2-resource-taxonomy` output column "Bounded native context response" (`:276`); `docs/development/reference/host.md:8` |
| G3 | Advisory rule | Keep every failure a release: a failed dispatch still prints `{}` and exits `0`. State that a stop decision grants no approval or permission | `CAP-HOST-lifecycle-observation` §4 `:131`, `:133-135`; `ARCH-08-1-agent-output` `:35-38`. No sentence is contradicted when failures keep releasing |
| G4 | Event set | `SubagentStop` in the Codex adapter's events, with its matcher rule | `CAP-HOST-lifecycle-observation` §2 `:63-64` (event list); `CAP-DIST-manifest-spec` `:63-65`; `codex.py:16-18` |
| G5 | Adapter layer | A lookup from host name to adapter; `SUPPORTED_HOSTS` with a second entry; the host key `claude-code`, because inventory compares the hook's host with the selected agent name (`inventory.py:214-223`) while MCP registration maps it to `claude` (`registrations.py:189-191`) | `CAP-HOST-lifecycle-observation` §1 "Other hosts are unsupported" (`:35`), §2 "Only `codex` is supported" (`:62`) |
| G6 | Claude Code adapter | Its registration file, event list, matcher and timeout rules, command and response rendering. The matcher-group shape and the response fields equal Codex's (`documented`), so `parse_config`, `plan_config` and the response renderer are reusable | New module beside `codex.py`; `CAP-HOST-lifecycle-observation` §3 "For Codex, sync MUST update only receipt-recorded matcher groups in `.codex/hooks.json`" (`:76-80`), §4 generated command (`:101-104`) |
| G7 | Host configuration boundary | A second shared file under management. `.claude/settings.json` and `.claude/settings.local.json` also hold permission and environment settings, and Claude Code rewrites the local file itself. Only the owned groups under `hooks` are written | `CAP-DIST-agent-projections`, host configuration boundary: "manage only their receipt-recorded matcher groups in `.codex/hooks.json` ... devkit never touches other host settings" (`:65-69`); `CAP-DIST-workspace-ownership` §2 (`:44-47`); `CAP-HOST-lifecycle-observation` §3 "permission settings remain host-owned" (`:95`). `CAP-MCP-runtime-registration` (`:59-60`) already reconciles Claude Code's `.mcp.json`, so the sentence is narrower than the code today |
| G8 | Registration planning | The locked-restore condition generalized from `.codex/hooks.json` to each adapter's file. A hook definition names one host, so a bundle that targets two hosts ships one asset per event and host, and each gives one `unprojected` report per other selected agent | `sync.py:730`; `CAP-DIST-sync-and-transactions` `:495-496`; `CAP-HOST-lifecycle-observation` §2 (`:67-69`) |
| G9 | Receipt, ownership and removal | A `host_hooks` record already holds `host`, `asset`, `event`, `handler`, `command`, `matcher`, `timeout`, and validation goes through the adapter, so a new host or event needs no new field. The ownership rule does not carry over to every Claude Code file. Ownership lives in the committed receipt, and sync refuses with `HOST_HOOK_CONFLICT` when a recorded group is missing from an existing file; no adopt mode exists. `.codex/hooks.json` rarely exists before devkit writes it. A Claude Code settings file routinely does, and where the file is ignored or machine-local, a second clone or worktree holds one without the group. The MCP reconciler avoids this by writing only untracked ignored files and keeping ownership in a machine-local ledger | `project/repositories/receipt.py:282-310` (strict keys at `:287`); `distribution/services/installation/receipt.py:86-99`; `host/services/configuration.py:65-72`; `CAP-DIST-sync-and-transactions` `:99-101`; `CAP-HOST-lifecycle-observation` §3 (`:82-93`, "No force/adopt mode exists" at `:85`); `ADR-mcp-runtime-and-shared-artifacts` (`:145-149`) |
| G10 | `devkit host status` | The `--host` option accepts the second host. For a gate, status cannot show that the hook ever ran: only the `observe` handler writes `last_received`. Needed: the runner records the same metadata for every dispatched handler | `host/cli.py:48-57`; `host/usecases/status.py:43-79`; `CAP-HOST-lifecycle-observation` §5 "The built-in `observe` handler MUST store only ..." (`:142-145`) |
| G11 | Handler-owned state | A loop breaker that survives between hook calls needs a store. The observer's files hold no session identity by rule; the handler's package keeps its own record with a hash of the session identity. Needed by the state-only block condition, by the name-aware condition if a cancel is to last beyond one stop, and by the narrow `SubagentStop` gate if the host does not bound repeated blocks (`gate-behavior-and-measurement.md` §3.1, §3.2) | `CAP-HOST-lifecycle-observation` §4 "Handlers MUST NOT ... log sensitive event content" (`:131`), §5 (`:142-145`) |
| G12 | Launch environment | The generated command is `devkit host hook ...`, resolved through the host's PATH. A host started without the project environment on PATH runs no hook and reports nothing to devkit. This holds for Codex today and for any further host. If a host holds a stop when the hook command fails (probe CX-7), a blocking gate needs a fallback in the generated command that prints `{}`, which changes the command the receipt records | `CAP-HOST-lifecycle-observation` §4 (`:101-104`); `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` (`:23-25`) |
| G13 | Handler package | A feature edge from the adaptive handler's feature to `devkit_dist.features.host` (the facade exports `HookEvent` and `HookResponse`; `models.hooks` is not a public module) and to the assignment feature; an entry point in `devkit.host.handlers` | `.devkit/architecture.toml:28-60`; `RULE-architecture`; `host/usecases/runner.py:21-37` |
| G14 | Bundle source snapshots | Not a gap for this work. A snapshot refuses a hook whose handler is not `observe`, but a snapshot source may declare only `devkit.bundles` entry points, so a package that carries a handler is refused before that check | `distribution/services/snapshots/support.py:114-122`; `distribution/services/snapshots/source.py:57-66` |
| G15 | Document drift in the sections above | The capability names the handler group `devkit_dist.features.host.handlers` at `:26` and `devkit.host.handlers` at `:113` (the code uses the second); its boundary list names module paths that moved; the reference page names `dispatch` and `inspect_host`, which the facade exports as `DispatchHostHook` and `InspectHost` | `CAP-HOST-lifecycle-observation` `:24-32`; `docs/development/reference/host.md:14-16` |
| G16 | Project lookup from the event's `cwd` | The hook command finds the project from the event's `cwd` (the Git top level of that directory) and checks that checkout's receipt and host file. The host loads the registration from the checkout it started in. An event whose `cwd` is another worktree is checked against the wrong checkout: where that worktree's receipt or host file lacks the registration, dispatch fails to `{}` and releases, and handler state lands under that checkout. This is the case for a `SubagentStop` of an assignee in its own worktree, for a `Stop` inside a Codex subagent thread if one fires, and for a Host whose directory is a worker's worktree at the stop. The command accepts `--workspace-root`, so an adapter with a project-directory variable can pin the root; Codex documents none | `host/cli.py:89-95`; `project/repositories/project.py:102-127`; `host/usecases/runner.py:63-78` |

Earlier records, none of which rejects a stop gate:

- `docs/materials/evaluations/agent-hooks.md` (2026-10-14) did not adopt runtime hooks because "no consumer needs
  them yet". It names three ownership models for a host hook file: a projected file devkit owns, a narrowly owned
  entry inside a settings file, or a printed snippet the user installs.
- `SPEC-hook-driven-integration-cleanup` deferred hook adapters for hosts other than Codex, and
  `SPEC-claude-terminal-mcp-approval` excluded a Claude Code `PreToolUse` approval hook. Both concern approval, not a
  stop gate.

### 3.1 The open decision inside a Claude Code adapter

G7 and G9 leave one decision that no evidence here settles: how a Claude Code registration gets installed, and,
where devkit writes it, into which file and with its ownership recorded where.

| Choice | Consequence |
| --- | --- |
| The shared `.claude/settings.json`, tracked, ownership in the committed receipt | The existing ownership and removal rules of the hook path carry over unchanged; this departs from the MCP practice of writing only untracked ignored files. The hook is registered for every clone and collaborator, and each needs `devkit` on the host's PATH. In a repository that ignores `.claude/`, as this one does, the file is per checkout and an existing file without the group is a `HOST_HOOK_CONFLICT` |
| The local `.claude/settings.local.json`, ownership in a machine-local store as MCP registration uses | No conflict between clones and nothing shared. It needs an ownership store outside the receipt, and devkit then writes a file the host itself rewrites when the user approves a permission |
| Either file with a rule that adopts an absent group | Removes the conflict; reverses "No force/adopt mode exists" |
| No file written by devkit: the user installs the registration | devkit prints the matcher groups for the user to paste and only reads the settings files to verify a registration at dispatch and in `devkit host status`. The host configuration boundary, the ownership rule and the three distribution capabilities stay as they are. It costs a manual step per checkout: once per repository where the shared settings file is tracked, and in each clone and each linked worktree a Claude Code session starts in where `.claude/` is ignored, as in this repository. The step recurs after every change to a registration, sync neither installs nor removes the hook, and a missing registration is a silent release that only `devkit host status` shows. This is the third ownership model of `docs/materials/evaluations/agent-hooks.md` |

For `SubagentStop` only, Claude Code documents a further path: a `Stop` hook in a subagent's frontmatter becomes
`SubagentStop` for that subagent, and devkit already writes the Claude Code role files as its own projections. The
frontmatter keys devkit accepts do not include hooks today
(`packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py:26-39`), the path is
extracted from documentation and unprobed, and it serves neither `SessionStart` nor the Host's `Stop`.

Whether devkit writes the registration at all (W4 or W4u) is the user's choice with the delivery option (question
q2), because it decides the number of specs. Under W4 the file and the place of its ownership record belong to the
adapter's own unit and are its main risk. The first three choices keep the adapter at
size L (W4). The fourth makes it size M (W4u): the adapter module, the lookup, the command that prints the
registration and the verification remain, and the sync, removal, ownership and boundary work falls away.

## 4. Work items

| # | Item | Modules | Tests | Documents | Depends on | Risk | Size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | Stop decision in the handler contract, rendered for Codex (G1 to G3) | `host/models/hooks/model.py`, `host/repositories/adapters/codex.py`, `host/usecases/runner.py`; if CX-7 shows a held stop, the fallback in the generated command (G12), which changes every recorded command | About 4 new cases in `test_hooks.py` | `CAP-HOST-lifecycle-observation` §4, `ARCH-08-2-resource-taxonomy`, `docs/development/reference/host.md`, and one decision on the blocking response | None | Low in code. Codex's behavior on a block, a timeout and a failed hook is unobserved (probes CX-3, CX-3b, CX-6, CX-7) | S |
| W2 | `SubagentStop` event for Codex (G4) | `codex.py` | About 2 cases | `CAP-HOST-lifecycle-observation` §2, `CAP-DIST-manifest-spec` | W1 for a decision on it | Low. The matcher rule for the event needs the vendor page read again | S |
| W3 | Dispatch observation for every handler (G10) | `host/usecases/runner.py`, `host/services/observation.py` | About 2 cases | `CAP-HOST-lifecycle-observation` §5 | None | Low | S |
| W4 | Claude Code hook adapter (G5 to G9, G12, G15) | New adapter module; `host/services/configuration.py`, `host/models/hooks/model.py`, `host/cli.py`, `distribution/usecases/sync.py`; an ownership store or an adopt rule under two of the three choices of section 3.1; optionally the hook definition for several hosts | 15 to 20 cases parallel to the Codex set, plus `test_cli.py`, `test_workspace_safety.py` and locked-sync cases | `CAP-HOST-lifecycle-observation` §1 to §5, `CAP-DIST-agent-projections`, `CAP-DIST-workspace-ownership`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions`, both reference pages, the installation guides, and the decision of section 3.1 | Probes CC-1 to CC-10 | Medium to high: the decision of section 3.1; devkit writes a file that holds permission settings; a host launched without the project environment runs no hook; first adapter for a second host | L |
| W4u | Claude Code hook adapter with a registration the user installs (the fourth choice of section 3.1) | New adapter module; `host/services/configuration.py`, `host/models/hooks/model.py`, `host/cli.py` with a command that prints the registration; `distribution/services/installation/host_hooks.py` skips the host; dispatch and status read the settings files | About 10 cases: validation, rendering, printed registration, dispatch and status with a present and an absent registration | `CAP-HOST-lifecycle-observation` §1 to §5, `CAP-DIST-manifest-spec`, the host reference page, the installation guides | Probes CC-1 to CC-10 | Medium: the manual step is per checkout and nothing reports a checkout that skipped it; a host launched without the project environment runs no hook | M |
| W5 | Antigravity hook adapter | New adapter; the runner's `cwd` and event-name checks, because the input carries `workspacePaths` and no documented event name; another registration shape and response shape | A full parallel set | The same documents as W4 | Probe AG | High: failure and timeout behavior undocumented; no subagent event | L |
| W6 | Ledger additions for a Host gate (N2, N3 of `gate-behavior-and-measurement.md`) | The assignment feature of `devkit-adaptive`: one recorded field on `new`, a list read without observation | Unit and integration cases in that feature | The assignment capability that `PROP-adaptive-assignment-cli` creates | `PROP-adaptive-assignment-cli`, which is accepted: W6 is a follow-up to that unit | Low. Records written before the field exists belong to no checkout | S |
| W6b | Paths outside the scope in the `list` observation of an `open` assignment (N6) | The assignment feature: the changed-path collection `verify` uses, applied before a return | Unit and integration cases in that feature | The assignment capability | `PROP-adaptive-assignment-cli` | Low | S |
| W7 | Session-start handler and hook preset | A new feature in `devkit-adaptive` with a handler entry point; hook assets and a preset in the `adaptive-dev` bundle; `.devkit/architecture.toml` | Unit cases for the text and its truncation; an integration case through `devkit host hook` on a temporary repository; the bundle preset tests; one installed-consumer case | `CAP-DLV-adaptive-development` rule 1 and §4, the assignment capability, one guidance sentence in the bundle | The delivered commands and the delivered `devkit-adaptive` package. W6 is optional: without it the injection lists the whole repository | Low: nothing is blocked | M |
| W8 | Host `Stop` gate handler | The feature of W7: one of the two block conditions of `gate-behavior-and-measurement.md` §3.1, the reason text, and a per-session record under `.devkit/transient/` (G11) for the state-only condition | Unit cases per row of the decision table; integration cases for block, repeated stop and unreadable ledger | The same capability with the decision table and the wrong-block statement; one guidance sentence; under the name-aware condition, the sentence of `CAP-DLV-adaptive-development` that the context file is not parsed and the sentence "No command reads or writes it" of the ledger storage decision of `PROP-adaptive-assignment-cli` | W1, W6, W7 | Medium: the behavior is the risk, not the code. A wrong block costs a turn and can push an agent to close assignments to pass | M |
| W9a | Narrow `SubagentStop` gate, for an assignee in its own worktree | The feature of W7: the conditions of `gate-behavior-and-measurement.md` §3.2; the root pinning of G16 where the host offers a variable; a record per subagent (G11) unless the probes show the host bounds repeated blocks | Unit cases per condition; integration cases with a linked worktree | The same capability | W1, W2, W6b, W7; probes CC-3b and CC-3c, or CX-4b and CX-4c | Medium to high: it is not buildable on a host that reports the Host's directory for a subagent; on Codex G16 has no remedy documented; no host states a cap on repeated `SubagentStop` blocks | M |
| W9b | `SubagentStop` gate for every assignee | A host agent identity in the assignment record, written by the delegating agent after the subagent starts; then the handler | Both features | The assignment capability and its command decision | W9a and an accepted design change in the assignment feature | High: it changes who records what in the assignment design | L |
| W10 | Probes and measurement | None | None | The results, recorded as material | Nothing for the probes; the delivered commands for the measurement | None to the code; it costs host sessions: about twelve steps per host for the probes; ten observed runs or 30 days, and fifteen scenario runs, per host for the measurement | Not a spec |

## 5. Delivery options

| Option | Items | Specs | Prevents | Does not prevent | Unverified before delivery |
| --- | --- | --- | --- | --- | --- |
| (a) Codex only: blocking `Stop` and session start, no new host | W1, W3, W6, W7, W8 | 1 (size L), plus W6 as a follow-up to the assignment unit, one further spec of size S, or inside this spec | F1 and F2 in Host sessions on Codex | Anything on Claude Code or Antigravity; F3 | The Codex probes: the review step, a block, the repeated stop after a tool call, `Stop` inside subagent threads, timeout behavior; that Codex is launched with `devkit` on PATH (G12) |
| (b) Codex and Claude Code: blocking `Stop` and session start | (a) plus W4 or W4u | 2: the host hook contract with the Claude Code adapter (L with W4, M with W4u), and the adaptive gates (L) | F1 and F2 on both hosts | Antigravity; F3 | The same, plus the Claude Code probes and the decision of section 3.1 |
| (c) Session-start injection only | Codex: W7, with W3 so that `devkit host status` shows the hook ran; W6 optional. With Claude Code: plus W4 or W4u | 1 (size M) on Codex; with Claude Code 2 under W4, or 1 (size L) under W4u | F2 | F1, F3 | `SessionStart` delivery of devkit's generated command and the visible context on each host; G12 |
| (d) No delivery | None | 0 | Nothing beyond the commands and guidance | F1, F2 and F3 keep the cost they have without a gate | Nothing |
| (e) Decide after the measurement | W10, then one of (a) to (d) by the criteria of `gate-behavior-and-measurement.md` §4.4 | 0 now | Nothing until the decision | Until the decision, what (d) does not prevent | The effect itself, which is what the wait measures |

The narrow `SubagentStop` gate (W2, W6b, W9a) is an addition to (a) or (b): one further spec of size M after the
Host gate exists, because it shares that feature and its capability section. W9b is in no option.

The smallest delivery depends on the host the user's adaptive Host sessions run on (question q1):

| Host of the Host sessions | Smallest delivery | Specs |
| --- | --- | --- |
| Codex | (c) on Codex | 1, size M |
| Claude Code | W3, W4u and W7 with a registration the user installs; or W4, then W7, with a registration devkit manages | 1, size L; or 2: size L, then size M |
| Both | (c) on Codex first; Claude Code with W4u or W4 added | 1, size M; then as the row above without W7 |

What option (e) consists of:

1. Nothing is accepted for delivery in this proposal now.
2. The probes of `live-probes.md` need nothing and run when question q3 says. The user runs them, or a Host session
   the user authorizes to register a hook in a throwaway directory and run a host there.
3. The measurement starts when the commands of `PROP-adaptive-assignment-cli` are delivered. The user takes it, or a
   Host session the user authorizes to run host sessions. It ends at ten observed runs per host or 30 days after that
   delivery, whichever comes first, with the constructed scenarios run five times each.
4. At the end the counts are read against the fixed criteria. A criterion met opens a delivery proposal for the
   items it names; none met is recorded as "not delivered" with the counts.
5. While it waits, the unit takes one of two states.
   - **Ended**: the proposal's status becomes `rejected` with the reason "delivery decision deferred until the
     measurement; a criterion met reopens it as a new proposal". A later hygiene pass writes the rejection decision
     from that sentence and deletes this directory. Before the status commit the Host moves the five materials under
     `docs/materials/` with material IDs, replaces their references to this directory's envelopes and proposal
     sections, and writes the answers to q1 and q3 into them. A draft proposal for the measurement, depending on
     `PROP-adaptive-assignment-cli`, carries the trigger, the owner and the end, so Backlog holds the pending work.
     This run writes none of that: its write scope is this directory.
   - **Kept**: the proposal stays in review on its Planning branch. Nothing moves, the questions and answers stay
     in its envelopes, and the materials are reachable only on that branch until the unit ends.
   Option (d) is the ended state with the reason "not delivered" and without the measurement draft.

Observations that bear on the choice:

1. **No option as packaged can start now.** W6 to W9 depend on commands that are accepted and not delivered yet, in
   a package that does not exist yet. W1 to W5 depend on nothing and could start, but they deliver a contract without a
   consumer, which `docs/materials/evaluations/agent-hooks.md` declined for that reason.
2. **The cost is concentrated in the second host.** Without W4 the whole delivery is one spec whose host-feature part
   is two small changes. With W4 it is two specs, a change to the host configuration boundary and the decision of
   section 3.1; with W4u it is smaller and changes no boundary, at the price of a manual installation per checkout.
3. **Which host matters is not in the repository.** The project selects `antigravity`, `claude-code` and `codex`
   (`.devkit/installation.json`). If adaptive Host sessions run on Claude Code, options (a) and (c) on Codex prevent
   nothing there.
4. **Session-start injection on Codex needs no new response in the hook contract.** The existing context response
   covers it. It is the smallest delivery.
5. **The gate's value is the difference between F1 with and without it, minus its wrong blocks.** Neither term is
   known; the criteria of `gate-behavior-and-measurement.md` §4.4 use both.

## 6. Decomposition (Q7)

The number of specs follows from the Claude Code adapter. W4 is a complex module by itself, with its own decision,
its own tests and a use for any bundle; everything else on the host side is two or three small changes that have no
consumer apart from the gate and travel with it. W4u is size M and can travel with a session-start handler in one
spec, but not with the whole of option (a).

- Options (a), (c) on Codex, (c) with Claude Code under W4u, and (d) are at most one spec. The proposal keeps a
  single size under them.
- Option (b), and (c) with Claude Code under W4, are two specs. Under either, this proposal is returned for
  decomposition with these children:

| Child | Content | Area | Size | Depends on |
| --- | --- | --- | --- | --- |
| Host hook stop decision and Claude Code adapter | W1, W3, and W4 or W4u (W1 only under (b)) | `capabilities/host/` | L with W4, M with W4u | The Claude Code probes; the decision of section 3.1 |
| Adaptive lifecycle gates | W7, and W8 under (b), with the measurement after delivery | `capabilities/delivery/` | L under (b), M under (c) | The first child; `PROP-adaptive-assignment-cli` with W6 |

- The narrow `SubagentStop` gate adds a third unit (W2, W6b, W9a) after those.
- The candidate design the draft listed (a blocking response, `SubagentStop`, a second host adapter and adaptive
  handlers for all three events) is therefore three specs.

Which case applies depends on the option the user carries forward and, with Claude Code, on W4 or W4u (question
q2), so the split is not made in this run.

## 7. Documents each change would edit

Living documents only; each also has specs and reconcile records among its inbound references, which stay as
history. Counts are the inbound references `devkit docs refs <ID> --direction in -n 0` listed.

| Document | Inbound | Edited by |
| --- | --- | --- |
| `CAP-HOST-lifecycle-observation` | 26 | W1, W2, W3, W4, W4u |
| `CAP-DIST-agent-projections` | 26 | W4 |
| `CAP-DIST-workspace-ownership` | 31 | W4 |
| `CAP-DIST-manifest-spec` | 40 | W2, W4 |
| `CAP-DIST-sync-and-transactions` | 75 | W4 |
| `ARCH-08-2-resource-taxonomy` | not listed | W1 |
| `CAP-DLV-adaptive-development` | 39 | W7, W8 |
| The assignment capability of `PROP-adaptive-assignment-cli` | not created yet | W6, W6b, W7, W8, W9a, W9b |

`ADR-mcp-runtime-and-shared-artifacts` (`:142-149`) binds MCP registration: project files only, automatic writes
only to untracked ignored files, a portable committed receipt. A hook adapter is bound by
`CAP-HOST-lifecycle-observation` §3, which has no tracked-file test. The MCP clause is a precedent for the second
choice of section 3.1, not a bar to the first.
