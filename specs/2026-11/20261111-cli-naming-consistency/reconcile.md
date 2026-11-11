---
reconcile_id: REC-cli-naming-consistency
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconcile: `SPEC-cli-naming-consistency`

- `CAP-DIST-in-repo-bundles`: rule 6 makes the refresh preview the form with neither digest, rule 7 adds the
  `ARGUMENT_INVALID` refusal for one digest, the interface block drops `--check` and lists that refusal among
  the exit-2 codes (AC-01 to AC-04).
- `CAP-DLV-cli-and-output` §1: `envelope new` is no longer listed among the hidden authoring commands (AC-05).
- `CAP-DLV-spec-bundles`: rules 1 and 5, the command synopsis, the option table and the bugfix example describe
  `--task-kind feature|bugfix`, its exclusion with `--workflow` and the `ARGUMENT_INVALID` refusals, and the §4.5
  code table names the `--task-kind` conditions of `ARGUMENT_INVALID` and `SPEC_UNBOUND` (AC-06, AC-07).
- `docs/development/reference/distribution.md`: the refresh example and the preview/apply note.
- Outside the Living Spec, `guides/install/existing-repository.md`, the devkit bundle's `in-repo-bundle`
  instruction and the spec bundle's `spec`, `worktree` and `spec-specify` guidance carry the same forms (AC-08).

## No impact

- `UC-route-development-intent` and `ADR-delivery-classification` show `devkit spec new --workflow sdd-spec-bugfix`,
  which stays valid; no use case goal changes. `ADR-bundle-source-snapshots` names no refresh flag. No decision
  record changes.
- `CAP-DLV-workflow-envelopes` describes `envelope new` without its help visibility.
- Entrypoints: the touched capabilities already list their doorway files or are touched for behavior wording only;
  `devkit spec entrypoints derive` candidates were reviewed and none added.
