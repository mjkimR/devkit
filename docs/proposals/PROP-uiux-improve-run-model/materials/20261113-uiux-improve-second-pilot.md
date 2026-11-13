---
id: MAT-uiux-improve-second-pilot
created_at: 2026-11-13
---

# [MAT-uiux-improve-second-pilot] app-uiux-improve run cost by route: attribution, second run and measurement plan

Evidence for `PROP-uiux-improve-run-model`. The first run is described in `MAT-uiux-improve-pilot`; this file adds
the commit attribution of that run, a second run in the same consumer, and a plan for measuring further runs. Paths,
commit hashes and identifiers of the consumer are masked.

## 1. First run: commits by cause

The branch carried 18 commits plus the merge. The attribution below follows a challenger review and the commit file
lists; a commit can have more than one cause.

| # | Commit content | Cause |
| --- | --- | --- |
| 1 | `spec.md`, `plan.md`, `tasks.md` authored | SDD structure |
| 2 | UX review round 1 envelope | optional round; tooling granularity |
| 3 | Round 1 folded into spec, plan and tasks | optional round, finding-driven (semantic defect) |
| 4 | Color system implemented, with tests | product |
| 5 | Polish of run controls, labels, brand, sync cue | product; partly scope creep (review finding) |
| 6 | Steering style file, UI README, spec/plan/tasks amendments | documentation; scope creep (build amendments) |
| 7 | Spec marked in progress | SDD structure (status only) |
| 8 | UX review round 2 envelope | optional round; tooling granularity |
| 9 | Code review envelope | tooling granularity |
| 10 | Test derives tint alphas; user authority for build amendments recorded | finding-driven (test gap); scope creep |
| 11 | Re-verification envelope | finding-driven; tooling granularity |
| 12 | Living Spec and UX documents updated, `reconcile.md` drafted | documentation; SDD structure |
| 13 | Reconcile check 1 envelope | tooling granularity |
| 14 | Reconcile findings fixed | finding-driven |
| 15 | Reconcile check 2 envelope | finding-driven; tooling granularity |
| 16 | Spec and reconcile marked completed | SDD structure (status only) |
| 17 | Feedback sweep envelope | tooling granularity |
| 18 | Final report envelope | tooling granularity |

Summary:

- Tooling granularity: 8 commits record one envelope each (2, 8, 9, 11, 13, 15, 17, 18). Commit-per-envelope is a
  tooling choice recorded as separate feedback (`FB-envelope-commit-companion-files` and related records); it is not
  evidence about the run model on its own.
- Optional rounds: UX review rounds 1 and 2 were optional. Round 1 also caught the run's semantic defect.
- Finding-driven: re-verification, reconcile fixes and the second reconcile check followed real findings.
- Scope creep: build-time amendments (a label preamble, an out-of-scope overflow fix pulled into a listed file,
  branding cleanup) were scope growth that the contract correctly surfaced; the added authority record followed.
- Coordinator error: a task focus turned into a non-goal (A4a), fixed in `PROP-uiux-improve-bundle-hygiene`.
- SDD structure alone: contract authoring (1), three lifecycle commits (7, 16, part of 12) and the mandatory check
  envelopes. This residue is the part a different run model would remove.
- Value: semantic defect (UX review), test gap (code review), stale UX documents kept in step (reconcile).

## 2. Second run: outside the workflow on explicit instruction

- Task: a control-density pass over the same SPA (shared native select, removal of ad-hoc control heights).
- Route: the user explicitly instructed the coordinator to proceed without the spec workflow and follow the skill's
  flow. No Unit and no envelopes. A plain branch from the main line; the coordinator asked for commit and merge
  authority once.
- Flow: coordinator inventory, then a brief and edit list (37 files, one new component directory and test selector
  updates) with base hashes, then one fresh Impeccable child (layout, polish, audit). The child loaded Impeccable by
  reading files from the plugin cache again, because the plugin was not enabled for this project. Acceptance
  compared `git status` with the edit list (41 files, all listed; package files at HEAD) and the coordinator compared
  screenshots. One question round settled three user decisions (keep a mobile control height, fix a leftover
  plugin-styled color now, commit and merge locally). Follow-up fixes, commit and a local no-fast-forward merge
  followed.
- Results: 43 ad-hoc selects in 29 files replaced by one shared component; 43 explicit control heights removed;
  project lint, type check and UI tests (406) passed; Impeccable detector 0 findings, audit 17/20.
- Incident: the shadcn-svelte CLI bumped an existing dependency while adding a component; the child reverted it, and
  the edit-list rule caught it. This is consumer tooling behavior, not a devkit or Impeccable issue; the user may
  report it to shadcn-svelte.
- Not done compared with the first run: no independent code review, no UX review, no Living Spec reconcile (the
  coordinator judged that no UX contract text changed; one steering line may follow).
- Cost: about three product commits and one merge; user stops: the initial instruction and one question round.
- Confounds: a narrower, less design-open task; a coordinator that had learned from the first run; no independent
  check to reveal what was missed.

## 3. Measurement plan

Record for each further run, through either route, and compare like tasks:

| Measure | How |
| --- | --- |
| Commits by cause | Classify each branch commit with the causes in section 1 |
| User stops | Count announcement or approval prompts, question rounds and unplanned interruptions |
| Defects caught, by check | Name the check (UX review, code review, project checks, before/after capture, reconcile) |
| Defects found after merge | Count issues traced to the run within a fixed window after integration |
| Documentation left stale | Count stale-document reports and whether each got a follow-up |
| Scope growth | Count mid-run scope changes and whether the user re-approved them |

Decide before the next runs what result would change the default, for example: the outside-workflow route keeps
defects found after merge at or below the workflow route's while cutting non-product commits.

## 4. Upstream reports

Upstream Impeccable behaviors from both runs are recorded as upstream feedback in devkit:
`FB-impeccable-autonomy-probe-in-subagent`, `FB-impeccable-context-target-no-visual-implementation` and
`FB-impeccable-audit-storage-write-missing`. The shadcn-svelte dependency bump (section 2) is not recorded in devkit.
