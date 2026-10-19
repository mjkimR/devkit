---
name: spec-specify
description: Turn a feature request or defect report into a verifiable spec.md with Given/When/Then criteria and non-goals, creating the bundle with `devkit spec new`.
---

# spec-specify: Specification Router

Use this skill when a spec bundle `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` needs its `spec.md`: a feature or substantial enhancement (workflow `sdd-spec-feature`, also after `devkit spec proposal handoff`) or a defect (workflow `sdd-spec-bugfix`). This file holds the bundle creation, the choice of reference and the contracts both references share.

## 1. Prerequisites

- Check whether an active spec already covers this work: `devkit spec list spec`. Completed specs are work history, not inputs; the current contract lives in `docs/capabilities/` and `docs/stories/`.
- Look for overlap, extension or conflict with the Living Spec: `devkit spec search "<query>"` (`--kind capability`, `--kind decision`), `devkit spec list capability decision`, and `devkit spec refs <ID> --direction in` for what depends on a document the change touches.
- Read `devkit spec policy`.
- Read the `contract-authoring` instruction before writing acceptance criteria and non-goals, and `living-spec-writing` before citing Living Spec documents.

## 2. Create or open the bundle

- **Handed-off bundle** (`devkit spec proposal handoff`): it already exists and is bound; `spec.md`, `plan.md` and `tasks.md` carry the skeleton marker. Rewrite `spec.md` in place, keeping the carried content that still holds.
- **New bundle**: on the slug's `dev-<slug>` branch, `devkit spec new <slug> --title "<Title>" --summary "<English sentence>"` (add `--workflow sdd-spec-bugfix` for a defect). It writes the skeletons (a bugfix bundle gets `spec.md` only; its `plan-tasks` stage writes the other two), sets the ID `SPEC-<slug>` and binds the bundle; in a monorepo it takes the current directory's namespace (or `--namespace <name>`). Never hand-make the bundle or its binding. The slug is kebab-case, has no date or sequence number and is unique among specs (`RULE-id-convention`).
- Read each skeleton before rewriting it (some hosts refuse to overwrite an unread file). `devkit workflow show --unit <dir>` shows the workflow, `devkit workflow next --unit <dir>` the current stage and what is unmet.

## 3. Choose the reference

| Situation | Reference |
| :--- | :--- |
| New capability, enhancement, contract change; bundle bound to `sdd-spec-feature` | [feature](references/feature.md): discovery questions, user story, acceptance scenarios, output standard |
| Defect with contract impact or uncertainty; bundle bound to `sdd-spec-bugfix` | [bugfix](references/bugfix.md): defect characterization, reproduction evidence before the fix, resolution and preservation evidence after it |

Read one reference, not both. A defect the session can reproduce and fix without written documents is `session` depth (workflow `sdd-session-bugfix`) and needs no `spec.md`.

## 4. Shared contracts

- **Non-goals** state **Scope Excluded**. Add **Rationale** and **When to Reconsider** when they help a later reader decide; do not fill them for form.
- **Acceptance criteria**: every H3 under the H2 whose title contains `Acceptance Criteria` is one scenario with exactly one `[AC-NN]` ID (`AC-` and at least two digits, unique in the spec) and Given/When/Then lines (`RULE-task-coverage`). Explanatory tables and prose go in paragraphs, never in an H3 there. Renumbering an ID later breaks the task links; add new IDs instead.
- **Measurable Then**: no "fast", "robust", "properly"; use verifiable bounds (exit code, status code, exact output line, count).
- **References**: cite capabilities, stories and ADRs by full ID in backticks (`` `CAP-<AREA>-<slug>` ``), never by Markdown path or a date- or number-based ID. Write example or fixture IDs in a scenario as plain text: in backticks or brackets they are references and must resolve; `related_capabilities` and `related_stories` hold bare `CAP` and `US` IDs that resolve (`RULE-document-reference`).
- **Invariants**: review `docs/architecture/` and the affected capabilities. If a `MUST` has to change, say that an ADR is required before implementation.
- **No questions during Development**: resolve what is unclear from the agreed intent, the issue, the proposal and the code; decide with the recommended option and record each inference in `spec.md` as an assumption. A point that needs the agreed goal, scope or contract changed is a problem for the Host, never a question to the user or a `[NEEDS CLARIFICATION]` marker.
- **Only what the change needs**: drop an optional output section that does not apply instead of writing "N/A".
- **Self-validation** before finishing: completeness (personas, inputs, outputs, edge cases), clarity (every AC measurable), consistency (non-goals and invariants respected), scenario IDs unique.

## 5. Definition of Done

- [ ] `spec.md` follows the agreed intent, with the choices made inside it recorded as assumptions, in the reference's output standard, keeping the `id` and `workflow` frontmatter and an English `summary` (`RULE-document-summary`).
- [ ] The skeleton marker line `<!-- devkit:skeleton -->` is removed from `spec.md`; until then `not-skeleton(spec.md)` keeps the `specify` (feature) or `characterize` (bugfix) stage open.
- [ ] `devkit rules check <dir>` reports no spec-rule violation other than coverage the tasks have not been written for yet; next is `spec-plan` (bugfix: at `plan-tasks`).
