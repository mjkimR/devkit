---
id: DESIGN-proposal-handoff
title: "Proposal handoff mechanism"
status: active
summary: "Walks devkit spec proposal handoff in source order on one real handoff: worktree, preflight, spec bundle, body carry, ADR promotion, moves, reference rewriting, record carry, scope registration, commit and rollback; contracts stay with the proposal capabilities."
area: delivery
related_capabilities: [CAP-DLV-proposal-lifecycle, CAP-DLV-proposal-planning, CAP-DLV-spec-bundles, CAP-COLL-work-scope-registry]
related_domains: [DOMAIN-delivery-relationships, DOMAIN-feedback-lifecycle]
related_designs: [DESIGN-workflow-stage-evaluation]
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/handoff.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/services/body.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/services/rewrite.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/services/history.py
---

# [DESIGN-proposal-handoff] Proposal handoff mechanism

A handoff turns an accepted proposal bundle into a spec unit in one pass that writes, moves, edits and deletes files
across `specs/`, `docs/decisions/`, `docs/materials/` and every document that pointed into the proposal. Its contract
is stated rule by rule in `CAP-DLV-proposal-lifecycle` §4.1 to §4.3, but the rules do not show the order the source
applies them in. That order decides which refusals leave the repository untouched, which failures are rolled back
and which are only reported once the handoff is done. This walk-through follows the composed
`devkit spec proposal handoff <slug> --effort <level>` through
[native_handoff.py](../../../../packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py),
[delivery handoff.py](../../../../packages/devkit-spec/src/devkit_spec/features/delivery/usecases/handoff.py) and
`handoff_proposal` in
[proposals handoff.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py).

## Handoff order

The command has two forms. Without `--effort` it runs only `HandoffProposalUseCase` in an existing `dev-<slug>`
checkout and commits nothing. With `--effort`, `HandoffUseCase` composes worktree creation, the handoff and one
commit from the retained base checkout (`CAP-DLV-proposal-lifecycle`, Host-authorized proposal lifecycle CLI). The
composed form runs these phases in order.

### 1. Base preflight and worktree

`prepare` reads only the base checkout and writes nothing. It refuses a linked worktree or a `dev-`/`plan-` branch
(`SPEC_PROPOSAL_WRONG_WORKTREE`), a dirty base (`SPEC_HANDOFF_BASE_DIRTY`), a `proposal.md` that is not committed
with `status: accepted`, a `needs_decompose: true` proposal, and a proposal whose `sdd-proposal` Planning is not
complete with its own `plan-accept` (`SPEC_HANDOFF_NOT_READY`). Invalid `task_kind`, effort, `title` or `summary`
values are `SPEC_PROPOSAL_INVALID`. An existing `dev-<slug>` checkout is reused only when devkit created it at the
reviewed base head and it is clean; anything else is `SPEC_HANDOFF_WORKTREE_CONFLICT`.

`HandoffUseCase.execute` then reads the `proposal-handoff` approval policy; under `auto` the requested effort has to
match the proposal's `dev_effort`. The execution then runs `prepare` again and refuses with `SPEC_HANDOFF_STALE` when the
base head, the accepted proposal text or the policy files changed since the first call. It starts `dev-<slug>` at
the reviewed head, with setup and sync. A setup or sync failure returns `needs_recovery` and leaves the worktree in
place, and so does a new worktree whose HEAD moved or whose files setup changed.

### 2. Handoff preflight

`handoff_proposal` runs inside `dev-<slug>`. Everything up to the first write is a check or a plan in memory, so a
refusal here writes nothing:

1. **Branch and proposal.** The handoff requires branch `dev-<slug>`. The proposal is read; a slug whose first
   segment has no letter, a status other than `accepted`, `needs_decompose: true` and, for a bundle bound to
   `sdd-proposal`, a missing effective `gate:plan-accept` record are refused
   (`SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` for the last). `namespace`, `summary`, `task_kind` and the effort hints are
   validated, the docs index is loaded, a malformed `depends_on` is refused and a same-slug spec is a conflict.
2. **Workflow binding.** `resolve_binding` picks `sdd-spec-<task_kind>`. A `bugfix` workflow that does not resolve is
   `SPEC_PROPOSAL_WORKFLOW_INVALID`; a missing `sdd-spec-feature` only leaves the spec unbound with
   `SPEC_PROPOSAL_UNBOUND` later (`CAP-DLV-proposal-lifecycle` §4.1 step 2).
3. **Plans.** For a bundle, the handoff plans the PADR promotions, lists the unit's workflow records, validates
   every feedback file and selects the open ones (`plan_open_feedback` in
   [feedback.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/usecases/feedback.py)), and
   plans every other bundle file as a carried extra. Translated aliases are checked, every destination is checked
   for collisions (`SPEC_PROPOSAL_TARGET_EXISTS`) and the partial-supersession pointers are planned. A merge into an
   existing materials directory is planned leaf by leaf in this same pass, over the `materials/` leaves and the
   carried files, so every merge conflict is known before the first write (`CAP-DLV-proposal-lifecycle` §4.1 step 5
   states the outcomes). Last, no destination may resolve outside the workspace.
