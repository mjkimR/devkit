# [RULE-proposal-boundaries] Proposal Boundaries Name Existing Paths

## 1. Overview

A proposal's `target_area` and `boundaries.owns` are copied into its spec at handoff as the carried scope and the
first task boundary. The rule keeps them pointing at real paths, so the boundary handed to Development names what
exists. The Planning executor clears its reports before the `plan-accept` request.

- **Phase and severity**: `linter`, `warning`: a report never refuses a commit, so a Backlog draft can keep the
  template placeholder until Planning settles the area.
- **What is checked**: proposal anchors (`docs/proposals/PROP-<slug>/proposal.md` and single-file
  `docs/proposals/PROP-<slug>.md`) whose `status` is `draft`, `reviewing` or `accepted`; `rejected` proposals are
  skipped. In each, `target_area` (optional; absent is not reported) and every `boundaries.owns` item.
  `boundaries.excludes` is not checked.
- **Resolution**: an entry is a literal repository-relative path and resolves when it names an existing path, tried
  in this order:
  1. relative to the repository root (`packages/devkit-spec/src/devkit_spec/`, `docs/glossary.md`);
  2. relative to the proposal's namespace docs root (`docs/packages/<name>/`, when `namespace` names a registered
     namespace), then to `docs/` (`capabilities/delivery/`, `stories/delivery/`);
  3. as a capability area under the namespace's `capabilities/`, then `docs/capabilities/` (`delivery/`).

  A trailing `/` requires a directory. A bare entry that matches a repository directory resolves there first: `src/`
  names the repository's `src/`, never a capability area of that name.
- **Paths the Development will create**: name the nearest existing parent directory (for a new rule folder,
  `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/`) and name the new path itself in the proposal text.
- **Targeting**: reported for the targeted anchors and in a whole-workspace run. There is no rescan for deleted
  paths, and a run targeting `.devkit/config.toml` does not recheck proposals. Snapshot runs (`--staged`, `--ci`)
  resolve paths in the snapshot's tree, where an empty directory does not exist.

## 2. Cause of Violation

Reported at the entry's line, or at its key:

- `target_area` is not a string: `target_area must be a path string`.
- `boundaries` is not a mapping: `boundaries must be a mapping with owns`.
- `owns` is not a list: `boundaries.owns must be a list of path strings`; an item is not a string:
  `boundaries.owns must contain only path strings`.
- An entry contains `<...>` (the template's `capabilities/<area>/`):
  `<field> entry '<value>' is the template placeholder; name the area`.
- An entry is absolute, has a `..` segment, a glob character, a backslash, a colon or a control character:
  `<field> entry '<value>' is not a literal repository-relative path`.
- No candidate exists: `<field> entry '<value>' names no existing path (repository path, docs-root path or capability
  area)`, or `... no existing directory ...` for an entry ending in `/`.

## 3. Remediation

Not fixable: the rule cannot know the intended area. Name the capability area or repository path the proposal owns;
for a path the Development will create, its nearest existing parent directory. An `accepted` proposal is never edited:
when an owned path moves after acceptance, the warning stays, and Development treats the boundary that no longer holds
as a problem.

## 4. Configuration

No settings. A project may raise the rule to `error` with its own severity override.

## 5. Exceptions

No inline suppression. `[rules] exclude` removes a file from every rule.

## 6. Example

```yaml
target_area: delivery/                       # a capability area
boundaries:
  owns:
    - capabilities/delivery/                 # docs-root path
    - packages/devkit-spec/src/devkit_spec/   # repository path
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/   # parent of a rule folder the Development creates
  excludes: []
```
