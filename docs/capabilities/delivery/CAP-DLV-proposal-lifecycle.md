---
id: CAP-DLV-proposal-lifecycle
title: Proposal lifecycle commands and handoff
summary: "Proposal lifecycle operations validate and carry approved scope into a spec, preserving decisions, feedback and references. CLI, library, output and recovery contracts separate confirmed Git effects from pending final verification."
area: delivery
status: active
created_at: 2026-11-10
usecases:
  - UC-plan-and-hand-off-a-proposal
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
  - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/accept.py
---

# [CAP-DLV-proposal-lifecycle] Proposal lifecycle commands and handoff

## 1. Summary

These operations create proposal/PADR files and carry an accepted proposal across layouts into Development.
Composed acceptance and handoff also perform guarded Git lifecycle effects under Host-carried authority.

## 2. Scope & Boundary

- **In-Scope**: handoff writes, body and reference relocation, prune, command/library/output/error interfaces,
  composed acceptance/handoff, review reports and partial-effect recovery.
- **Out-of-Scope**: Planning/layout/eligibility and preservation policy (`CAP-DLV-proposal-planning`); workflow
  evaluation (`CAP-DLV-workflow-orchestration`); generic spec scaffolding (`CAP-DLV-spec-bundles`).
- **Non-Goals**: **Scope Excluded**: inferring approval, dispatching agents or granting publication authority.

## 3. Business Rules & Policies

1. **Planning policy**: Lifecycle operations MUST retain the approval, eligibility, preservation and retirement
   policies in `CAP-DLV-proposal-planning` §3; the interfaces below define their execution and recovery.
2. **Verification boundary**: Confirmed Git effects MUST remain distinct from pending landed-head verification,
   as specified under Host-authorized proposal lifecycle CLI.

## 4. Interfaces & Data Contracts

### 4.1 Handoff Steps

Before its first write, handoff MUST validate the projected live unit dependency graph: replace the source
PROP anchor with the new SPEC, carry outgoing edges and rewrite live incoming depends_on targets, written with the
proposal's ID or one of its aliases, in memory; every other document keeps its aliases in the projection.
Exclude the source PROP from the projection; a pre-existing same-slug SPEC is still a collision. Malformed lists,
missing/ambiguous/wrong-kind or auxiliary anchors and live cycles refuse with SPEC_PROPOSAL_INVALID and a repair
directive, without writes. Completed SPEC targets are terminal; retained completed history is not rewritten.
Existing write rollback remains in force. Reference relocation is not fulfillment or persistent lineage.

With `<YYYY-MM>` and `<YYYYMMDD>` today's date:

1. **Spec bundle** `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` with the skeletons of `CAP-DLV-spec-bundles`: `spec.md`
   (`SPEC-<slug>`, the proposal's `summary`, `status: planned`, `created`, the proposal's `namespace` and
   nonempty `depends_on`, `decomposed_from` and `supersedes`, and the proposal's `aliases` with `PROP-` replaced by
   `SPEC-` (`CAP-DOCS-document-model` section 3.5); milestone membership is not carried; the two origin fields are provenance and do not require the source to survive. The problem statement starts with `Handed off from proposal PROP-<slug> on <date>.` and the
   preserved materials and blueprint references, then the carried body), `plan.md` (target area, blueprint
   reference, planned and excluded boundaries) and `tasks.md` (one task whose boundary is `boundaries.owns`, else
   `target_area`, and whose `_Requirements:` lists every acceptance criterion ID).
2. **Workflow binding** of `spec.md` to `sdd-spec-<task_kind>`. For `task_kind: bugfix` the workflow MUST resolve
   and validate, or the handoff fails before writing (`SPEC_PROPOSAL_WORKFLOW_INVALID`, the devkit code in its
   details). For `feature` (or no field), `sdd-spec-feature` is bound when the project has it; otherwise `spec.md`
   stays unbound with a `SPEC_PROPOSAL_UNBOUND` notice. An `sdd-spec-bugfix` spec gets `spec.md` only; the target
   area and boundaries go into a `### Target Area & Boundaries` section of its carried notes.
3. **Blueprint**: `target-docs.md` is copied into the spec bundle as written; step 6 then rewrites its `proposal`
   provenance and its links like those of any other file.