4. **Body carry.** `carry_proposal_body` in
   [body.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/services/body.py) splits the body
   after the first H1 into H2 sections and sorts each by its heading into a spec section, as the classification
   table of `CAP-DLV-proposal-lifecycle` §4.2 states. `spec_files` then renders `spec.md`, `plan.md` and `tasks.md`
   as skeletons, with the origin line, the preserved materials path and the blueprint reference, and drops the
   proposal's own path from the planned boundaries. A `bugfix` spec keeps `spec.md` only.
5. **Projected dependency graph.** The dependency projection runs last because it needs the rendered `spec.md`:
   it removes the proposal from an in-memory copy of the index, adds the new spec, points every live `depends_on`
   written with the proposal's ID or alias at the spec, and refuses a missing, ambiguous or wrong-kind target or a
   cycle with `SPEC_PROPOSAL_INVALID` (`CAP-DLV-proposal-lifecycle` §4.1, the paragraph before the numbered steps).

### 3. Writes, inside the rollback boundary

One `try` block performs every write, recording what it wrote (`written`), moved (`moved`) and edited (`edited`):

1. `write_spec_bundle` writes the skeletons and binds `spec.md`; `target-docs.md` is copied.
2. Each PADR is written as its ADR with `ADR-` IDs and the accepted status, then each planned
   "Superseded in part by" pointer is written into its target ADR, keeping the original text for restoration.
3. `materials/` moves (whole, or per absent subtree and leaf in a merge), then open feedback into the spec's
   `feedback/` and the carried extras into the materials directory, through `move_path`. Across file systems
   `move_path` copies and leaves the source for later removal.

Any exception there restores the edited ADRs from their original text and runs `roll_back` in
[specs.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/usecases/specs.py) on the rest: moves
go back newest first, then written paths are removed newest first. A directory created inside a moved `materials/`
travels with that move back, so `roll_back` follows it to where it went and removes it there only when it holds no
file. A directory still holding something that could not be moved back is kept. A complete rollback re-raises an advisory error unchanged; anything else, or an incomplete rollback,
becomes `SPEC_PROPOSAL_HANDOFF_FAILED` with the leftovers in its details. `proposal.md` is kept in both cases; after an incomplete rollback, the paths listed in the details may still sit
at their destinations.
After the block, copied cross-file-system sources are removed.

### 4. Rewriting, removal and record carry

From here nothing raises; problems become notices on a handoff that already happened. A `RelocationPlan` maps every
old path to its new one, the docs index is reloaded, and the scan set is every Markdown file under `docs/` and
`specs/` except the proposal and completed spec bundles (their `feedback/` stays in). Four passes run in order
(`CAP-DLV-proposal-lifecycle` §4.3):

1. `rewrite_history` in
   [history.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/services/history.py) turns a
   link or bundle-relative code span naming a dropped workflow record into a historical Git citation, only when the
   record's bytes at HEAD match. It runs before ordinary relocation, so the next pass never points such a link at a
   deleted record.
2. `rewrite_links` in
   [rewrite.py](../../../../packages/devkit-spec/src/devkit_spec/features/proposals/services/rewrite.py) finds
   inline links and images outside code with devkit's `extract_links` and relocates them with `relocate_links`,
   which writes each changed file through an atomic replace.
3. `rewrite_ids` rewrites ID references written with the proposal's or a promoted PADR's ID or alias: `PROP-<slug>`
   to `SPEC-<slug>`, `PADR-<x>` to `ADR-<x>`.
4. `rewrite_paths` replaces code-span paths relative to the bundle in carried documents with the new ID or path.

The bundle is then deleted; a failure is `SPEC_PROPOSAL_CLEANUP_FAILED`. The gate carry writes the proposal's
`gate:plan-accept` into the spec's `decisions/` under the same name, with the spec's workflow, the original `by`
and the note `PROP-<slug>` (followed by the original note when there was one); a failure is
`SPEC_PROPOSAL_GATE_NOT_CARRIED`. The result then adds `SPEC_PROPOSAL_UNBOUND` for an unbound spec,
`SPEC_PROPOSAL_LINK_UNRESOLVED` when anything stayed unresolved, and `SPEC_PROPOSAL_REFS_REWRITTEN` when at least
one rewrite has kind `id`, naming the files to reread. The `spec-next` skill's post-handoff check follows up the
`[UNRESOLVED_LINK]` and `[REWRITTEN ... kind=id]` lines.

### 5. Scope registration and commit

