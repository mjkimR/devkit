---
name: sdd-baseline
description: "Adopt SDD from an implemented incubation product: verify the user-selected retained behavior, structure, choices and project checks, prepare current documents and an evidence report, then activate SDD on the user's decision without reconstructing experiment history."
---

# SDD baseline adoption

Use only when the user invokes or confirms this playbook to adopt SDD from incubation.
A working app can remain in incubation; elapsed time, code size and experiment count never start this procedure.
Preparation and package selection do not activate SDD.

## Constraints

- Reuse existing current documents and evidence; create only what the selected retained product needs.
- Preserve unrelated edits and existing SDD history, including completed Units and accepted SDD decisions.
- Create no retrospective proposal, spec Unit, workflow approval, envelope or ADR for a discarded experiment.
- Describe retained choices and known reasons as current facts; label unknown reasons instead of inventing history.
- Use applicable independent build, lint, tests and actual usage checks; skipped or unavailable required evidence is a gap.
- Leave product corrections, document deletion and legacy containment outside this playbook unless separately authorized.

## 1. Establish scope and keep incubation active

1. Read relevant run instructions, current documents, implementation and any available incubation context.
   Consume current goal, constraints, retained choices, assumptions and run evidence without requiring a context filename or parser.
2. Record repository identity, exact HEAD, relevant dirty paths, effective approach and selected assets.
   Run `uv run devkit config show` to inspect JSON `configuration.development.approach` and `sources["development.approach"]`.
   If the project already uses SDD, use ordinary reconciliation or brownfield adoption rather than claim a graduation.
3. Identify the user-selected retained behavior and representative flows, important structure/interfaces, current choices and exclusions.
   Reuse decisions already supplied; present remaining scope uncertainty before rewriting documents.
4. If the spec package or assets are absent, present their installation/selection effects and follow the repository's supported installation instructions.
   Keep the effective approach incubation during package and asset preparation.
   Package installation and `uv run devkit add spec` alone never establish readiness or authorize activation.
5. Run `uv run devkit get-context docs` before document authoring.
   Read the baseline report template [when opening or resuming the report](references/report-template.md).
   Reuse the repository's ordinary evidence location; default to `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`.
   The report is an ordinary material, with no workflow binding or lifecycle status.

## 2. Compare the retained product with evidence

1. For each retained item, connect its implementation location, current document or missing-document destination,
   applicable check or usage observation, source identity and result in the report.
   Mark each item `verified`, `gap` or `excluded`; excluded items never count as verified coverage.
2. Draft or correct current capabilities/use cases, architecture, retained-choice documents and run instructions only where that coverage needs them.
   A complete architecture set or one ADR per experiment is not required.
   Reuse accurate documents rather than duplicate them.
3. Run the applicable project commands and exercise representative retained user flows.
   Record exact commands/interactions, revision or dirty source identity, environment, observed outcome and limitations.
   A passing document-format check proves its checked conditions; it does not prove semantic product readiness.
4. Present mismatches together for disposition: correct the document, separately authorize a behavior correction,
   narrow the retained scope on the user's decision, or defer adoption and remain in incubation.
   Never waive a required retained behavior or missing required evidence into readiness.
5. Re-run affected checks and compare the corrected documents to implementation until retained coverage has no unresolved mismatch or required evidence gap.
   Stop before activation while a retained item is `gap`, an applicable required check failed/skipped, or usage evidence is missing.
   State bounded coverage and exclusions; do not infer whole-repository consistency from a selected product scope.

## 3. Activate only the ready effects

1. Recheck the relevant source and dirty paths against report evidence.
   If they changed, invalidate affected observations and repeat the affected comparison/checks before readiness.
2. Present the ready report/revision, retained scope, actual check outcomes, selected SDD assets and exact policy effects, including the integration provider.
   If the provider is absent or `project`, present configuring `spec` as a necessary activation effect; retain an existing `spec` provider.
   For another configured provider, verify its SDD readiness contract or report the unresolved compatibility before activation.
   If that provider change is not authorized, report the mismatch and do not claim successful SDD adoption.
   Reuse an explicit user decision already bound to the same source and effects; otherwise obtain that decision now.
   Preparation intent alone does not authorize activation against an unknown final scope.
3. Edit only `.devkit/config.toml` to set `[development] approach = "sdd"`; preserve the rest of the shared configuration.
   Use the existing `[development]` table when present instead of creating a duplicate table.
   If the authorized effects include the necessary provider change, set `[integration] provider = "spec"` in the same shared configuration.
   Preserve approval, worktree, other integration and project-check settings unless their change was authorized.
   Do not introduce a universal SDD settings profile or a second approach source.
4. Run `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy` and `uv run devkit sync --check`.
   Verify the effective approach is SDD, selected guidance agrees and the next requested change enters ordinary SDD routing.
   Re-run affected document/project checks if activation changed their applicable inputs.
5. Record observed final policy/asset state and remaining limitations in the report.
   Subsequent changes follow ordinary selected SDD policies; the baseline creates no historical delivery Units.

## Recovery

- If installation, policy update or sync fails, record the actual partial policy/asset/file state and the failed command.
- Report the next supported recovery action; claim neither successful adoption nor automatic rollback.
- Resume from the existing report after revalidating source and affected evidence; do not duplicate baseline documents.
- Keep unrelated edits and bounded exclusions visible throughout recovery.

## Completion

- Every retained item has truthful current-state documentation and observed verification evidence.
- No unresolved retained-scope mismatch or missing required check/usage evidence remains.
- The user's decision covers the exact ready source, scope and activation effects.
- Inspection reports SDD, `uv run devkit sync --check` exits `0`, and selected guidance and next development routing agree.
- The report identifies actual outcomes and limitations without invented prior approvals, discarded decisions or delivery history.
