---
id: CAP-DLV-proposal-planning
aliases:
  - CAP-DLV-proposal-incubation
title: Proposal Planning and Handoff
summary: "Proposal Planning defines bundle layout, eligibility, approval, retirement and handoff policy. Detailed lifecycle execution and command interfaces belong to CAP-DLV-proposal-lifecycle."
area: delivery
status: active
created_at: 2026-10-13
usecases:
  - UC-plan-and-hand-off-a-proposal
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/SKILL.md.jinja
  - packages/devkit-spec/src/devkit_spec/features/policy/cli/commands.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py
---

# [CAP-DLV-proposal-planning] Proposal Planning and Handoff

## 1. Summary

Proposal Planning settles an idea (a feature, a technical spike, an architectural change) before it becomes a feature
spec: `proposal`-depth work, whose direction must be decided first, shapes it in a proposal bundle bound to workflow
`sdd-proposal`. `devkit_spec.features.proposals`
implements the lifecycle and `devkit spec proposal new|padr|accept|handoff|prune|check` exposes it. `accept` is the
one writer of an acceptance, after Planning or directly for an eligible draft in Backlog
(`ADR-proposal-acceptance`). The handoff is a cross-layout
move devkit's own `devkit workflow handoff` cannot make: it creates the spec bundle (`CAP-DLV-spec-bundles`), carries
the proposal body, promotes preliminary decisions, moves materials, rewrites what pointed into the proposal and
removes it.

## 2. Scope & Boundary

- **In-Scope**: proposal bundle layout and frontmatter, slug rules, Planning eligibility, acceptance authority,
  handoff preservation policy and retirement/feedback policy.
- **Out-of-Scope**:
  - Detailed lifecycle command, write, output, library and recovery interfaces: `CAP-DLV-proposal-lifecycle`.
  - The stages and gates of `sdd-proposal` and of the workflow the spec follows: `CAP-DLV-delivery-workflows`.
  - Planning's question rounds, acceptance and rejection procedure and the Backlog decomposition: the `spec` skills
    (`CAP-HARN-agent-guidance`).
  - The spec bundle skeleton and binding rules shared with `devkit spec new`: `CAP-DLV-spec-bundles`.
  - Registering the new bundle's work scope: `CAP-COLL-work-scope-registry`.
  - Format and reference rules over proposal files: `CAP-GOV-spec-rules`.
- **Non-Goals**:
  - **Scope Excluded**: inferring approval. Neither `accept` nor handoff derives the user's choice from context;
    `accept` requires explicit user acceptance or owning `plan-accept=auto` policy and creates no task-intent approval record.
  - **Scope Excluded**: moving into a worktree. Handoff runs in the workspace it is given; task worktrees are
    devkit's `devkit worktree`.
  - **Scope Excluded**: archives. Rejected and handed-off proposals are deleted; Git history keeps them.

## 3. Business Rules & Policies

1. **A proposal and a spec never share a slug**: a handed-off `PROP-<slug>` maps to exactly one `SPEC-<slug>`.
   `new` and `handoff` MUST refuse a slug whose `SPEC-<slug>` exists, declared or as an alias
   (`SPEC_PROPOSAL_SLUG_CONFLICT`); a document that cannot be indexed never blocks them.
2. **Approval is explicit and recorded**: handoff MUST require `status: accepted`, which `accept` writes once the
   user gave `plan-accept` or owning policy delegated it. Anything else is `SPEC_PROPOSAL_NOT_APPROVED` (`INTERACTION`: stop and ask the user; its
   `[FIX]` names `devkit spec proposal accept`). A bundle bound to `sdd-proposal` MUST also have its effective accepted
   `gate:plan-accept` record (the rule of rule 12 that carries it); without it the handoff refuses before writing
   (`SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED`, `INTERACTION`: never record an acceptance unasked; without a `worker`
   envelope the user's acceptance is repaired with `accept --direct` on the base, with one the user decides on
   reverting the Planning merge). A single-file or unbound proposal, which carries no gate record, and one bound to
   another workflow keep the status-only rule. A proposal marked `needs_decompose: true` is split in Backlog, never
   handed off (`SPEC_PROPOSAL_NEEDS_DECOMPOSE`), and one proposal hands off to exactly one spec.
