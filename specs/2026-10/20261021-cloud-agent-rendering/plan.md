---
id: PLAN-cloud-agent-rendering
spec: SPEC-cloud-agent-rendering
---

# Technical Plan: `SPEC-cloud-agent-rendering`

## 1. Constitution & Invariant Review

`ADR-execution-aware-agent-rendering` authorizes the bounded template and receipt changes. Runtime authority, layering, personal-output restrictions and workflow gates remain unchanged. No new dependencies or migrations.

## 2. Components and Interfaces

- Distribution templates expose reserved `execution.environment` beside scalar `vars`; resolve once before canonical and personal planning, with projectless local default.
- Manifest discovery accepts exactly one constitution source; common subagents render before contract parsing even with no agents. Native variants retain current formats. Managed and projected paths use final Markdown names.
- Core Receipt adds optional strict local/cloud render provenance, never effective-configuration authority. The writer always supplies it; absent evidence refreshes through normal receipt planning.
- Personal ledger digest includes the selected in-memory render mode. Context reads the receipt mode; unrecorded personal evidence fails stale while canonical reads remain valid.
- Maintained spec Markdown uses explicit templates. Workflow prose is transport-neutral; configuration-key references are classified separately. Source installation guides distinguish local onboarding and cloud CLI setup.

## 3. Failure Modes

Preserve transactional writes, configuration race checks, ownership/manual-edit conflicts, raw override digests, locked restrictions and personal forbidden-output checks. Both inventories use the same mode so personal preferences cannot masquerade as canonical environment changes. No-save output provenance can differ from runtime settings by design.

## 4. Verification

AC-01/05: full inventory corpus and final path tests across hosts, local routing preservation, packaging/consumer smoke and runtime cloud regression coverage. AC-02/04: receipt roundtrip, unrecorded bootstrap, no-save mismatch, environment-only change, idempotence/reversal, locked/check/dry-run, personal ledger, context, race/rollback/manual edits and worktree isolation. AC-03: templates, validation without agents, collisions, native variants, overrides and combined language/personal restrictions.

Run focused dist/spec tests, lint/type checks, `just test-affected` with full fallback, `just test-dist`, `just smoke`, governance checks and independent HIGH code/reconcile review loops.

## Boundary extension

The Host authorized the markdown_link rule, its colocated tests and guide because source template renames otherwise make the commit gate reject correct final Markdown links. Resolution is confined to declared same-bundle templates; missing and unrelated files still fail. The authoring/harness context CLI encountered the expected unrecorded personal-render evidence state after the implementation; source instructions were read directly, without changing installed receipts or projections.

The Host also authorized the two template-source entrypoint repairs and local/cloud guidance qualifiers in `CAP-HARN-agent-guidance`; other harness contracts remain outside this unit.
