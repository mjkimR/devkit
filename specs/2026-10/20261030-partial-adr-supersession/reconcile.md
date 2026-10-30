---
reconcile_id: REC-partial-adr-supersession
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/decisions/README.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-delivery-decision-boundaries.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-viewer.md
    resolution: modified
  - file: docs/decisions/2026-10/20261025-subagent-level-projection.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-worktrees-branches-and-scope.md
    resolution: modified
  - file: docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-orchestration-workers.md
    resolution: modified
  - file: docs/decisions/2026-10/20261025-five-subagent-levels.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-package-split-and-namespaces.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-roadmap-and-milestones.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-keep-incubation-guidance-opt-in-and-current-state-based.md
    resolution: modified
  - file: docs/decisions/2026-10/20261029-extend-incubation-with-optional-discovery-teams.md
    resolution: modified
  - file: docs/decisions/2026-10/20261029-keep-discovery-plans-distinct-from-delivery-commitments.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-scope-only-explicit-working-tree-targets-in-the-evaluator.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-immutable-decisions-editable-records.md
    resolution: modified
  - file: docs/decisions/2026-10/20261024-viewer-working-tree.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-adaptive-dev-approach-name.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-archive-terminal-milestones-in-roadmap.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-document-package.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-drop-the-base-checkout-equality-from-worker-validation.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-milestone-merging.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-scope-snapshot-runs-to-diff-paths-including-deletions.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-spec-intake-playbook-discovery.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-viewer-planning-proposal-overlay.md
    resolution: modified
---

# Reconcile: `SPEC-partial-adr-supersession`

## Contract comparison

- `CAP-DOCS-document-model` gains "Decision supersession": `superseded` and `superseded_by` only for an ADR whose
  in-force decisions are all replaced; a partly replaced ADR stays `accepted`, carries no `superseded_by` and gains a
  "Superseded in part by" line; a decision's `supersedes`/`superseded_by` are unparsed metadata. It matches the
  unchanged index and search code (terminal status `superseded` only, `kinds.py`; `supersedes` skipped on documents
  other than Unit anchors, `parse.py`) and the new `RULE-document-reference` test. The renaming step a sibling worker
  edits is untouched.
- The docs bundle states the same rule in `decision-writing` (Supersession section, description updated), the
  decision template (status comment, an optional commented `supersedes` key and an HTML comment under the heading) and the seeded `docs/decisions/README.md`
  schema comments; `test_writing_guidance.py` asserts the guide and template. The repository's own
  `docs/decisions/README.md` opening paragraph and schema comments say the same. The `adr-compaction` playbook treats
  a clause named by an in-part line as not in effect, consistent with `ADR-immutable-decisions-editable-records`
  ("superseded parts are left out").
- `CAP-DLV-proposal-planning` 4.4 names the PADR's commented `# supersedes: [ADR-<slug>]` line and handoff step 4
  states that `supersedes` reaches the ADR unchanged, the unchanged placeholder line is dropped, and handoff edits no
  ADR it names. Scaffold and handoff tests verify all three (`_drop_supersedes_placeholder` in `handoff.py`).
- The spec constitution's sentence ("a changed decision is a new ADR with `supersedes`") holds for whole and partial
  replacements and is unchanged; no AGENTS.md change.
- No rule or code requires a superseded target to be `status: superseded`; nothing needed adapting.

## Decision ledger

Criterion: an ADR is wholly replaced when its superseder replaces or restates every clause; partly replaced when the
superseder replaces named clauses and leaves the rest in the earlier ADR ("supersedes only", "remain in force",
"preserve" or "retained from the superseded decision"). Every in-part line quotes or directly derives from the superseder's statement
of what it replaces or from its outcome (the `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` and
`ADR-keep-incubation-guidance-opt-in-and-current-state-based` lines are derived). No decision changed.

Changed:

- `ADR-local-and-pull-request-integration`: `superseded` to `accepted`, `superseded_by` dropped; its existing
  `ADR-host-cli-lifecycle-authority` pointer rewritten as "Superseded in part by". Its merge construction, readiness,
  policy binding and the other clauses that pointer names stay in force; `CAP-INT-mcp-services` keeps that merge
  construction as its current contract (see "Open: outside the write scope"). The `ADR-moved-target-merge` line is unchanged.