3. **The follow-up workflow comes from `task_kind`; effort hints stay on the proposal**: `workflow` in `proposal.md` is devkit's
   binding of the proposal unit itself; `task_kind` (`feature` or `bugfix`, confirmed at `plan-accept`) selects the follow-up workflow `sdd-spec-<task_kind>` (any other value is `SPEC_PROPOSAL_INVALID`), while `planning_effort` and `dev_effort` (`low` | `medium` | `high`, scaffolded default `medium`) are non-authoritative activity-effort hints on `proposal.md`. `planning_effort` guides Planning and `dev_effort` is refined before `plan-accept` to guide Development (`[HANDOFF]` and `HandoffResult.dev_effort` expose it). After handoff the bound workflow carries the
   `task-kind` and `spec.md` has neither a `kind` field (`ADR-delivery-classification`) nor `planning_effort`/`dev_effort` fields (confirmed run effort is recorded on `worker-NN.yaml` envelopes).
4. **Validate everything before writing**: handoff checks the slug, the proposal file and its frontmatter, the
   approval, `namespace` (`global` or registered, else `SPEC_PROPOSAL_INVALID`), `summary` (a string, else
   `SPEC_PROPOSAL_INVALID`), `planning_effort` and `dev_effort` (`low` | `medium` | `high` when present, else `SPEC_PROPOSAL_INVALID`), the slug conflict, the workflow binding and every path it would create before its first
   write. A path that already exists (except the dated materials directory, which is merged into: `CAP-DLV-proposal-lifecycle` §4.1, step 5), a
   merge conflict with that directory, two PADRs that would become the same ADR, a graduating `ADR-<slug>` or
   `SPEC-<slug>` or a translated alias (`CAP-DLV-proposal-lifecycle` §4.1, steps 1 and 4) that equals an existing document ID or alias or another
   ID or translated alias graduating in the same handoff, a carried bundle file whose path under the materials directory a file or symbolic link of `materials/`
   takes too (or lies below; a `materials/` that is itself a symbolic link takes every such path), or a path it would
   create (the spec bundle, an ADR, the materials directory, a carried file) whose directory resolves outside the
   workspace is `SPEC_PROPOSAL_TARGET_EXISTS`; a proposal alias whose `SPEC-` translation has a date-based form
   (`PROP-<YYYYMMDD>-<x>`) is `SPEC_PROPOSAL_INVALID`; a legacy proposal or PADR slug whose first segment has no letter is
   `SPEC_PROPOSAL_SLUG_INVALID`.
5. **Roll back a failed write**: any failure while writing the spec bundle, the blueprint, the ADRs or moving the
   materials and carried files removes what was written, restores the text of every ADR it gave a pointer
   (`CAP-DLV-proposal-lifecycle` §4.1, step 4), moves them back and keeps the proposal, so the handoff can be rerun. The roll-back MUST NOT remove a directory that still holds something it could not move back, and MUST
   NOT move, remove or record a path that existed before the handoff: no pre-existing file or directory of a merged
   materials directory is recorded as written or moved, on one file system or across file systems. An advisory
   error (such as `FRONTMATTER_INVALID` binding `spec.md`) is reported with its own code after a complete roll-back,
   any other failure, and any incomplete roll-back, as `SPEC_PROPOSAL_HANDOFF_FAILED`. Across file systems the materials and carried files are copied
   and their sources removed only after every write succeeded, so a partial copy is removed like any other written
   file.
6. **Promoted decisions are accepted**: a PADR promoted to an ADR is accepted by definition.
7. **Rewriting never fails a handoff**: what cannot be mapped stays as it was and is reported
   (`SPEC_PROPOSAL_LINK_UNRESOLVED`); rewritten ID references are reported for rereading
   (`SPEC_PROPOSAL_REFS_REWRITTEN`), because whether a sentence named the proposal as its origin or as the work to do
   cannot be decided mechanically.
8. **Removal last**: the proposal is removed after every write and rewrite; if it cannot be removed the handoff still
   succeeded and `SPEC_PROPOSAL_CLEANUP_FAILED` names what to delete. Nothing else in the bundle is lost with it:
   files outside `proposal.md`, `target-docs.md`, the promoted `PADR-*.md` and `materials/` are carried to the
   materials directory first (`CAP-DLV-proposal-lifecycle` §4.1, step 5), except open feedback, which enters the spec's feedback directory.
   Operating-system junk and the unit's workflow records (rule 12) are excluded.
