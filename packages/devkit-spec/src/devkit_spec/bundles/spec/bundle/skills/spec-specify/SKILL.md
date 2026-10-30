---
name: spec-specify
description: Turn a feature request or defect report into a verifiable spec.md with Given/When/Then criteria and non-goals, creating the bundle with `devkit spec new`.
---

# spec-specify: Specification Router

Use when a spec bundle needs its `spec.md`: a feature (workflow `sdd-spec-feature`, also after
`devkit spec proposal handoff`) or a defect (workflow `sdd-spec-bugfix`). A defect the session can reproduce and fix
without documents is `session` depth and needs no `spec.md`.

## 1. Prerequisites

- Check overlap with active specs (`devkit docs list spec`) and the Living Spec (`devkit docs search "<query>"`,
  `devkit docs refs <ID> --direction in`). Completed specs are history, not inputs.
- Read `devkit spec policy` and the `contract-authoring` and `living-spec-writing` instructions.

## 2. Create or open the bundle

- A handed-off bundle already exists and is bound: rewrite its `spec.md` in place, keeping carried content that
  still holds.
- Otherwise, on `dev-<slug>`, run `devkit spec new <slug> --title "<Title>" --summary "<English sentence>"` (a defect:
  add `--workflow sdd-spec-bugfix`). Never hand-make a bundle or its binding.
- Read each skeleton before rewriting it; some hosts refuse to overwrite an unread file.

## 3. Choose the reference

Read [feature](references/feature.md) for a bundle bound to `sdd-spec-feature`, or [bugfix](references/bugfix.md)
for `sdd-spec-bugfix`.

## 4. Shared contracts

- **Acceptance criteria**: each H3 under the `Acceptance Criteria` H2 is one scenario with one `[AC-NN]` ID and
  Given/When/Then lines with verifiable bounds (exit code, status code, exact output line, count); other prose goes
  in paragraphs. Add new IDs instead of renumbering: tasks link to them.
- **References**: cite documents by full ID in backticks; write example or fixture IDs as plain text (backticked IDs
  must resolve). A rename spec writes the old IDs as plain text in its mapping tables and prose, because
  `devkit rules fix` rewrites a backticked alias to the new ID.
- **Non-goals**: state **Scope Excluded**; add **Rationale** or **When to Reconsider** only when they help a later
  reader.
- **Invariants**: if a `MUST` in `docs/architecture/` or an affected capability has to change, state that an ADR is
  required before implementation.
- **No questions**: resolve what is unclear from the agreed intent, issue, proposal and code with the recommended
  option, recording each inference as an assumption. If the goal, scope or contract must change, raise a problem for
  the Host instead of asking the user. Explicit user instructions take precedence.
- **Source feedback**: keep the full FB IDs and scope from Planning or the carried proposal in a `Source feedback`
  section.
- Drop an optional section that does not apply instead of writing "N/A".
- **Screens**: when the change adds or changes what a person sees and operates, add a `Screens` section to `spec.md`
  with one draft per screen, modal or panel in the `ux` template's shape (`ux-writing`), with the use case step
  citations and `docs/steering/ux-objects.md` rows they need. A bundle handed off from a proposal: carry the Screens drafts of
  `target-docs.md` here, so `spec-sync` and the reconcile verification read one place. An open screen arrangement:
  take the recommended candidate and record the others as an assumption.

## 5. Completion

- [ ] `spec.md` keeps the `id` and `workflow` frontmatter and an English `summary`; the `<!-- devkit:skeleton -->`
  line is removed.
- [ ] When `spec.md` has a Screens section, offer the optional UX review before the plan: delegate the `ux-reviewer`
  (`spec-ux-review`, recommended at `medium` and `high`) on the drafts and fold its findings into `spec.md` before
  `spec-plan` (feature) or `plan-tasks` (bugfix), recording its `ux-review` envelope at this stage.
- [ ] `devkit rules check <dir>` reports no violation except task coverage not yet written; next is `spec-plan`. Do
  not commit yet: the `specify` stage boundary is committed only once `plan.md` and `tasks.md` satisfy
  `RULE-task-coverage`.