4. **PADR promotion**: each `decisions/PADR-<slug>.md` becomes `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`. Every
   `PADR-<slug>` in it becomes `ADR-<slug>`, a frontmatter `status: draft` (or `proposed`) becomes
   `status: accepted`, and a body line `- **Status**: Draft` (or `Proposed`) becomes `- **Status**: Accepted`. The
   rest of the frontmatter, `summary` included, is kept, except that each item of the PADR's `aliases` has `PADR-`
   replaced by `ADR-`, so the own-prefix rule holds after the rename. Only the IDs of the PADRs this handoff promotes
   change, and never inside a file name (`PADR-<slug>.md` in a link is left to step 6). Other files under
   `decisions/` are not promoted. A `supersedes` reaches the ADR unchanged, and the scaffold's commented
   `# supersedes:` line, left unchanged, is dropped. For each `supersedes` entry that resolves to one ADR whose
   status is not `superseded`, the handoff MUST write one body line "Superseded in part by `ADR-<new>`: <clause>"
   below that ADR's first H1 heading (after the frontmatter when it has none), as a paragraph of its own, in
   promotion order when several PADRs name the same ADR, and MUST NOT write it when a visible line of that ADR
   already names the promoted ADR by its ID or an alias; `<clause>` is the promoted ADR's partial-supersession
   statement source text for that target, copied verbatim. A missing statement MUST fail with `SPEC_PROPOSAL_INVALID`
   before the first write; its error names the PADR and target and its fix names the statement to add.
   A composed handoff preserves its created worktree and proposal on this handoff-step failure. The pointer is the
   line `RULE-decision-supersession` requires, so the handoff commit passes the gate; each line is reported as
   `[SUPERSEDED_IN_PART: <adr> path= line= by=]` (JSON `pointers`). The handoff writes no `status: superseded` or
   `superseded_by` (a whole supersession is the author's edit), and an entry that resolves to nothing, to several
   documents or to a non-ADR is left to `RULE-document-reference`
   (`SPEC-proposal-scaffold-and-handoff-pointers`).
5. **Feedback and materials**: open `feedback/*.md` files move into the new spec's feedback directory;
   settled feedback follows the generic extras route. `materials/` moves to `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` when it holds a file other
   than operating-system junk (`.DS_Store`, `Thumbs.db`, `desktop.ini`) or a symbolic link. Every other bundle file the
   steps above do not carry (settled feedback, a `notes.md` beside `proposal.md`, an image, a non-PADR file under `decisions/`, a
   hidden file other than junk) moves into the same directory, except the unit's workflow records (`CAP-DLV-proposal-planning` rule 12), at its path relative to the bundle, which is created
   for them when `materials/` is not moved. Junk is never carried and is deleted with the proposal. Symbolic links
   are moved as links, never followed: a carried file whose path in `materials/` is taken, or lies below a file or
   symbolic link there or below a `materials/` that is itself a symbolic link, and a destination (the spec bundle,
   an ADR, the materials directory, a carried file) whose directory resolves outside the workspace are refused
   before writing (`SPEC_PROPOSAL_TARGET_EXISTS`).

   **Merging into an existing materials directory** (`ADR-proposal-handoff`): when the
   dated directory already exists, the handoff merges into it per leaf, planned in one preflight pass over the
   `materials/` leaves and the carried files:

   - The directory and every existing directory on the way to a planned path MUST be a real directory by `lstat`; a
     symbolic link or a file there is a conflict.
   - A real directory present on both sides is descended into; an absent path is moved, a directory as a whole when
     it holds material (one holding only junk or nothing stays with the proposal); the destination's other files are
     left alone. Non-symlink junk of the proposal is dropped; junk of the destination is ignored.
   - A path that is a regular file on both sides by `lstat` with identical bytes is a duplicate: the destination file
     stays as it is and the proposal copy is deleted with the proposal.
   - Differing bytes (`different-content`), a file against a directory (`file-directory`), a symbolic link on either
     side, equal link text included (`symbolic-link`), and any other non-regular file (`non-regular`) are conflicts.
     The handoff refuses every conflict before its first write with `SPEC_PROPOSAL_TARGET_EXISTS` in mode
     `INTERACTION` (no guardrail, actor `USER`): the conflict is a data collision the user resolves, so the agent asks
     the user and `[FIX]` is the reconciliation for once they agree. `[TARGET]` lists the destination paths, `[DETAIL]` one `<source> -> <destination>: <kind>` line per conflict, and the fix names
     the first conflict's source path, destination path and kind and the way to reconcile that path, never removal
     of the directory. When the dated path itself is not a real directory, the fix says to rename it aside with its
     content kept, or to replace it with a real directory holding that content. A same-path pair of regular files
     that cannot be read for the comparison is `SPEC_PROPOSAL_INVALID`, both paths in `[TARGET]`.
   - Every move writes only a path that was absent in preflight. The handoff gives no concurrent-change guarantee: a
     file written at a planned path between preflight and its move may be replaced, the same window the ADR writes
     have.
6. **Rewriting** of what pointed into the proposal (4.3).
7. **Removal** of the proposal, with its workflow records.
8. **Gates**: the proposal's `plan-accept` record carried to the spec (`CAP-DLV-proposal-planning` rule 12).

A failure in steps 1 to 5 rolls back: what was moved goes back, what was written is removed (a directory created
inside the moved `materials/` is followed back and removed when empty), and the proposal is kept. Every pre-existing
path of a merged materials directory stays byte-identical, since none of them was recorded as written or moved. A directory that
still holds something the roll-back could not move back is kept, never removed; `SPEC_PROPOSAL_HANDOFF_FAILED` then
lists what could not be undone in its details.

The new spec's workflow is then evaluated from its first stage, after the gates step 8 recorded. Inside a linked worktree, at either `[tool.spec] worktree` level, the CLI also
registers the new bundle in the work-scope registry (`CAP-COLL-work-scope-registry`). Automatic registration failures
produce only verbose diagnostics and preserve the primary handoff output, exit code and `--strict` behavior. They
create no worker registration/update/ACK duty. Primary handoff notices and errors retain their own semantics.

### 4.2 Carrying the Proposal Body

The body of a bundle's `proposal.md` after the frontmatter and the first H1 is split into H2 sections (fenced code is
never a heading), each classified by its heading, case-insensitively:

| Heading contains | Lands in | How |
| --- | --- | --- |
| (text before the first H2), `background`, `hypothesis`, `problem`, `motivation`, `origin` | 1. Problem Statement & Motivation | heading kept as H3, inner headings demoted one level |
| a non-goal keyword together with `acceptance`, `validation` or `verification` | 5. Carried Proposal Contract | heading kept as H3, inner headings demoted; positive scenarios kept apart from exclusions, to be rewritten as criteria and non-goals |
| `non-goal`, `non goal`, `scope excluded`, `out of scope` | 3. Non-Goals | body only; a placeholder item when none |
| `acceptance` | 4. Acceptance Criteria & Behavioral Contracts | body only, with acceptance criterion IDs |
| anything else | 5. Carried Proposal Notes (6. when a carried contract precedes it) | heading kept as H3, inner headings demoted; not contracts |

