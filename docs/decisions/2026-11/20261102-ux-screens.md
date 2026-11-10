---
id: ADR-ux-screens
title: UX screen documents, step links and pre-code review
summary: "For specifying screens, we add one UX kind linked to use case steps and checked by link and coverage rules, drafted before code and reviewed by an isolated walkthrough, to give a reviewed checkable contract, accepting no flow document, no rule check before code and an unenforced review."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-ux-drafts-before-code
  - ADR-ux-review-before-code
  - ADR-ux-screen-documents
  - ADR-ux-step-links-and-coverage
---

# [ADR-ux-screens] UX screen documents, step links and pre-code review

Superseded in part by `ADR-remove-plan-intent-gate`: the inline Planning boundary is before implementation rather than before `plan-intent`.
Comparing screen candidates during Planning and retaining the recommended candidate during Development remain.

- **Status**: Accepted
- **Date**: 2026-11-02
- Superseded in part by `ADR-namespace-steering-registers`: the clauses requiring one root-only register, unconditional root creation with the first UX document, and root-only writes of drafted register rows by `spec-sync`. Shared rows stay global, namespace rows stay local, and files are created only when needed; other screen and register contracts remain.
- Superseded in part by `ADR-explicit-ux-coverage-exception-notation`: the Step links and coverage clauses for empty Step cells and uncited steps or extensions, which now exclude classifications with a reason; the off-screen phrase and the known limit that every uncited step retains a warning. Classified steps retain their flow effects.
- Superseded in part by `ADR-ux-coverage-step-targeting`: the uncited-step report targeting clause only: the report belongs to a targeted use case, else the first targeted listing UX document; `RULE-ux-links` keeps its existing targeting.

---

## 1. Context & Problem Statement

The Living Spec has no document for what a person sees and operates. Use cases state intent without interface detail
(`usecase-writing` instruction) and capabilities own behavior contracts. A kind is identified only by its ID prefix;
registering one touches the ID grammar, the rules' directory and stem logic, relation-field typing, templates, seeds
and the viewer (`MAT-ux-documentation-planning-spike` §1). Practice separates screens (purpose, content, states,
interactions, exits) from flows (a screen inventory with a transition table) (`MAT-ux-documentation-practice` §1).

The milestone requires the spec rules to report use case steps without a screen and screen interactions that serve
no step, where links are declared. Every link rule reads frontmatter only; use case steps cite capabilities in
prose, and nothing maps a body reference to a step (`MAT-ux-documentation-planning-spike` §3). All current use cases
number their steps and extension keys regularly, so a step segmenter is cheap. Not every step happens on a screen
(system steps, off-screen actor decisions), and a screen can carry interactions no single task needs (global
navigation, help).

`spec-sync` writes `docs/` at `living-spec-draft`, after code review, so `docs/` states what exists
(`MAT-ux-documentation-planning-spike` §6). Implementation and the UX review need the screens before
`build-verify`. A UX document links use case steps and capabilities, so writing it into `docs/` early also needs the
use case and capability changes it links; otherwise the rules refuse the commit or the review walks the old use case.

Agents grade their own interface work leniently and layouts converge to generic averages; a separate evaluator with
graded criteria and a round cap is the documented mitigation (`MAT-ux-documentation-practice` §3-§4). An LLM reviewer
is credible for a step-by-step walkthrough over declared links and for single-screen content, not for severity or
real-user validation. devkit has an isolated read-only reviewer pattern (`code-reviewer` with `spec-review`), but its
`review` envelope and the review loop require P1-P3 severity (`MAT-ux-documentation-planning-spike` §5). A stage
switched on by content is excluded by `CAP-DLV-delivery-workflows` under `ADR-delivery-classification`.

---

## 2. Decision Drivers

### Screen documents

- One contract per fact: transitions are not written in two documents.
- Few kinds, prefixes and relation fields.
- A text contract owned by devkit and independent of the project's wireframe medium.
- Checkable structure: element, states, interactions and targets in fixed places.

