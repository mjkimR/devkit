# [RULE-reconcile-contract] Reconcile Record Contract

## 1. Overview

`reconcile.md` in a spec bundle records how the change was reconciled into the Living Spec (`docs/`): which files
changed with the work and which needed no change, and why. The `spec-sync` skill writes it; `RULE-spec-lifecycle`
requires it to be `resolved` before the spec is `completed`. The rule keeps the record well formed and, at commit
time, backed by the diff.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: every targeted `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/reconcile.md` of a current spec bundle. A
  completed bundle's record (its `spec.md` `status` is `completed`) is history, checked only when named as an
  explicit target.
- **Diff evidence**: in a snapshot run (`devkit rules check --staged`, which the commit gate runs, and `--ci` on a
  pull request), a well-formed `resolved` record that the diff changes must have each `modified` target changed or
  deleted on the branch: under `--ci` the whole branch against its merge base, at commit time the staged diff plus
  the branch's earlier commits since its merge base with the branch it integrates into (the `devkitBase` a `devkit
  worktree start --no-worktree` recorded, else the base checkout's branch, else `origin/HEAD`), so a Living Spec
  page committed at an earlier stage boundary counts. When no such base is found (work committed straight on the
  base branch), the staged diff alone is the evidence and earlier commits do not count. A record whose frontmatter is
  unchanged from the base claims nothing new and is not re-checked. A plain `devkit rules check` checks the form
  only.
- **Formal-document assessment**: the record's frontmatter indexes the design, domain and operations assessment its
  body details. A role is covered by affected IDs in its typed relation list (`related_designs`, `related_domains`,
  `related_operations`) or by `formal_docs.<role>: "none: <reason>"`, never both; `RULE-document-reference` checks
  that the listed IDs exist. A present `formal_docs` is checked for form in every run. In a snapshot run, a
  `resolved` record that the diff changes and that no parent of the commit has `resolved` MUST cover every role. The
  parents are the snapshot base and, in a staged run, each commit named by `MERGE_HEAD`, `CHERRY_PICK_HEAD` or
  `REVERT_HEAD` when present, so concluding a merge never requires coverage of a record the other branch resolved.
  A record resolved at the base, a `pending` record and every record in a plain run need no coverage.

## 2. Cause of Violation

Every violation is reported at line 1:

- No frontmatter: `reconcile.md has no frontmatter`; malformed frontmatter: `frontmatter is malformed: <reason>`.
- A missing or blank `reconcile_id`: `reconcile_id is missing`. Its value is `RULE-id-convention`'s concern.
- `status` other than `pending` or `resolved`: `status must be pending or resolved, got <value>`.
- `targets` missing or not a list: `targets must be a list (empty when nothing in the Living Spec is affected)`.
- A target that is not a mapping: `targets[<n>] must be a mapping of file, resolution and rationale`.
- A `file` that is not a unique workspace-relative path: `targets[<n>].file <value> must be a unique
  workspace-relative path`. A safe path not written in canonical form (`./docs/a.md`, `docs//a.md`, `docs/a/`):
  `targets[<n>].file <value> must be written in canonical form: <path>`, since uniqueness and the diff evidence
  compare paths as written.
- A `resolution` other than `modified` or `waived`: `targets[<n>].resolution must be modified or waived, got
  <value>`.
- A waiver whose `rationale` has fewer than 20 non-whitespace characters, since a waiver says why the file needs no
  change: `targets[<n>] waiver of <file> needs a rationale of at least 20 non-whitespace characters, has <count>`.
- `formal_docs` not a mapping: `formal_docs must be a mapping of design, domain and operations to a none reason`.
- A key other than `design`, `domain` or `operations`: `formal_docs.<key> is not a role: use design, domain or
  operations`.
- A value that is not a string starting `none: `: `formal_docs.<role> must be a string starting "none: " followed by
  the reason`.
- A reason after `none: ` with fewer than 20 non-whitespace characters: `formal_docs.<role> needs a reason of at
  least 20 non-whitespace characters, has <count>`.
- A role with both a nonempty relation list and a reason: `formal_docs.<role> conflicts with related_<roles>: give
  affected IDs or a none reason, not both`.
- In a snapshot run, a newly resolved record with a role covered by neither: `formal_docs role <role> is not covered:
  list affected IDs in related_<roles> or give formal_docs.<role>: "none: <reason>"`.
- In a snapshot run, a `modified` target the branch does not change: `target <file> is resolved as modified but
  absent from the staged diff or the branch's earlier commits` (commit time) or `... absent from the ci diff`.

## 3. Remediation

Not fixable. Give `reconcile.md` a `reconcile_id`, `status` `pending` or `resolved` and `targets` as a list of
`{file, resolution: modified|waived, rationale}` (`targets: []` when nothing in the Living Spec is affected), with a
rationale of at least 20 non-whitespace characters for each waiver. Cover each formal role: list the design, domain
or operations IDs the change creates, changes or retires in its relation list, or give a bounded source-based reason
`formal_docs.<role>: "none: <reason>"`. For a missing diff evidence, change the Living
Spec file on the branch (with the record or in an earlier commit), or correct the target's resolution.

## 4. Configuration

No settings.

## 5. Exceptions

No inline suppression. A Living Spec file that needs no change is recorded as `resolution: waived` with its
rationale, never left out of a `modified` claim.

## 6. Example

```yaml
---
reconcile_id: REC-<slug>
status: resolved            # pending while reconciliation is under way
targets:
  - file: docs/capabilities/core/CAP-CORE-search.md
    resolution: modified    # changed with this work
  - file: docs/usecases/core/UC-find-docs.md
    resolution: waived
    rationale: The use case's acceptance criteria are unchanged by the new ranking mode.
related_designs: [DESIGN-search-ranking]   # affected design IDs; a role is IDs or a reason, never both
formal_docs:
  domain: "none: ranking adds no concept, identity or lifecycle"
  operations: "none: no new symptom or action owner for search"
---
```