9. **Rejection changes the status only**: the party that received the user's rejection sets `status: rejected`
   with the user's decision and its reason in the commit message (kept through a squash), rewritten as one English
   decision sentence and never as a conversation quote (the records rule of the spec constitution), and merges the
   Planning branch; no worker runs. A later hygiene pass writes a rejection ADR outside the proposal directory,
   restating that decision and reason, referencing the proposal and the rejection commit, preserves open feedback,
   and deletes the proposal in the same commit; no `archive/`
   directory is kept. Feedback remains with the rejected proposal until that cleanup; no new rejection sweep runs. A `rejected`
   proposal is never resumed, accepted or handed off, and the tools hold to it: its `plan-accept` is never answered,
   the attach check refuses it on `plan-` and `dev-` branches, and a
   whole-workspace `devkit rules check -p hygiene` warns about each rejected proposal still in the base
   (`SPEC_PROPOSAL_REJECTED_PENDING`, the `devkit.hygiene` extension) until its cleanup is done. Open questions of
   the last Planning run are closed with `choice: null` answers giving the rejection as the decision (01 §6.2), so
   they do not hold the merge of the Planning branch.
10. **Discovery is dynamic**: active proposals are listed with `devkit docs list proposal`, never through catalog
    tables maintained in README files. A `draft` whose `plan-<slug>` exists, locally or fetched from a remote, is
    listed as `reviewing` with its `planning_branch` through devkit-spec's status overlay
    (`CAP-DOCS-document-lookup` section 3.6): Planning is running there (01 §5.1). Only the display changes;
    the base's `status` is never written for it, and a branch made elsewhere shows once it is fetched.
11. **Hand off on the slug's Development branch**: at either `[tool.spec] worktree` level, a handoff in a checkout,
    linked or base, whose branch is not `dev-<slug>` (a detached HEAD included) MUST be refused before anything is
    read or written (`SPEC_PROPOSAL_WRONG_WORKTREE`), so the spec bundle never lands on another task's branch and the
    accepted proposal is never deleted from the base itself. A workspace outside Git is not checked.
12. **Workflow records stay behind; acceptance carries by name**: proposal workflow decisions and envelopes,
    including historical intent decisions, MUST be dropped with the retired proposal and listed; Git history keeps
    them. The effective accepted `gate:plan-accept` record MUST be carried to the bound spec with its original `by`
    and `PROP-<slug>: <note>` provenance (`PROP-<slug>` when no note exists). It retains the proposal stage, satisfies no spec stage and serves only
    the acceptance audit trail. Returns and cancellations retain their existing voiding semantics. An unbound spec
    records nothing. A recording failure returns `SPEC_PROPOSAL_GATE_NOT_CARRIED` without undoing the handoff;
    restore the acceptance audit record from history after resolving the cause. No intent decision is carried.
