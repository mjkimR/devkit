---
name: spec-sync
description: Reconcile a completed spec into the Living Spec (docs/capabilities/, docs/usecases/) and its reconcile.md record.
---

# spec-sync: Living Specification Reconciliation Workflow

Run at `living-spec-draft`, after `spec-review` passes; write `docs/` by the `living-spec-writing` instruction. The
`spec` skill's `references/completion.md` owns record and evidence rules; its `references/effort.md` and
`references/review-loop.md` own verification by effort.

## Steps

1. **Impact**: find affected documents from `spec.md` and the diff (`devkit docs refs <ID> --direction in`,
   `devkit docs search "<topic>"`). Update or create capabilities, use cases (templates in
   `.devkit/managed/docs/templates/`) and `docs/architecture/`; if the change did introduce or rename a domain term,
   update the owning `docs/steering/glossary.md` or `docs/packages/<name>/steering/glossary.md` where it exists. No index tables in directory `README.md` files.
   - Assess design, domain and operations against the implemented diff: affected IDs/statements, source identity,
     owner, action and evidence, or a bounded unaffected reason. Use the core per-kind instruction and template.
     Do not require unaffected layers or whole-layer traversal.
   - Screens: if `spec.md` has a `Screens` section, write its drafts and register rows by
     [screens](references/screens.md).
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

   Include every modified or deleted formal document and support file as a `modified` target. Compare removed
   paths and their replacements explicitly in the body; required mismatches cannot be waived. Ordinary support
   links need actual destination checks, beyond formal reference rules.

   Every written UX document, changed use case and modified root or namespace `steering/ux-objects.md` is a target; every drafted screen
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

## Formal document maintenance

- Create/update: compare the retained source identity and statements, sole owner and useful current routes. Give
  independent details their own formal IDs; regenerate a supporting artifact only when its actual source changed.
- Support location: a DESIGN keeps support files beside `design.md` in its bundle
  `designs/<area>/DESIGN-<slug>/`; a DOMAIN or OPS keeps them in the sibling `<ID>/artifacts/` directory.
- Rename/root move: move a DESIGN's whole bundle directory, or a DOMAIN/OPS file together with its
  `<ID>/artifacts/` directory. For same-kind rename keep the old-ID alias; unchanged-ID area and root moves need
  none. Repair current prose/typed references with `devkit rules fix`, ordinary incoming/support links and relative
  source links inside and outside the moved bundle or support directory. Check global and registered namespace
  destinations, collisions and absence of old folders; an alias never legalizes an orphan.
- Split: allocate every statement, independent detail and retained artifact to exactly one canonical owner. Move
  each support file to its owner's support location and repair links; leave no stale duplicate. Keep an old active
  ID only if it still owns a maintained subject; otherwise retire it and link useful successors. Never alias one ID
  to two nodes.
- Reclassify: retire the old identity and create the receiving kind's canonical node. Transfer sole statement and
  artifact ownership, repair current routes/ordinary links and reject cross-prefix aliases.
- Retire: retain resolvable history/provenance and useful successors without ADR supersession fields. In the same
  change as source deletion, remove/replace obsolete DESIGN entrypoints while retaining useful live anchors; put
  removed source coordinates only in explicitly historical prose with the source commit. DOMAIN/OPS use body
  source/action-owner links. Retired nodes remain rule-checked. Verify shared support users before moving/removing
  files; keep every retained artifact under one live or retired canonical parent, or historical materials with provenance.

Verify canonical/alias resolution, incoming/outgoing refs, namespace selection, actual ordinary link destinations,
source agreement and support bytes after composed operations. Formal reference checks do not prove ordinary links.
