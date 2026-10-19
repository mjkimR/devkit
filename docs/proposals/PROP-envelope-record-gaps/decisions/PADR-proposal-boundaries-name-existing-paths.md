---
id: PADR-proposal-boundaries-name-existing-paths
title: Proposal boundaries name existing paths
summary: Adds a devkit-spec rule that every target_area and boundaries.owns entry of a proposal resolves to an existing path, warning on misses and reporting the template placeholder under its own message.
proposal: PROP-envelope-record-gaps
status: draft
created_at: 2026-10-19
---

# [PADR-proposal-boundaries-name-existing-paths] Proposal boundaries name existing paths

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

`target_area` and `boundaries.owns` in `proposal.md` are free text. Nothing checks them when the proposal is created,
at `plan-intent` or at handoff, which copies them into the spec's carried notes and task boundary
(`proposals/handoff.py`, `proposals/specs.py`). A proposal declared `capabilities/core/`, an area that does not exist
(`FB-proposal-boundaries-unchecked`). `devkit spec proposal new` without `--target-area` writes the placeholder
`capabilities/<area>/` into both fields. Evidence: `materials/spike-evidence.md`.

## 2. Decision Drivers

- The current proposals use three forms (a bare area `delivery/`, a docs-root path `capabilities/delivery/` or
  `stories/delivery/`, a repository path `packages/...` or `docs/glossary.md`); all resolve today and none should need
  rewriting.
- A Backlog draft keeps the placeholder until Planning settles the area, and the first Planning commit (`status:
  reviewing`) comes before the spike; neither may be refused.
- The boundary carried into Development must name real paths by `plan-accept`.
- The rules engine applies one severity per rule: the evaluator overwrites each violation's severity with the rule's
  effective severity (`packages/devkit/src/devkit/rules/engine/evaluator.py`, `CAP-GOV-rule-authoring`), and
  `devkit.rules` is outside this proposal.
- An accepted proposal is never edited; a premise that no longer holds is a problem and a close
  (`CAP-DLV-delivery-workflows`).
- A rule is not a gate or a policy.

## 3. Considered Options

- **A. A new rule `RULE-proposal-boundaries`** in the devkit-spec bundle, linter phase, with its guide and tests in its
  folder (`CAP-GOV-rule-authoring`).
- **B. More checks in `RULE-spec-format`**, which already validates the effort hints and `namespace` of proposal
  anchors; it is an error rule, so the new reports would refuse draft commits.
- **C. A check in `devkit spec proposal handoff` only**: too late, after `plan-accept`.

Severity, given one per rule: **S1** warning, with the Planning executor clearing the proposal's reports before the
`plan-accept` request; **S2** error on `accepted` proposals only, which refuses the acceptance commit the Host writes
after the user accepted and turns a later path move into an error on an unchangeable proposal; **S3** two rules
(placeholder error, missing path warning), which still refuses the first Planning commit of a placeholder draft.

## 4. Decision Outcome

- **Option A with severity S1 (warning).** The rule reads every proposal anchor (`docs/proposals/PROP-<slug>/proposal.md`
  and single-file proposals) whose `status` is `draft`, `reviewing` or `accepted`; `rejected` proposals are skipped. It
  reports on the anchor, the line of the entry. A run reports a proposal when the anchor is in the run's targets or
  in a whole-workspace run; there is no deleted-path rescan, and a run targeting `.devkit/config.toml` does not
  recheck proposals.
- **Entries**: `target_area` (a string, optional; absent is not reported) and every `boundaries.owns` item. A
  non-list `owns` or a non-string item is reported as malformed. `boundaries.excludes` is not checked.
- **Resolution**: an entry is normalized with `devkit_spec.entrypoints.normalize` (absolute paths, `..` and glob
  characters are reported as invalid) and resolves when it names an existing path, with the snapshot semantics of
  `devkit_spec.entrypoints` existence checks, tried in this order: relative to the repository root; relative to the
  proposal's namespace docs root (`docs/packages/<name>/`, when `namespace` names a registered namespace), then to
  `docs/`; as a capability area under `<namespace docs root>/capabilities/`, then `docs/capabilities/`. A trailing
  `/` requires a directory. A bare entry that matches a repository directory resolves there; the guide says so.
- **Placeholder**: an entry containing `<...>` (the template's `capabilities/<area>/`) is reported as a placeholder,
  with its own message and fix (name the area), not as a missing path.
- **Procedure**: before the `plan-accept` request the Planning executor runs `devkit rules check` on the proposal and
  clears every `RULE-proposal-boundaries` report (`workflows/sdd-proposal.md` gate rules, next to the `dev_effort`
  review). An accepted proposal whose owned path later moves keeps its warning; Development treats a boundary that no
  longer holds as a problem and a close, never an edit of the proposal.
- **Paths the Development will create** (the user's answer `new-boundary-paths`, `envelopes/answer-01.yaml`): the
  proposal names the nearest existing parent directory in `target_area` or `boundaries.owns` (for example
  `packages/devkit-spec/src/devkit_spec/bundle/rules/` for a new rule folder) and names the new path itself in the
  proposal text. No new frontmatter key or entry marker; handoff copies the boundary unchanged. The rule's guide and
  the proposal template comment state this form.
- Not fixable: the rule cannot know the intended area.

## 5. Consequences

- devkit-spec: the rule, its guide and tests, its registration, the proposal template comment (the accepted forms),
  `CAP-DLV-proposal-incubation` (proposal frontmatter), `CAP-GOV-spec-rules` (the rule catalog with its warning
  severity) and the `plan-accept` rule of `workflows/sdd-proposal.md`.
- Warnings do not refuse commits (`GATE_RULES_WARNINGS`); a draft or a reviewing proposal with a placeholder commits.
- A project can raise the rule to error with its own severity override; this proposal changes no policy.
