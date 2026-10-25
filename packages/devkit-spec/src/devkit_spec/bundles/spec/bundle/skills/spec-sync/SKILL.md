---
name: spec-sync
description: Reconcile a completed feature spec and discovered behaviors into the durable Living Spec (docs/capabilities/, docs/usecases/) and its reconcile.md record, so documentation never rots.
---

# spec-sync: Living Specification Reconciliation Workflow

Use this skill at the `living-spec-draft` stage, after `spec-review` passes. Write `docs/` by the
`living-spec-writing` instruction. The record and evidence rules are in the `spec` skill's `references/completion.md`;
verification by effort is in its `references/effort.md` and `references/review-loop.md`.

## Steps

1. **Impact**: from `spec.md` and the code changes, find affected documents (`devkit spec refs <ID> --direction in`,
   `devkit spec search "<topic>"`). Update or create capabilities, use cases (templates in
   `.devkit/managed/spec/templates/`) and `docs/architecture/`; if the change did introduce or rename a domain term,
   update `docs/glossary.md` where it exists. Write no index tables in directory `README.md` files.
   - The spec's user stories state the request, not the contract; copy none into `docs/`. Fold the delivered behavior
     into the use cases it changes: new or changed steps, extensions with their codes, postconditions and scenarios
     (`usecase-writing`).
2. **Record**: create `reconcile.md` in the bundle, one target per changed Living Spec file, or the no-impact
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

3. **Deferred work and source feedback**: apply the Deferred Work Handoff of `completion.md` and
   [source feedback](../spec/references/source-feedback.md), and record destinations and resolutions in
   `reconcile.md`.
4. **Entrypoints**: run the `spec-entrypoints` skill for this bundle.
5. **Verify**: run the reconcile check for the effort and record it with
   `devkit workflow envelope new --unit <dir> --kind reconcile-check --stage living-spec-draft`; the other flags are in
   the `spec` skill's [envelope reference](../spec/references/envelope.md). Return an
   implementation-versus-contract mismatch to `build-verify` (`fix-verify` for a bugfix); never document it away.
   Run `devkit rules check --staged` or `devkit rules check --ci --base <ref>`, plus the project lint where it covers
   Markdown.
6. **Complete**: once every target is reflected or waived, set `reconcile.md` `status: resolved`, then run
   `devkit rules fix <dir>/spec.md` to set the spec `completed`. Commit the documentation with the feature code or
   right after it.

## Completion

- [ ] `devkit workflow next --unit <dir>` shows `frontmatter(reconcile.md status resolved)` and
  `anchor-status-completed` met.
- [ ] `devkit rules check` (`--staged` or `--ci --base <ref>`) and the project lint pass.
