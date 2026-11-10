---
id: PROP-partial-adr-supersession-statements
title: Structured partial-supersession statements for ADRs
summary: "Record each partial replacement once, as a structured statement in the superseding ADR, let handoff copy it into the earlier ADR's pointer and let the CLI and viewer show a decision's partial replacements, so earlier ADRs stay readable without manual pointer clarification."
status: reviewing
created_at: 2026-11-10
target_area: capabilities/documents/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/decision_supersession.py
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md
    - packages/devkit-docs/src/devkit_docs/features/documents/
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md
    - docs/capabilities/documents/CAP-DOCS-document-model.md
    - docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    - docs/decisions/README.md
  excludes:
    - packages/devkit/src/devkit_agt/features/rules/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-partial-adr-supersession-statements] Structured partial-supersession statements for ADRs

## 1. Background & Hypothesis

A decision is never changed in place: a new ADR names the earlier one in `supersedes`. When only part of the earlier
ADR is replaced, the earlier ADR stays `accepted` with a "Superseded in part by `ADR-<new>`" line
(`SPEC-partial-adr-supersession`). Partial replacement is the common path: 17 of the 65 ADRs carry such a line and
none is wholly superseded.

Which clauses were replaced has no defined home:

- `devkit spec proposal handoff` fills the pointer with the new ADR's `summary`, which states the new decision, not
  the replaced clauses. Someone must rewrite it after handoff. Guidance gave that step to the Host
  (`FB-handoff-pointer-carries-summary-not-clauses`), the handoff docstrings still give it to Development
  (`FB-handoff-pointer-owner-docstring-mismatch`), and a summary pointer has already reached Development
  (`FB-partial-supersession-pointer-still-summary`, recurring). Six existing pointers still copy a summary.
- The superseding ADRs already describe their replaced scope, in free-form sentences ("This replaces <target> …",
  "Replaces in <target>: …") that no tool can extract.
- `adr-consolidation` reads the replaced scope from the earlier ADR's pointer, so consolidation depends on the
  manually clarified text.
- No command or viewer page shows a decision's partial replacements; `devkit docs refs --direction in` mixes them with
  every other incoming reference.

A `spec`-depth attempt to flag summary-copy pointers with `RULE-decision-supersession` stopped on rule-engine
severity and the six existing copies; the user redirected the work to the ADR model
([attempt findings](materials/supersession-pointer-attempt.md)).

### Hypothesis

Partial supersession becomes reliable when the replaced scope is written once and everything else derives from it:

1. **Single source**: the superseding ADR carries one structured "replaces in part" statement per earlier ADR, written
   at PADR time by the author who knows the scope.
2. **Derived pointer**: handoff copies that statement into the earlier ADR's pointer instead of the summary, so the
   earlier ADR stays readable on its own and nobody rewrites the pointer after handoff.
3. **Checked consistency**: a rule checks that each partial superseder has a statement for each `supersedes` target
   that stays accepted, and that the earlier ADR's pointer matches it.
4. **Queryable state**: the CLI (and the Living Spec viewer, if Planning keeps it in scope) shows a decision's partial
   replacements from the statements.
5. **Deferred consolidation**: both ADRs stay as they are, linked, until a hygiene pass consolidates them;
   `adr-consolidation` reads the replaced scope from the statements.

### Scope and non-goals

- In scope: the statement convention in the decision template, PADR scaffold and `docs/decisions/README.md`;
  `RULE-decision-supersession` checks; the handoff pointer; `adr-consolidation` Step 2; the post-handoff reference;
  a CLI view of partial replacements; the Living Spec owners (`CAP-DOCS-document-model`, `CAP-DLV-proposal-planning`);
  migration of existing partial superseders to the convention without changing any decision.
- Non-goals:
  - Changing the rules engine's severity model (`packages/devkit/src/devkit_agt/features/rules/`).
  - Changing any decision's meaning; migration edits wording and structure only.
  - Consolidating ADRs as part of this work.

## 2. Technical Spike Questions

- **Q1 — Statement form**: Where and in what form does the superseding ADR state its replaced scope: a frontmatter
  field, or a fixed Decision Outcome sentence or subsection per target? `SPEC-partial-adr-supersession` rejected a
  structured field (`superseded_in_part_by`, `status: amended`); read its reasons first.
- **Q2 — Pointer derivation**: Does handoff copy the statement verbatim, or a shorter derived form? How does a later
  wording repair of either ADR stay consistent?
- **Q3 — Rule checks and severity**: Which checks are errors without breaking `main` or the handoff commit gate?
  Do the existing superseders already satisfy the convention after migration?
- **Q4 — Migration**: Which existing partial superseders need their prose restated in the convention, and do the six
  summary-copy pointers become derived pointers in the same change?
- **Q5 — CLI and viewer**: Which command shows partial replacements (a `devkit docs refs` option or another
  command)? Is the viewer in this proposal or a separate one?
- **Q6 — Owner question**: Once the pointer is derived, does any post-handoff clarification remain, and what do the
  handoff docstrings and post-handoff reference say?

## 3. Proposed Design & Impact

To be settled in Planning. Expected touch points: the decision template and PADR scaffold, `docs/decisions/README.md`,
`RULE-decision-supersession`, `handoff.py`, the `spec-next` post-handoff reference, the `adr-consolidation` playbook,
the `devkit docs` commands, the owning capabilities and the existing partial superseders. The viewer may split into a
separate proposal; Planning re-judges `size` and returns the draft for decomposition if it needs two specs.

## 4. Lifecycle & Retirement Criteria

Planning answers Q1–Q6, records the statement-form decision as a PADR and drafts the Living Spec targets. On
acceptance, handoff starts Development.

## 5. Source feedback

- `FB-partial-supersession-pointer-still-summary` (recurring): a summary pointer reached Development despite the
  guidance-only post-handoff clarification.
- `FB-handoff-pointer-owner-docstring-mismatch`: the handoff docstrings and the post-handoff reference name different
  owners for the pointer clarification (Q6).
