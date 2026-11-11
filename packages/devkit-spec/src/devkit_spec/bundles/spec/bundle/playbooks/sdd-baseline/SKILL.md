---
name: sdd-baseline
description: "Adopt SDD from an implemented adaptive-development product: verify the user-selected retained behavior, structure, choices and project checks, prepare current documents and an evidence report, then activate SDD on the user's decision without reconstructing experiment history."
---

# SDD baseline adoption

Use only when the user invokes or confirms this playbook to adopt SDD from adaptive development; elapsed time, code
size and experiment count never start it.

## Constraints

- Reuse existing current documents and evidence; create only what the selected retained product needs.
- Preserve unrelated edits and existing SDD history, including completed Units and accepted SDD decisions; keep
  unrelated edits and bounded exclusions visible, recovery included.
- Create no retrospective proposal, spec Unit, workflow approval, envelope or ADR for a discarded experiment.
- Describe retained choices and known reasons as current facts; label unknown reasons instead of inventing history.
- Use applicable independent build, lint, tests and actual usage checks; skipped or unavailable required evidence is
  a gap.
- Leave product corrections, document deletion and legacy containment outside this playbook unless separately
  authorized.

## 1. Establish scope and keep adaptive development active

1. Read relevant run instructions, current documents, implementation and any adaptive-dev current context (goal,
   constraints, retained choices, assumptions, run evidence) without requiring a context filename or parser.
2. Record repository identity, exact HEAD, relevant dirty paths, effective approach and selected assets: inspect JSON
   `configuration.development.approach` and `sources["development.approach"]` from `uv run devkit config show`. If
   the project already uses SDD, use ordinary reconciliation or brownfield adoption instead of claiming a graduation.
3. Identify the user-selected retained behavior and representative flows, important structure and interfaces,
   current choices and exclusions. Reuse decisions already supplied; present remaining scope uncertainty before
   rewriting documents.
4. If the spec package or assets are absent, present their installation and selection effects and follow the
   repository's supported installation instructions. Keep the effective approach adaptive-dev during package and
   asset preparation; preparation, package installation and `uv run devkit add spec` never establish readiness or
   authorize activation.
5. Run `uv run devkit get-context docs` before document authoring. Read the
   [report template](references/report-template.md) when opening or resuming the report. Write the report as an
   ordinary material, with no workflow binding or lifecycle status, in the repository's ordinary evidence location;
   default to `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`.

## 2. Compare the retained product with evidence

1. For each retained item, record in the report its implementation location, current document or missing-document
   destination, applicable check or usage observation, source identity and result. Mark it `verified`, `gap` or
   `excluded`; excluded items never count as verified coverage.
2. Draft or correct current capabilities, use cases, architecture, retained-choice documents and run instructions
   only where that coverage needs them, reusing accurate documents; a complete architecture set or one ADR per
   experiment is not required.
3. Run the applicable project commands and exercise representative retained user flows. Record exact commands or
   interactions, revision or dirty source identity, environment, observed outcome and limitations. A passing
   document-format check proves only its checked conditions, not semantic product readiness.
4. Present mismatches together for disposition: correct the document, separately authorize a behavior correction,
   narrow the retained scope on the user's decision, or defer adoption and remain in adaptive development. Never
   waive a required retained behavior or missing required evidence into readiness.
5. Re-run affected checks and compare corrected documents to implementation until retained coverage has no
   unresolved mismatch or required evidence gap. Stop before activation while a retained item is `gap`, an
   applicable required check failed or was skipped, or usage evidence is missing. State bounded coverage and
   exclusions instead of inferring whole-repository consistency from a selected product scope.

## 3. Activate only the ready effects

1. Recheck the relevant source and dirty paths against report evidence; if they changed, invalidate affected
   observations and repeat the affected comparison and checks before readiness.
2. Present the ready report and revision, retained scope, actual check outcomes, selected SDD assets and exact
   policy effects. Reuse an explicit user decision already bound to the same source and effects; otherwise obtain
   that decision now. Preparation intent alone does not authorize activation against an unknown final scope.
3. Edit only `.devkit/config.toml` to set `[development] approach = "sdd"`, in the existing `[development]` table
   when present instead of a duplicate table, and preserve the rest of the shared configuration.
   Preserve approval, worktree, other integration and project-check settings unless their change was authorized.
   Introduce no universal SDD settings profile and no second approach source.
4. Run `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy` and `uv run devkit sync --check`.
   Verify the effective approach is SDD, selected guidance agrees and the next requested change enters ordinary SDD
   routing. Re-run affected document and project checks if activation changed their inputs.
5. Record the observed final policy and asset state and remaining limitations in the report. Later changes follow
   ordinary selected SDD policies; the baseline creates no historical delivery Units.

## Recovery

- If installation, policy update or sync fails, record the failed command and the actual partial policy, asset and
  file state, and report the next supported recovery action; claim neither successful adoption nor automatic
  rollback.
- Resume from the existing report after revalidating source and affected evidence, without duplicating baseline
  documents.

## Completion

- Every retained item has truthful current-state documentation and observed verification evidence, with no
  unresolved mismatch or missing required evidence.
- The user's decision covers the exact ready source, scope and activation effects.
- Inspection reports SDD, `uv run devkit sync --check` exits `0`, and selected guidance and next development
  routing agree.
- The report states actual outcomes and limitations without invented prior approvals, discarded decisions or
  delivery history.