`HandoffProposalUseCase` calls the `before_registration` guard, then `auto_register`
([flow.py](../../../../packages/devkit-spec/src/devkit_spec/features/scope/usecases/flow.py)), which registers the
new spec in the work-scope registry only in a linked worktree and turns every failure into a verbose diagnostic
(`CAP-COLL-work-scope-registry`). The composed form then stages the whole worktree delta and commits it once as
`spec: hand off <slug> to Development` under the normal commit gate. A refused commit is
`SPEC_HANDOFF_COMMIT_REFUSED` with the writes left staged. A final check verifies that the landed HEAD has
the reviewed base as its only parent and that the worktree is clean, else `SPEC_HANDOFF_STALE`. Nothing after the
handoff writes is rolled back: a stopped composed handoff reports `needs_recovery`, clears the next command and
names the repair in `dev-<slug>` (`ADR-proposal-handoff`).

## Worked example: the formal document templates handoff

Commit `93e72152c` (`spec: hand off formal-document-templates to Development`) created
`SPEC-formal-document-templates` from the bundle `docs/proposals/PROP-formal-document-templates/` at its single
parent `5664442947e`. The bundle held `proposal.md` (bound to `sdd-proposal`, `task_kind: feature`,
`milestone: MS-documentation-system-evolution`, `depends_on: [SPEC-design-bundle-layout]`), one PADR, one open
feedback file, `materials/template-survey.md`, one decision record and eleven envelopes. Each phase left these traces:

| Phase | What the commit shows |
| --- | --- |
| Preflight | The projected graph replaced the proposal with the spec and kept its edge to `SPEC-design-bundle-layout`, which resolved; nothing was refused. |
| Bundle and body carry | `proposal.md` became `specs/2026-11/20261116-formal-document-templates/spec.md` with the carried `summary` and `depends_on`, no `milestone`, and the origin line plus the preserved materials path. `## 1. Background & Hypothesis` went to the problem statement as an H3. `## 2. Technical Spike Questions`, `## 3. Proposed Design & Impact` and `## 4. Lifecycle & Retirement Criteria` went to Carried Proposal Notes; the H3 sections `Non-Goals` and `Expected acceptance evidence` inside section 3 travelled with it as H4, so Non-Goals and Acceptance Criteria kept their placeholders. `plan.md` and `tasks.md` took the target area and `boundaries.owns`. |
| ADR promotion | The PADR became `docs/decisions/2026-11/20261116-problem-first-formal-document-openings.md` as `ADR-problem-first-formal-document-openings` with `status: accepted` in its frontmatter. Its `supersedes: [ADR-linked-domain-relationship-views]` produced a "Superseded in part by" line below that ADR's H1, copying the partial-supersession statement. |
| Moves | The open feedback file `FB-scout-lacks-web-search` moved to the spec's `feedback/` with `status: open` unchanged. `materials/` moved to `docs/materials/2026-11/20261116-formal-document-templates/`. |
| Rewriting | The citation of `envelopes/scout-01.yaml` to `envelopes/scout-04.yaml` in the survey became historical Git citations at `5664442947e`. ID references in the survey, the feedback file and the promoted ADR's `proposal` field now name `SPEC-formal-document-templates`; those `id` rewrites raise `SPEC_PROPOSAL_REFS_REWRITTEN`. The code spans `materials/template-survey.md` in `spec.md` became the repository path. The bare origin line keeps the proposal ID, since bare text is never rewritten. |
| Removal and record carry | The proposal, its decision record and eleven envelopes are deleted. A new `decisions/01-gate-plan-accept.yaml` in the spec carries `gate:plan-accept` with `workflow: sdd-spec-feature`, `by: user` and the note naming the proposal. |
| Commit | One commit whose only parent is the reviewed base. |

One difference from the current source: this commit predates the own-path filter (`cc42066c8`), so its `plan.md`
and `tasks.md` still list `docs/proposals/PROP-formal-document-templates/` as a planned boundary. The same handoff
today would omit that path.

## Authority boundary

`CAP-DLV-proposal-lifecycle` owns the handoff steps, body carry and rewriting contracts (§4.1 to §4.3), the output
and codes (§4.6, §4.8) and the composed command (Host-authorized proposal lifecycle CLI).
`CAP-DLV-proposal-planning` owns acceptance, Planning feedback routing (§3.1) and the gate record that the handoff
carries. `CAP-DLV-spec-bundles` owns the spec skeletons, `CAP-COLL-work-scope-registry` the registration and
`ADR-proposal-handoff` the composed commit transaction.

## Update triggers

- `handoff_proposal`, `HandoffUseCase`, `prepare`, `carry_proposal_body`, `roll_back`, the four rewrite passes, the
  gate carry or `auto_register` change their order, inputs or failure handling.
- `CAP-DLV-proposal-lifecycle` §4.1 to §4.3 change an outcome this walk-through cites.
- The worked example is in doubt: compare it with `git show --name-status -M 93e72152c`.
