---
id: CAP-DLV-adaptive-development
aliases:
  - CAP-DLV-idea-incubation
title: Adaptive Development
summary: "An opt-in content bundle supports adaptive product iteration and reusable execution agents with bounded optional teams, caller-owned lifecycle authority, isolated writers and source-specific verification."
area: delivery
status: active
usecases:
  - UC-advance-an-idea
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/subagents/swarm-worker.md
---

# [CAP-DLV-adaptive-development] Adaptive Development

## 1. Summary

The opt-in `adaptive-dev` catalog bundle supplies `/adaptive-dev` for adaptive product iteration, three optional
support roles, three reusable execution archetypes and a current-context template. The invoking agent is the coordinator (master). A product can remain
in adaptive development; no amount of work implies eventual SDD adoption. Explicit research teams are a separate bundle
(`CAP-DLV-deep-research`); this bundle neither invokes nor suggests them and links their retained material by ID.

`ADR-adaptive-development-and-research` owns the bundle's contents and its retained approach check and current context,
linking a research material by its ID, and the approach, bundle, entry and context-file names.
`ADR-skill-local-swarm-roles` owns reusable execution agents and optional role leads;
`ADR-worktree-isolated-parallel-workers` owns isolated writers and aggregate verification.

## 2. Scope and Boundary

- **In-Scope**: adaptive clarification, bounded research/experiments, representative implementation and actual
  usage, reusable execution agents, optional role leads, mutable current facts and resume.
- **Out-of-Scope**: explicit research teams and their retained materials (`CAP-DLV-deep-research`), shared approach
  policy (`CAP-DLV-project-policy`), generic projection (`CAP-DIST-agent-projections`), document formats
  (`CAP-DOCS-document-model`), project build/test tools and the separate baseline readiness/activation procedure
  (`CAP-DLV-sdd-baseline-adoption`).
- **Scope Excluded**: a runtime scheduler, agent bus, new wheel, mandatory role sequence, model routing, fixed
  management hierarchy, automatic approach switching, automatic implementation/publication, per-change SDD
  artifacts and reconstructed experiment history.

## 3. Business Rules and Policies

1. **Explicit selection**: WHERE `adaptive-dev:core` is selected, sync MUST deploy the bundle's entry and roles
   without seeding context or product documents. Core retains the six entry/support/template assets and adds
   `swarm-planner`, `swarm-worker` and `swarm-verifier`; `adaptive-dev:agents` MUST select only these three archetypes,
   with no adaptive entry, pointer or context template. Neither preset changes approach or caller lifecycle authority. Test: `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py`.
2. **Independent installation**: The bundle MUST install with docs/catalog without a devkit-spec distribution.
   Test: `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`.
3. **Approach inspection**: WHEN the entry starts product work, the coordinator MUST inspect the effective common
   development approach rather than infer it from bundle selection.
4. **Inactive entry**: IF the approach is not `adaptive-dev`, THEN the entry MUST stop product actions and report the
   shared configuration action before any user-directed approach change.
5. **Unreadable policy**: IF policy inspection fails, THEN the coordinator MUST report the actual error and next
   configuration action without performing product work.
6. **Adaptive clarification**: WHEN the next action needs a product decision, the coordinator SHOULD reuse known
   answers and ask only the consequential missing decision.
7. **Bounded evidence**: WHEN research or an experiment informs work, the coordinator MUST distinguish observations,
   assumptions, limitations and the decision informed; an experiment names its write boundary and stop condition.
8. **Representative implementation**: WHEN implementation is retained, the coordinator MUST provide executable run
   and verification instructions for its representative flow.
9. **Truthful verification**: WHEN reporting a check, the coordinator MUST identify actual source/artifact-specific
   execution and limitations; skipped, unavailable or inconclusive evidence remains unverified. Worker, aggregate
   and applicable landed-target results MUST identify their actual checked SHAs/artifacts, commands and outcomes.
