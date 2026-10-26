---
id: PLAN-spec-playbook-discovery
spec: SPEC-spec-playbook-discovery
---

# Technical Plan: `SPEC-spec-playbook-discovery` Task-aware playbook discovery through spec

## 1. Constitution & Invariant Review

- `ADR-external-playbook-execution` §4 ("Ordinary requests do not authorize discovery") and its §5 consequence, and
  the compaction-invocation statement of `ADR-immutable-decisions-editable-records` §4, are partially replaced by the
  accepted `ADR-spec-intake-playbook-discovery`; each affected statement gets a one-line pointer. Exact
  receipt-backed retrieval without execution authority and external scheduling and execution stay in force.
- `ADR-playbook-aliases-as-identifiers` is unaffected: intake searches name and description only.
- `CAP-HARN-agent-guidance` §3 principle 7 ("Playbooks on request only"), `CAP-DIST-context-and-playbooks` §1, §3,
  §5 and `ARCH-08-2-resource-taxonomy` (`package-playbook` entry conditions, consumption table, entry-point contract)
  state the explicit-only rule and are reconciled at `living-spec-draft`.
- `devkit-dist` must not depend on `spec` semantics (`AGENTS.md` boundaries): the generated skill names no `spec`
  asset and speaks of "another installed entry skill" generically.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `spec` skill (`skills/spec/SKILL.md.jinja`) | The routing list gains step 1 "Playbook discovery at intake" before classification: intake definition, skip table, conversation-level stops, not-skipped cases, the single bounded search, canonical-noun query, the four-condition selection rule, confirm-first offer line, silent no-match, error-as-no-match and the recorded selection. The old "Do not search or route to playbooks" constraint is removed. |
| `spec` reference `references/playbooks.md` (new) | Read only on a match: the confirm-first offer, recording the selection in the `plan-intent` note and records, loading the bundle context, reading the body (search path or `devkit playbook get`), prerequisites, following the procedure, no nested search, declined candidates. |
| `spec` guidance fragment `guidance/spec-pointer.md` | One clause: a new task intake runs the `spec` skill's intake step (playbook discovery) first. |
| `spec` playbooks `brownfield-adoption`, `feedback-hygiene`, `adr-compaction` | Entry condition reads "the user invoked or confirmed it". |
| `spec` `bundle.toml` playbook comment, seed `docs/README.md`, `spec-next` recommendation | Spec-side wording names intake discovery next to explicit invocation. |
| `devkit_dist` `playbook_skill.py` | Generic, spec-neutral body: explicit invocation for the current task, exact retrieval, a confirmed candidate offered by another installed entry skill counts as explicit invocation, explicit discovery steps, draft offer only for explicit discovery. Frontmatter description reworded; invocation policies unchanged. |
| `devkit_dist` `guidance_block.py` | Playbook line: "find and run an operational playbook (explicit invocation or a confirmed offer)". |
| `devkit_dist` `cli/playbooks.py` | Group help: "Search and retrieve occasional procedures; retrieval grants no execution authority." |
| `devkit` bundle constitution | Playbook clause names explicit requests, a confirmed offer of an installed entry skill and failing-rule remediation. |
| `maintenance` playbooks, catalog README | Entry condition "invoked or confirmed". |
| Living Spec | `CAP-HARN-agent-guidance`, `CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`, `ARCH-08-cross-cutting`, `CAP-DLV-drift-reconciliation`, `CAP-DLV-weekly-report`, `UC-reconcile-living-spec-drift`, `UC-inspect-weekly-repository-progress`, `CAP-DIST-content-packages`, root `AGENTS.md` line, the two ADR pointers. |

No new dependency, command, option, schema or code path: the search primitive and its options already exist. The
change is guidance text plus the generated skill text.

## 3. Component & Interface Design

Intake order in the `spec` skill:

```text
user message -> intake? (skip table, conversation stops) --no--> ordinary path (no search)
                    | yes
                    v
   devkit playbook search "<canonical English query>" --limit 3 --max-bytes 4096
                    | candidates (metadata only) / error -> treated as no match
                    v
   selection rule: operation-not-topic AND primary operation AND scope fits -> at most one offer line
                    v
   classification statement [+ "Playbook: <bundle>/<id> fits; confirm to use it."]
        confirm -> references/playbooks.md (invocation)      decline / no match -> ordinary path
```

## 4. Error Handling & Edge Cases

- Search errors (`NOT_SYNCHRONIZED`, `CONFIG_LOCAL_RENDER_STALE`, `ARGUMENT_INVALID`, `SEARCH_EXTRA_MISSING`, a lock
  timeout) count as no match; intake never runs their remediation and reports one line only when the error also
  blocks the task.
- No `spec` bundle: the consumer sees only the generic `devkit-playbook` skill; nothing searches at intake.
- A selected playbook continuing into a Unit or proposal: the ID goes into the `plan-intent` note so a worker that
  skips discovery still follows it.

## 5. Verification & Test Plan

- `devkit-spec`: new `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py` pins
  AC-01 to AC-05, AC-07 (spec playbooks and catalog playbooks) and AC-08 against rendered text; the existing bundle
  budget and link tests cover the new reference.
- `devkit-dist`: `test_playbooks.py` gains assertions on the generated skill text, guidance line and CLI help
  (AC-06); `test_guide_bundle.py` keeps its constitution directive.
- Commands: `just lint devkit-spec`, `just lint devkit-dist`, `just check devkit-spec`, `just check devkit-dist`,
  `just test-affected`, `just test-dist`, `just rules-check`, then `uv run devkit sync` with the tracked changes
  committed.
- AC-09: manual run in a scratch consumer under `tmp/` with `maintenance` selected, recorded in
  `materials/manual-run.md` as manual evidence.
