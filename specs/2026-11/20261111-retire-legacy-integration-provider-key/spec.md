---
id: SPEC-retire-legacy-integration-provider-key
title: Reject the legacy [integration] provider key
summary: Removes the code path that accepts and ignores a legacy [integration] provider key, so the retired readiness-provider selection leaves no reader, diagnostic or documentation behind.
status: planned
created: 2026-11-11
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-DLV-project-policy
  - CAP-DLV-sdd-baseline-adoption
related_usecases:
  - UC-adopt-sdd-from-adaptive-development
workflow: sdd-spec-feature
---

# [SPEC-retire-legacy-integration-provider-key] Reject the legacy [integration] provider key

## 1. Problem Statement & Motivation

Handed off from proposal PROP-retire-legacy-integration-provider-key on 2026-11-11.
- **Preserved Materials**: `docs/materials/2026-11/20261111-retire-legacy-integration-provider-key`

`ADR-post-merge-verification` removed the readiness provider from integration, but `[integration]` still accepts an
ignored legacy `provider` key: `effective()` in `devkit_agt/features/integration/services/providers.py` lets
`provider` through, and its error text, the `policy()` docstring, `CAP-INT-mcp-services` §5 and four other documents
still describe the ignored value. `devkit config template --print` documents no `[integration]` table, and the
guidance sentences about the key were already removed (`docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md`
G1-11, G3-10). The reader, its error text and the documentation remain for a key no consumer needs.

The only consumer configuration carrying the key is `resource-indexer` (`provider = "spec"`), which pins devkit to an
older revision (`legacy-key-inventory.md` in the preserved materials). The user decided that it is a pilot consumer
that accepts the breakage and deletes the key when it next moves its pin.

## 2. User Stories

- **US-1**: As an agent running `devkit integration`, I want a leftover `[integration] provider` key refused with a
  fix that says the readiness-provider selection is retired and the key is deleted, so that I remove dead
  configuration instead of carrying it.
- **US-2**: As a maintainer, I want the Living Spec and quick references to state that `[integration]` accepts no
  keys, so that nobody documents or reintroduces a provider setting.

## 3. Non-Goals

1. **Scope Excluded**: a deprecation-warning period, a new notice or error code, or compatibility handling for
   `resource-indexer`; no edit of any consumer repository.
2. **Scope Excluded**: removing `integration` from devkit-dist `RESERVED_TABLES`. devkit-dist and
   `docs/development/reference/distribution.md` do not change: the table stays a reserved namespace that currently
   accepts no keys, so devkit-dist keeps passing it through unread instead of rejecting it on every configuration read.
3. **Scope Excluded**: the `ready_provider` test fixtures and the exported `Readiness`/`Evidence` models. The fixtures
   guard the `CAP-INT-mcp-services` §4 content boundary and read no configuration.
4. **Scope Excluded**: a new feature edge, and any change to the effective policy digest (it already excludes
   `provider`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The retired provider key is refused with a deletion fix
- **Given** a repository whose `.devkit/config.toml` has `[integration]` with `provider = "<any value>"`
- **When** `devkit integration prepare <branch>` (or `IntegrationService.prepare`) reads the policy
- **Then** it raises `INTEGRATION_CONFIG_INVALID` before any Git effect, the message names `provider`, and the fix
  says the readiness-provider selection is retired and to delete the key from `[integration]`

### [AC-02] Other keys and invalid shapes stay actionable
- **Given** `[integration]` with any other key (`unknown = "x"`), or a non-table `integration = "x"`
- **When** the policy is read
- **Then** it raises `INTEGRATION_CONFIG_INVALID` whose message names the offending key or shape and whose fix says to
  remove it, since `[integration]` accepts no keys

### [AC-03] An absent or empty table needs no setting
- **Given** a configuration with no `[integration]` table, or an empty `[integration]` table
- **When** `prepare` and `integrate` run
- **Then** they complete as before, and the effective policy digest equals the digest of the same configuration
  without the table

### [AC-04] Documentation states the table accepts no keys
- **Given** `CAP-INT-mcp-services`, `CAP-DLV-project-policy`, `CAP-DLV-sdd-baseline-adoption`,
  `UC-adopt-sdd-from-adaptive-development`, the integration quick reference and the devkit-agt README
- **When** a reader looks up `[integration]`
- **Then** `CAP-INT-mcp-services` §5 states that `[integration]` MAY be absent or empty and every key, the retired
  `provider` included, raises `INTEGRATION_CONFIG_INVALID`; the README integration row lists no readiness providers;
  and `rg -n -i "ignored legacy|legacy provider|legacy .integration. provider|legacy values are ignored" docs/capabilities docs/usecases docs/development/reference packages/devkit/README.md packages/devkit/src`
  prints no line

## 5. Assumptions

- The README's sentence on the `project` readiness provider describes the gate feature's provider, not the
  integration key, and stays.
- `test_merge_needs_no_readiness_provider_or_claims` parametrizes over an ignored legacy key; its legacy case becomes
  an empty `[integration]` table, which keeps the "no provider needed" claim under AC-03.

## 6. Source feedback

- `docs/materials/2026-11/20261111-review-refactor-guidance-cli/report.md` G3-10 (code part, deferred because the
  code surface was not selected in that run).