13. **Backlog changes only a draft not in Planning**: Backlog edits, splits and deletes proposals by hand, so before
    each such change the agent MUST run `devkit spec proposal check <slug>`, which refuses
    (`SPEC_PROPOSAL_IN_PLANNING`) while `plan-<slug>` exists locally or as a fetched remote branch (Planning changes the
    proposal on that branch only), and for a proposal that is no longer `draft` (01 §5.1). Fetch first to see a
    branch made elsewhere. The list display of rule 10 is not the check: Planning may start right after a listing.
    `padr` applies the branch half of the guard itself: while `plan-<slug>` exists it writes a PADR only from the
    checkout of that branch (`SPEC_PROPOSAL_IN_PLANNING` elsewhere). Beside its edits Backlog may accept an eligible
    draft directly (rule 14), the one status change it makes, and, on the user's explicit decision at pickup, delete a
    draft without PADRs to do it as a `session` task (`ADR-delivery-classification`), preserving
    its open feedback (3.1); both commit only on the base checkout.
    A rough `size: XL` draft stays valid in Backlog, but it is decomposed before Planning. One predicate decides:
    `size` absent or exactly `S`, `M` or `L` passes; any other value (`XL`, `xl`, a typo) fails, and every refusal
    names the allowed values. The `sdd-proposal` `intent-proposal` exit `frontmatter(proposal.md size S|M|L|)` stays
    unmet (`detail="size=XL"`, exit `0`); no intent approval request exists; `accept --direct` blocks (rule 14); a
    `plan-` attach of a proposal not `accepted` is refused (`WORKTREE_ATTACH_REFUSED`), never a `dev-` attach or the
    readiness of an accepted proposal; a Planning run returns a failing proposal as for decomposition. Agents read
    the unmet check as "decompose first" and never edit the size to pass it. The exits, applied on the user's
    decision: split (`new --decomposed-from`, keeping the parent's `milestone`) or promote (a new milestone holding
    the children, for three or more children or a long-running theme). Backlog MAY delegate a decomposition to the
    read-only `decomposer` role (`CAP-DLV-delivery-roles` §4.1), only for a merged `needs_decompose` return, the
    user's request or an `XL` draft; the Host verifies its return and applies the split with these commands, and
    the parent's open feedback still takes the retirement move (3.1), never a child.
    For decomposition discovered in Planning, its executor commits `draft` plus `needs_decompose: true`, retained
    materials and answers closing pending questions. The Host integrates that return and removes local and fetched
    Planning branch blockers under existing merge, cleanup and network authority, then reruns the Backlog check on
    the base before creating children. Changing status alone is insufficient. The decomposition refusal retains
    `SPEC_PROPOSAL_IN_PLANNING` and directs the caller to this Host-managed return, never to retry on the plan branch.
14. **One writer of an acceptance**: `accept` records the user's acceptance in one step, after the user's explicit
    acceptance (`--by user`) or validated owning policy delegation (`--by policy`). Its form follows from the
    status: `planning` for a proposal in review on its `plan-<slug>` (another branch is
    `SPEC_PROPOSAL_WRONG_WORKTREE`), `direct` with `--direct` for an eligible draft, `repair` with `--direct` for an
    `accepted` proposal without an effective `gate:plan-accept`; every other combination, a `rejected`, single-file or
    unbound proposal included, is `SPEC_PROPOSAL_ACCEPT_REFUSED`. A direct acceptance and a repair MUST hold every
    condition of `ADR-proposal-acceptance` the tool checks, all reported at once
    (`SPEC_PROPOSAL_NOT_ELIGIBLE`, one `blocking:` detail each): no
    `needs_decompose: true`, a `size` absent or `S`, `M` or `L` (else `size: <value> (decompose first: ...)`), no `supersedes`, no local or fetched `plan-<slug>`, `task_kind` `feature` or `bugfix`
    (absent: `feature`), no envelope hold, and the base checkout: the main worktree on a branch that is not `plan-*`
    or `dev-*` and, when `origin/HEAD` resolves, is its target (outside Git not checked). A repair also refuses a
    proposal with a `worker` envelope (Planning ran). `--note` (required with `--direct`) is the eligibility reason;
    the record's note becomes `direct acceptance, Planning skipped: <reason>; task_kind <kind> confirmed`. The
    command writes `status: accepted` (not for a repair; only the value changes) and records `gate:plan-accept`
    through devkit's `record_answer`, so the workflow decides whether `collect-feedback` passed, is switched off or is
    skipped by policy; when the gate does not open it restores `proposal.md` byte-for-byte and reports the unmet
    checks and hold reasons (`SPEC_PROPOSAL_GATE_NOT_OPEN`). `--check` runs every eligibility check and writes nothing; no intent prerequisite or pending-intent condition exists. Without `--mode` it never commits, merges or hands off, and Backlog commits a direct
    acceptance on the base; with `--mode` it composes the commit, the Planning merge and an optional handoff
    (Host-authorized proposal lifecycle CLI, below).

15. **Planning review before acceptance**: when a bound proposal in Planning reaches `plan-accept`, the agent reviews the proposal, PADRs and envelopes directly for the final committed `plan-<slug>` source before presenting acceptance. Acceptance operates on the committed proposal directly and does not require a shared artifact report. `devkit spec proposal report <slug> [--source-sha <sha>]` can be run to inspect a summary briefing. Acceptance records `status: accepted` and `gate:plan-accept` on the committed proposal.

### 3.1 Planning feedback retirement