10. **Iteration scope**: WHILE the product goal and constraints hold, the coordinator MAY reconstruct retained code,
    tests and documents without per-change SDD Units, approvals, envelopes or immutable experiment history.
11. **Changed direction**: IF the goal or constraints change, THEN the coordinator MUST obtain user direction before
    dependent work.
12. **Optional support**: WHERE a separable question or usage scope warrants delegation, the coordinator MAY invoke
    the corresponding support or execution agent directly, in flat delegation or through an optional role lead;
    no action requires all roles or a fixed team count.
13. **Role boundaries**: WHEN a role is invoked, the coordinator MUST supply one goal, absolute boundaries,
    source/base identity, permitted actions and Git operations, checks, stop condition and expected output before
    verifying the actual return. Child authority MUST narrow the parent assignment; nesting MUST stop at
    Host → lead → child and fit the Host-wide allowance including waiting leads. Unknown/exhausted capacity or
    unavailable nesting requires direct, flat or sequential fallback without settings changes. The role reports
    native/emulated availability truthfully.
13a. **Assignment handoff**: WHEN delegating a deliverable, the coordinator MUST name one owner, dependency or
    none, completion evidence and expected integration handoff alongside the existing assignment fields.
13b. **Shared interface**: WHEN concurrent writers depend on an unsettled shared interface, the coordinator MUST
    assign its ownership and resolve it before dependent concurrent writes, or sequence those writers.
13c. **Interface identity**: WHEN an assignment depends on a shared interface, the coordinator MUST provide the
    agreed interface and its source or artifact identity; a missing version requires explicit input or deferral.
    A changed interface requires reassessing dependent assignments before accepting their results.
13d. **Role checks**: WHERE the architect overlay is used, it MUST identify deliverables, blocking dependencies,
    interface ownership and assumptions that invalidate the split. WHERE the builder overlay is used, it MUST check
    the agreed interface and failure handling and report unresolved mismatches. WHERE the qa-tester overlay is used,
    it MUST report expected and observed behavior, reproduction and coverage limits. WHERE the reviewer overlay is
    used, it MUST check the actual diff for correctness, regressions, caller compatibility and failure handling and
    label unproven concerns as hypotheses. No overlay expands caller authority.
14. **Current context ownership**: WHEN retained resume facts change or work pauses, the coordinator MUST update
    project-owned `.devkit/adaptive-dev.md`; roles return evidence or drafts instead of editing that file. Failure
    checkpoints MUST retain source identity, dirty/unmerged results, active ownership and next recovery action;
    passing QA is not a prerequisite.
15. **Context preservation**: WHEN sync, removal or re-selection runs, sync MUST preserve existing project-owned
    context and product notes. Tests: catalog integration and installed-consumer tests.
16. **Voluntary adoption**: WHEN the user explicitly requests SDD adoption, the coordinator MUST leave activation to
    the separately available baseline procedure while explaining preparation with adaptive development still active.
17. **Useful alternatives**: WHEN research choices affect resume, current facts SHOULD link retained notes, surviving
    alternatives and conditions that would reopen a choice, and link a retained research material by its `MAT-<slug>`
    ID rather than copy it.
18. **One name**: Documents MUST call the approach "adaptive development"; identifiers and commands MUST use
    `adaptive-dev`. The former `incubation` name MUST NOT be accepted: no `incubation` bundle alias
    (`SELECTION_INVALID`) or approach value (`DEVELOPMENT_CONFIG_INVALID`), and no fallback read of
    `.devkit/incubation.md`. Tests: `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` and
    `packages/devkit-dist/tests/integration/features/project/test_development.py`.

19. **Reusable execution contracts**: Public archetypes MUST omit a skill prerequisite and source model/effort defaults;
    compatible callers retain their own workflow and authority, including SDD. Existing bundle-qualified model policy applies.
    Projects MAY extend via distinct prefixed IDs or verified caller-owned absolute overlays without changing shipped defaults;
    overlays MUST NOT expand tool, write or Git permissions. Public IDs have one owning bundle.