### Step links and coverage

- Use cases stay intent-level: no interface detail in steps.
- Reuse of existing reference resolution, alias rewriting and `devkit spec refs`.
- Both directions checkable: step to screen and interaction to step.
- Commits are refused only for contradictions, not for legitimately screen-less steps.

### Draft timing

- The screen contract exists and is reviewed before the code that implements it.
- `docs/` keeps current-state timing; no partial Living Spec ahead of its behavior.
- One copy of each screen in the Living Spec once delivered.

### Review

- Independence from the author: a fresh, read-only context.
- Fit to evidence: walkthrough plus graded criteria with cited evidence; no severity.
- No change to the workflow engine (`devkit-agt`), to the code-review round state or to `ADR-delivery-classification`.
- Deterministic results are reported, not re-judged.

---

## 3. Considered Options

### Document set

- **One `UX` kind of interface elements, the use case as the flow** (selected in `ADR-ux-screen-documents`): one kind
  and one template; the flow graph is derived from the interactions' targets; no single overview of navigation.
- **Two kinds, `SCR` and `FLOW`** (rejected in `ADR-ux-screen-documents`): an explicit overview; two kinds, two
  templates, and transitions repeated in the screens and the flow.
- **One kind with two document shapes told apart by frontmatter** (rejected in `ADR-ux-screen-documents`): one kind,
  but each shape has its own sections and rules, so the template and every reader carry two schemas.
- **Keep the current state** (free-form materials or capability sections) (rejected in `ADR-ux-screen-documents`): no
  traceability and nothing to check.

### Step-screen link

- **UX IDs cited in step prose, step keys in the screen's interactions** (selected in
  `ADR-ux-step-links-and-coverage`): reuses body references; one new step segmenter; the use case names where a step
  happens, and a redesign or a second interface edits use cases.
- **A trailing marker per step** (rejected in `ADR-ux-step-links-and-coverage`): a new micro-syntax with no added
  information.
- **A frontmatter map of step key to UX ID** (rejected in `ADR-ux-step-links-and-coverage`): clean prose, but
  dict-valued fields need new parsing and keys drift on renumbering.
- **Links on the screen side only** (rejected in `ADR-ux-step-links-and-coverage`): use cases stay free of UX IDs;
  "step without a screen" needs a reverse index and the use case author cannot see the screens.

### Draft timing

- **Drafts before code, Living Spec at sync** (selected in `ADR-ux-drafts-before-code`): screens and the use case step
  citations they need are drafted in `target-docs.md` (proposal) or a Screens section of `spec.md` (spec depth) in the
  UX template's shape; the review reads the drafts; `spec-sync` writes `docs/ux/` and the use case changes; the link
  rules first check them at `living-spec-draft`, before integration.
- **Contract slice at specify** (rejected in `ADR-ux-drafts-before-code`): UX documents and every use case and
  capability change they link are written to `docs/` on the development branch at `specify`; rules and review run
  before build, at the cost of an exception to current-state writing that covers use cases and capabilities, not only
  screens.
- **Review only after `spec-sync`** (rejected in `ADR-ux-drafts-before-code`): no timing change; the review cannot
  shape the build.

### Review method and placement

- **Walkthrough only** (rejected in `ADR-ux-review-before-code`): lowest cost; misses single-screen content problems.
- **Walkthrough plus a 0/1/2 rubric with evidence** (selected in `ADR-ux-review-before-code`): covers both; one run
  per round.
- **Merged independent runs** (rejected in `ADR-ux-review-before-code`): offsets run-to-run inconsistency at several
  times the cost.
- **Placement as a conditional workflow stage** (rejected in `ADR-ux-review-before-code`): a stage switched on by
  content is a non-goal of `CAP-DLV-delivery-workflows` (`ADR-delivery-classification`), and it would need a new check
  primitive.
- **Placement as an optional delegation before code** (selected in `ADR-ux-review-before-code`): no engine change; not
  enforced.