Bodies are verbatim apart from heading levels; leading and trailing blank lines and trailing horizontal rules are
trimmed. Acceptance criteria get IDs so the spec satisfies `RULE-task-coverage`: an H3 with exactly one `[AC-NN]`
keeps it; another H3 becomes `### Scenario <n> [AC-NN]: <text>`; a body without H3 gets a
`### Scenario <n> [AC-NN]: Carried from proposal` heading before each top-level list item (or one before everything
when it has no list); an empty section gives one placeholder `### [AC-01] <scenario>` with Given/When/Then lines. A
new ID is `AC-<position>` (its scenario's place among the H3s), or the next higher number when an H3 with one tag
already uses it, so the IDs of a carried section are unique.

### 4.3 Rewriting Links and References

Every Markdown file under `docs/` and `specs/` is scanned, except the proposal itself, directories starting with `.`,
symbolic links and the files of completed spec bundles (`spec.md` with `status: completed`), which record the
proposal as it was; their `feedback/` is scanned, since feedback stays current.

- **Relative Markdown links** (inline links and images outside code, devkit's `extract_links`) that resolve into the
  proposal are pointed at the new locations by devkit's `relocate_links`, which replaces each changed file
  atomically: `proposal.md` (or the single file) to `spec.md`, `target-docs.md` to its
  copy, each PADR to its ADR, anything under a moved `materials/` to the same path under the moved directory
  (whether or not the file exists; a link into a `materials/` that was not moved is `unmapped`), each carried file to
  its new path, and the bundle directory to the spec bundle. URLs, root-relative and fragment-only links are left
  alone; a `#fragment`, a `?query` and a trailing `/` are kept. Files written for the bundle's location (the carried `spec.md`, the
  copied blueprint, the promoted ADRs, the moved materials and carried files) have their links resolved from where
  they were written, so a link outside
  the bundle keeps its target and one that still resolves to the same file keeps its spelling. In a merged
  materials directory this holds per moved file and per subtree moved whole; a pre-existing file resolves its links
  from where it is, so only its links into the proposal change. A link to a dropped duplicate points at the kept
  destination file.
- **Document ID references** (frontmatter reference fields, `` `ID` `` and `[ID]` in prose, and the `proposal`
  provenance field) are rewritten from the IDs of the documents actually written: `PROP-<slug>` to `SPEC-<slug>`,
  each `PADR-<slug>` to its `ADR-<slug>`, and `PROP-<slug>-target` to itself (a `[ID]` becomes `` `ID` ``). A
  reference written with an alias of the proposal or a promoted PADR is rewritten exactly like one written with its
  old ID, to the new canonical ID, across the same scan set (ADRs, the ADRs promoted in this handoff and feedback
  included, completed bundles excluded), because the translation removes the alias's only declaration. This is the
  handoff's own rename. Bare text, inline code other than a lone ID and fenced code do not change.
- **Code-span paths** (`kind=path`) in the bodies of the documents the handoff wrote or moved out of a bundle
  proposal (the carried `spec.md` and blueprint, the promoted ADRs, moved feedback and other carried files): an inline
  code span holding a path relative to the bundle (`` `decisions/PADR-x.md` ``,
  `` `materials/notes.md` ``) that names a relocated file becomes the new document's ID in backticks
  (`` `ADR-x` ``), or else its new repository-relative path. Directory-only spans, including `` `materials/` ``
  and paths resolving to relocated directories without a trailing slash, remain unchanged so generic prose keeps
  its meaning. Frontmatter, fenced code and spans naming nothing relocated do not change.
- **Dropped workflow record citations**: before ordinary relocation, relative Markdown links in scanned documents
  and bundle-relative code spans in carried prose that name an exact dropped record become explicit historical
  Git citations. The full handoff HEAD commit and repository-relative path identify the record, only when its
  bytes at HEAD equal the file about to be deleted. A Markdown link becomes its label followed by the historical
  citation; an existing query or fragment is retained separately as a selector. Rewrites retain `kind=link` or
  `kind=path`. Without Git history, with an untracked record, or when the record differs from HEAD, the citation
  remains unchanged and is reported as `unmapped`; no handoff archives the record, and the plain handoff creates no
  commit (the composed handoff commits afterwards, Host-authorized proposal lifecycle CLI).

| Unresolved reason | Meaning |
| --- | --- |
| `unmapped` | A link into the proposal with no new location (the `decisions/` directory, a path that does not exist). |
| `ambiguous` | Another document declares the same ID or alias, so it is not rewritten. |
| `unreadable`, `unwritable` | The file could not be read, parsed or written (line `0`); the link rewrites of a file that could not be written are not reported as rewritten. |

The `spec-next` skill's post-handoff check follows up the reported lines.

The rewrite also covers a sibling draft that is in its own Planning on `plan-<other>`: its `depends_on` and ID
references to the handed-off proposal are rewritten, because a skipped `depends_on` dangles once `dev-<slug>` lands
and every later handoff that projects the graph refuses. WHEN the sibling's Planning merges into the base first and
merging the base into `dev-<slug>` conflicts in a file under `docs/proposals/PROP-<other>/`, the Host SHOULD take the
base version of that file and run `devkit rules fix` on it, which rewrites each citation `RULE-document-reference`
reports as `PROP-<slug> was handed off` to `SPEC-<slug>` (`FB-handoff-rewrite-edits-sibling-draft`).

### 4.4 Prune

A handoff deletes the proposal in the worktree it runs in; merging that branch removes the tracked files from the
base checkout but leaves their directories. `devkit spec proposal prune [<slug>]` removes `docs/proposals/PROP-<slug>/` (every `PROP-*` directory without a slug) when it
holds no file at any depth (a symbolic link counts as a file; devkit's `remove_empty_tree`). A directory holding any
file is kept, and one that cannot be listed fails the prune before anything is removed. devkit-spec's
`devkit.post_finish` extension (`devkit_spec.features.delivery.usecases.cleanup.after_finish`) prunes the finished slug after a successful `devkit worktree finish`
(`ADR-worktrees-and-scope`) and, on the guarded integration path (`SPEC-hook-driven-integration-cleanup`), plans and executes the exact `CleanupTarget(kind="proposal-prune", identity="docs/proposals/PROP-<slug>", revision=<source_sha>)` target, emitting `SPEC_POST_FINISH_CLEANUP` notices; the command remains for other checkouts and a failed extension is retried after inspecting current Git state and rerunning the appropriate CLI operation.

### 4.5 Commands and Options

Every command takes `-w/--workspace-root`, `--format text|json`, `-q`, `-v` and `--strict` (`CAP-HARN-command-mount`).

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --target-area capabilities/governance/
uv run devkit spec proposal new fast-engine --milestone MS-foundation --with-target-docs
uv run devkit spec proposal new rate-limits --namespace api --task-kind bugfix --planning-effort low --dev-effort high
uv run devkit spec proposal new fast-engine-v2 --supersedes PROP-fast-engine        # close by supersede
uv run devkit spec proposal new fast-engine --summary "Replaces the regex rule engine with an AST parser."
uv run devkit spec proposal padr fast-engine "Use AST parser"        # decisions/PADR-use-ast-parser.md
uv run devkit spec proposal padr fast-engine "2024 roadmap" --slug roadmap-2024
uv run devkit spec proposal accept fast-engine --by user --mode accept_only        # local Host, plan-<slug> after review
uv run devkit spec proposal accept fast-engine --by user --note "..."                # cloud-pr route (autohub), plan-<slug>
uv run devkit spec proposal accept small-fix --by user --direct --check --note "<reason>"  # read-only first
uv run devkit spec proposal accept small-fix --by user --direct --note "<reason>"   # base checkout, after the sweep
uv run devkit spec proposal handoff fast-engine                      # status: accepted (plan-accept recorded)
uv run devkit spec proposal prune [<slug>]                           # base checkout; finish's extension does it per slug
uv run devkit spec proposal check fast-engine                        # before any Backlog edit, split or delete
```

| Option | Command | Meaning |
| --- | --- | --- |
| `--title/-t` | `new` | Title (default: the slug). |
| `--target-area/-a` | `new` | Capability area the proposal targets (default `capabilities/<area>/`); also the owned boundary. |
| `--milestone/-m` | `new` | One existing MS ID at the global or a namespace roadmap root, or one of its aliases, written as the canonical ID; otherwise ARGUMENT_INVALID before writes, with a fix naming `devkit docs list milestone --all-namespaces`. Proposal membership only; not carried to `spec.md`. |
| `--decomposed-from` | `new` | Editable draft PROP ID; checks source existence, draft status and absence of a Planning branch before writing. |
| `--task-kind` | `new` | Write `task_kind: feature\|bugfix` (default `feature`); anything else is `ARGUMENT_INVALID`. |
| `--planning-effort` | `new` | Write `planning_effort: low\|medium\|high` (default `medium`); anything else is `ARGUMENT_INVALID`. |
| `--dev-effort` | `new` | Write `dev_effort: low\|medium\|high` (default `medium`); anything else is `ARGUMENT_INVALID`. |
| `--supersedes` | `new` | Write `supersedes: PROP-<old>`; a value that is not another proposal's ID is `ARGUMENT_INVALID`, a proposal that does not exist `SPEC_PROPOSAL_NOT_FOUND`, one that is not `accepted` `SPEC_PROPOSAL_NOT_APPROVED`; nothing written. |
| `--needs-decompose` | `new` | Write `needs_decompose: true`. |
| `--namespace` | `new` | Write `namespace: <name>`: `global` or registered in `[[tool.docs.namespaces]]`, else `ARGUMENT_INVALID` with the valid names in `[FIX]`. Omitted: the namespace the current directory lies in (`CAP-DOCS-namespaces`), else no field and the bundle is global. |
| `--slug` | `padr` | The PADR slug for its ID and file name (default: the title's slug); refused when its first segment has no letter. |
| `--summary` | `new`, `padr` | Write `summary: <text>`. After stripping surrounding whitespace, empty, longer than 300 characters, or with a letter outside the Latin script: `ARGUMENT_INVALID` (`[TARGET] --summary`), nothing written. A promoted ADR keeps its PADR's summary. |
| `--with-target-docs` | `new` | Also write `target-docs.md`. |
| `--by` | `accept` | Required: `user` for explicit acceptance or `policy` under owning `plan-accept=auto`; other values are usage errors (exit `2`). |
| `--note` | `accept` | The decision note; with `--direct` the eligibility reason, required (blank: `ARGUMENT_INVALID`, `[TARGET] --note`, before the proposal is read). |
| `--direct` | `accept` | Accept an eligible draft on the base checkout, or repair an accepted proposal without its record and without a `worker` envelope (`CAP-DLV-proposal-planning` rule 14). |
| `--check` | `accept` | Run every check of the form and write nothing. The composed `--mode` form has no dry run: with `--mode`, `--check` is a usage error (exit `2`) saying that the composed acceptance's readiness refusals in preparation come before its first write and a later failure returns `needs_recovery` with `completed_steps`, and naming `devkit spec proposal report <slug>` and `devkit workflow envelope check --unit docs/proposals/PROP-<slug>` for the read-only material the Host presents; `--direct` with `--mode` is the usage error `composed acceptance cannot use --direct`. |

### 4.6 Output

```text
[PROPOSAL: PROP-fast-engine path=docs/proposals/PROP-fast-engine/proposal.md dir=docs/proposals/PROP-fast-engine target_docs=- workflow=sdd-proposal planning_effort=medium dev_effort=medium]
[NEXT_CMD: uv run devkit workflow next --unit docs/proposals/PROP-fast-engine]
[PADR: PADR-use-ast-parser path=docs/proposals/PROP-fast-engine/decisions/PADR-use-ast-parser.md proposal=PROP-fast-engine]
[PROPOSAL: PROP-fast-engine path=docs/proposals/PROP-fast-engine/proposal.md status=draft editable=yes]
[ACCEPT_CHECK: PROP-small-fix form=direct path=docs/proposals/PROP-small-fix/proposal.md eligible=yes pending=-]
[ACCEPTED: PROP-small-fix form=direct path=docs/proposals/PROP-small-fix/proposal.md status=accepted decision=docs/proposals/PROP-small-fix/decisions/02-gate-plan-accept.yaml]
[HANDOFF: PROP-fast-engine spec=SPEC-fast-engine dir=specs/2026-10/20261013-fast-engine workflow=sdd-spec-feature dev_effort=medium]
[TARGET_DOCS: specs/2026-10/20261013-fast-engine/target-docs.md]
[MATERIALS: docs/materials/2026-10/20261013-fast-engine]
[PROMOTED_ADR: ADR-use-ast-parser path=docs/decisions/2026-10/20261013-use-ast-parser.md padr=PADR-use-ast-parser]
[SUPERSEDED_IN_PART: ADR-regex-rules path=docs/decisions/2026-09/20260901-regex-rules.md line=9 by=ADR-use-ast-parser]
[DROPPED_RECORD: docs/proposals/PROP-fast-engine/decisions/01-gate-plan-intent.yaml]
[DROPPED_RECORD: docs/proposals/PROP-fast-engine/decisions/02-gate-plan-accept.yaml]
[CARRIED_GATE: gate:plan-accept decision=specs/2026-10/20261013-fast-engine/decisions/01-gate-plan-accept.yaml]
[REWRITTEN: docs/usecases/core/UC-x.md:5 kind=id from=PROP-fast-engine to=SPEC-fast-engine]
[REWRITTEN: docs/usecases/core/UC-x.md:9 kind=link from=../../proposals/PROP-fast-engine/proposal.md to=../../../specs/2026-10/20261013-fast-engine/spec.md]
[UNRESOLVED_LINK: docs/usecases/core/UC-x.md:9 kind=link target=../../proposals/PROP-fast-engine/decisions/ reason=unmapped]
[SCOPE: SPEC-fast-engine namespace=3f2a... revision=1 scopes=6 unresolved=2 shared_path=/repo/.git/devkit-spec-scope token=...]
[NEXT_CMD: uv run devkit workflow next --unit specs/2026-10/20261013-fast-engine]
[PRUNED: docs/proposals/PROP-fast-engine]
[OK: nothing to prune]
```

- `new`: one `[PROPOSAL: ...]` line (`target_docs=-` without `--with-target-docs`, `workflow=-` when unbound, `planning_effort=<effort>`, `dev_effort=<effort>`), ending
  with `namespace=<name>` when the bundle reports a namespace: the field written, else `global` in a workspace that
  registers namespaces (none for a global bundle in a workspace without them); then `[NEXT_CMD: ...]` when
  `proposal.md` is bound to `sdd-proposal`. JSON: `id`, `dir`, `path`, `target_docs`, `workflow`, `planning_effort`, `dev_effort`, `namespace`
  (`null` when none is reported), `next_command`, `notices`.
- `padr`: one `[PADR: ...]` line. JSON: `id`, `path`, `proposal`.
- `check`: one `[PROPOSAL: ... status=draft editable=yes]` line. JSON: `id`, `path`, `status`, `editable`.
- `accept`: `[ACCEPTED: <id> form=planning|direct|repair path= status=accepted decision=<record>]`; with `--check`
  `[ACCEPT_CHECK: <id> form= path= eligible=yes|no pending=<requests>|-]` and nothing written; the result reports eligibility without a pending-intent condition. JSON: `proposal`, `path`,
  `form`, `status` (the current one under `--check`), `checked`, `eligible`, `decision` (`null` under `--check`),
  `pending`. The composed `--mode` form is described under the Host-authorized lifecycle CLI.
- `handoff`: `[HANDOFF: ...]` (`workflow=-`: unbound; `dev_effort=<effort>` when the proposal declared `dev_effort`), `[TARGET_DOCS: ...]` and `[MATERIALS: ...]` when the bundle had
  them (`[MATERIALS: <dir> merged=yes]` when merged into an existing directory), one
  `[DROPPED_DUPLICATE: <path>]` per kept destination file whose identical proposal copy was dropped, one
  `[PROMOTED_ADR: ...]` per PADR, one `[SUPERSEDED_IN_PART: <adr> path=<path> line=<n> by=<promoted ADR>]` per
  "Superseded in part by" line written into an ADR (4.1, step 4), one `[DROPPED_RECORD: <path>]` per workflow record of the proposal
  unit, one `[CARRIED_GATE: <request> decision=<path>]` per approval carried by name (`CAP-DLV-proposal-planning` rule 12),
  one `[REWRITTEN: <path>:<line> kind=link|id|path from= to=]` per rewrite, one
  `[UNRESOLVED_LINK: <path>:<line> kind= target= reason=]` per link or reference left as it was, `[SCOPE: ...]` when
  it registered the bundle, and `[NEXT_CMD: ...]` when `spec.md` is bound. JSON: `proposal`, `spec`, `dir`,
  `workflow`, `dev_effort` (`null` when absent), `target_docs`, `materials`, `materials_merged` (boolean),
  `dropped_duplicates` (workspace-relative destination paths), `decisions` (`id`, `path`, `padr`), `pointers` (`adr`,
  `path`, `line`, `by`; 4.1, step 4), `dropped_records` (paths),
  `carried_gates` (`request`, `decision`), `rewritten_files`, `rewritten`
  (`path`, `line`, `kind`, `from`, `to`), `unresolved` (`path`, `line`, `kind`, `target`, `reason`), `next_command`,
  `notices`, `scope` (`record`, `token`, `namespace`, `shared_path`, or `null`).
- `prune`: `[PRUNED: <dir>]` per directory removed, else `[OK: nothing to prune]`. JSON: `{"pruned": [...]}`.

### 4.7 Library

```python
from devkit_spec.features.proposals import (
    AcceptProposalUseCase,
    CreateProposalUseCase,
    PruneProposalsUseCase,
    handoff_proposal,
)
from devkit_spec.features.proposals.usecases.scaffold import CreateProposalDecisionUseCase

created = CreateProposalUseCase().execute(root, "fast-engine", title="Fast Engine", with_target_docs=True)  # CreatedProposal
padr = CreateProposalDecisionUseCase()
padr.execute(root, "fast-engine", "Use AST parser", summary="Parses rules with an AST.")  # CreatedDecision
padr.execute(root, "fast-engine", "2024 roadmap", padr_slug="roadmap-2024")  # PADR-roadmap-2024
accepted = AcceptProposalUseCase().execute(root, "small-fix", by="user", note="<reason>", direct=True)  # AcceptResult (check=True: read-only)
result = handoff_proposal(root, "fast-engine")  # HandoffResult
result.dir, result.workflow, result.dev_effort, result.decisions, result.rewritten, result.unresolved, result.notices
PruneProposalsUseCase().execute(root, "fast-engine")  # list of removed dirs
```

`CreateProposalUseCase().execute` also takes `target_area`, `milestone`, `task_kind`, `planning_effort`, `dev_effort`, `namespace`, `summary`, `supersedes`, `decomposed_from`,
`needs_decompose` and `cwd` (the
directory whose namespace applies when `namespace` is omitted);
`carry_proposal_body` and `ensure_ac_ids` implement 4.2, `RelocationPlan`, `Rewritten` and `Unresolved` 4.3.

### 4.8 Codes

`0` success; `1` a negative answer (`check`: `SPEC_PROPOSAL_IN_PLANNING`; `accept --check`: `eligible=no`) or a
composed operation that stopped after some effects; `2` refused or failed (nothing was handed off or accepted).
Warnings exit `0` (`1` under `--strict`, which never turns a `2` into a `1`). Every command an advisory or
`[NEXT_CMD: ...]` names is written as the agent runs it, `uv run devkit ...`.

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `SPEC_PROPOSAL_SLUG_INVALID` | `ERROR` (`INPUT_ERROR`) | `ProposalSlugError` | The slug, or a PADR title or `--slug`, keeps no letter or digit after normalization; a new proposal's or PADR's slug, or at handoff a legacy proposal's or PADR's, has no letter in its first segment (`[FIX]`: rename it, or pass `--slug` to `padr`). |
| `SPEC_PROPOSAL_EXISTS` | `ERROR` (`INPUT_ERROR`) | `ProposalExistsError` | `new`: the bundle or `PROP-<slug>.md` exists, or another document declares `PROP-<slug>` as an alias; `[TARGET]` lists it. |
| `SPEC_PADR_EXISTS` | `ERROR` (`INPUT_ERROR`) | `ProposalDecisionExistsError` | `padr`: a document already declares the PADR ID; `[TARGET]` lists it. |
| `SPEC_PROPOSAL_SLUG_CONFLICT` | `ERROR` (`INTERACTION`) | `ProposalSlugConflictError` | `SPEC-<slug>` exists (`[TARGET]`); the user picks another slug or drops the duplicate. |
| `SPEC_PROPOSAL_NOT_FOUND` | `ERROR` (`INPUT_ERROR`) | `ProposalNotFoundError` | No bundle or single-file proposal has the slug (`padr`: no bundle); `new`: `--supersedes` names a proposal that does not exist. |
| `SPEC_HANDOFF_NOT_READY` | `ERROR` (`INTERACTION`) | `HandoffNotReadyError` | The composed `proposal handoff --effort` finds no committed `proposal.md`, a proposal that is not accepted or needs decomposition, or no completed `sdd-proposal` Planning with its own `plan-accept`; `[DETAIL]` names the condition, `[TARGET]` the proposal. |
| `SPEC_HANDOFF_BASE_DIRTY` | `ERROR` (`INTERACTION`) | `HandoffBaseDirtyError` | The composed handoff: the retained base checkout has uncommitted changes, listed in `[TARGET]`. |
| `SPEC_HANDOFF_WORKTREE_CONFLICT` | `ERROR` (`INTERACTION`) | `HandoffWorktreeConflictError` | The composed handoff: a `dev-<slug>` worktree (`[TARGET]`) exists that devkit did not create for this accepted base, or holds changes or another commit; `[DETAIL]` says which. It is never reused or removed. |
| `SPEC_HANDOFF_STALE` | `ERROR` (`INTERACTION`) | `HandoffStaleError` | The composed `proposal handoff --effort` CLI found the base, accepted plan or policy changed since its check, before any effect (exit `2`); or it created the Development worktree, which no longer holds the reviewed base commit or whose files setup changed, or whose handoff commit landed but is not one clean direct child of the reviewed base: the result is `status=needs_recovery` with this error listed, the worktree is kept for inspection and the command exits `1`. For a landed but unclean commit `[FIX]` repairs `dev-<slug>` in place and never reruns. |
| `SPEC_HANDOFF_COMMIT_REFUSED` | `ERROR` (`INPUT_ERROR`) | `HandoffCommitRefusedError` | The composed handoff: `git commit` refused the handoff transaction in `dev-<slug>`; nothing landed, the writes stay staged there, `[DETAIL]` carries the commit output and `[TARGET]` every dirty path. The result is `status=needs_recovery` with `[HANDOFF_STOPPED: ...]` (or `[ACCEPTED_STOPPED: ...]`), `commit=-` and `[NEXT_ACTION: ...]`, exit `1`; `[FIX]` commits in that worktree after the cause is fixed, never a rerun. |
| `SPEC_HANDOFF_REPLY_INVALID` | `ERROR` (`INPUT_ERROR`) | `HandoffReplyError` | The composed `proposal handoff` CLI needs `--effort low`, `--effort medium` or `--effort high` (an automatic handoff the proposal's `dev_effort`); the caller corrects the effort and reruns. |
| `SPEC_PROPOSAL_REJECTED_PENDING` | `WARNING` | `ProposalRejectedPendingWarning` | `rules check -p hygiene` (whole workspace): a rejected proposal is still in the base; `[FIX]` finds the rejection commit, writes the rejection ADR and deletes the proposal in one commit (`CAP-DLV-proposal-planning` rule 9). |
| `SPEC_PROPOSAL_IN_PLANNING` | `ERROR` (`BLOCKED`) | `ProposalInPlanningError` | `check` (exit `1`, its negative answer): Backlog may not change the proposal, because its `plan-<slug>` exists (locally or fetched; `CAP-DLV-proposal-planning` rule 13) or it is no longer `draft`. `padr` and `new --decomposed-from` (exit `2`): `plan-<slug>` exists and the checkout is not on it, or the parent left `draft`. |
| `SPEC_PROPOSAL_INVALID` | `ERROR` (`INPUT_ERROR`) | `ProposalInvalidError` | `[TARGET]` names the file. A needed handoff pointer has no partial-supersession statement; or the proposal, its blueprint or a PADR cannot be read or its frontmatter does not parse; the composed acceptance or handoff finds a `task_kind`, effort, `title` or `summary` it cannot use; or, at handoff, `namespace` is not a string naming `global` or a registered namespace, `summary` is not a string, `task_kind` is not `feature` or `bugfix`, or `planning_effort`/`dev_effort` is present and not `low`, `medium` or `high`; or a same-path pair of regular files of a materials merge cannot be read for the byte comparison. |
| `SPEC_PROPOSAL_NOT_APPROVED` | `ERROR` (`INTERACTION`) | `ProposalNotApprovedError` | `handoff`: status is not `accepted`, `plan-accept` was not given; `[FIX]` records it with `devkit spec proposal accept` after the user's acceptance. `new`: the proposal `--supersedes` names is not `accepted`; a supersede replaces an accepted proposal only. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | `ERROR` (`INTERACTION`) | `ProposalAcceptanceUnrecordedError` | `handoff`, or the composed `accept --mode` on `plan-<slug>`: a bundle bound to `sdd-proposal` says `accepted` without an effective accepted `gate:plan-accept` (`CAP-DLV-proposal-planning` rule 2); nothing written. `[FIX]` names the slug's exact repair command. |
| `SPEC_PROPOSAL_POLICY_NOT_AUTO` | `ERROR` (`BLOCKED`) | `ProposalPolicyNotAutoError` | `accept --by policy` (with or without `--mode`) while the owning `plan-accept` policy is not `auto`; nothing written. The composed form checks it before the checkout, and every command a composed refusal names keeps the caller's own `--by`. `[REPORT]` says the user accepts explicitly or changes the policy; no fix suggests `--by user`. |
| `SPEC_PROPOSAL_ACCEPT_REFUSED` | `ERROR` (`INPUT_ERROR`) | `ProposalAcceptRefusedError` | `accept`: the status does not allow the form (a draft without `--direct`, a proposal in review with it, an accepted proposal whose record exists, a rejected one), or the proposal is single-file or unbound (`CAP-DLV-proposal-planning` rule 14). |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | `ERROR` (`INTERACTION`) | `ProposalNotEligibleError` | `accept --direct`: one or more direct-acceptance conditions fail, each a `blocking:` detail; nothing written. `[FIX]` names the exact `worktree start plan-<slug>` command. `accept --check` reports the same conditions under `pending` as `eligible=no` and exits `1`. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | `ERROR` (`INTERACTION`) | `ProposalGateNotOpenError` | `accept`: the workflow did not open `gate:plan-accept` (a missing sweep, a hold); the status is restored, `[DETAIL]` lists the unmet checks and hold reasons and `[TARGET]` the proposal; the user resolves them with the agent before the same command reruns. |
| `SPEC_PROPOSAL_NEEDS_DECOMPOSE` | `ERROR` (`INTERACTION`) | `ProposalNeedsDecomposeError` | The proposal carries `needs_decompose: true`; Backlog splits it into new drafts. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | `ERROR` (`INPUT_ERROR`) | `ProposalWrongWorktreeError` | `handoff` in a checkout, linked or base, on another branch than `dev-<slug>`, at either `[tool.spec] worktree` level (`CAP-DLV-proposal-planning` rule 11); `[TARGET]` is the branch to run on and `[FIX]` starts `dev-<slug>`, or continues an existing one with its committed unit directory. `accept` without `--direct` on another branch than `plan-<slug>`. The composed `accept --mode` and `handoff --effort` off the retained base checkout, with the exact command in `[FIX]`. |
| `SPEC_PROPOSAL_WORKFLOW_INVALID` | `ERROR` (`MAINTENANCE`) | `ProposalWorkflowError` | `task_kind: bugfix` and `sdd-spec-bugfix` does not resolve or validate; `[DETAIL]` carries devkit's code. |
| `SPEC_PROPOSAL_TARGET_EXISTS` | `ERROR` (`BLOCKED`; `INTERACTION` for a merge conflict) | `ProposalTargetExistsError` | The spec bundle or an ADR file exists, a proposal path conflicts with the existing materials directory it would merge into (`INTERACTION`: `different-content`, `file-directory`, `symbolic-link`, `non-regular`, or the dated path is not a real directory; the fix names the first conflict's source, destination and kind), two PADRs map to one ADR, another document declares a promoted ADR's ID, the spec ID or a translated alias as its ID or an alias, two graduating IDs or translated aliases coincide, a carried bundle file clashes with a file or symbolic link of `materials/` (or `materials/` is itself a symbolic link), or the directory of the spec bundle, an ADR, the materials directory or a carried file resolves outside the workspace. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | `ERROR` (`MAINTENANCE`) | `ProposalHandoffError` | A write failed; what was written is removed, the materials and carried files moved back, the proposal kept. When the roll-back was incomplete, `[DETAIL]` lists what could not be moved back or removed (kept, never deleted). |
| `SPEC_PROPOSAL_CLEANUP_FAILED` | `WARNING` | `ProposalCleanupWarning` | The handoff completed but the proposal could not be removed, or the post-finish prune of the slug's empty proposal directories failed (`CAP-COLL-work-scope-registry`). |
| `SPEC_PROPOSAL_LINK_UNRESOLVED` | `WARNING` | `ProposalLinkUnresolvedWarning` | Links or references into the proposal were left as they were; the `[UNRESOLVED_LINK]` lines list them. |
| `SPEC_PROPOSAL_REFS_REWRITTEN` | `NOTICE` | `ProposalReferencesRewrittenNotice` | ID references now name the spec or the ADRs; reread each `[REWRITTEN ... kind=id]` sentence. |
| `SPEC_PROPOSAL_MILESTONE_INACTIVE` | `NOTICE` | `ProposalMilestoneInactiveNotice` | `new --milestone`: the canonical milestone is done or dropped; creation succeeds and the notice names its ID and state and advises membership review. Milestone status and completion assertions are unchanged; no approval gate is added and `--strict` still exits `0` for this notice. |
| `SPEC_PROPOSAL_UNBOUND` | `NOTICE` | `ProposalUnboundNotice` | `new`: `sdd-proposal` is not available, `proposal.md` is unbound. `handoff`: `task_kind` is `feature` (or absent) and `sdd-spec-feature` is not available, `spec.md` is unbound. The `[FIX]` is `devkit workflow bind --unit <dir> --workflow <id>`. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | devkit's `ArgumentError` | `accept`: `--direct` with a blank `--note`. `new`: `--namespace` is neither `global` nor registered, `--task-kind` is not `feature` or `bugfix`, `--planning-effort` or `--dev-effort` is not `low`, `medium` or `high`, `--supersedes` names no other proposal. `new`, `padr`: stripped `--summary` is empty, longer than 300 characters or not English. |
| `DOCS_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_docs.base.errors.DocsConfigError` | `[tool.docs]` is malformed and the namespace registry must be read: `new` without `--namespace global`, a proposal's `namespace` other than `global` at handoff, or a handoff in a linked worktree (`CAP-DOCS-namespaces`). |


## Host-authorized proposal lifecycle CLI

The Host presents the proposal's findings, source commit, target branch, worktree path and effects, receives the
user's conversational decision under `ask`, then invokes the CLI. CLI invocation alone does not establish approval;
the CLI does not accept a proof, token or published report and cannot authenticate the conversation. It revalidates
source, base policy, workflow readiness, worktree provenance and cleanup targets before each mutation. `auto`
authority comes only from the retained base policy.

`devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff --by user` (`--effort` selects the
Development effort of `accept_and_handoff`) validates
the reviewed `plan-<slug>`, records `status: accepted` and `gate:plan-accept`, commits the exact acceptance delta,
and executes approved local Planning integration. Both modes return acceptance and merge effects with
`verification=pending`; `accept_and_handoff` MUST leave handoff not started. Its continuation retains requested and
selected mode, activity effort, authorized handoff scope, authority and landed SHA. The Host synchronizes dependencies
and runs final checks in fresh processes, then invokes the existing handoff command under unchanged authority.
Changed scope/effects require revalidation. `accept_only` completes only after its accepted landing passes final checks.
WHEN a moved target changed the reviewed proposal directory, preparation MUST refuse before the acceptance commit
with `SPEC_PROPOSAL_APPROVAL_NOT_READY`. Git conflicts refuse with `WORKTREE_MERGE_CONFLICT`. No old-runtime merged
content rules or receipt checks run. A conflict-free moved target becomes the first parent and the exact acceptance
commit the second parent (`ADR-post-merge-verification`).

`devkit spec proposal handoff <slug> --effort low|medium|high` validates an already accepted
proposal on the retained base, creates or validates `dev-<slug>`, runs setup and sync, then performs proposal handoff
and scope registration. An automatic handoff uses the proposal's declared `dev_effort`. The command reports the
worktree, spec bundle, selected effort, notices and completed effects. Setup or handoff failures preserve the
proposal and any created worktree for inspection; the command never rolls those effects back automatically.

WHEN the handoff and scope registration succeed, the composed handoff MUST stage the whole delta `git status` reports
in `dev-<slug>` (the worktree was clean at the reviewed base head before the handoff) and commit it once with the
subject `spec: hand off <slug> to Development` under the normal commit gate
(`ADR-proposal-handoff`). It reports `commit`, the HEAD read after `git commit` returns
(a metadata-rewriting post-commit hook changes the SHA), and checks that HEAD's single parent is the reviewed base
head and the worktree is clean; a landed commit that fails either check is `status: needs_recovery` with
`SPEC_HANDOFF_STALE`, the landed `commit` and the parents or dirty paths, no next command and a next action whose
`[FIX]` repairs `dev-<slug>` in place (commit or remove the dirty paths, make HEAD one commit on the reviewed base),
never a rerun, which refuses that worktree. Every stopped outcome after the handoff writes clears the nested
handoff's next command. IF `git commit` refuses (the gate, a missing
identity, signing), THEN nothing landed: the result is `status: needs_recovery` with `commit: null`,
`SPEC_HANDOFF_COMMIT_REFUSED`, no next command and a next action, exit `1`, and the handoff's writes stay staged and
uncommitted in `dev-<slug>`; nothing is rolled back. The Host fixes the cause there and commits; a rerun refuses the
dirty worktree (`SPEC_HANDOFF_WORKTREE_CONFLICT`). The plain `devkit spec proposal handoff <slug>` stays write-only:
it commits nothing, and its writes are committed with the post-handoff link fixes.

Both commands print one outcome (`ARCH-08-1-agent-output`). Acceptance prints
`[ACCEPTED: PROP-<slug> status=accepted mode= authority= completed= target_sha= landed_sha= verification=pending handoff=not_started]`
and `[NEXT_ACTION: "..."]` naming synchronization, final checks and the authorized fresh handoff continuation.
Acceptance MUST NOT emit handoff worktree or commit fields before handoff occurs. JSON includes the continuation's
mode, effort, unit, landed SHA, authority and handoff-authorized flag. The separate handoff command prints
`[HANDOFF: PROP-<slug> status=handed_off spec= dir= worktree= effort= authority= commit=]` and its next command.
Successful Git effects exit `0` (`1` under strict warnings); this is not a final-test pass. A failure after effects
prints the corresponding `_STOPPED` sentinel, completed effects, next action and errors, exiting `1`. A refusal
before effects exits `2` with its errors. JSON returns one result or error document.

This composed handoff and `accept --mode accept_and_handoff` read the `proposal-handoff` policy. The plain
`devkit spec proposal handoff <slug>` in a `dev-<slug>` checkout is the Host-run step after the `proposal-handoff`
decision and reads no policy itself.

These operations do not dispatch a worker, create a pull request or authorize final Development integration. A
partial result requires Git/worktree inspection; after an already-landed operation, recovery runs only a guarded
remaining cleanup. `ADR-delivery-approval-and-lifecycle-authority` defines Host authorization and recovery boundaries.

The composed `devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff` is the
single Planning acceptance route of a local Host, which runs it itself (the basic form without `--mode`
records acceptance on the `cloud-pr` route): it already includes the integration and cleanup, so
no git-operator job precedes or follows it, and git-operator has no acceptance operation. A refusal raised in
preparation leaves nothing written. WHEN a refusal comes after the acceptance commit (a Git conflict or a target that moved between preparations), THEN the result is
`needs_recovery` with `completed_steps` and the accepted, unmerged `plan-<slug>` returns to the Host with the
reported code; the Host prepares the source on that branch (a base merge and `devkit rules fix` when the code
calls for them) and only then reruns the same command, which continues from the acceptance commit. A rerun that
would repeat a deterministic refusal is not made.


## Proposal review briefings and combined acceptance

`devkit spec proposal report <slug> [--source-sha <sha>]` prints the report template Markdown for the proposal at
that source on stdout (JSON: `proposal`, `source_sha`, `report`), read-only; `--source-sha` defaults to the workspace
`HEAD`, and JSON reports the resolved SHA. The source is a real full commit at clean current `plan-<slug>` HEAD (reviewing or accepted),
or a clean accepted base HEAD for standalone handoff.
Language is the owning workspace preference, normalized to ko/en. The briefing reports three sections for outcome,
decisions and proposed approval effects (identifying the recommended Development effort), plus any boundary impacts,
planning effort/support, open decisions/waivers and unverified areas.
Proposal reports are not stored as shared artifacts; acceptance operates directly on the committed proposal files and git HEAD.

`devkit spec proposal accept` requires the Host to present the findings and effects before an `ask` invocation.
Its result separates completed acceptance/integration from pending final verification and unstarted handoff.
`--by user` records decision provenance; it is not an authenticated credential. Required-PR refuses this local route.

The invocation binds exact source/base commits, Git and extension identities, effective configuration, environment,
and cleanup targets. The common-directory integration lock covers acceptance and
integration. Only the service-created acceptance record/status delta and its direct-child commit are permitted;
normal commit gates and retained Git/authority checks still run. The base cannot advance during the
invocation; a base that moved before it is merged by the integration itself. Cleanup
revisions equal to the source SHA may follow only that exact verified acceptance child with identical targets.
Both modes yield after accepted merge/cleanup; combined mode pins the landed result in its continuation. No final
Development merge is authorized. If the Host conversation is declined, canceled or unavailable, the Host does not
invoke the CLI and no lifecycle state changes.

Partial progress returns completed steps, source/acceptance/landed SHAs, integration progress, worktree results and
a next action. No executable credential survives a return or restart. The Host retains its existing decision for unchanged authorized handoff scope; changed effects need revalidation. Fresh decisions cover only additional effects: accepted Planning commits are never replayed, and strictly matched clean pinned worktrees can retry
setup/handoff. Dirty or mismatched partial state requires inspection; it is never rolled back or treated as completed
merely because a branch exists. The one exception is the acceptance commit itself: when the commit gate refuses
it, nothing has landed, so the service withdraws its own two acceptance writes (the status change and the gate
record), leaves the Planning worktree as it was and reports `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED` with the gate's
output as details. See `ADR-proposal-acceptance` and `ADR-delivery-approval-and-lifecycle-authority`.

`proposal report` checks the slug and `--source-sha` before it reads the checkout, so a missing proposal is never
reported as a dirty tree.

| Code | Mode | Meaning | Action |
| --- | --- | --- | --- |
| `SPEC_REPORT_ARGUMENT_INVALID` | `INPUT_ERROR` | `report`: the slug is not a proposal slug or `--source-sha` is not a full lowercase commit SHA; `[TARGET]` is `SLUG` or `--source-sha`. | Correct the argument. |
| `SPEC_REPORT_SOURCE_NOT_HEAD` | `INPUT_ERROR` | `report`: `--source-sha` is not the current commit of this checkout, nor of the proposal's `plan-<slug>` worktree (also when there is none). | Pass the current SHA or omit `--source-sha`. |
| `SPEC_REPORT_SOURCE_DIRTY` | `INTERACTION` | `report`: the source checkout has uncommitted changes, listed in `[TARGET]`; they may be the user's work. | Once the user has decided what happens to them and the checkout is clean, rerun. |
| `SPEC_REPORT_WRONG_CHECKOUT` | `INPUT_ERROR` | `report`: neither `plan-<slug>` with a proposal in review or accepted, nor the retained base with an accepted proposal. | Run it in the `plan-<slug>` worktree. |
| `SPEC_REPORT_SOURCE_INVALID` | `INPUT_ERROR` | `report`: a committed record (`[TARGET]`) is not a regular file, a PADR's ID differs from its file name, an envelope is not a mapping, the proposal declares another ID, or an effort is not `low`, `medium` or `high`. | Correct and commit the record. |
| `SPEC_PROPOSAL_NOT_FOUND` | `INPUT_ERROR` | `report`: the proposal is not in the source commit. | Pass the slug of a committed proposal. |
| `SPEC_PROPOSAL_APPROVAL_NOT_READY` | `INTERACTION` | The composed acceptance: Planning on `plan-<slug>` has unmet checks, problems, open questions or holds, needs decomposition, is not in review at `direction-handoff`, or `plan-<slug>` does not exist; or the moved target changes the reviewed proposal directory; `[DETAIL]` lists each condition and `[TARGET]` the proposal or branch. | After the user agrees, finish Planning there and rerun; for a changed proposal scope, merge the base into `plan-<slug>`, run `devkit rules fix` on the proposal, commit and rerun. |
| `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED` | `INPUT_ERROR` | The composed acceptance: the commit gate refused the acceptance commit on `plan-<slug>` (`[TARGET]`); the writes were withdrawn and `[DETAIL]` carries the gate's output. | Run `uv run devkit rules check` there, fix and commit, then rerun. |
| `SPEC_PROPOSAL_APPROVAL_REPLY_INVALID` | `INPUT_ERROR` | The requested or confirmed mode is not `accept_only` or `accept_and_handoff`, `accept_and_handoff` has no `low`, `medium` or `high` effort, or a reply widens `accept_only`; `[TARGET]` is `--mode` and `--effort`. | The caller corrects the mode or effort and reruns. |
| `SPEC_PROPOSAL_APPROVAL_STALE` | `INTERACTION` | Reviewed scope or exact acceptance delta changed. | Report what changed and the completed effects; after the user approves again, rerun for the remaining scope. |
| `SPEC_CONFIG_INVALID` | `INPUT_ERROR` | The composed acceptance: the retained base's integration policy cannot run it (`INTEGRATION_CONFIG_INVALID` in `[DETAIL]`). | Correct `.devkit/config.toml` of the base checkout. |

### Policy-aware decision boundaries

`plan-accept`, `proposal-handoff`, and `dev-integration` independently allow `ask` or `auto`, default `ask`.
CLI acceptance binds the source and base commits, configuration, environment and setup.
Owning `plan-accept=auto` authorizes checked acceptance and the Planning merge regardless of Development's final-result
policy. Source-only auto cannot grant authority, and prospective revocation refuses execution. With handoff auto it
returns an authorized continuation using the accepted `dev_effort`, run only after Host final verification; with handoff ask it leaves the accepted proposal waiting
for its separate start decision. The CLI `mode` is `accept_only` or `accept_and_handoff`; `accept_only` never starts Development even when both policies are auto, and cannot widen that requested scope.
Handoff runs under Host-carried authority for `ask` or base policy authority for `auto`. Eligibility, Git identity and partial-effect recovery apply under either authority. Internal worker sequencing, review,
retries and fixes inside the approved scope are delegated to the Host, rather than additional user approval gates.


## Approach precondition

Proposal creation, acceptance and handoff are SDD lifecycle mutations. WHILE the common approach is `adaptive-dev`,
these operations MUST refuse before changing files, branches or records with `SPEC_LIFECYCLE_INACTIVE`.
Read-only existing proposal inspection remains available. `CAP-DLV-delivery-workflows` owns the shared applicability
boundary; the direct and composed operations use the same check.