20. **Writer isolation**: Concurrent writers MUST own separate worktrees and absolute boundaries; parents MUST wait
    before writing in child-owned checkouts. Unavailable isolation requires serial writers. Actual changed paths MUST
    be checked before integration; only the Host integrates into the final target.
21. **Recovery**: On failure/interruption, the lead MUST stop or collect children before releasing ownership and
    preserve active, dirty or unmerged worktrees until results are retained or removal has separate authority.
    Failed combined checks return to bounded repair with reproducing evidence or an explicit unresolved result.

22. **Risk-based probes**: WHEN verifying a change, the coordinator MUST choose normal, relevant failure and integration probes from the changed behavior and consequence of failure and retain the expected signal, actual interaction, source identity, outcome and limitation.
23. **Probe classification**: IF a probe fails before valid product execution, THEN the coordinator MUST classify a harness or environment failure only on evidence and otherwise retain an unknown cause; product behavior remains unverified until a valid product probe passes.
24. **No-progress diagnosis**: IF no assignment repair bound is supplied and two consecutive attempts produce the same symptom without material new diagnostic evidence, THEN the coordinator MUST change strategy before another equivalent attempt. Material evidence changes or tests a causal hypothesis, isolates a dependency or identifies a distinct failure. The trigger does not cap authorized work or establish completion.
25. **Useful recovery facts**: WHEN a failed approach affects the next action, the Host MUST retain its reason, source identity, owner, surviving hypothesis, retry condition and next recovery action; on resume the coordinator rechecks applicability.

Distribution checks enforce file/metadata contracts. Clarification, evidence, optionality and resume are semantic
agent contracts; keyword assertions alone do not establish them.

## 4. Interfaces and Data Contracts

### Distribution and entry

Install devkit-docs and devkit-catalog, then select `uv run devkit add adaptive-dev` (`adaptive-dev:core`).
The skill and six registered agent contracts use existing projection mechanisms. No adaptive-development runtime or CLI is
added.

`uv run devkit config show` exposes `configuration.development.approach` and its source.
The entry requires `adaptive-dev`; invalid policy propagates `DEVELOPMENT_CONFIG_INVALID`, exit 2.
A valid SDD result produces a guidance-level stop with the shared `[development] approach = "adaptive-dev"` action,
not a new error code. Selection/invocation changes no approach. Read `get-context adaptive-dev` once and the docs
context/instructions before relevant document work.

`/adaptive-dev` keeps small questions inline and invokes no other bundle's entry. A retained research material is an
input it reads by its `MAT-<slug>` ID when the user supplies or the current context links it.

### Optional roles

| Role | Result | Source and Git boundary |
| --- | --- | --- |
| product-clarifier | Candidate users/problems, alternatives and missing questions | Read-only; no invented user decision |
| product-researcher | Evidence for one product decision, or an explicitly bounded experiment | Read-only by default; assigned scratch notes or prototype writes only |
| usage-reviewer | Expected versus observed representative usage | Read-only product source; assigned test-data interactions only |

Every product-support role leaves the index and HEAD unchanged and commits/publishes nothing. A result contains status
(`completed`, `needs_input` or `failed`), summary, source/artifact identity, observations with evidence/failure
conditions, recommendation or draft, assumptions and unverified areas. An experiment also returns actual changed
paths, commands and outcomes. The Host verifies boundaries and evidence before fold-back; direct communication
is optional host functionality and never changes authority. Adaptive product iteration has no SDD envelope requirement; an external SDD caller retains its own required records.

### Reusable execution agents and overlays

| Agent | Product and Git boundary |
| --- | --- |
| swarm-planner | Read-only sources, index and HEAD; descendants remain read-only |
| swarm-worker | Assigned source/test paths; commit only with explicit payload authority; no final integration/publication |
| swarm-verifier | Read-only product sources and Git; assigned ignored probe/test outputs may be written |

