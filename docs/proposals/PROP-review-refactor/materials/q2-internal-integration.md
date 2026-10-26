# Q2 and integration evidence (scout return, internal)

Evidence base: worktree at plan-review-refactor, base 3a820609. Citations are `path:line`.

## Shared bounding pattern

The two existing maintenance playbooks bound a run the same way:

- Intake records repository identity, HEAD and dirty paths, scope, permitted roots, prior reports and the report
  destination, and missing scope is clarified before inspection
  (drift-reconciliation.md:12-17; CAP-DLV-drift-reconciliation.md:31-33).
- Candidates are listed, and a large area is split into explicit batches.
- Coverage records what was reviewed, what was excluded and why, and the gaps. A run with zero findings still names
  its coverage.
- The user decides all findings in one round, and unanswered findings stay pending.
- Evidence is revalidated when HEAD or dirty paths move, and completion is claimed only for the batch.
- weekly-report adds a unique run ID, an exclusively created report file, and linking to open feedback and
  proposals instead of duplicating them (weekly-report.md:21-25,49-52).

## What differs for review-refactor

1. There is no second ledger to compare against. Findings are criteria-based, cite a location and a maintenance
   cost, and separate an evidenced problem from preference. drift-reconciliation's `deterministic` /
   `semantic-assessment` split is the closest precedent.
2. The run changes source by design. drift-reconciliation's "track structural cleanup separately"
   (drift-reconciliation.md:52-53) cannot be copied, because structural cleanup is this playbook's main output.
3. Findings and implemented changes are kept as separate ledgers. Each change carries its behavior-preservation
   evidence and its resulting commit.
4. Dispositions differ from drift-reconciliation's: refactor or delete with behavior preserved, a contract-changing
   follow-up, defer, or keep (waive).
5. A bundle asset may not cite authoring-repository IDs (.devkit/managed/spec/AGENTS.md:11;
   agent-asset-writing.md:49-53). The playbook therefore states the rule-growth criterion itself instead of naming
   `CAP-GOV-rule-authoring`.

## Packaging

- `all` is implicit and reserved (CAP-DIST-manifest-spec.md:143-148), so review-refactor joins it automatically.
- `devkit add` records the preset name. Projects that already select `maintenance:upkeep` would receive
  review-refactor on their next sync if it joins `upkeep` (bundle.toml:11-12; CAP-DIST-content-packages.md:193-195).
- No version bump is needed. All packages share the root VERSION (ARCH-07-deployment.md:52-56), and precedent
  commits 03382f09 and e07b6cd7 changed no version field.
- Tests: packages/devkit-catalog/tests/integration/bundles/test_bundles.py:88-121,124-128 hard-codes the
  maintenance preset and asset sets.

## Files Development touches

- New: playbooks/review-refactor.md, CAP-DLV-<slug>.md, docs/usecases/governance/UC-<slug>.md.
- Edited: bundle.toml, test_bundles.py, packages/devkit-catalog/README.md (:10, :53-61),
  guides/install/bundle-recommendations.md:33, and CAP-DIST-content-packages.md:190-202.
- Optional: CAP-DIST-context-and-playbooks.md:13 (its `usecases:` list).
- Not touched: pyproject.toml, smoke.sh, VERSION, MS-maintenance-operations.

The current `boundaries.owns` misses tests, README, guides, use cases and CAP-DIST.
PROP-maintenance-history declares identical owns and edits the same files, so the two need sequencing.

## Overlap

No existing asset runs a repository-wide review-and-refactor pass:

- sdd-overall-refactor executes work but has no discovery criteria (sdd-overall-refactor.md:99-119).
- spec-review and code-reviewer review a single diff.
- feedback-hygiene is a destination for follow-ups.
- agent-asset-writing ("cut every line that does not change its next action") supplies the guidance criteria
  (agent-asset-writing.md:8-9,46-47).
- cli-tool and devkit-dev rules provide deterministic structure evidence where installed.
- drift-reconciliation boundary: a mismatch against an agreed contract routes to drift-reconciliation; a
  maintenance cost in consistent code belongs to review-refactor.

## Routing (classification.md:7-10,13-14)

- A behavior-free change across several areas is `overall-refactor`.
- A refactor inside one feature or module is `feature` at `session` depth, or at `spec` depth when the Living Spec
  must change.
- Contract-changing removals become follow-ups.
- The playbook names only "the repository's development workflow", with devkit-spec specifics stated conditionally.

## Interactions with other proposals and ADRs

- **PROP-spec-playbook-discovery**: avoid naming `devkit-playbook` or "explicit only". Neutral form: "Run only when
  invoked for the current task, by name or by exact `devkit playbook get maintenance/review-refactor`; selection
  never executes it."
- **PROP-maintenance-history**: avoid "no history backend". Record forward-compatible fields: run ID, intake SHA,
  dirty state, scope, outcome, and the resulting commit of each change.
- **ADR-external-playbook-execution** (:39-43,52-56): an external invocation grants no gated approval, so an
  external run stops at the decision round.
- **ADR-playbook-aliases-as-identifiers**: no aliases are needed; the description carries the search phrases.

## Q2 options

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| A. One surface per run inside user-named roots | drift-reconciliation.md:14-16 | Low, but three runs for a full pass | Misses cross-surface findings, such as CLI help against docstrings |
| B. All surfaces with a top-N candidate cap | weekly-report.md:51-52 | Medium | Arbitrary cap; ranking across surfaces mixes incomparable criteria; large mixed diffs |
| C. User-selected scope at intake, split into batches, one decision round per batch | drift-reconciliation pattern | Low | Batch splitting is agent judgment |
| D. Diff-driven, since the last run or a named ref | weekly-report.md:14-16 | Depends on history | Misses accumulated debt; coupled to PROP-maintenance-history |

The scout recommends C, with one surface as the default batch unit and cross-surface findings citing both sides.
This should change if most valuable findings turn out to span surfaces: then allow multi-surface batches with a cap
on implemented changes.
