---
id: PLAN-partial-adr-supersession
spec: SPEC-partial-adr-supersession
---

# Technical Plan: `SPEC-partial-adr-supersession` Keep partially superseded ADRs accepted and searchable

## 1. Constitution & Invariant Review

None. The whole/partial rule is the "Decision changes" outcome of `ADR-immutable-decisions-editable-records`; this
Unit states it in the decision format and repairs status metadata and pointers, which that ADR lists as editorial
edits. `ADR-terminal-statuses-are-historical` keeps `superseded` terminal; nothing changes in the index, search or
rules. The docs bundle stays approach-neutral (`ADR-document-and-sdd-bundles`): the added text defines what the
`superseded` status and the in-part line mean, not a delivery lifecycle.

## 2. Architecture Overview & Impact

- **Document model contract** (`CAP-DOCS-document-model`): a "Decision supersession" subsection beside "Feedback
  lifecycle" states the statuses, the whole/partial rule and that a decision's `supersedes` and `superseded_by` are
  metadata the index does not read (section 3.3 rule 6 covers Unit anchors only). A sibling worker edits the renaming
  step of this capability; this Unit touches only the new subsection.
- **Docs bundle** (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`): a `Supersession` section in
  `instructions/decision-writing.md`; the decision template's status comment and body status line; the seeded
  `seed/docs/decisions/README.md` schema comments. The repository's own `docs/decisions/README.md` gets the same
  statement in its opening paragraph and schema comments.
- **Spec bundle** (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`): the `adr-compaction` playbook reads
  "Superseded in part by" lines as not in effect when it groups and writes a replacement.
- **PADR scaffold** (`features/proposals/usecases/scaffold.py`, `_padr`): one commented frontmatter line after
  `proposal:`. Handoff (`handoff.py`) already keeps the rest of the frontmatter, so an uncommented `supersedes` reaches
  the ADR unchanged; it drops the exact placeholder line when left unchanged (review-01), and never opens another ADR.
- **Delivery contract** (`CAP-DLV-proposal-planning` 4.4 and handoff step 4): the commented key and that handoff
  edits no superseded ADR; Development writes its status or in-part line.
- **Ledger** (`docs/decisions/`): the corrections in section 4.

No rule or code requires a superseded target to be `status: superseded`: `parse.py` skips `supersedes` on documents
other than Unit anchors, `RULE-document-reference` checks the `PROP-` kind only on those anchors, and the proposal
scaffold's `accepted` check (`_check_superseded`) concerns proposals. Nothing to adapt beyond a regression test.

## 3. Component & Interface Design

PADR frontmatter after this change (the commented line is new; the decision template carries the same optional key):

```yaml
---
id: PADR-<slug>
title: <title>
summary: <Y-statement>
proposal: PROP-<slug>
# supersedes: [ADR-<slug>]   # an ADR this decision replaces, wholly or in part; name the replaced clauses in Decision Outcome
status: draft
created_at: <date>
---
```

In-part line in an earlier ADR, directly below its H1 heading, one per partial superseder:

```markdown
Superseded in part by `ADR-<new>`: <the clauses it replaces, in its own words>.
```

## 4. Storage & State Management

Ledger classification. Criterion: an ADR is wholly replaced when its superseder replaces or restates every clause (it
says "as a whole" or carries the retained clauses over in its own text); it is partly replaced when the superseder
replaces named clauses and leaves the rest in the earlier ADR ("supersedes only", "remain in force", "preserve" or
"retained from the superseded decision").

