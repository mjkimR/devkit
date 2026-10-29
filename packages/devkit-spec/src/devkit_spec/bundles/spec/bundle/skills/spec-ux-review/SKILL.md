---
name: spec-ux-review
description: Review drafted screens before code by walking each linked use case through them and scoring each screen on a six-item rubric with evidence; records ux-review envelopes without severity, at most two rounds.
---

# spec-ux-review: UX Walkthrough Review

The `ux-reviewer` role runs this skill in isolation and read-only (`ADR-ux-review-before-code`). It is an optional
delegation before code, never a stage:

- Planning: on the Screens drafts of `target-docs.md`.
- Spec depth: after the Screens section of `spec.md` is written and before the plan (inside `specify` before
  `spec-plan` for `sdd-spec-feature`, inside `characterize` before `plan-tasks` for `sdd-spec-bugfix`), recorded at
  that stage so its fixes precede `plan.md` and `tasks.md`.
- The effort reference recommends it at `medium` and `high` when screens change. A `session` task applies the
  `ux-writing` instruction and runs no review.

## Inputs

- The Screens drafts in the UX template's shape (`ux-writing`), with the use case step citations they need.
- The use cases the drafts list in `usecases`, as they will read after the change.
- `docs/steering/ux-objects.md` when it exists, and the register rows drafted with the screens.
- The Evidence each draft links (a wireframe, mock-up or screenshot), when present.

## Steps

### Step 1: Walkthrough

Walk each linked use case's main success scenario, then each extension, through the screens its steps cite. At
every step answer four questions, each with the screen content that decides it:

1. Will the actor try to do the right thing here?
2. Will the actor notice that the control for it is available?
3. Will the actor connect the control with the goal?
4. After the action, will the actor see progress toward the goal?

A "no" is a finding naming the use case, the step key and the screen.

### Step 2: Rubric

Score each screen 0, 1 or 2 on every item; every score below 2 gets evidence (the draft's section, node or row) and
a finding:

- **R1 task fit**: the primary task and the facts to commit to it are present; secondary items have a place.
- **R2 one primary region**: no competing primary regions and no information dumping.
- **R3 states**: every state offers a next action or says why none exists.
- **R4 feedback**: every interaction gives feedback; irreversible ones confirm or can be undone.
- **R5 terms**: labels use the use case's and the glossary's terms.
- **R6 objects**: representations and calls to action match `docs/steering/ux-objects.md` plus the drafted rows for
  the role; record it as not applicable, with the reason, only when neither the file nor drafted rows exist or no
  steering slot is free.

### Step 3: Link items, by hand

Before code the drafts are not in `docs/ux/`, so `RULE-ux-links` and `RULE-ux-coverage` do not read them; check
their items on the drafts yourself: `usecases` and Step cells agree with the step citations, every step is covered,
targets name drafted or existing screens, every screen has an exit, a modal closes, every screen is reachable from
an entry. Label each such finding `link check (reviewer judgment)` in its `issue` and keep it out of the rubric; the
rules confirm it at `living-spec-draft`. Use rule results as inputs only for screens already in `docs/ux/` that the
drafts link and leave unchanged; report them, never re-judge them.

## Report

Findings carry no severity. Record one `ux-review` envelope per round; the reviewed `spec.md` may be uncommitted, so
name the last commit and state the uncommitted draft in an assumption:

```bash
devkit workflow envelope new --unit <dir> --kind ux-review --stage <specify|characterize|spike> \
  --summary "<use cases walked; rubric per screen, e.g. UX-a R1=2 R2=1 R3=2 R4=2 R5=2 R6=n/a>" \
  --head $(git rev-parse HEAD) --assume "reviews the uncommitted Screens section of spec.md" --findings-file - <<'YAML'
- issue: "<UC> 2: the actor cannot tell the draft was saved (walkthrough question 4)"
  evidence: "spec.md Screens > <screen> > Interactions row Save"
  failure_condition: "<when the actor fails>"
  suggested_action: "<recommended change to the draft>"
YAML
```

- At most two rounds per unit. A second round reviews the revised drafts and the first round's findings.
- In Development the implementer closes the last round with a further `ux-review` envelope that repeats each finding
  with `resolution: resolved`, or `resolution: waived` and a `waiver` reason.
- In Planning open findings go to the user at `plan-accept`, listed in the acceptance request next to the
  `challenger` and `scout` envelopes.

## Completion

- [ ] Every linked use case was walked, main scenario and extensions, and every screen scored on R1-R6.
- [ ] The envelope holds the findings without severity, and the round count is at most two.
