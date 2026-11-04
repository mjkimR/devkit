# Global roadmap root inventory (Planning spike, Q1)

Every place that hard-codes the global roadmap root `docs/roadmap/` or treats the milestone kind as global only, with
the change the namespace root needs. Line numbers are those of the Planning branch head; a kind- or status-based
location needs no change and is listed to show it was examined.

## Code

| Location | Today | Needed change |
| --- | --- | --- |
| `packages/devkit-docs/src/devkit_docs/features/documents/models/milestones.py:8` (`milestone_path_valid`) | Regex `docs/roadmap/(_archive/)?MS-<slug>.md` | Unchanged. Callers pass `living_path(path, namespaces=registered)`, which already maps `docs/packages/<name>/roadmap/X` to `docs/roadmap/X` for a registered namespace and leaves an unregistered one as it is. |
| `packages/devkit-docs/src/devkit_docs/features/governance/usecases/id_convention.py:371-392` | Walks `{docs_root}/roadmap` for every docs root, then `valid = docs_root == "docs" and milestone_path_valid(path, status)`; the remediation at lines 102, 390 and 405 names the global root only | Validate `milestone_path_valid(living_path(path, namespaces=registered), status)`; name both roots in the remediation (`docs/roadmap/` or `docs/packages/<name>/roadmap/`, `_archive/` for done/dropped). |
| `packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py:286-299` (`Kind.MILESTONE` row) | `format_scope=FormatScope.GLOBAL`: `RULE-spec-format` scans `docs/roadmap` only | `FormatScope.EVERY_ROOT`, so `_directories` adds `docs/packages/<name>/roadmap` for each registered namespace (the `_archive/` subdirectory is reached by the recursive file walk). |
| `packages/devkit-docs/src/devkit_docs/features/governance/usecases/spec_format.py:164-176` | `if path.startswith("docs/roadmap/")` guards the milestone status set and `created_at` checks | Test `living_path(path, namespaces=registered).startswith("docs/roadmap/")`. |
| `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py:12-31` (`milestone_id`, the `--milestone` validation) | `milestone_path_valid(found[0].path, found[0].status)` and the message "one existing global milestone" | Validate through `living_path` with the registered namespaces; message and fix name a milestone at either root and `devkit docs list milestone --all-namespaces`. |
| `packages/devkit-docs/src/devkit_docs/features/documents/repositories/index.py:70-73, 223` | Discovery covers every file under `docs/` (so `docs/packages/<name>/roadmap/` is indexed today); `historical` is status-based | No change. |
| `packages/devkit-docs/src/devkit_docs/features/documents/services/namespaces.py:108-137` (`namespace_of`, `living_path`, `docs_roots`) | Membership by docs root; mapping limited to registered namespaces | No change; these supply the namespace layer the proposal relies on. |
| `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py:171-176` | `depends_on` graph over every `Kind.MILESTONE` document | No change: IDs are repository-wide, so a cross-namespace edge resolves. |
| `packages/devkit-spec/src/devkit_spec/features/governance/usecases/hygiene.py:64-95` (`milestone_members`) | Kind- and status-based over the index | No change. |
| `packages/devkit-docs/src/devkit_docs/features/documents/models/parse.py:71-78` | `depends_on`/`milestone` field shapes by kind | No change. |
| `packages/devkit-viewer/src/devkit_viewer/features/browse/repositories/worktree.py:149-151, 177-179` | Dashboard roots `docs/roadmap`, `docs/roadmap/_archive`; the viewer reads the Git tree without the namespace registry | Out of this proposal unless the user decides otherwise (Planning question q1); `CAP-VIEW-repository-viewer` 4.1 restates the global roots as a MUST. |

## Tests

| Location | Content |
| --- | --- |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/tests/` | Milestone placement fixtures (global roots); gains the namespace fixtures named in the proposal. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/spec_format/tests/test_rule.py:285-305` | Milestone status and `created_at` fixtures at `docs/roadmap/`; gains a namespace root fixture. |
| `packages/devkit-spec/tests/integration/features/proposals/test_roadmap.py` | `--milestone` validation; gains a namespace milestone. |
| `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_archive_guidance.py` | Guidance text assertions on the shipped references. |

## Documents and bundle text

| Location | Text to generalize |
| --- | --- |
| `docs/capabilities/documents/CAP-DOCS-namespaces.md` 3.4 (and the kinds a namespace mirrors) | Add `roadmap/` to the directories the rules treat like `docs/`. |
| `docs/capabilities/governance/CAP-GOV-spec-rules.md` "Milestone validation contract" (line 480) | "Other nesting and namespace roadmap locations are invalid" becomes the two-root rule; the `RULE-spec-format` scope list (line 202) gains the namespace roadmap. |
| `docs/capabilities/delivery/CAP-DLV-proposal-planning.md` lines 264 and 502 | "one existing global MS ID" becomes a milestone at either root. |
| `docs/architecture/ARCH-01-introduction-and-goals.md` "Repository roadmap" (line 53-55) | Names the namespace root beside `docs/roadmap/`. |
| `docs/decisions/2026-11/20261102-roadmap-and-milestones-ledger.md` lines 208-209 | Gains the "Superseded in part by" pointer (Development writes it). |
| `docs/roadmap/README.md` | "Milestones are global documents" becomes the two roots. |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja` lines 3, 19, 69-70; `roadmap-catalog.md` line 3; `milestone-completion.md` step 3 and Later changes | Name the milestone's own roadmap root instead of `docs/roadmap/`. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/milestone.md` lines 33-34 | Placement sentence names the roadmap root the milestone lives under. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/guide.md` line 42, 59; `rules/spec_format/guide.md` lines 11-12 | Milestone row and scope sentence gain the namespace root. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/architecture/ARCH-01-introduction-and-goals.md` line 27 | Seeded roadmap sentence; optional, names the namespace root. |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/next-work.md` | Already lists milestones with `--all-namespaces`; no change. |

## Selection (Q3 evidence)

`devkit docs list milestone` follows `CAP-DOCS-namespaces` 3.3: from a package directory the default selection is that
package plus the global documents, from the repository root (inside no docs root and no source path) every namespace,
and `--namespace`/`--all-namespaces` behave as for the other kinds. Membership of a milestone under
`docs/packages/<name>/roadmap/` is `<name>` by 3.2 rule 1 without any change.

## Consumer evidence

`playground/g-sandbox` keeps five package docs directories under `docs/packages/` (`platform`, `caravan-trade`,
`scavenger-crew`, `wasteland-gunsmith`, `workshop-mercenary`), each with its own `steering/`, and no `docs/roadmap/`
at all; it has not adopted devkit yet (no `.devkit/config.toml`), so none of the five is a registered namespace today.
Once registered, their milestones have nowhere valid to live without this proposal.