---

## 4. Decision Outcome

### Screen documents

Decided by the user (`ux-document-set` and `ux-objects`). (ADR-ux-screen-documents)

- One kind `ux`, prefix `UX`, at `docs/ux/<area>/UX-<slug>.md` and `docs/packages/<name>/ux/<area>/UX-<slug>.md`,
  statuses `draft`, `active` and `deprecated` (no terminal status, so `ADR-terminal-statuses-are-historical` needs no
  new entry). It is registered as a row of the kind definition table of `SPEC-table-driven-document-kinds` (accepted).
  Visual style is not restated in UX documents; a screen refers to the project's steering style files.
  (ADR-ux-screen-documents)
- Frontmatter `element` is `screen`, `modal` or `panel`, a small value inside one schema that only the UX link rule
  (`RULE-ux-links`) reads and validates; relation fields `usecases` (UC IDs) and `capabilities` (CAP IDs).
  (ADR-ux-screen-documents)
- Sections: Purpose, Content (prose region rules and a content tree with conditions next to its nodes; no
  character-cell layouts), States, Interactions (`Trigger | Step | From | To | Target | Capability | Feedback`) and an
  optional Evidence section naming the project's own wireframe, mock-up or screenshot. (ADR-ux-screen-documents)
- Objects are named by glossary terms. Their representations and calls to action per role live in the steering file
  `docs/steering/ux-objects.md` (one topic, under the steering caps of `SPEC-foundation-documents`), scoped to the
  objects the use cases touch; the glossary's term table, its Owner check and its 24576-byte budget stay untouched,
  and devkit's own glossary gains only the new terms. The `ux-writing` instruction creates the file with the project's
  first UX document; `docs-skeleton` seeds nothing, so projects without an interface never carry it. The register rows
  a change adds are drafted with its Screens drafts, and `spec-sync` creates or updates `docs/steering/ux-objects.md`
  together with `docs/ux/` and lists it in `reconcile.md`. (ADR-ux-screen-documents)
- The register meets the steering caps: its rows hold only the object, role, representation names and call-to-action
  names; at the 24576-byte body cap it keeps only the objects of use cases with UX documents; when no steering slot is
  free, the review records R6 as not applicable with the reason. (ADR-ux-screen-documents)
- The `ux-writing` instruction asks for two or three contrasting candidates where a screen's arrangement is open, in
  Planning only (proposal Planning, or inline Planning before `plan-intent` at spec depth); in Development the
  recommended candidate is taken and the others are recorded as an assumption in `spec.md`. (ADR-ux-screen-documents)

### Step links and coverage

Decided by the user (`step-screen-link`, `ux-checks` and `coverage-strictness`). (ADR-ux-step-links-and-coverage)

- A use case step cites the UX ID of the screen it happens on in backticks, next to its capability citations; the use
  case gains no frontmatter field. (ADR-ux-step-links-and-coverage)
- A UX document lists the use cases it serves in `usecases`; each interaction's Step cell is the use case ID as a code
  span followed by the step key (`` `UC-<slug>` 2a ``), so the ID is an ordinary reference.
  (ADR-ux-step-links-and-coverage)
- A new error-severity rule (working name `RULE-ux-links`) reports contradictions: a missing or invalid `element`; a
  missing Interactions section or a table without the seven columns; a Step key that names no step of that use case
  or a step that does not cite the screen; a `usecases` entry with no Step key naming it; a target that is not a UX
  ID, `close`, `back` or `end`; a modal without a `close` or `back` row; a screen without an exit; a screen not
  reachable from an entry. (ADR-ux-step-links-and-coverage)
- A system step cites the screen its response appears on, so only a step that truly happens off-screen (a mail sent,
  a background job) cites none; `ux-writing` and `usecase-writing` say so. (ADR-ux-step-links-and-coverage)
