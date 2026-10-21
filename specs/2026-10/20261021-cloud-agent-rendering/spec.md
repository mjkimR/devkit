---
id: SPEC-cloud-agent-rendering
title: Render cloud agent assets without MCP guidance
summary: Make sync --cloud render CLI-only agent instructions without MCP routes, using execution-aware templates and coverage for constitution and subagent assets.
status: planned
created: 2026-10-21
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-cloud-agent-rendering] Render cloud agent assets without MCP guidance

## 1. Problem Statement & Motivation

Handed off from proposal PROP-cloud-agent-rendering on 2026-10-21.
- **Preserved Materials**: `docs/materials/2026-10/20261021-cloud-agent-rendering`

### 1. Background & Hypothesis

`SPEC-worker-shared-state-mcp` defines dual access to shared artifacts: MCP is the primary local route, and
CLI serves cloud execution. Local orchestration checks the MCP connection and asks the user to connect when it
is unavailable. Cloud agents should receive only the applicable CLI instructions, without MCP discovery,
connection, approval or fallback instructions.

Existing `devkit sync --cloud` records the execution environment but does not pass it into Jinja rendering.
Current template declarations support presentation language defaults, while constitution and subagent assets
are outside the supported templated kinds. Environment-aware output also affects local-render evidence and
repeat-sync behavior. Therefore complete cloud guidance removal needs a bounded distribution change and an
asset audit rather than a manually supplied template variable.

This proposal separates that work from shared artifact storage. It is queued for Planning; no rendering or
runtime policy change is authorized by this draft alone.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Render cloud agent assets without MCP guidance so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Resolved Direction

`ADR-execution-aware-agent-rendering` recommends a reserved `execution.environment` template input, with
exactly `local` or `cloud`, separate from configurable `vars`. Resolve the invocation flag first, then the
checkout's effective execution setting, then the existing `local` default. Pass that single selected value
through both canonical and effective inventory planning before rendering. Projectless bundle planning uses
`local`. No environment variables, paths, clock, callable or general configuration object enter the sandbox.

This is a canonical rendering dimension, not a personal override. Ordinary sync may change tracked managed
or projected files and the canonical receipt when switching environment. Locked sync preserves its existing
canonical-output restrictions and refuses a change that requires canonical/tracked updates. Personal variables
and presentation language still compare two inventories under the same execution environment: they cannot alter
constitutions, guidance, inventory structure or other forbidden outputs.

Extend explicit `.md.jinja` support to the bundle constitution and host-neutral subagent contract Markdown. Render
before header/frontmatter/host validation and projection, including no-selected-agent validation. Keep ordinary
`.md` literal, collision detection, sandbox restrictions, raw override provenance, final managed `.md` paths and
lazy Jinja loading. Executable workflow, hook, rule and gate assets do not gain template support. Native subagent variants keep their current host-specific formats without new template support; audit any variant separately and use a host-neutral contract for conditional text.

### 3. Proposed Design & Impact

#### Render evidence and reversibility

The typed canonical receipt records the actual `execution_environment` used for output; extend its closed core
schema and writer in place, without a schema-version bump or legacy migration path. This narrowly adds
`packages/devkit-dist/src/devkit/core/receipt.py` to Development ownership. The receipt field is rendering evidence,
never execution authorization. The field is optional in the one current schema: absence means unrecorded,
never inferred `local` or effective configuration. Every new writing sync supplies it. Ordinary sync reads an
unrecorded receipt to retain ownership/conflict checks and generates fresh evidence; status/check reports missing
evidence, and locked sync refuses the receipt update. Context can still validate and read canonical bytes against
an unrecorded receipt without claiming an environment; personal render evidence that requires a mode is stale
until sync. No separate legacy reader, schema dispatch or migration is introduced. Existing canonical configuration readers and runtime environment guards retain
their authority. Sync status/check planning compares desired inputs to rendered evidence, including an environment
change with identical bytes. Personal render digests bind to this render environment and the canonical receipt,
using the selected in-memory value before persistence rather than rereading the old local file.

`--cloud` and `--local` remain mutually exclusive. Writing sync saves the selected local key unless `--no-save`;
dry-run/check write nothing. `--no-save --cloud` renders and records cloud output but leaves runtime configuration
unchanged. Context reads validate those output bytes against the receipt and personal evidence using the receipt's
render environment; they do not confuse it with persisted runtime authorization. The next ordinary sync uses the
saved/default environment and restores that output, and status/check reports the pending difference. This behavior
must be documented so an invocation flag cannot be mistaken for a persistent runtime guard. Transaction rollback,
configuration-race detection, manual-edit conflicts and worktree-local configuration isolation remain intact.

