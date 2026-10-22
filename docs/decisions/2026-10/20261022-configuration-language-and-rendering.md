---
id: ADR-configuration-language-and-rendering
title: Configuration, language preference and execution-aware rendering
summary: "For shared config, local preferences and execution-dependent guidance, we use a restricted local overlay with an ignored render ledger, one presentation language preference and a reserved execution input, to keep shared policy and receipts reproducible, accepting more render paths and checks."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-separate-shared-configuration-from-local-execution-and-rendering
  - ADR-shared-language-preference-with-bounded-approval-content
  - ADR-execution-aware-agent-rendering
---

# [ADR-configuration-language-and-rendering] Configuration, language preference and execution-aware rendering

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `capabilities/distribution/` (`CAP-DIST-manifest-spec`,
  `CAP-DIST-sync-and-transactions`), `capabilities/mcp/`, `capabilities/worktree/`, `packages/devkit-dist`,
  `packages/devkit-core`, `packages/devkit-mcp`, the `response-style` bundle, installation guides

---

## 1. Context & Problem Statement

Template variables change committed receipt hashes and can change tracked guidance. Ignored files do not travel with
worktrees. A local environment label must constrain execution without granting approval authority.

Response-style has a bundle language variable; native integration and handoff forms contain domain-owned English
text. MCP can carry server-supplied Unicode, but native UI fidelity and chrome remain host responsibilities. A
transport package must not become the owner of integration/handoff semantics or infer language from conversation.

`CAP-DIST-manifest-spec` allowed templates only in selected Markdown asset kinds and excluded the constitution.
`CAP-DIST-sync-and-transactions` stores execution selection but personal rendering cannot change constitution or
guidance output. MCP guidance occurs both in always-loaded and on-demand assets. A user variable with a default
would permit transport drift from the selected execution environment and would not cover those surfaces.

The evidence for the local-configuration part is in
`docs/materials/2026-10/20261020-local-config-execution-environment/configuration-evidence.md`.

---

## 2. Decision Drivers

- Personal preferences must not leak into shared files; shared policy and snapshot verification stay reproducible.
- Worktree creation supplies its initial preferences before setup; each created checkout owns subsequent changes.
- A base-anchored service identifies its configuration workspace independently of its runtime root.
- The foundation belongs to devkit-dist and cannot import the harness, following `ADR-dist-foundation-ownership`.
- One local-capable language preference serves real consumers without exposing governance config to templates,
  changing approval authority, translating immutable source evidence, or promising host UI control.
- Preserve explicit consumer choices and shared receipt determinism; use the existing core configuration and the
  extracted MCP workspace binding.
- Deterministic cloud/local reversal, complete reachable guidance, preserved local functionality, unchanged runtime
  authority, strict receipt evidence and a small template API.

---

## 3. Considered Options

### Local configuration and rendering (`ADR-separate-shared-configuration-from-local-execution-and-rendering`)

- **Merge every local key into existing config/receipt**: small implementation; enables governance weakening and
  personal committed receipt/guidance changes. Rejected.
- **Copy local config before worktree setup**: simple, explicit snapshot with independent worktrees; base edits do
  not propagate and raw Git worktrees need explicit provisioning. Selected for worktrees.
- **Runtime-only language command with no rendering**: no second ledger; existing templated skill/native projection
  does not reflect the preference without a new per-reply lookup contract. Rejected.
- **Restricted local overlay and ignored render ledger** (Selected): preserves personal rendering and shared
  verification; requires explicit runtime reader routing, stale-ledger checks and restricted asset kinds.
- **Live retained-base preference inheritance**: no copying; couples independent checkouts and needs missing-base and
  multi-source restriction rules. Rejected.

### Language preference (`ADR-shared-language-preference-with-bounded-approval-content`)

- **Read response-style's variable directly from all services**: fewest new fields; couples runtime behavior to an
  optional content bundle and makes a conversation-only override alter approvals. Rejected.
- **Global preference plus one manifest default binding** (Selected): shared ownership, explicit consumer overrides,
  vars-only templates; one small manifest/config extension plus domain templates.
- **Inject all presentation config into template globals**: easy template access; expands the existing scalar-only
  contract and hides bundle inputs. Rejected.