- The graph is computed per listed use case. Its edges are every interaction of the screens that use case's steps
  cite. Its entries are the screens cited by the first step, by a step whose preceding step cites no screen, and by an
  extension bullet. A screen needs no exit when it is cited by the last main-scenario step, by an extension that ends
  the use case, or by a step whose next step cites no screen; an extension's next step is the step it resumes at.
  Panels are exempt from exit and reachability and are reached from the screens whose content tree names them.
  (ADR-ux-step-links-and-coverage)
- A separate warning-severity rule (working name `RULE-ux-coverage`, the `RULE-spec-progress` precedent) reports, for
  every use case a UX document lists, a step or extension that cites no UX ID, and an interaction whose Step cell is
  empty. (ADR-ux-step-links-and-coverage)
- A report concerns two documents; it is reported on the UX document, or on the use case when only the use case is in
  the run, as `RULE-traceability-link` does for the targeted side. (ADR-ux-step-links-and-coverage)
- Extension-to-state coverage is not checked. (ADR-ux-step-links-and-coverage)

### Drafts before code

Decided by the user (`ux-document-timing`): drafts before code, Living Spec at sync. (ADR-ux-drafts-before-code)

- `spec-specify` and the target-docs blueprint gain a Screens draft section in the UX template's shape. On a bundle
  handed off from a proposal, `spec-specify` carries the Screens drafts of `target-docs.md` into `spec.md`, so
  `spec-sync` and the reconcile verification read one place. (ADR-ux-drafts-before-code)
- In a draft, an ID the change creates (a new UX, UC or CAP ID) is plain text, never a code span or brackets, so
  `RULE-document-reference` does not resolve it before the document exists; existing IDs stay code spans.
  (ADR-ux-drafts-before-code)
- Register rows the change adds are drafted with the Screens drafts. (ADR-ux-drafts-before-code)
- `spec-sync` creates or updates `docs/steering/ux-objects.md` with the drafted rows, lists it in `reconcile.md`, and
  writes each drafted screen to `docs/ux/` and the step citations to the use cases, turning the new IDs into code
  spans, and lists each in `reconcile.md`. (ADR-ux-drafts-before-code)

### Review before code

Decided by the user (`review-method` and `review-placement`). (ADR-ux-review-before-code)

- A `ux-reviewer` subagent (isolated, read-only) bound to a new `spec-ux-review` skill walks each linked use case's
  main scenario and extensions through its screens, answering per step: will the actor try the right thing, notice
  the control, connect it to the goal and see progress. (ADR-ux-review-before-code)
- It then scores each screen 0, 1 or 2 with evidence for every score below 2 on: **R1 task fit** (the primary task and
  the facts to commit to it are present; secondary items have a place); **R2 one primary region** (no competing
  primary regions, no information dumping); **R3 states** (every state offers a next action or says why none exists);
  **R4 feedback** (every interaction gives feedback; irreversible ones confirm or can be undone); **R5 terms** (labels
  use the use case's and glossary's terms); **R6 objects** (representations and calls to action match the existing
  steering object register plus the drafted register rows for the role; recorded as not applicable only when neither
  the file nor drafted rows exist). (ADR-ux-review-before-code)
- Before code the screens are drafts the rules do not read, so the reviewer checks the link-rule items (link
  agreement, uncovered steps, targets, exits, reachability, modal close) on the drafts by hand, labels them as its own
  judgment and keeps them out of the rubric; the rules confirm them at `living-spec-draft`. Rule results are inputs
  only for screens already in `docs/ux/` that the drafts link and leave unchanged. (ADR-ux-review-before-code)
- Findings carry no severity and are recorded as `ux-review-NN` envelopes, separate from `review`; at most two rounds
  per unit. In Development the implementer closes the last round by a further `ux-review` envelope marking each
  finding `resolved` or `waived` with a reason; in Planning open findings go to the user at `plan-accept`, listed in
  the acceptance request next to the `challenger` and `scout` envelopes (`sdd-proposal` and the planning reference
  change accordingly). (ADR-ux-review-before-code)