Planning writes direct `feedback/<name>.md` files with `FB-<name>` and existing feedback metadata.
Handoff preflight requires readable frontmatter, a path-derived ID, nonblank title, a known status and an undated
kebab-case name. Missing/unknown status, unreadable/malformed files, nested directories and symbolic-link feedback
sources are refused with `SPEC_PROPOSAL_INVALID` before writes. Non-Markdown sidecars and README keep generic
preservation. Unsafe/conflicting destinations use `SPEC_PROPOSAL_TARGET_EXISTS`.

Only `open` feedback enters the new spec's `feedback/`; `promoted`, `resolved`, `dismissed` and
`forwarded` files follow the materials path. IDs, statuses and observation dates stay unchanged. Feedback uses
the existing preflight, move, cross-filesystem rollback and exact/source relocation maps, never generic carry a second
time. Link/ID rewrites retain the best-effort notice contract of rule 7.

A proposal receiving feedback records full source FB IDs and its received scope in a `Source feedback` body
section. Handoff carries those references into the spec (feature and bugfix); drafting retains them. Promotion routes
work and closes the feedback without claiming implementation success. Promoted and other terminal sources require
no completion edits or re-verification; their references remain traceability. Handoff never resolves open feedback.
Only direct fixes of explicit open sources are checked at completion under `ADR-feedback-lifecycle-ledger`.

Without handoff, rejection/decomposition return keeps feedback in place until authorized Host deletion; a draft
deleted for a session reclassification (rule 13) preserves its open feedback the same way, in its deletion commit.
Before any such deletion, the Host moves open files once to `specs/<current-month>/feedback/<today>-<name>.md` in
the same commit, preserving observation dates; settled records remain in Git. Inspect all source/destination paths
and IDs.
Keep the source on invalid input, collision, failed move or unresolved live dependency. Update relative links;
historical references to retired proposal/PADR/settled-feedback IDs use existing strikethrough syntax plus retrievable
Git revision/path context. Current document-reference/link validation must pass before committing deletion.
Do not copy observations into every decomposed child or automatically settle them. The `spec` skill's
`references/feedback-retirement.md` defines the Host procedure; no cleanup command is added.

## 4. Interfaces & Data Contracts

### 4.1 Bundle Layout

```text
docs/proposals/PROP-<slug>/
├── proposal.md       # required: background, hypothesis, spike questions, design; the workflow anchor
├── target-docs.md    # optional (--with-target-docs): blueprint of the Living Spec changes once accepted
├── decisions/        # preliminary decision records, PADR-<slug>.md; devkit's gate records <NN>-<request>.yaml
├── envelopes/        # devkit envelopes of the proposal unit (a delegated spike), when any
├── feedback/         # direct feedback files; open files follow the spec at handoff
└── materials/        # research, benchmarks, surveys
```

`new` writes only the files (`proposal.md`, and `target-docs.md` with `--with-target-docs`): Git tracks no empty
directory, so a `plan-<slug>` worktree would not hold one. Each directory is created by the command that first writes
into it: `decisions/` by `padr` or devkit's first gate record, `envelopes/` by the first envelope, `feedback/` by the
first feedback file and `materials/` by its first file (`SPEC-proposal-scaffold-and-handoff-pointers`).

A single-file proposal `docs/proposals/PROP-<slug>.md` can be handed off too; it has no PADRs, materials or
blueprint, and its body is not carried (the spec gets the plain skeleton). `target-docs.md` is recommended for
`size: M` or `L` or when Living Spec structural changes are expected: `proposal.md` says why, `target-docs.md`
what `docs/` will look like.

Markdown under `materials/` follows the material convention (file `<YYYYMMDD>-<slug>.md`, `id: MAT-<slug>`,
`created_at`, H1 `# [MAT-<slug>] <title>`); `RULE-spec-format` skips `materials/` directories, so the frontmatter is
recommended, not checked. Non-Markdown files need no metadata. After handoff the files live under `docs/materials/`.

### 4.2 Slugs

