---
id: SPEC-language-setting-coverage
title: Extend language settings to MCP approval content
summary: Share a local-capable presentation language preference between response-style and domain-owned English/Korean MCP approval content, without claiming host UI localization.
status: completed
created: 2026-10-20
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-language-setting-coverage] Extend language settings to MCP approval content

## 1. Problem Statement & Motivation

Handed off from proposal PROP-language-setting-coverage on 2026-10-20.
- **Preserved Materials**: `docs/materials/2026-10/20261020-language-setting-coverage`
- Target Docs Blueprint: `PROP-language-setting-coverage-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

A language preference currently affects only response-style. Integration and handoff build their native approval
messages in English, and MCP transports that supplied text to the host. Share a small presentation preference
between these concrete consumers. Localize devkit-owned copy, while keeping host controls and embedded repository
or provider content outside that promise.

`ADR-shared-language-preference-with-bounded-approval-content` records the accepted design. The evidence and
alternatives are in `docs/materials/2026-10/20261020-language-setting-coverage/language-coverage-evidence.md`; `target-docs.md` names reconciliation targets.
Design acceptance does not establish implementation or localized native UI support.

## 2. User Stories

- **US-1**: As a developer, I want a shared local-capable language preference so that response guidance and devkit-owned approval content can use English or Korean consistently.

## 3. Non-Goals

1. **Scope Excluded**: Host-owned UI, arbitrary provider/user text, CLI/advisory output, locale detection, dynamic translation, host registration and approval authority.

## 4. Acceptance Criteria & Behavioral Contracts

The integrated prerequisites provide `core.local_config`, `core.mcp_context` and `devkit_mcp.server`. It permits that future runtime's context-plumbing modules/tests and, among
existing packages, only: dist core/config/CLI, distribution variable declarations and inventory/readers with their
tests; agt integration rendering/service/tests; spec handoff rendering/tests; catalog response-style manifest and
its tests. New translation helpers belong beside their domains. No other package behavior, host registration,
approval enforcement or catalog bundle is included. Development narrows file boundaries against the integrated
prerequisites before implementation. Documentation boundaries are limited to the targets named in `target-docs.md`.

### Scenario 1 [AC-01]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
1. Configuration tests cover absent/shared/local values, exact `auto/en/ko`, unsupported-string English fallback
   with visible provenance, wrong types, malformed local files and inherited worktree copies. Dist-only imports
   remain SDK/domain-free. MCP requests resolve the owning workspace while executor preferences differ.

### Scenario 2 [AC-02]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
2. Manifest tests cover the one valid `default_from` reference, invalid references/types, absent versus explicit
   consumer overrides, projectless defaults and existing free-text overrides. Shared receipts stay fixed under
   local language changes; eligible response-style outputs change; tracked/forbidden outputs refuse; sync repairs
   stale local-render state. An explicit shared consumer override versus a local global preference is exercised.

### Scenario 3 [AC-03]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
3. English/Korean static-template parity checks cover every integration route and conditional branch plus handoff.
   Assert decision-relevant statements and identical interpolated scope/evidence, escaping and truncation limits.
   Domain reviewers inspect both languages for semantic equivalence; substring/snapshot checks alone are not a
   semantic translation review. No accepted plan/provider evidence is translated. The handoff form's message
   remains sufficient when all schema titles/descriptions are omitted by a fixture client.

### Scenario 4 [AC-04]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
4. SDK/stdio fixtures assert UTF-8 preservation, schema keys/enum/default/required equivalence and canonical reply
   parsing. Both languages exercise explicit approval, submit false, decline/cancel, unavailable form, malformed
   reply and stale-scope behavior. Local/cloud and workspace-identity guards remain independent of language.
   Changing preference during an open form does not change its text or confer new authority; a new request uses it.

### Scenario 5 [AC-05]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
5. Harmless native fixtures for each available CLI record exact client/server/SDK/protocol versions, requested
   content and observed message/title/description/enum behavior separately. Their accept/decline/cancel handlers
   return data only and cannot create worktrees, merge, push, clean or change real config/trust. Record omitted or
   transformed fields, boolean widgets, buttons, validation errors and permission prompts as client-owned behavior.
   If fixtures cannot run under current permissions, retain an explicit per-host unverified status in docs/report.

### Scenario 6 [AC-06]: Carried from proposal
- **Given** the accepted shared-language contract below and integrated prerequisite APIs.
- **When** the corresponding configuration, rendering or approval flow is exercised.
- **Then** the following verification obligations hold.
6. Run lint/type checks, `just test-affected`, focused distribution-only/packaging checks where imports change,
   governance checks, mandatory medium code review and separate reconcile review. No product-wide output
   translation or unrelated regression expansion is required. Development effort remains medium.

## 5. Accepted Design and Development Assumptions

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Selected Design

#### Preference and resolution

Add optional `[presentation] language = "auto" | "en" | "ko"` to shared and allowed local configuration.
The value is a string; the three listed values are supported choices, not a closed validation enum. Missing values
resolve to `auto`. An unsupported string resolves to `en` for these shared-preference consumers; preserve the
requested value and mark fallback in resolver/inspection metadata. Wrong types and malformed configuration fail
with the existing `CONFIG_INVALID` contract. Identifiers are exact lowercase strings; no locale aliases,
OS-language detection, environment variables, conversation sampling or language-tag negotiation is added.

Core owns a dependency-free language result containing requested value, resolved preference (`auto|en|ko`), source
and fallback flag. It accepts an explicitly bound workspace, uses the effective configuration resolver, and does
not import domains, transport or catalog bundles. A shared-only resolution path supplies canonical asset planning.
Expose the same provenance and fallback through `devkit config show --effective`; this is diagnostic metadata,
not translated agent output. The preference grants no execution authority.

`SPEC-local-config-execution-environment` owns overlay validation, precedence, worktree copies and render ledgers.
This follow-up extends its local allowlist by exactly `presentation.language`. Shared config then local config
selects each preference key. Copy and independent-worktree semantics remain its contract. Development starts after
that implementation and `SPEC-standalone-devkit-mcp` are integrated and their concrete APIs rechecked; Planning
does not read or rely on mutable sibling implementation. This proposal neither changes their accepted scope nor
implements a second resolver.

#### Response-style binding

Keep the existing bundle-specific `language` variable and its `auto` default. Add one narrowly supported optional
manifest declaration, `default_from = "presentation.language"`, valid only on string variables and only for this
exact reference. No arbitrary config access, dotted lookup engine, settings registry or extra template namespace
is introduced. Manifest validation rejects unsupported references/types as `BUNDLE_INVALID`.

Response-style opts in through that declaration. A supplied bundle variable wins, including explicit `auto`, `en`,
`ko`, or an existing free-text language. Only an absent bundle-specific value uses the shared language result;
projectless bundle planning uses the declaration's ordinary `auto` default. Existing explicit free-text overrides
keep their current semantics and never control MCP. The effective merge chooses per-key values first, then the
consumer override wins: a shared explicit response-style `language="auto"` still overrides local
`presentation.language="ko"`. To inherit, remove that explicit consumer override; to override it personally,
set the bundle-specific local value. Config inspection shows both selecting values and their sources.

Templates still receive only `vars`; no project config object is exposed. Canonical inventory resolves shared
preferences only; local inventory resolves effective preferences. Existing local-render checks reject changes to
forbidden kinds or tracked outputs even if a template opts into this default. Ordinary sync is needed to rerender
response-style; runtime approval language is reread per request. A changed local preference makes old rendered
assets stale under the existing ledger contract until sync. With `auto`, response-style follows the user's current
request; MCP deterministically uses English because it has no trusted conversation-language input. An explicit
`ko` or `en` aligns the two consumers unless a response-style override was supplied.

#### Approval content ownership

The initial translations are reviewed static English and Korean templates owned by each domain: integration in
`devkit-agt`, handoff in `devkit-spec`. No runtime machine translation, remote service, shared translation framework
or translated SDK errors is introduced. The runtime supplies the owning configuration workspace context through
the service boundary selected by the MCP extraction; domain execution continues to use its retained executor root.
The tool caller cannot select language or a different configuration workspace in arguments. Neither service reads
the executor's preference by accident.

Resolve language at the start of each confirmation request and keep that rendered-language snapshot for that
form. A preference change while a form is open changes the next form, not its content or the scope of an accepted
reply. Existing environment, stale-scope, policy and config-identity checks still run independently; this snapshot
cannot excuse a cloud transition or vanished workspace. Do not add presentation language to approval scope or make
it new authority. When inspecting immutable scope, keep rendered copy out of business equality/digests unless an
existing domain check already binds the complete request; preserve those existing checks.

Localize every devkit-owned action heading, explanatory sentence, field title/description and fixed placeholder
in integration's local merge, fast-forward, cleanup-only and pull-request branches, plus handoff's development,
setup, effort and final-integration limitations. This includes existing truncation and absent-value markers.
Messages themselves must explain the approval choice and handoff effort values, because a client may omit or
transform field metadata. Use the existing flat boolean/string schema; do not add `oneOf`, `enumNames`, translated
schema values or client/version sniffing just for localization. The message pairs `low`, `medium`, `high` with their
localized meanings; returned enum values remain canonical.

Preserve paths, branches, SHAs, repository selectors, commands, codes, property keys, booleans, action names,
`low|medium|high`, defaults and required fields exactly. Preserve quoting, control-character escaping and existing
summary truncation limits. Repository titles/summaries, accepted plan text, provider disclosures, checks,
unverified-platform text and extension identities remain quoted verbatim; they are supplied evidence, not owned
translation copy. A Korean form may therefore contain English source evidence. Do not summarize or translate the
accepted plan, omit caveats, or infer semantic equivalents for third-party content. Optional metadata such as
field title/description remains supplied text, never evidence of what a particular client actually displayed.

Native `accept/decline/cancel`, `approve=true` authorization, default false, missing capability, stale-scope guards
and process-local resume authority are unchanged. Translation must not add a new path around these checks.

#### Host support and honest coverage

Supported target hosts remain the Codex CLI and Claude Code terminal CLI. The protocol carries supplied messages
and schema labels; actual display is client-owned. Host headings, buttons, boolean widgets, help, validation errors,
permission/trust prompts and chrome are outside devkit's language guarantee. A host's assistant-response language
setting is not proof of native form localization. No whole-screen localization claim is made.

Official-source and protocol evidence is distinct from visible terminal evidence. The existing English Claude
approval material proves approval outcomes only; it does not prove Korean rendering or field-label fidelity.
Planning may be accepted with that explicit live-evidence gap. Development can report tested owned-content
support, but must keep each CLI's localized visible-form status unverified until its harmless fixture is observed.
Unavailable UI evidence is a reported limitation, not a license to modify real trust/config or run business actions.
No such live fixture was launched in this Planning turn.

### 4. Lifecycle & Retirement Criteria

Ready for `plan-accept` after the PADR, bounded language semantics, challenger disposition, dependency order and
live-evidence limitation are reviewed. Acceptance chooses this design; it does not start Development or certify
host-rendered UI. No separate essential design question remains beyond accepting or declining this recommendation.

Scope excluded: translating all CLI/advisory/machine output, repository documents or arbitrary user/provider text;
MCP tool descriptions and result payloads; host-owned UI, permission/trust configuration, VS Code/SDK/desktop host
support, locale detection, dynamic translation services, arbitrary preference registries and new approval authority.
SDK transport fixtures are evidence only and do not add SDK-host product support.