| ADR | Now | Superseder | Finding | Change |
| --- | --- | --- | --- | --- |
| `ADR-local-and-pull-request-integration` | superseded | `ADR-host-cli-lifecycle-authority` | partial (its own pointer) | accepted, drop `superseded_by`, normalize pointer |
| `ADR-delivery-decision-boundaries` | superseded | `ADR-host-cli-lifecycle-authority` | partial (its own pointer) | accepted, drop `superseded_by`, normalize pointer |
| `ADR-viewer` | superseded | `ADR-viewer-working-tree` | partial: only the Git-ref reads change | accepted, drop `superseded_by`, body status, add line |
| `ADR-subagent-level-projection` | superseded | `ADR-five-subagent-levels` | partial: five "preserve[s]" five clauses | accepted, drop `superseded_by`, add line |
| `ADR-adr-compaction` | superseded | `ADR-immutable-decisions-editable-records` | whole: restates compaction, reverses the rest | none |
| `ADR-bounded-high-effort-review-loop` | superseded | `ADR-host-owned-review-loop-recovery` | whole ("as a whole", carried over) | none |
| `ADR-medium-review-delegation` | superseded | `ADR-bounded-high-effort-review-loop` | whole (medium rules restated, high replaced) | none |
| `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` | superseded | `ADR-apply-review-refactor-changes-in-parallel-checkouts` | whole (full restatement) | none |
| `ADR-dist-foundation-ownership` | superseded | `ADR-foundation-and-mcp-package-ownership` | whole ("as a whole", carried over) | none |
| `ADR-worktrees-branches-and-scope` | accepted + `superseded_by` | `ADR-host-owned-scope-observation` | partial ("replaces only") | drop `superseded_by`, add line |
| `ADR-host-cli-lifecycle-authority` | accepted | `ADR-reusable-lifecycle-resource-manager` | partial ("supersedes only") | add line |
| `ADR-orchestration-workers` | accepted | `ADR-subagent-level-projection`, `ADR-drop-the-base-checkout-equality-from-worker-validation`, `ADR-reusable-lifecycle-resource-manager` | partial | normalize two pointers, add line |
| `ADR-five-subagent-levels` | accepted | `ADR-lean-subagent-level`, `ADR-reusable-lifecycle-resource-manager` | partial ("supersedes only") | add two lines |
| `ADR-package-split-and-namespaces` | accepted | `ADR-single-release-version` | partial ("supersedes only") | add line |
| `ADR-roadmap-and-milestones` | accepted | `ADR-archive-terminal-milestones-in-roadmap` | partial ("partially supersedes only") | add line |
| `ADR-keep-incubation-guidance-opt-in-and-current-state-based` | accepted | `ADR-extend-incubation-with-optional-discovery-teams` | partial ("preserve") | add line |
| `ADR-extend-incubation-with-optional-discovery-teams` | accepted | `ADR-split-deep-research-bundle` | partial ("retained from") | add line |
| `ADR-keep-discovery-plans-distinct-from-delivery-commitments` | accepted | `ADR-retain-research-as-cited-materials` | partial ("retained from") | add line |
| `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` | accepted | `ADR-scope-snapshot-runs-to-diff-paths-including-deletions` | partial ("Supersedes: the follow-up section") | add line (review-01) |

After reconcile-check-01: the pointers in `ADR-immutable-decisions-editable-records` ("Partly replaced by") and
`ADR-viewer-working-tree` ("replaces this statement") take the "Superseded in part by" form, and every superseder an
in-part line names lists the earlier ADR in `supersedes` (`ADR-adaptive-dev-approach-name`,
`ADR-archive-terminal-milestones-in-roadmap`, `ADR-document-package`,
`ADR-drop-the-base-checkout-equality-from-worker-validation`, `ADR-milestone-merging`,
`ADR-scope-snapshot-runs-to-diff-paths-including-deletions`, `ADR-spec-intake-playbook-discovery`,
`ADR-viewer-planning-proposal-overlay`), so the `adr-compaction` closure reaches each pair. `ADR-moved-target-merge`
already names `ADR-local-and-pull-request-integration`.

ADRs that already carry a valid "Superseded in part by" or equivalent pointer at the affected statement keep it
(`ADR-spec-package-on-devkit`, `ADR-test-selection-and-ci`, `ADR-parse-memo-location-and-format`,
`ADR-parse-memo-failure-and-write-policy`, `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`,
`ADR-own-development-approach-policy-outside-sdd`, `ADR-immutable-decisions-editable-records`,
`ADR-viewer-working-tree`). `ADR-moved-target-merge` is out of scope.

## 5. Error Handling & Edge Cases

- An in-part line holds backticked IDs, so `RULE-document-reference` resolves them; every superseder named exists.
- A commented YAML line in the PADR frontmatter parses to nothing, so the scaffold's parsed frontmatter is unchanged.
- Restoring `accepted` returns an ADR to browsing and search; its references were already checked on every run (rule
  8), so no new reference violation can appear.

## 6. Verification & Test Plan

- AC-01: `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` asserts the supersession rule
  in `decision-writing` and the template; `just test devkit-spec bundles/spec`; `just test devkit-docs bundles/docs`.
- AC-02: a `RULE-document-reference` test (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`)
  with an ADR and a PADR naming an accepted ADR in `supersedes`, reporting nothing.
- AC-03: `test_proposal_scaffold.py` (`test_create_padr`) asserts the commented line and unchanged parsed frontmatter;
  `test_proposal_handoff.py` asserts that an uncommented `supersedes` reaches the ADR and the old ADR is unchanged.
- AC-04: `uv run devkit docs list decision --status superseded -n 0` lists five ADRs (baseline nine);
  `uv run devkit docs search "Local and Pull Request Integration"` lists `ADR-local-and-pull-request-integration`
  (baseline: absent); `uv run devkit rules check` clean.
- Lint and types: `just lint-check devkit-spec`, `just lint-check devkit-docs`, `just check devkit-spec`;
  `just test-affected` (with its `mode=full` fallback); `uv run devkit sync --check` after `uv run devkit sync`.
