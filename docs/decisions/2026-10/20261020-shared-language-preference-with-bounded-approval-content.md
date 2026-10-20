---
id: ADR-shared-language-preference-with-bounded-approval-content
title: Shared language preference with bounded approval content
summary: "Define one shared and local presentation language preference for response-style and domain-owned MCP approval text, while preserving machine values and separating host rendering from content coverage."
proposal: SPEC-language-setting-coverage
status: accepted
created_at: 2026-10-20
---

# [ADR-shared-language-preference-with-bounded-approval-content] Shared language preference with bounded approval content

- **Status**: Accepted
- **Date**: 2026-10-20

## 1. Context & Problem Statement

Response-style has a bundle language variable; native integration and handoff forms contain domain-owned English
text. MCP can carry server-supplied Unicode, but native UI fidelity and chrome remain host responsibilities. A
transport package must not become the owner of integration/handoff semantics or infer language from conversation.

## 2. Decision Drivers

One local-capable preference should serve real consumers without exposing governance config to templates, changing
approval authority, translating immutable source evidence, or promising host UI control. Preserve explicit consumer
choices and shared receipt determinism. Use the existing core configuration and extracted MCP workspace binding.

## 3. Considered Options

| Option | Benefit | Cost / decision |
| --- | --- | --- |
| Read response-style's variable directly from all services | Fewest new fields | Couples runtime behavior to an optional content bundle and makes a conversation-only override alter approvals; rejected. |
| Global preference plus one manifest default binding | Shared ownership, explicit consumer overrides, vars-only templates | Selected; one small manifest/config extension plus domain templates. |
| Inject all presentation config into template globals | Easy template access | Expands the existing scalar-only contract and hides bundle inputs; rejected. |
| Infer user language or ask an LLM to translate each request | Broad apparent language coverage | Nondeterministic scope wording and no trusted request-language signal; rejected. |
| Localize native UI through host configuration | Apparent consistency | No devkit authority over host UI; response-language settings do not establish it; excluded. |

## 4. Decision Outcome

Add `[presentation] language` with supported values `auto`, `en`, `ko`, absent `auto`, unsupported string fallback
`en`, and selecting source/fallback inspection. Core resolves only the explicitly bound configuration workspace.
MCP maps auto to English; response-style auto continues to follow the current conversation. All nonstring values
remain configuration errors. No alias or locale inference is included.

A string variable may declare only `default_from="presentation.language"`; a supplied bundle value wins, and
projectless planning uses its normal manifest default. Response-style opts in with its existing default and
explicit override behavior intact. Templates keep only `vars`; canonical and effective inventories resolve their
respective config snapshots. Local-render eligibility and receipt boundaries are unchanged.

Domains own reviewed static English/Korean confirmation templates. Messages explain all choices even when a host
omits schema metadata. Canonical keys, action values, identifiers and evidence are preserved; source/provider prose
is displayed verbatim. English and Korean are coverage of owned supplied content, not the entire visible screen.
The runtime propagates owning-workspace context without taking over domain language copy or approval logic.
Language is sampled once per form; environment and stale-scope checks remain independent and unchanged.

Development depends on the integrated implementations of `SPEC-local-config-execution-environment` and
`SPEC-standalone-devkit-mcp`. This is a follow-up extension of their contracts. There is no second config resolver,
registration implementation, business approval flow or standalone translation service.

## 5. Consequences

A shared response-style override can deliberately win over a local global preference; inspection and documentation
must make that precedence visible. Existing explicit free-text response-style overrides remain conversation-only.
An auto preference can produce a Korean conversation and an English deterministic form, so users seeking the same
language choose `ko` explicitly. Unsupported shared strings fall back visibly to English.

Domain template parity requires semantic review and route coverage. Source evidence may remain English in a Korean
form, and client buttons/errors may remain English as well. Protocol/SDK tests establish payload behavior only.
Localized live-form evidence remains separately unverified until harmless native observations exist; acceptance of
this recommendation does not certify it. A later host version may alter presentation without changing payloads.