- It runs as an optional delegation before code: in Planning on the drafted screens, and at spec depth after the
  Screens section of `spec.md` is written and before the plan: inside `specify` before `spec-plan` for
  `sdd-spec-feature`, inside `characterize` before `plan-tasks` for `sdd-spec-bugfix`, recorded at that stage so that
  its fixes precede `plan.md` and `tasks.md`. The reviewed `spec.md` is not yet committed there, so the envelope names
  the last commit and states the uncommitted draft in its assumptions; the effort table recommends it at `medium` and
  `high` when screens change. A `session` task applies the `ux-writing` instruction and runs no review.
  (ADR-ux-review-before-code)

---

## 5. Consequences

- **Positive**:
  - One place per transition; the reviewer and the rules read one table shape. (ADR-ux-screen-documents)
  - Contradictions are mechanical once screens are in `docs/ux/`; screen-less steps stay visible without blocking
    commits. (ADR-ux-step-links-and-coverage)
  - No exception to current-state writing; the review still runs before build. (ADR-ux-drafts-before-code)
  - An independent check before build without engine changes. (ADR-ux-review-before-code)
- **Negative / Risks**:
  - No written overview of navigation across use cases. (ADR-ux-screen-documents)
  - A project with an interface spends one of its ten steering files on the register. (ADR-ux-screen-documents)
  - A use case step parser to maintain (tolerating an intro paragraph, prose in Extensions, the escaped `\*a` key and
    free-form `Covers` lines). (ADR-ux-step-links-and-coverage)
  - Known limit: inserting a step before two consecutive steps on the same screen shifts their keys without a report,
    because the shifted step still cites the screen. (ADR-ux-step-links-and-coverage)
  - Known limit: a system step that wrongly cites no screen exempts the screen before it from the exit check and makes
    the screen after it an entry; only the coverage warning on that step remains. (ADR-ux-step-links-and-coverage)
  - No mechanical check before code. A link defect found at `living-spec-draft` that the code shares (for example a
    missing exit) returns the unit to `build-verify`, which repeats code review; one only in the documents is fixed at
    sync. (ADR-ux-drafts-before-code)
  - Nothing blocks a unit that skips the UX review; `CAP-DLV-delivery-roles` contains the seventh role, and the effort
    table and its review rule name the UX review. (ADR-ux-review-before-code)
- **Follow-ups**:
  - A derived navigation listing (from the targets) if projects report that screens alone are hard to navigate.
    (ADR-ux-screen-documents)
  - Extension-to-state coverage when projects report missing error states. (ADR-ux-step-links-and-coverage)
  - A contract slice at specify if projects report link defects found only at sync. (ADR-ux-drafts-before-code)
  - Enforcing the review needs a decision superseding `ADR-delivery-classification`. (ADR-ux-review-before-code)
  - Merged independent runs if rubric scores prove inconsistent across runs. (ADR-ux-review-before-code)

---

## 6. Confirmation

- `RULE-id-convention` for the location, `RULE-document-reference` for the field kinds, `RULE-ux-links` for `element`
  and the Interactions table shape, and the template's skeleton check. (ADR-ux-screen-documents)
- Rule tests under each rule's own `tests/` (`CAP-GOV-rule-authoring`), with fixtures for every report, the element
  cases and the tolerated step-format deviations; `CAP-GOV-spec-rules` documents both rules.
  (ADR-ux-step-links-and-coverage)
- The reconcile verification at its effort (the `reconcile-reviewer`, or the implementer's self-check at `low` and on
  a permitted `medium` skip) checks that every drafted screen in `spec.md` has a `docs/ux/` target in `reconcile.md`;
  `RULE-ux-links` checks the written screens. The skills' text is Review only. (ADR-ux-drafts-before-code)
- Role-contract tests for the new role and skill; review of the skill text. The review's own quality is Review only.
  (ADR-ux-review-before-code)