- **Infer user language or ask an LLM to translate each request**: broad apparent language coverage; nondeterministic
  scope wording and no trusted request-language signal. Rejected.
- **Localize native UI through host configuration**: apparent consistency; no devkit authority over host UI and
  response-language settings do not establish it. Excluded.

### Execution-aware rendering (`ADR-execution-aware-agent-rendering`)

- **Configurable `vars.cloud` or inherited default**: consumers can disagree with execution selection; personal
  constitution output remains forbidden. Rejected.
- **Move all conditional text to existing templated skills**: the always-loaded constitution and projected worker
  contracts retain routing text or lose necessary boundaries; indirect references still need an audit. Rejected as
  sole solution.
- **Reserved execution input plus constitution/subagent template support** (Selected): adds two validation surfaces
  and one typed receipt field; keeps source locality and all current personal restrictions.
- **Treat execution output as personal rendering**: requires broadening forbidden outputs/tracked eligibility and
  weakening canonical meaning. Rejected.

---

## 4. Decision Outcome

### Local configuration, execution constraint and render ledger

- Use restricted local overlays and an ignored render ledger, with creation-time worktree copying: copy before
  setup/first sync, then independent ownership. The proposal defines the exact eligibility, errors, precedence,
  transaction behavior and acceptance matrix.
  (ADR-separate-shared-configuration-from-local-execution-and-rendering)
- Keep `read_project_config` shared-only; add `read_effective_config` and the independent explicit-root execution
  resolver in core. (ADR-separate-shared-configuration-from-local-execution-and-rendering)
- Local config cannot alter governance or topology.
  (ADR-separate-shared-configuration-from-local-execution-and-rendering)
- Shared receipt bytes remain canonical; a transient ledger permits only ignored human-readable asset bytes to differ.
  The local ledger is never an authority for executable rule/workflow/gate files or snapshot policy.
  (ADR-separate-shared-configuration-from-local-execution-and-rendering)
- New devkit worktrees receive the local file from the base caller before setup. Attach preserves an existing
  worktree's choice. No live inheritance, process cloud latch or global environment override is introduced.
  (ADR-separate-shared-configuration-from-local-execution-and-rendering)
- A retained MCP service binds a configuration workspace separately from its runtime and integration roots.
  Environment is a runtime constraint, never an approval grant; MCP owns enforcement and rechecks the bound workspace.
  (ADR-separate-shared-configuration-from-local-execution-and-rendering)

### Presentation language preference

- Add `[presentation] language` with supported values `auto`, `en`, `ko`, absent `auto`, unsupported string fallback
  `en`, and selecting source/fallback inspection. All nonstring values remain configuration errors. No alias or
  locale inference is included. (ADR-shared-language-preference-with-bounded-approval-content)
- Core resolves only the explicitly bound configuration workspace. MCP maps `auto` to English; response-style `auto`
  continues to follow the current conversation. (ADR-shared-language-preference-with-bounded-approval-content)
- A string variable may declare only `default_from="presentation.language"`; a supplied bundle value wins, and
  projectless planning uses its normal manifest default. Response-style opts in with its existing default and explicit
  override behavior intact. (ADR-shared-language-preference-with-bounded-approval-content)
- Templates keep only `vars`; canonical and effective inventories resolve their respective config snapshots.
  Local-render eligibility and receipt boundaries are unchanged.
  (ADR-shared-language-preference-with-bounded-approval-content)
- Domains own reviewed static English/Korean confirmation templates. Messages explain all choices even when a host
  omits schema metadata. Canonical keys, action values, identifiers and evidence are preserved; source/provider prose
  is displayed verbatim. English and Korean are coverage of owned supplied content, not the entire visible screen.
  (ADR-shared-language-preference-with-bounded-approval-content)
- The runtime propagates owning-workspace context without taking over domain language copy or approval logic.
  Language is sampled once per form; environment and stale-scope checks remain independent and unchanged.
  (ADR-shared-language-preference-with-bounded-approval-content)
- This is a follow-up extension of the `SPEC-local-config-execution-environment` and `SPEC-standalone-devkit-mcp`
  contracts: there is no second config resolver, registration implementation, business approval flow or standalone
  translation service. (ADR-shared-language-preference-with-bounded-approval-content)