Archetypes declare emulated support on Codex and Claude Code, and unverified support on Antigravity. Projection
checks do not establish native invocation, path confinement, nested execution, performance or all-host support.
Execution settings remain subordinate to effective host policy; no host/model/approval override is granted.

Before delegation, resolve local architect, builder, qa-tester or reviewer overlays from the invoked skill's directory,
not the cwd or reference directory. Verify existence and pass the absolute path. Compatible external callers can
supply their own verified absolute role file without loading adaptive orchestration or another bundle's private assets.
Use the registered-role mechanism when available; label generic role-file emulation or direct fallback explicitly.

Assignments and returns identify goal/result, source/base/final SHA where committed, actual paths, permitted actions,
checks/commands/outcomes, stop condition, remaining depth/allowance, defects and unverified areas. Leads verify their
aggregate scope; the Host verifies combined and applicable landed-target results under the consuming project's
required checks. Product-support no-commit rules remain separate from expressly assigned worker commits.

### Evidence-scoring test support

Repository test support can score supplied combined-check and interrupted-writer evidence without invoking a model:
`python packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py <evidence.json>`. The input identifies the
scenario, source, availability and evidence kind; artifact paths are relative to the evidence file. Combined evidence
uses source-matched child and aggregate JSON reports. Recovery evidence uses a retained work file plus source-matched
ownership and recovery JSON records. The result contains observations and a limitation: the scorer does not
authenticate artifacts or execute an agent. Unavailable and incomplete evidence stay distinct; synthetic successful
fixtures report `fixture_pass`, not a behavioral pass. The scorer does not remove artifacts.

The evidence JSON uses `scenario` (`combined-check` or `interrupted-writer`), nonempty `source`, boolean `available`,
`evidence_kind` (`observed` or `synthetic`), and an `artifacts` object. For a combined check it also supplies boolean
`completion_claimed`, and `artifacts.child` and `artifacts.combined` name JSON files with matching `source` and an
`outcome` of `pass` or `fail`. For an interrupted writer, `artifacts.work` names the retained nonempty work file;
`artifacts.ownership` names JSON containing matching `source`, `owner`, and `work_artifact` equal to the work path;
`artifacts.recovery` names JSON with matching `source` and `owner` plus nonempty `next_action`.

For example, the input below refers to two JSON files whose contents are `{"source":"abc","outcome":"pass"}`:

```json
{"scenario":"combined-check","source":"abc","available":true,"evidence_kind":"synthetic",
 "completion_claimed":true,"artifacts":{"child":"child.json","combined":"combined.json"}}
```

This example returns `fixture_pass`. `pass` means sufficient supplied observed evidence; `fail` identifies a
child-pass/combined-fail claim; `inconclusive` means unsupported, inconsistent or incomplete evidence; `unavailable`
means execution was unavailable. The scorer cannot establish the authenticity of a supplied observation.

### Product notes and resume

Product notes reuse existing destinations and are written only when they help the next decision or describe
retained behavior. Native capability/use-case/decision/milestone semantics apply only when their subject warrants
them.

`.devkit/adaptive-dev.md` remains mutable project-owned Markdown, not managed/transient state or a parsed lifecycle.
Keep current goals, choices versus assumptions, source-specific checks, unresolved evidence and exact note links,
retained research material IDs, useful surviving alternatives/reopening conditions and the next action. Remove superseded experiments only when
they no longer inform work. A fresh context rechecks identities and applicability instead of replaying history.

## Integration and final verification

Adaptive development uses the same explicit-branch Git integration as SDD without task labels, claims or provider
selection. The Host performs independent branch checks and, after approved landing and cleanup, synchronizes the
landed dependencies and runs required final checks in fresh processes. No implicit Unit or verification ledger is
created. A final failure leaves delivery unfinished until target repair and recheck pass
(`CAP-INT-mcp-services`, `CAP-DLV-delivery-workflows`, `ADR-post-merge-verification`).