A slug is normalized: a leading `PROP-` and a trailing `.md` are dropped, every run of characters other than letters,
digits, `_` and `-` becomes `-`, outer dashes are trimmed, and the result is lower-cased (`"PROP-Fast Engine"` is
`fast-engine`). A slug, or a PADR title, with no letter or digit left is `SPEC_PROPOSAL_SLUG_INVALID`. The slug of a
new proposal or PADR also needs a letter in its first `-` segment (`2024-budget` reads as the retired number-based ID
`2024`; `RULE-id-convention`): `new` and `padr` refuse one with `SPEC_PROPOSAL_SLUG_INVALID`, and `handoff` refuses a
legacy proposal or PADR whose slug starts that way, before writing anything, with a `[FIX]` to rename it.

### 4.3 `proposal.md` Frontmatter

| Key | Meaning |
| --- | --- |
| `id` | `PROP-<slug>`. |
| `title` | `--title` (default: the slug). |
| `summary` | One or two English sentences (`--summary`); carried to `spec.md`. Without the option, `new` writes the commented placeholder `# summary: <one or two English sentences: what this proposal changes and why>`, which the agent replaces with the field before committing. |
| `status` | `draft` (scaffolded), `reviewing`, `accepted`, `rejected`. |
| `created_at` | Scaffold date. |
| `target_area` | `--target-area` (default `capabilities/<area>/`, a trailing `/` added): the capability area on graduation. It and every `boundaries.owns` entry name an existing repository path, docs-root path or capability area, a path the Development will create by its nearest existing parent directory, and a path a `depends_on` prerequisite will create or move by its current path until that prerequisite lands, the expected path then going into Development's `_Boundary:` entries; `RULE-proposal-boundaries` warns on the rest and on the placeholder, and the Planning executor clears its reports before the `plan-accept` request (`ADR-proposal-acceptance`). |
| `namespace` | Optional (`--namespace`): `global` or a registered namespace (`CAP-DOCS-namespaces`); carried to `spec.md`. Every file of the bundle belongs to it. |
| `priority` | `critical`, `high` (scaffolded), `medium`, `low`. |
| `size` | `S` (single fix), `M` (scaffolded; 1-2 sessions), `L` (complex module), `XL`: the work would produce two or more specs, or bundles deliverables of a different nature (work that would need separate specs or a different `task_kind`). `XL`: a new CLI command with a viewer redesign it does not need (two specs), or a parser bugfix with a new search feature (`bugfix` and `feature`); not `XL`: two agent contracts and the command checks that route work to them, in one `feature` spec. An `XL` draft is decomposed before Planning (rule 13). |
| `milestone` | Optional (`--milestone`): one existing MS ID at the global roadmap root or a registered namespace's roadmap root (`CAP-GOV-spec-rules` Milestone validation contract) for planned/active or in that root's flat _archive/ for done/dropped, or one of its aliases (the canonical ID is written); canonical filename/identity and status/location are validated before writing and never carried to `spec.md`. A done or dropped milestone returns `SPEC_PROPOSAL_MILESTONE_INACTIVE` without blocking creation or changing the milestone. |
| `boundaries` | `owns` (scaffolded: the target area) and `excludes` (scaffolded: `docs/decisions/`); carried to `plan.md` and `tasks.md`. |
| `task_kind` | `feature` (scaffolded default) or `bugfix` (`--task-kind`): the provisional `task-kind`, confirmed at `plan-accept`; the spec follows `sdd-spec-<task_kind>`. |
| `planning_effort` | `low`, `medium` (scaffolded default) or `high` (`--planning-effort`): non-authoritative Planning `activity-effort` hint, stated at intake; not carried to `spec.md`. |
| `dev_effort` | `low`, `medium` (scaffolded default) or `high` (`--dev-effort`): non-authoritative Development `activity-effort` hint, provisional in Backlog and refined during Planning before `plan-accept`; returned by `handoff` (`dev_effort`) and not carried to `spec.md`. |
| `supersedes` | Optional (`--supersedes PROP-<old>`): the accepted proposal a close by supersede replaces; it must exist (`SPEC_PROPOSAL_NOT_FOUND`) and be `accepted` (`SPEC_PROPOSAL_NOT_APPROVED`). |
| `decomposed_from` | Optional (`--decomposed-from PROP-<source>`): an editable draft source; another slug, existing, draft, and without a Planning branch. Carried as provenance even after source deletion. |
| `needs_decompose` | Optional (`--needs-decompose`): `true` marks a draft Backlog splits before Planning starts. |
| `workflow` | devkit's binding of the proposal unit (`sdd-proposal`). |