- `ADR-delivery-decision-boundaries`: `superseded` to `accepted`, `superseded_by` dropped; its pointer ("supersedes
  only ... native MCP lifecycle execution and confirmation clauses"; gates, `auto` authority and Host autonomy remain)
  rewritten as "Superseded in part by".
- `ADR-viewer`: `superseded` to `accepted`, `superseded_by` dropped, body status Accepted, in-part line added.
  `ADR-viewer-working-tree` replaces only the Git-object reads at a selected ref and keeps the server, packaging and
  proposal-review route ("Keep the Python and Svelte packaging", "The exact-generation proposal-review route remains
  unchanged").
- `ADR-subagent-level-projection`: `superseded` to `accepted`, `superseded_by` dropped, in-part line added.
  `ADR-five-subagent-levels` replaces its level names and the all-roles-inherit default and "preserve[s] ... from the
  superseded decision" distribution-time resolution, shared-only overrides, conflict rules, native variants and
  inheritance limitations.
- `ADR-worktrees-branches-and-scope`: `superseded_by` dropped (it was `accepted`), in-part line added;
  `ADR-host-owned-scope-observation` "replaces only that ADR's skill-maintained refresh decision".
- `ADR-host-cli-lifecycle-authority`: in-part line for `ADR-reusable-lifecycle-resource-manager` ("supersedes only
  Host-only lifecycle invocation clauses").
- `ADR-orchestration-workers`: in-part line for `ADR-reusable-lifecycle-resource-manager` (same clause); its existing
  pointers for `ADR-subagent-level-projection` ("This decision alone is superseded by") and
  `ADR-drop-the-base-checkout-equality-from-worker-validation` ("supersedes the base-checkout clauses below") rewritten
  as "Superseded in part by" with the same clauses.
- `ADR-five-subagent-levels`: in-part lines for `ADR-lean-subagent-level` ("supersedes only the closed five-preset
  registry and compact-only Flash mapping") and `ADR-reusable-lifecycle-resource-manager` (its scout-only
  source-preset and default-inheritance clause, for the `git-operator` manager).
- `ADR-package-split-and-namespaces`: in-part line for `ADR-single-release-version` ("supersedes only the
  independent-version clause").
- `ADR-roadmap-and-milestones`: in-part line for `ADR-archive-terminal-milestones-in-roadmap` ("partially supersedes
  only the root-only milestone storage convention"); the `ADR-milestone-merging` line is unchanged.
- `ADR-keep-incubation-guidance-opt-in-and-current-state-based`: in-part line for
  `ADR-extend-incubation-with-optional-discovery-teams`, which preserves its catalog ownership, installation,
  approach check, evidence and context clauses and extends its entry and role set.
- `ADR-extend-incubation-with-optional-discovery-teams`: in-part line for `ADR-split-deep-research-bundle`, which moves
  the research entry and three roles out of `incubation:core` (the new entry has no approach gate and writes no
  `.devkit/incubation.md`) and lists the clauses "Retained from the superseded decision".
- `ADR-keep-discovery-plans-distinct-from-delivery-commitments`: in-part line for
  `ADR-retain-research-as-cited-materials`, which replaces where research is retained and lists the clauses "Retained
  from the superseded decision".

- `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`: in-part line for
  `ADR-scope-snapshot-runs-to-diff-paths-including-deletions` ("Supersedes: the follow-up section"; its outcome scopes
  the snapshot runs the earlier ADR left unscoped). Found by review-01.

- Pointer wording (reconcile-check-01): `ADR-immutable-decisions-editable-records` ("Partly replaced by
  `ADR-spec-intake-playbook-discovery`") and `ADR-viewer-working-tree` ("`ADR-viewer-planning-proposal-overlay` replaces
  this statement") now use the "Superseded in part by" form with the same clauses.
- `supersedes` metadata (reconcile-check-01): each superseder an in-part line names now lists the earlier ADR, so the
  ledger follows the `CAP-DOCS-document-model` rule and the `adr-compaction` closure reaches every pair:
  `ADR-adaptive-dev-approach-name` (five ADRs), `ADR-archive-terminal-milestones-in-roadmap`, `ADR-document-package`
  (three ADRs), `ADR-drop-the-base-checkout-equality-from-worker-validation`, `ADR-milestone-merging`,
  `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`, `ADR-spec-intake-playbook-discovery` and
  `ADR-viewer-planning-proposal-overlay`. `ADR-subagent-level-projection` already names an alias of
  `ADR-orchestration-workers` (its effort-preset member).

Reviewed, unchanged:

- Stay `superseded` (wholly replaced): `ADR-adr-compaction` (`ADR-immutable-decisions-editable-records` reverses its
  append-only framing and its "later changes" clause and restates compaction, closure, authority and checks),
  `ADR-bounded-high-effort-review-loop` (`ADR-host-owned-review-loop-recovery` "replaces ... as a whole", other rules
  carried over), `ADR-medium-review-delegation` (`ADR-bounded-high-effort-review-loop` replaces its `high` clause and
  restates its `medium` and `low` rules), `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`
  (`ADR-apply-review-refactor-changes-in-parallel-checkouts` restates the whole outcome with one change),
  `ADR-dist-foundation-ownership` (`ADR-foundation-and-mcp-package-ownership` "replaces ... as a whole", rules carried
  over).
- Already carry a valid pointer: `ADR-spec-package-on-devkit`, `ADR-test-selection-and-ci`,
  `ADR-parse-memo-location-and-format`, `ADR-parse-memo-failure-and-write-policy`,
  `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`, `ADR-own-development-approach-policy-outside-sdd`,
  `ADR-immutable-decisions-editable-records`, `ADR-viewer-working-tree`.
- Not touched: `ADR-moved-target-merge` (excluded scope). `ADR-mcp-runtime-and-shared-artifacts` says it "replaces
  only the package split's whole-host MCP placement and its MCP server-version owner" without naming an ADR ID; in
  `ADR-package-split-and-namespaces` the whole-host move is only a considered option already marked superseded by its
  own member, and no server-version clause is stated, so no pointer was added rather than guessing a target.

## Open: outside the write scope

These Living Spec statements now contradict the ledger and need an edit outside this worker's write scope
(`docs/capabilities/integration/`, `docs/capabilities/viewer/`, `docs/architecture/`); they are the problem of
`worker-01.yaml`, and `reconcile.md` stays `pending` until they are reflected:

- `CAP-INT-mcp-services` (reconcile-check-01, P1): "`ADR-host-cli-lifecycle-authority` supersedes the former lifecycle
  MCP execution interface and `ADR-local-and-pull-request-integration`" reads as a whole replacement. Proposed text:
  "`ADR-host-cli-lifecycle-authority` supersedes the former lifecycle MCP execution interface and, in part, the
  lifecycle request, native confirmation and resume interface of `ADR-local-and-pull-request-integration`, which
  remains authoritative for the merge construction and route guards below, this capability's current contract." The
  `ADR-moved-target-merge` sibling may edit the same paragraph.
- `ARCH-05-1-containers` and `CAP-VIEW-repository-viewer` (P3): "`ADR-viewer` as superseded by
  `ADR-viewer-working-tree`" should read "as superseded in part by", since `ADR-viewer` is `accepted` again.

## Entrypoints

`devkit spec entrypoints derive` proposed only bundle text, tests and the sync receipt for both capabilities; none is a
reading doorway. `CAP-DLV-proposal-planning` already declares `scaffold.py`, and `CAP-DOCS-document-model` already
declares the docs bundle's `bundle.toml`, so no entrypoint changed.

## Verification

- Review: `review-01.yaml` (medium, independent `code-reviewer`) found 1 P2 and 4 P3; the implementer fixed and
  self-verified all of them in 1a2905aa (`reverify-01.yaml`).

- Baseline at 257b5d98 (head before the change): `devkit docs search "Local and Pull Request Integration"` did not
  list `ADR-local-and-pull-request-integration`; `devkit docs list decision --status superseded -n 0` listed nine.
  After: the ADR is the first hit (`status=accepted`), and the superseded list holds five.
- `just test-affected` (mode=partial) after the review-01 fixes: 2081 passed. `just test devkit-spec bundles/spec` 700,
  `just test devkit-docs bundles/docs` 198, `just test devkit-spec features/proposals` 379 passed. Lint and Pyright on
  devkit-spec and devkit-docs clean; `devkit rules check` clean.
- The initial `devkit sync --check` passed (exit 0). `devkit sync` wrote `.devkit/installation.json` as the only
  tracked output (Task 1, `(sync output)`); managed copies were regenerated, never edited.

## Source feedback

- `FB-partial-supersession-hides-in-force-clauses`: resolved. The decision format now states the whole/partial rule,
  the PADR scaffold offers `supersedes`, and `ADR-local-and-pull-request-integration` and the other partly replaced
  ADRs are `accepted` and searchable. Its suggested structured field was not adopted by the agreed scope
  (`SPEC-partial-adr-supersession` Non-Goal 1); nothing in the agreed scope is deferred.