### Execution-aware rendering

- Expose only `execution.environment` alongside `vars`, with `local`/`cloud` values controlled by sync invocation or
  workspace resolution. Both canonical and effective inventory use the same selected value. Use `local` for
  projectless planning. Extend the sandbox API narrowly, with no mutable runtime configuration object.
  (ADR-execution-aware-agent-rendering)
- Render explicit constitution and host-neutral subagent contract `.md.jinja` files before their existing validation
  and host projection. Preserve final `.md` consumer paths, strict undefined handling, collisions, raw-source override
  digests and ordinary `.md` literal behavior. Leave executable asset kinds untemplated; use transport-neutral
  workflow prose and conditional Markdown references instead. (ADR-execution-aware-agent-rendering)
- The receipt stores the actual render environment as an optional strictly typed field in the one current schema.
  Absence is an explicit unrecorded state, never an inferred default. New writing sync always records it; ordinary
  sync can read an unrecorded receipt, retain ownership/conflict checks and regenerate evidence. Status/check reports
  missing evidence and locked sync refuses the needed receipt update. There is no legacy reader, version dispatch or
  migration. (ADR-execution-aware-agent-rendering)
- Context may read hash-validated canonical bytes without claiming a render mode; personal evidence that requires that
  mode is stale until sync. Personal evidence includes that render environment. Context validates rendered bytes
  without treating the receipt as runtime authority. (ADR-execution-aware-agent-rendering)
- `--no-save` can intentionally produce output different from persisted runtime selection; the next
  sync/status/check plans from saved selection, and runtime guards always read effective execution configuration
  independently. Locked sync continues to reject canonical changes; ordinary sync can rewrite tracked canonical
  guidance. (ADR-execution-aware-agent-rendering)
- Cloud operational text provides only supported CLI paths and explicit Host boundaries for unavailable operations.
  Local text retains MCP-first discovery/connection and native approval routes. Audit the reachable maintained
  surface, including references and variants, instead of claiming arbitrary source files or custom overrides are
  MCP-free. Installation guides distinguish cloud setup from optional local onboarding.
  (ADR-execution-aware-agent-rendering)

---

## 5. Consequences

- **Negative / Risks**:
  - Distribution runtime readers must deliberately select effective rendering; engines and Git snapshots remain on
    the canonical receipt. Existing ignore-file seed-only behavior changes only for the managed local-config entry.
    Local preferences require ignored native destinations; refusal preserves tracked state. Existing config writers
    retain shared destinations.
  - A shared response-style override can deliberately win over a local global preference; inspection and
    documentation must make that precedence visible. Existing explicit free-text response-style overrides remain
    conversation-only.
  - An `auto` preference can produce a Korean conversation and an English deterministic form, so users seeking the
    same language choose `ko` explicitly. Unsupported shared strings fall back visibly to English.
  - Source evidence may remain English in a Korean form, and client buttons/errors may remain English as well. A later
    host version may alter presentation without changing payloads.
  - Consumers switching environment may see tracked generated changes. `--no-save` does not change persistent runtime
    authorization. Language/personal preference restrictions remain unchanged.
  - The narrow core receipt schema change is justified by its closed schema; no generic existing field can honestly
    carry render mode.
- **Follow-ups**:
  - The standalone MCP proposal consumes the resolver and owns its request context and approval logic, without
    copying config parsing.
  - Domain template parity requires semantic review and route coverage. Localized live-form evidence remains
    separately unverified until harmless native observations exist.
  - Execution-aware rendering development includes the core receipt reader as well as distribution planning,
    serialization, context evidence, bundle assets/tests and installation guidance; runtime/MCP implementations stay
    out of its scope.

---

## 6. Confirmation

- Local configuration: Medium Development with independent review and reconcile verification.
- Language preference: domain template semantic review and route coverage; protocol/SDK tests establish payload
  behavior only. Acceptance does not certify localized live-form evidence.
- Execution-aware rendering: tests cover both dimensions (execution environment and personal rendering) and both
  host-independent validation and host-specific projection; high Development effort, with medium Planning including
  one scout and one challenger.
