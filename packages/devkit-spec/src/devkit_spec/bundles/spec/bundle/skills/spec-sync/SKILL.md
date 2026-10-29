---
name: spec-sync
description: Reconcile a completed feature spec and discovered behaviors into the durable Living Spec (docs/capabilities/, docs/usecases/) and its reconcile.md record, so documentation never rots.
---

# spec-sync: Living Specification Reconciliation Workflow

Run at `living-spec-draft`, after `spec-review` passes; write `docs/` by the `living-spec-writing` instruction. The
`spec` skill's `references/completion.md` owns record and evidence rules; its `references/effort.md` and
`references/review-loop.md` own verification by effort.

## Steps

1. **Impact**: find affected documents from `spec.md` and the diff (`devkit docs refs <ID> --direction in`,
   `devkit docs search "<topic>"`). Update or create capabilities, use cases (templates in
   `.devkit/managed/docs/templates/`) and `docs/architecture/`; if the change did introduce or rename a domain term,
   update `docs/steering/glossary.md` where it exists. No index tables in directory `README.md` files.
   - Screens: write each draft of the spec's `Screens` section to `docs/ux/<area>/UX-<slug>.md` (template `ux`) with
     its step citations to the use cases, and the `Screens` section's register rows to `docs/steering/ux-objects.md`
     (created with the project's first UX document); make plain-text new IDs code spans. `RULE-ux-links` and
     `RULE-ux-coverage` check them from then on.
   - Copy no user stories into `docs/` (they state the request, not the contract); fold the delivered behavior into
     the use cases it changes: steps, extensions with codes, postconditions, scenarios (`usecase-writing`).
2. **Record**: create `reconcile.md` in the bundle with one target per changed Living Spec file, or no-impact
   reasoning in the body:

   ```yaml
   ---
   reconcile_id: REC-<slug>
   status: pending            # pending | resolved
   targets:
     - file: docs/capabilities/<area>/CAP-<AREA>-<slug>.md
       resolution: modified   # modified | waived (with a substantive rationale)
   ---
   ```

   Every written UX document, changed use case and `docs/steering/ux-objects.md` is a target; every drafted screen
   has a `docs/ux/` target.
3. **Deferred work and source feedback**: apply `completion.md`'s Deferred Work Handoff and
   [source feedback](../spec/references/source-feedback.md); record destinations and resolutions in `reconcile.md`.
4. **Entrypoints**: run `spec-entrypoints` for this bundle.
5. **Verify**: run the reconcile check for the effort; record it with
   `devkit workflow envelope new --unit <dir> --kind reconcile-check --stage living-spec-draft` (other flags: the
   `spec` skill's [envelope reference](../spec/references/envelope.md)). Return an implementation-versus-contract
   mismatch to `build-verify` (`fix-verify` for a bugfix); never document it away. Run `devkit rules check --staged`
   or `--ci --base <ref>`, plus the project lint where it covers Markdown.
6. **Complete**: once every target is reflected or waived, set `reconcile.md` `status: resolved`, then
   `devkit rules fix <dir>/spec.md` sets the spec `completed`. Commit the documentation with the feature code or
   right after it.

## Completion

- [ ] `devkit workflow next --unit <dir>` shows `frontmatter(reconcile.md status resolved)` and
  `anchor-status-completed` met.
- [ ] `devkit rules check` (`--staged` or `--ci --base <ref>`) and the project lint pass.