#### Agent guidance audit

Audit the complete selected maintained bundle surfaces: constitution, instruction bodies, skill entries and their
on-demand references, subagent contracts and host variants, guidance fragments, and machine workflow prose.
`MAT-cloud-rendering-audit` records starting locations and the required disposition. Convert conditional Markdown
to explicit templates; generated links and retrieval paths must name final `.md` files. Workflow executable files
stay ordinary files: use transport-neutral operational wording that preserves checks/gates, and put transport
selection in rendered skill/reference guidance. No host role, workflow gate or permission setting changes.

Cloud rendered guidance MUST contain no MCP tool identifiers, discovery/connection requests, registration steps,
native form/approval instructions, or MCP fallback routes. It presents supported CLI inspection/artifact operations
and the separately authorized CLI/PR path only. When no authorized cloud mutation exists, it states the boundary
and returns the result to the Host; it must not invent CLI equivalence or weaken approval requirements. Local
rendering preserves the existing MCP-first route and local-orchestration connection check. Existing runtime cloud
restrictions remain enforced independently of rendered text.

Consumer installation guides remain source documents rather than synced templates: clearly separate local optional
MCP onboarding from cloud setup, whose instructions use `sync --cloud` and CLI only. Repository source, capability
and architectural documentation may explain both transports. The MCP-free claim applies to the rendered executable
agent guidance corpus, not arbitrary repository reads, configuration key reference tables or source guide text.
An audit must explicitly classify each match, not use a broad exclusion for an entire asset kind. Third-party
bundles and arbitrary user overrides are not automatically rewritten; template mechanics apply to them, while the
MCP-free content guarantee covers repository-maintained selected bundle assets without custom content overrides.

#### Acceptance evidence for Development

- **AC1:** Fresh cloud sync over the maintained bundle selection produces MCP-free executable guidance across all
  supported host projections and on-demand context/reference paths. A complete asset inventory test fails for an
  unclassified surface or residual operational MCP instruction; it also checks that required CLI flows survive.
- **AC2:** Local → cloud → local produces deterministic restoration of final bytes, destinations and receipt
  environment. Repeating either mode is idempotent. Shared/local flags, default mode, `--no-save`, dry-run/check,
  locked refusal, identical-output environment changes and cross-worktree isolation have explicit assertions.
- **AC3:** Constitution and subagent templates validate before writes, including malformed rendered YAML, unsupported
  names/kinds, raw overrides, collisions, host variants, no selected agents and unavailable host projections.
  Environment and language combine without bypassing existing personal-render restrictions.
- **AC4:** Receipt round trips, missing canonical render provenance and first-sync refresh, stale/missing personal evidence, manual output edits, override drift, race detection
  and transaction rollback remain correct when environment changes. Context validates the actual rendered mode;
  runtime authorization still uses effective configuration, including the `--no-save` mismatch case.
- **AC5:** Local orchestration still requires its existing connection check; cloud instructions preserve human
  approval boundaries and existing cloud runtime rejection tests pass. No shared-storage or integration mutation
  capability is introduced. Packaging includes template sources and references resolve to final Markdown.

Validation includes focused rendering/receipt/context/projection and spec bundle audit tests, lint/type checks,
`just test-affected` with its full fallback intact, `just test-dist`, and consumer smoke for packaging/CLI wiring.
Planning supplies static source evidence; it does not claim those implementation checks have run.

Non-goals: MCP runtime authorization changes; host trust/sandbox or workflow gate changes; cloud integration
mutations; remote shared storage; arbitrary source-file concealment; templating executable assets; implementation
of in-flight exact-playbook retrieval APIs; automatic Development or acceptance.

### 4. Lifecycle & Retirement Criteria

This follows `SPEC-worker-shared-state-mcp` and relates to `SPEC-proposal-review-and-approval`. Existing APIs and
contracts are the planning baseline; later shared-artifact or exact-retrieval changes require a fresh dependency
check at Development. Do not assume another worktree's APIs are available. Development effort is high because
receipt authority, personal evidence, template validation and several host projections interact; Planning remains
medium with an evidence scout and one independent challenger pass.

Reconcile `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership`,
`CAP-DIST-agent-projections` and `CAP-DIST-context-and-playbooks` when implementation changes their contracts.
Promote the PADR through the normal handoff only after plan-accept. This proposal is ready for that decision only
after the challenger findings are resolved and the Planning envelopes/checks are committed.

