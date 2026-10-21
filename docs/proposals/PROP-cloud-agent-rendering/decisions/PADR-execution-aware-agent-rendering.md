---
id: PADR-execution-aware-agent-rendering
title: Execution-aware agent rendering
summary: Use a reserved execution input for canonical rendering and extend templates to constitutions and subagent contracts while preserving runtime authority and personal-render restrictions.
proposal: PROP-cloud-agent-rendering
status: draft
created_at: 2026-10-21
---

# [PADR-execution-aware-agent-rendering] Execution-aware agent rendering

- **Status**: Draft
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`CAP-DIST-manifest-spec` allows templates only in selected Markdown asset kinds and excludes the constitution.
`CAP-DIST-sync-and-transactions` stores execution selection but personal rendering cannot change constitution or
guidance output. MCP guidance occurs both in always-loaded and on-demand assets. A user variable with a default
would permit transport drift from the selected execution environment and would not cover those surfaces.

## 2. Decision Drivers

Deterministic cloud/local reversal, complete reachable guidance, preserved local functionality, unchanged runtime
authority, strict receipt evidence and a small template API determine the choice.

## 3. Considered Options

| Option | Consequence | Disposition |
| --- | --- | --- |
| Configurable `vars.cloud` or inherited default | Consumers can disagree with execution selection; personal constitution output remains forbidden | Rejected |
| Move all conditional text to existing templated skills | Always-loaded constitution and projected worker contracts retain routing text or lose necessary boundaries; indirect references still need an audit | Rejected as sole solution |
| Reserved execution input plus constitution/subagent template support | Adds two validation surfaces and one typed receipt field; keeps source locality and all current personal restrictions | Recommended |
| Treat execution output as personal rendering | Requires broadening forbidden outputs/tracked eligibility and weakening canonical meaning | Rejected |

## 4. Decision Outcome

Expose only `execution.environment` alongside `vars`, with `local`/`cloud` values controlled by sync invocation or
workspace resolution. Both canonical and effective inventory use the same selected value. Use `local` for
projectless planning. Extend the sandbox API narrowly, with no mutable runtime configuration object.

Render explicit constitution and host-neutral subagent contract `.md.jinja` files before their existing validation and
host projection. Preserve final `.md` consumer paths, strict undefined handling, collisions, raw-source override
digests and ordinary `.md` literal behavior. Leave executable asset kinds untemplated; use transport-neutral
workflow prose and conditional Markdown references instead.

The receipt stores actual render environment as an optional strictly typed field in the one current schema.
Absence is an explicit unrecorded state, never an inferred default. New writing sync always records it; ordinary
sync can read an unrecorded receipt, retain ownership/conflict checks and regenerate evidence. Status/check reports
missing evidence and locked sync refuses the needed receipt update. Context may read hash-validated canonical
bytes without claiming a render mode; personal evidence that requires that mode is stale until sync. This is
one current schema, without a legacy reader, version dispatch or migration. Personal evidence includes
that render environment. Context validates rendered bytes without treating the receipt as runtime authority.
`--no-save` can intentionally produce output different from persisted runtime selection; the next sync/status/check
plans from saved selection, and runtime guards always read effective execution configuration independently.
Locked sync continues to reject canonical changes; ordinary sync can rewrite tracked canonical guidance.

Cloud operational text provides only supported CLI paths and explicit Host boundaries for unavailable operations.
Local text retains MCP-first discovery/connection and native approval routes. Audit the reachable maintained
surface, including references and variants, instead of claiming arbitrary source files or custom overrides are
MCP-free. Installation guides distinguish cloud setup from optional local onboarding.

## 5. Consequences

Development includes the core receipt reader as well as distribution planning, serialization, context evidence,
bundle assets/tests and installation guidance. The narrow core schema change is justified by its closed schema;
no generic existing field can honestly carry render mode. Runtime/MCP implementations stay out of scope.

Consumers switching environment may see tracked generated changes. `--no-save` does not change persistent runtime
authorization. Language/personal preference restrictions remain unchanged. Tests must cover both dimensions and
both host-independent validation and host-specific projection. High Development effort is warranted; medium
Planning includes one scout and one challenger. Acceptance remains the user's decision.
