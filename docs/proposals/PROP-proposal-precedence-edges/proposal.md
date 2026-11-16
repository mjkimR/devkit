---
id: PROP-proposal-precedence-edges
title: Ordering claims between proposals checked when made
summary: Has Backlog and the first Planning turn verify a draft's claims about other proposals' handoff order against base status and Development branches, so a stale ordering premise surfaces before it shapes the draft or its first decision.
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: harness/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/proposals/PROP-proposal-precedence-edges/
  excludes:
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/base/
    - packages/devkit-docs/
    - packages/devkit/
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-proposal-precedence-edges] Ordering claims between proposals checked when made

## 1. Background & Hypothesis

`FB-draft-precedence-claim-unenforced`: a draft proposal stated in prose that its handoff precedes the handoff of
two accepted proposals, and argued its change was cheap because neither had a spec yet. Nothing flagged the stale
premise: `depends_on` is declared only by the dependent, the accepted proposals carried no edge to the draft, and
`devkit spec proposal check` reported `editable=yes` with no notice.

Planning found that the premise was false before the draft existed: both dependents were handed off two to five
minutes before the draft was committed, and the base still showed them `accepted` because a handoff lives on
`dev-<slug>` until integration (`materials/observed-case-timeline.md`). No handoff-time edge could have fired.

Hypothesis: checking each proposal a draft names as following it, by base `status` and by local or fetched
`dev-<slug>` branches, when the claim is written and again at the first Planning turn, surfaces a stale ordering
premise before it shapes the draft or its first decision; an ordering still in the future goes to the user as a
sequencing decision.

## Source feedback

- `FB-draft-precedence-claim-unenforced`: the whole item (detection of a stale ordering premise between proposals).

## 2. Technical Spike Questions

- **Q1** (settled): Should a draft declare a prerequisite edge onto accepted proposals (for example a `precedes:`
  list) that `devkit spec proposal handoff` checks, or should the existing `depends_on` on the dependents stay the
  only edge? Answer: `depends_on` on the dependent stays the only edge; no new field, no edit of an accepted
  proposal and no handoff check (Planning decision 1).
- **Q2** (settled): Should Planning start or `devkit spec proposal check` report the current status of every proposal
  or spec the draft names as following it? Answer: yes as a guidance step at draft authoring and at the first
  Planning turn, reading base status and `dev-<slug>` branches; `proposal check` stays the editability guard
  (Planning decisions 2 to 4).

## 3. Proposed Design & Impact

### Planning decisions

1. **No new ordering edge; accepted proposals stay unedited** (by: host, from repository evidence). A `precedes:` field
   would reverse the successor-declared edge chosen in `ADR-roadmap-and-milestones-ledger` (the both-ways `after` edge
   was rejected) and needs a new reference field in `devkit-docs`. A reverse `depends_on` written onto an accepted
   proposal contradicts `ADR-proposal-acceptance` ("an accepted proposal is never edited") and rule 13 of
   `CAP-DLV-proposal-planning`. Neither would have caught the observed case, because both handoffs ran before the
   claim existed (`challenger-01.yaml` findings 1 and 2). An ordering a draft wants against an accepted proposal is a
   sequencing decision for the user, made when the draft is written; when the premise no longer holds, the existing
   routes apply (rewrite the draft, or return or close the accepted proposal through `CAP-DLV-delivery-workflows`).
2. **Check named proposals when the claim is written** (by: host). Backlog guidance (`references/backlog.md`,
   Requests and decomposition) adds one step: when a draft claims its handoff precedes, or its cost depends on the
   state of, another proposal or spec, check each named one before committing the draft: its `status` on the base and
   whether a local or fetched `dev-<slug>` exists (`git branch -a --list 'dev-<slug>' '*/dev-<slug>'`), within the
   existing fetch authorization and never fetching implicitly. A `dev-<slug>` branch or a `SPEC-<slug>` means the
   proposal was handed off: rewrite the premise. A still-accepted proposal with no `dev-` branch: ask the user to
   sequence the two before committing the draft, and state the decision in the draft's body.
3. **Recheck at the first Planning turn** (by: host). `references/planning.md`'s head-pinned recheck applies on the
   first turn too, not only after a Host refresh, and for each proposal the draft names as following it adds the
   same `dev-<slug>` check: a base or HEAD read alone shows a handed-off proposal as `accepted` until its Development
   integrates (`challenger-01.yaml` finding 3). A stale premise is updated before the first Planning decision.
4. **No CLI change** (by: host). `devkit spec proposal check` is the Backlog editability guard and refuses once
   Planning starts, so it cannot report at Planning start; ordering claims live in prose with no mechanical edge to
   read; the feedback is a non-recurring `workaround`. A handoff-time prerequisite notice would rarely fire (2 of 81
   handoffs) and repeats the pickup override of the direct unit prerequisite procedure
   (`challenger-01.yaml` findings 4 and 5). Planning records no PADR: the steps restate no lasting policy beyond the
   accepted ADRs above.

### Design, domain and operations impact

- **Design**: unaffected; no component, interface or structure changes (guidance text only).
- **Domain**: `DOMAIN-delivery-relationships` unaffected; prerequisite, membership and provenance semantics are
  unchanged and no edge is added.
- **Operations**: unaffected; no runbook or operational procedure reads proposal ordering.
- **Capability**: `CAP-HARN-agent-guidance` "Repository Backlog and next work" gains one statement owning the two
  checks (statement owner); the bundle references carry the procedure.

### Assets

- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`: decision 2.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`: decision 3.
- `docs/capabilities/harness/CAP-HARN-agent-guidance.md`: the owning statement.
- A bundle-text test under `packages/devkit-spec/tests/integration/bundles/spec/` (beside
  `test_unit_dependency_guidance.py`), local and cloud.

Before editing a bundle reference, run `uv run devkit get-context authoring` and apply `agent-asset-writing`; keep
the bundle within `test_bundle_budgets.py`.

### Non-Goals

- A `precedes:` field, a reverse `depends_on` on accepted proposals, or any change to `depends_on` semantics.
- A handoff, accept or `proposal check` notice or refusal; any change under `packages/devkit-spec/src/devkit_spec/features/`.
- Parsing ordering claims out of proposal prose.

### Expected acceptance evidence

- **AC-01**: `references/backlog.md` (local and cloud) states that a draft claiming to precede another proposal's
  handoff, or depending on its state, checks each named proposal's base `status` and local or fetched `dev-<slug>`
  branch before the draft is committed, rewrites a premise a handoff made stale, and asks the user to sequence an
  ordering against a still-accepted proposal. A bundle-text test asserts each clause.
- **AC-02**: `references/planning.md` applies the head-pinned recheck on the first Planning turn and adds the
  `dev-<slug>` check for proposals the draft names as following it. A bundle-text test asserts it.
- **AC-03**: `CAP-HARN-agent-guidance` states the two checks; `devkit rules check` passes on the changed documents.
- **AC-04**: no file under `packages/devkit-spec/src/devkit_spec/features/` or `packages/devkit-docs/` changes
  (`git diff --stat` of the Development range).

## 4. Lifecycle & Retirement Criteria

Retired when the accepted design is handed off and `FB-draft-precedence-claim-unenforced` is marked promoted to it.