The scaffolded body has sections `1. Background & Hypothesis`, `2. Technical Spike Questions`,
`3. Proposed Design & Impact` and `4. Lifecycle & Retirement Criteria`.

### 4.4 PADRs and the Blueprint

- `padr <slug> <title> [--summary TEXT] [--slug SLUG]` writes `decisions/PADR-<padr slug>.md`, where the PADR slug is
  `--slug` (a leading `PADR-` dropped, normalized as in 4.2) or else the title's slug; the title stays free text, so
  `padr plans "2024 roadmap" --slug roadmap-2024` works where the title alone is refused. The file has `id`, `title`, `summary` (or
  the commented placeholder `# summary: <English Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>`), `proposal:
  PROP-<slug>`, the commented line `# supersedes: [ADR-<slug>]` (uncommented, it names the ADRs the decision replaces; the comment names the `Supersedes in part` sentence for Decision Outcome,
  wholly or in part, and Decision Outcome names the replaced clauses; `CAP-DOCS-document-model`), `status: draft`,
  `created_at`, and a body shaped like the decision template (`- **Status**: Draft`,
  `- **Date**`, then Context & Problem Statement, Decision Drivers, Considered Options, Decision Outcome,
  Consequences, Confirmation). PADR IDs are unique across the repository, aliases included (`SPEC_PROPOSAL_EXISTS`).
- A PADR has no withdrawn status: one withdrawn before `plan-accept` is deleted from `decisions/` in the Planning fold
  commit, and the proposal's Planning decisions name its ID and the reason. Handoff promotes every PADR left there.
- `target-docs.md` declares `id: PROP-<slug>-target`, `proposal: PROP-<slug>`, `status: draft`, `created_at` and
  `targets: []` (one `- file: <workspace-relative path>` per Living Spec file the proposal changes; read by
  `devkit spec scope collect` as `future` evidence once the proposal has a `plan-*` source, while a queued draft is
  not observed). Its body covers the capability ledger, use cases, architecture and decisions,
  conventions and governance, and a before/after comparison. Under use cases, a `Screens (docs/ux/)` subsection holds
  the drafted screens when the proposal changes what a person sees: one draft per screen, modal or panel in the `ux`
  template's shape, with the use case step citations and root `docs/steering/ux-objects.md` or namespace
  `docs/packages/<name>/steering/ux-objects.md` rows they need and new IDs in plain text; namespace UX reads both
  registers when they exist; `spec-specify` carries them into `spec.md` at handoff (`ADR-ux-screens`).

### Milestone closure boundary

Normal PROP-to-SPEC handoff or mechanical identity relocation does not change milestone scope/decomposition
and requires no milestone review, reset or reconfirmation. Handoff removes direct membership without proving
implementation; unfinished work still in the agreed scope blocks closure. At close, inspect code/Git as needed
rather than retaining delivery lineage. Actual new work, exclusion or moving scope elsewhere changes semantic
scope; explicit exclusion/movement is a scope disposition, never delivery. `CAP-HARN-agent-guidance` defines the
current two-confirmation Backlog review. No lifecycle hook or runtime milestone mutation is introduced.

### 4.5 Handoff Steps

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.1, including preflight, writes and recovery.

### 4.6 Carrying the Proposal Body

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.2.

### 4.7 Rewriting Links and References

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.3.

### 4.8 Prune

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.4.

### 4.9 Commands and Options

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.5.

### 4.10 Output

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.6.

### 4.11 Library

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.7.

### 4.12 Codes

Detailed contract: `CAP-DLV-proposal-lifecycle` §4.8.

## Host-authorized proposal lifecycle CLI

Detailed contract: `CAP-DLV-proposal-lifecycle` Host-authorized proposal lifecycle CLI.

## Proposal review briefings and combined acceptance

Detailed contract: `CAP-DLV-proposal-lifecycle` Proposal review briefings and combined acceptance.

### Policy-aware decision boundaries

Detailed contract: `CAP-DLV-proposal-lifecycle` Policy-aware decision boundaries.

## Approach precondition

Detailed contract: `CAP-DLV-proposal-lifecycle` Approach precondition.
