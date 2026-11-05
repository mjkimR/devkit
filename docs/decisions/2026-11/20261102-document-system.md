---
id: ADR-document-system
title: The document system in devkit-docs and devkit-spec as its SDD layer
summary: "For documents and SDD on devkit, we keep the document model, kind table, parse memo and rules in a devkit-docs wheel and docs bundle, and SDD in devkit-spec mounted as devkit spec, to keep devkit and documents process-free, accepting more wheels, two contexts and devkit's versions."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-spec-package-on-devkit
  - ADR-rebuild-spec-on-devkit
  - ADR-mount-under-the-devkit-command-line
  - ADR-policy-in-the-tool-spec-table
  - ADR-rules-implemented-in-the-package
  - ADR-skills-named-spec
  - ADR-docs-skeleton-is-opt-in
  - ADR-content-keyed-document-parse-memo
  - ADR-parse-memo-failure-and-write-policy
  - ADR-parse-memo-location-and-format
  - ADR-kind-definition-table-keyed-on-the-declared-kind-enum
  - ADR-document-package
  - ADR-document-and-sdd-bundles
---

# [ADR-document-system] The document system in devkit-docs and devkit-spec as its SDD layer

Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: the spec bundle's rule-asset distribution clause and the document templates and the docs skeleton in the devkit-spec methodology list (its lifecycle templates stay).

Superseded in part by `ADR-selective-package-versions`: only the root-version advancement and same-version
qualifiers in the Document package and bundles Package clause; document and SDD ownership remain.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `ARCH-03-context`, `ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-08-cross-cutting`, `CAP-HARN-agent-guidance`, `CAP-HARN-command-mount`, `CAP-GOV-spec-rules`,
  `CAP-TRACE-code-entrypoints`, `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`, `CAP-DOCS-document-model`

---

## 1. Context & Problem Statement

**Spec package on devkit.** Spec-driven development was delivered as a standalone Go CLI with its own installer,
managed directory, rule runner, workflow engine, commit command, worktree commands, search and web viewer, one
executable per platform. devkit has the same generic engines: asset distribution, rules, workflows, commit gates,
search, worktrees and the Agent Advisory Protocol. Keeping both meant two implementations of every engine, two output
contracts, platform builds and macOS runner minutes in CI. Building on devkit raises the package's shape:

- **Commands**: devkit-spec needs commands of its own (`resolve`, `refs`, `list`, `search`, `new`, `proposal`,
  `entrypoints`, `scope`, `policy`). Agents, Git hooks and CI already run `uv run devkit ...`, and devkit offers the
  `devkit.commands` entry-point group: an installed package adds a command group to the `devkit` root group, imported
  only when its command runs.
- **Policy**: earlier implementations read policy from a dedicated configuration file (approvals per gate, the feedback
  sweep, pull requests, branch cleanup and `git.worktree`). `.devkit/config.toml` already models most of it:
  `[workflow.approvals]` (gate policy `ask`, `auto`, `off`), `[workflow.stages]` and `[worktree]` (`pull_request`,
  `delete_branch`, `setup`); devkit passes `[tool.<name>]` tables through unread.
- **Rules**: devkit's rule engine loads `kind = "rule"` assets from the synchronized copies of a bundle
  (`.devkit/managed/<bundle>/rules/<name>/rule.py`) and instantiates the rule classes a rule file defines; the guide
  beside the file is what `devkit rules explain` prints. The spec rules share a substantial library: the document
  index, the Markdown scanner, namespaces and the entrypoint path contract.
- **Skill names**: earlier skill designs used `sr` and `sr-*` (the specify-stage skill was `sr-spec`). devkit-spec ships
  them in the bundle `spec`, next to the command group `devkit spec` and the constitution returned by
  `devkit get-context spec`; users invoke skills by name and workflow definitions list them per stage.
- **Docs skeleton**: a `docs/` skeleton (`template/docs`, plus `glossary.yaml`) was written automatically on
  initialization. In devkit, a `kind = "document"` asset with `seeded = true` is written once where the target file is
  absent and is project-owned afterwards; an `auto_select` bundle's default preset deploys on the next `devkit sync`
  after installation.

**Document package and bundles.** One wheel held two kinds of feature. The document system (document model, lookup and
search, namespaces, document rules) serves any repository that keeps devkit documents; the SDD delivery process
(proposals, spec bundles, workflows, scope, workers, lifecycle rules) is the other. The document code imported the
delivery process: it read Planning branches to show draft proposals as `reviewing`, read namespaces through the
`[tool.spec]` policy reader and shared error, layout and helper modules with lifecycle code, so another delivery
process, such as idea incubation, could not build on the documents without SDD
(`docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md` lists the seams). Separating the
implementations still left every distributable document asset in spec: a consumer that installs only devkit-docs
lacks document guidance and rule deployment, and selecting spec introduces SDD entry obligations.
`MS-idea-incubation` needs the document formats independently of that lifecycle.

**Parse memo.** Every `DocumentIndex.load` walks `docs/` and `specs/`, reads each Markdown file and parses its
frontmatter and prose. On this repository (693 candidate files, 637 documents) the load takes about 300 ms of the
430 ms a resolve needs; YAML loading and prose scanning are most of it, the walk takes 12 to 16 ms and reading the files
8 to 53 ms (`docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`). Each command is a new process,
so the in-process memo keyed by path and text never survives between agent calls. `CAP-DOCS-document-model` excluded a
persistent cache of documents because a second source of truth can go stale, and the earlier derived-data cache was
dropped in the rebuild on devkit; a persisted result has to keep the guarantee behind both: a load returns what a fresh
build returns. The text a load parses depends on its reader: the walk reads with `Path.read_text`, which turns CRLF
and lone CR into LF, while the rules decode the bytes and keep CR; reference and alias offsets are positions in that
text, and `devkit rules fix` rewrites at them. Agents run lookups and rule checks in parallel in one worktree, a
process can be killed while writing, and the memo file can be truncated, hand-edited or written by another devkit
version; none of this may change a command's result, exit code or advisories, because the memo is an optimization the
agent never acts on (`ARCH-08-1-agent-output`). Writing about 1 MB on every call would cost more than the lookups it
serves. The memo needs a file that Git ignores, that belongs to one worktree and that loading cannot turn into code
execution. `.devkit/transient/` is the per-checkout, Git-ignored state directory: the seeded `.devkit/.gitignore`
ignores `/transient/` (`CAP-DIST-workspace-ownership`), devkit-dist keeps its journal, lock and `deployed.json` there
and devkit-agt its work units; every Git worktree has its own. The repository `.gitignore` ignores neither `.devkit/`
nor any cache directory at the root. Frontmatter values include `datetime.date` (375 in this repository), which plain
JSON cannot hold, and nested mappings may have integer, boolean, null or date keys, which `json.dumps` silently turns
into strings.

**Kind table.** The facts that make up a document kind lived in about a dozen modules (`MAT-kind-facts-inventory`
section 1): the prefix map, Living Spec membership and directories, the summary requirement, terminal statuses,
entrypoint-bearing kinds, heading-token kinds and the field-to-prefix map of the reference rule. Some consumers fall
back between kinds ("not a use case, so a capability"), so a new kind that misses one place is silently treated as
another. `Kind` members are referenced statically in 51 places outside `ids.py`, and kind-specific behavior
(lifecycles, unit anchors, path grammars) depends on that.

---

## 2. Decision Drivers

- No second implementation of a generic engine devkit already has. (ADR-rebuild-spec-on-devkit)
- devkit stays SDD-agnostic: the document model and its rules never move into devkit. (ADR-rebuild-spec-on-devkit)
- No platform binaries and no Go toolchain in consumer projects. (ADR-rebuild-spec-on-devkit)
- One agent-first output contract and one advisory format across all commands. (ADR-rebuild-spec-on-devkit)
- CI cost of private runners (no macOS builds). (ADR-rebuild-spec-on-devkit)
- One place for an agent to look for every command; devkit's startup path (lazy command loading), output options,
  Agent Advisory Protocol rendering and exit codes without reimplementing them; no drift between two root command
  groups. (ADR-mount-under-the-devkit-command-line)
- One source of truth per setting: devkit's engines act on the same value the agent reads; no second configuration
  file; agents read effective policy (defaults applied) through a command, never by parsing TOML.
  (ADR-policy-in-the-tool-spec-table)
- Rule code is tested and versioned with the package that defines the document model; every rule loads the same
  document index, and a file is parsed once per run; the deployed rule file stays stable; devkit's engine instantiates
  only classes defined in the rule file. (ADR-rules-implemented-in-the-package)
- One name for the bundle, the commands and the skills; skill names say what the skill does; no skill name that reads
  as a stutter or is confused with the router. (ADR-skills-named-spec)
- Installing the package never writes documentation a project did not ask for; a new project can still start from the
  arc42 and Living Spec structure in one command; seeded files belong to the project once written.
  (ADR-docs-skeleton-is-opt-in)
- The document system depends on no delivery process; a delivery process plugs in without editing it.
  (ADR-document-package)
- Repositories that keep SDD observe the same behavior. (ADR-document-package)
- Ownership stays explicit: one regular package per wheel and one owner per `[tool.<name>]` table.
  (ADR-document-package)
- No external consumer exists yet, so interfaces change in place without shims (AGENTS.md Compatibility).
  (ADR-document-package)
- Document-only installations carry no implicit SDD entry, approval or history obligations.
  (ADR-document-and-sdd-bundles)
- Existing SDD installations retain their lifecycle guidance and default behavior. (ADR-document-and-sdd-bundles)
- Each asset has one owning wheel and bundle; generic distribution semantics remain unchanged.
  (ADR-document-and-sdd-bundles)
- Results identical to a fresh build after edits, renames, deletions, alias changes and branch switches, in any
  worktree, independent of file timestamps and clocks. (ADR-content-keyed-document-parse-memo)
- No second source of truth: the files stay the only input to what a load returns.
  (ADR-content-keyed-document-parse-memo)
- Lookup latency in the common case, where no document changed since the last call.
  (ADR-content-keyed-document-parse-memo)
- A parser change invalidates every persisted result without a manual version bump.
  (ADR-content-keyed-document-parse-memo)
- Every result equals a fresh build, whatever state the memo file is in. (ADR-parse-memo-failure-and-write-policy)
- No new advisory, code or exit status; diagnostics only under `-v`. (ADR-parse-memo-failure-and-write-policy)
- No lock wait on the lookup path and no deadlock between readers and writers.
  (ADR-parse-memo-failure-and-write-policy)
- No write when nothing changed; rule runs write nothing beyond their fixes. (ADR-parse-memo-failure-and-write-policy)
- Never shown by `git status`, never staged, never read by the rules (they skip Git-ignored files).
  (ADR-parse-memo-location-and-format)
- One memo per worktree, with no cross-worktree sharing to coordinate. (ADR-parse-memo-location-and-format)
- Loading a damaged or planted file yields at worst wrong-shaped data, which validation rejects, never code execution.
  (ADR-parse-memo-location-and-format)
- Load cost small next to the 300 ms it saves. (ADR-parse-memo-location-and-format)
- One place to read and change each per-kind fact. (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- A missing fact for a kind fails a check instead of falling back to another kind.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Pyright keeps seeing every `Kind` member; the layer direction stays intact (models never import higher layers).
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Every current ID, path, rule code, message and output stays byte-identical.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)

---

## 3. Considered Options

### Package shape
- **Python layer on devkit** (selected in `ADR-rebuild-spec-on-devkit`): ships the methodology as a devkit bundle and
  the SDD commands as a devkit command group; one pure wheel (`py3-none-any`); devkit's engines reused as they are; one
  output contract and error boundary. Cons: devkit-spec follows devkit's minor versions and breaking changes; behaviour
  that depended on the standalone CLI's commands is reshaped where devkit cannot call devkit-spec.
- **Keep the standalone Go CLI next to devkit** (rejected in `ADR-rebuild-spec-on-devkit`): no porting work, but every
  engine twice, two receipts, two hook systems, two output contracts; platform builds remain.
- **Move spec-driven development into devkit** (rejected in `ADR-rebuild-spec-on-devkit`): one package, but devkit stops
  being SDD-agnostic and every devkit consumer receives one methodology's rules and commands.
- **Port to Python as a standalone tool** (rejected in `ADR-rebuild-spec-on-devkit`): no dependency on devkit, but
  duplicates devkit as the Go CLI does, only in another language.

### Command entry
- **`devkit spec` through `devkit.commands`** (selected in `ADR-mount-under-the-devkit-command-line`): one executable;
  `devkit --help` lists `spec`; devkit's error boundary; an import failure fails only `devkit spec`
  (`COMMAND_PLUGIN_INVALID`). Cons: the plugin is visible only in the environment devkit-spec is installed in;
  `devkit --version` reports devkit only.
- **A separate `devkit-spec` console script** (rejected in `ADR-mount-under-the-devkit-command-line`): duplicates the
  root group, its options and its boundary; two executables; the groups drift.
- **`python -m devkit_spec`** (rejected in `ADR-mount-under-the-devkit-command-line`): not discoverable from
  `devkit --help`; a second invocation convention.

### Policy location
- **devkit's tables for what devkit models, `[tool.spec]` for the rest** (selected in
  `ADR-policy-in-the-tool-spec-table`): devkit's engines read their own settings; no duplicate keys. Cons: policy spans
  several tables, which is why the policy command exists.
- **Everything in `[tool.spec]`** (rejected in `ADR-policy-in-the-tool-spec-table`): two sources of truth; devkit's
  engines would not see the mirrored values.
- **A devkit-spec configuration file** (rejected in `ADR-policy-in-the-tool-spec-table`): a second file to find,
  validate and keep consistent.

### Rule code location
- **Logic in `devkit_spec.rules`, thin subclass files in the bundle** (selected in
  `ADR-rules-implemented-in-the-package`): rules are ordinary package modules covered by the package's tests and share
  `document_index(ctx)` and the other helpers. Cons: the deployed file imports `devkit_spec`, so the package must be
  installed wherever `devkit rules` runs.
- **Full rule code in the deployed rule files** (rejected in `ADR-rules-implemented-in-the-package`): the shared
  library is duplicated or loaded by path; code tested as copies; a change rewrites every managed file.
- **Built-in rules in devkit** (rejected in `ADR-rules-implemented-in-the-package`): puts the document model into
  devkit.

### Skill names
- **`spec`, `spec-*`, with `sr-spec` renamed `spec-specify`** (selected in `ADR-skills-named-spec`): names match the
  bundle and commands; stage skills match stage ids. Cons: users relearn the names.
- **Keep `sr`, `sr-*`** (rejected in `ADR-skills-named-spec`): a legacy prefix unrelated to the bundle and the
  commands.
- **Mechanical rename including `spec-spec`** (rejected in `ADR-skills-named-spec`): a stutter, easy to confuse with the
  `spec` router.

### Docs skeleton
- **A separate `docs-skeleton` preset** (selected in `ADR-docs-skeleton-is-opt-in`): no surprise files; one command for
  a new project. Cons: one more step for projects that want it.
- **The skeleton in the `core` preset** (rejected in `ADR-docs-skeleton-is-opt-in`): writes into existing `docs/` trees
  wherever a seeded file is absent.
- **No skeleton** (rejected in `ADR-docs-skeleton-is-opt-in`): new projects rebuild the directory structure, arc42
  chapters and glossary by hand.

### Document package
- **A separate devkit-docs wheel that devkit-spec depends on** (selected in `ADR-document-package`): one owner per
  package and an enforceable boundary, at the cost of one more wheel to release.
- **Keep one package and control lifecycle features through presets** (rejected in `ADR-document-package`): the
  cheapest change, but the coupling inside one package has no import boundary to enforce.
- **A second regular package inside the devkit-spec wheel** (rejected in `ADR-document-package`): separates imports,
  but one wheel would hold two packages, against `ADR-package-ownership-and-release-version`.

### Document and SDD bundles
- **Separate docs and spec bundles** (selected in `ADR-document-and-sdd-bundles`): aligns with wheel ownership and
  enables independent selection; requires context, reference, seed and test repairs and a second context read in SDD
  sessions.
- **Keep spec unchanged** (rejected in `ADR-document-and-sdd-bundles`): no distribution cost, but docs-only consumers
  lack its corresponding guidance and rules.
- **Add document/lifecycle presets within spec** (rejected in `ADR-document-and-sdd-bundles`): fewer bundle names, but
  a docs-only install still depends on the SDD wheel and its runtime extensions or duplicates document assets across
  wheels.

### Parse memo key
- **Content digest per file** (selected in `ADR-content-keyed-document-parse-memo`): every load still walks and reads
  every file and hashes the text it parses (BLAKE2b, about 2.5 ms here), then reuses the stored parse result when the
  path and digest match. Correct by construction: the parse result is a function of the path and the text, the
  identity the in-process memo already uses. A digest of the raw bytes instead would be wrong: one set of bytes gives
  different texts to different readers.
- **Keep rebuilding per load** (rejected in `ADR-content-keyed-document-parse-memo`): always correct, about 300 ms per
  call on this repository.
- **Stat signature (size, mtime, ctime, inode)** (rejected in `ADR-content-keyed-document-parse-memo`): skips reading
  unchanged files (10 to 50 ms more per call), but a write within one timestamp tick after the stat goes unnoticed on
  coarse-timestamp file systems, and guarding that race needs clock comparisons that clock skew on network file
  systems breaks.
- **Persist the whole index under one tree key** (rejected in `ADR-content-keyed-document-parse-memo`): any edit
  rebuilds everything, and computing the tree key still needs per-file identity.

### Parse memo failures and writes
- **Lock-free atomic replace, last writer wins** (selected in `ADR-parse-memo-failure-and-write-policy`): each writer
  replaces the file in one rename; a reader sees the old or the new memo, never a partial one. Two concurrent writers
  lose one update, which costs a parse later.
- **Lock-protected read-modify-write** (`devkit_core.core.file_lock`) (rejected in
  `ADR-parse-memo-failure-and-write-policy`): serializes writers, but every lookup takes a lock, and a read-only file
  system or a stuck holder needs extra handling.
- **Per-entry files** (rejected in `ADR-parse-memo-failure-and-write-policy`): no lost updates, but hundreds of small
  files to read per load.
- **Report a corrupt memo as a notice** (rejected in `ADR-parse-memo-failure-and-write-policy`): visible, but tells the
  agent nothing it must act on.

### Parse memo location and format
- **A file under the worktree's `.devkit/transient/`** (selected in `ADR-parse-memo-location-and-format`): ignored by
  the seeded `.devkit/.gitignore`, per worktree, follows the existing transient convention; absent in a workspace that
  was never synced.
- **The worktree's Git directory** (`<git-dir>/devkit-spec-document-index.json`) (rejected in
  `ADR-parse-memo-location-and-format`): ignored without any `.gitignore`, but needs the Git directory resolved on every
  call and puts derived data where devkit-spec otherwise keeps only the scope token.
- **A user cache directory** (`~/.cache/devkit/...`, keyed by worktree path) (rejected in
  `ADR-parse-memo-location-and-format`): outside the workspace, survives worktree removal as garbage and needs its own
  cleanup.
- **Format: JSON with every container tagged** (selected in `ADR-parse-memo-location-and-format`): lists and mappings
  become tagged objects and a mapping a list of key-value pairs, so no value is ambiguous; the frontmatter of all 637
  documents decodes in 1.4 to 1.9 ms.
- **Format: pickle** (rejected in `ADR-parse-memo-location-and-format`): fastest (about 5 ms) and keeps every type, but
  loading a crafted file runs code.
- **Format: JSON with tagged dates only** (rejected in `ADR-parse-memo-location-and-format`): about 3 ms to decode, but
  a nested non-string key is coerced to a string and a literal one-key mapping shaped like a tag decodes as a date.

### Kind table
- **Declared enum plus one row per member** (selected in
  `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`): the enum stays the static name of a kind, the row holds
  its data, and a check requires exactly one row per member; a new kind adds a member and a row.
- **Keep the scattered constants** (rejected in `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`): no change
  cost; a new kind still needs a search and fallbacks stay silent.
- **Table generates the enum** (`StrEnum("Kind", rows)`) (rejected in
  `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`): one source in theory; Pyright loses every member, so 51
  static references fail `just check` or turn into string lookups.

---

## 4. Decision Outcome

devkit-spec is a Python layer on devkit, mounted as `devkit spec`, and the document system is the separate devkit-docs
wheel and docs bundle it depends on. The document index persists a content-keyed parse memo per worktree, and document
kinds are a declared enum with one definition row per member. These best satisfy the drivers of no duplicated engine,
an SDD-agnostic devkit, a document system free of any delivery process, results identical to a fresh build and one
place per kind fact.

### Spec package on devkit

- Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: document templates and "docs skeleton" in the next item; lifecycle templates stay.
- devkit-spec is a Python package on devkit's public surface. It keeps only what is spec-driven: the methodology
  (routes, workflow definitions, stage skills, role contracts, templates, docs skeleton, reconciliation) and the policy
  that turns devkit's engines into SDD behaviour (which rules run, which checks gate a stage, how search scopes and pins
  documents, which routes run in a worktree). devkit stays SDD-agnostic and owns every generic engine.
  (ADR-rebuild-spec-on-devkit)
- devkit-spec ships its commands as the `devkit spec` group through
  `[project.entry-points."devkit.commands"] spec = "devkit_spec.cli:cli"`, with no console script; the commands inherit
  devkit's loading, output contract and error boundary. (ADR-mount-under-the-devkit-command-line)
- `devkit spec --version` prints `[VERSION: devkit-spec <version>]`; `devkit --version` reports devkit only.
  (ADR-mount-under-the-devkit-command-line)
- Approvals, stage switches and worktree integration stay in devkit's tables (`[workflow.approvals]`,
  `[workflow.stages]`, `[worktree]`); `[tool.spec]` holds `worktree` and `[tool.spec.scope]`; `devkit spec policy`
  prints the effective values of both. Mapping: approvals to `[workflow.approvals]`
  (`ADR-delivery-approval-and-lifecycle-authority`), the feedback sweep to `[workflow.stages]` (`collect-feedback`), `pull_request`
  and branch cleanup to `[worktree]`, `git.worktree` to `[tool.spec] worktree`. (ADR-policy-in-the-tool-spec-table)
- The spec rules are implemented and tested in the package; each `bundle/rules/<name>/rule.py` imports the package's
  rule class and subclasses it, with the guide `guide.md` beside it. Rules read files only through `ctx.cache` so
  snapshot runs and rechecks see the right tree. (ADR-rules-implemented-in-the-package)
- The bundle's skills are named `spec` and `spec-<x>` after the bundle and command group; the specify-stage skill is
  `spec-specify`, not `spec-spec`. The workflow `skills:` lists and the role contracts' `skill` fields use these names.
  (ADR-skills-named-spec)
- The seeded `docs/` skeleton (Living Spec directories, arc42 chapters, glossary and search synonyms) ships in its own
  preset, `[presets.docs-skeleton] assets = ["docs-skeleton"]`, added with `devkit add docs:docs-skeleton`, so
  installing devkit-spec never writes files into an existing `docs/` tree. (ADR-docs-skeleton-is-opt-in)
- A generic capability devkit-spec needs is added to devkit first. (ADR-rebuild-spec-on-devkit)
  → `ARCH-05-1-containers` §2.5 (MUST)

### Document package and bundles

- **Package**: `devkit-docs` with the regular package `devkit_docs` owns `features/documents`, the document rules'
  implementations and services (`features/governance`), the entrypoint path contract, the `DOCS_` errors and the
  document layout vocabulary. Its version advances only for changed payload or exact-pin dependencies
  (`ADR-selective-package-versions`). devkit-spec pins its selected actual version and keeps the delivery process and the lifecycle rules. This extends the wheel list of
  `ADR-package-ownership-and-release-version`. (ADR-document-package)
- **Kind vocabulary**: every document kind, the delivery kinds included, stays in the document package's kind table.
  The formats and path grammars of proposals, spec bundles, feedback and milestones are document structure. What a
  delivery process does with them stays in that process. (ADR-document-package)
- **Extension point**: a delivery process changes how `devkit docs list` shows documents through the entry-point
  group `devkit.docs.status_overlay`; devkit-spec registers the Planning display of draft proposals. A failing
  overlay is left out with a `DOCS_OVERLAY_FAILED` warning, like devkit's other extension groups. Other lifecycle
  behavior moves only when a seam requires it. (ADR-document-package)
- **Configuration**: document namespaces are `[[tool.docs.namespaces]]`, owned and read by devkit-docs. The rules and
  the `devkit docs` commands read only `[tool.docs]`, so a malformed `[tool.spec]` is reported by the commands that
  read it (`devkit spec policy`, `scope`, `proposal`, integration), not by a rules run. The document memo lives with
  its package under `.devkit/transient/docs/`. (ADR-document-package)
- **Commands and codes**: `devkit docs resolve|refs|list|search` replace the `devkit spec` forms. The document codes
  move from `SPEC_` to `DOCS_`, and `DOCS_CONFIG_INVALID` reports a malformed `[tool.docs]`. (ADR-document-package)
- **Scanner**: the document model keeps using devkit-agt's Markdown scanner; moving it to devkit-core is unrelated to
  this boundary. (ADR-document-package)
- Superseded in part by `ADR-retire-native-approval-and-moved-ownership-clauses`: the next item.
- **Distribution**: the spec bundle keeps shipping every rule asset, and the document rules' wrappers import
  devkit_docs. A document-only installation is separate work (`SPEC-document-bundle-split`). (ADR-document-package)
- devkit-docs owns the auto-selected `docs:core`, all shared writing instructions, document rules and templates, the
  document-only constitution/pointer, steering context discovery and opt-in `docs:docs-skeleton`.
  (ADR-document-and-sdd-bundles)
- devkit-spec retains auto-selected `spec:core`, lifecycle templates/rules/workflows/roles/skills/playbooks, the SDD
  pointer and lifecycle obligations. It requires the docs context rather than copying its instructions.
  (ADR-document-and-sdd-bundles)
- Package installation selects both bundles for SDD by default through the existing package dependency and
  auto_select semantics. Explicitly deselecting a bundle changes assets, not installed Python extensions.
  (ADR-document-and-sdd-bundles)
- Shared writing policy describes document structure and current-state authoring. SDD retains accepted-decision
  supersession, completed-artifact preservation and mandatory reconciliation in its own guidance.
  (ADR-document-and-sdd-bundles)
- No migration shim, cross-bundle dependency engine or runtime lifecycle bypass is introduced. The supported SDD setup
  includes docs; the supported clean document-only setup omits the devkit-spec distribution.
  (ADR-document-and-sdd-bundles)

### Parse memo

- The memo keys each file by content digest, because that meets the identity and no-second-source drivers without any
  timestamp or clock assumption; the prototype cut the index load from about 310 ms to about 55 ms.
  (ADR-content-keyed-document-parse-memo)
- **Entry key**: the workspace-relative path and the BLAKE2b digest of the UTF-8 encoding of the exact text
  `parse_document` would receive, after the reader's decoding and newline handling. A load reads every file the walk
  (or the caller's file list) yields, computes the digest and reuses the stored result only on an exact match; any
  other file is parsed again. A renamed file is a new path and is parsed again. The same file read by a walk and by the
  rules reader gives two texts and two digests when it holds CR, so neither reuses the other's offsets.
  (ADR-content-keyed-document-parse-memo)
- **Stored result**: what parsing yields for that path and text: the `Document`, "no document" (no well-formed ID), or
  the `DOCS_DOCUMENT_INVALID` reason of a malformed frontmatter. A file that cannot be read or decoded has no text and
  no entry; it is reported as before on every load. (ADR-content-keyed-document-parse-memo)
- **Parser fingerprint**: one value for the whole memo, from a format version, the source bytes of every module on the
  read, parse and codec path (`devkit_docs.features.documents.models`, `devkit_docs.features.documents.repositories`
  with the memo codec, `devkit_core.core.frontmatter` and `devkit_core.base.errors`), the PyYAML version and whether
  libyaml is present, and the Python version. A different fingerprint discards the memo. When a module's source cannot
  be read, the memo is not used. (ADR-content-keyed-document-parse-memo)
- **Derived state stays per load**: ID and alias maps, `historical`, ordering and problems are built from the entries
  on every load; only the per-file parse result is reused. (ADR-content-keyed-document-parse-memo)
- **Scope of reuse**: every `DocumentIndex.load` reads the memo of its root, including loads with a caller-supplied
  file list and reader, because a text key is valid for any source of the text. In practice that is walk loads and
  spec rule runs on the working tree (and in-place staged runs); a materialized Git snapshot is a temporary directory
  without `.devkit/transient/` and has no memo. (ADR-content-keyed-document-parse-memo)
- `WorkspaceCache.get_catalog` (devkit-agt) is not changed: it is a generic catalog without the document model, and
  `devkit-agt` cannot depend on `devkit-spec`. (ADR-content-keyed-document-parse-memo)
- Failures and writes use lock-free atomic replace, last writer wins, with a memo trusted only after validation,
  because it meets the identity, silence and no-wait drivers; a lost update only costs a later parse.
  (ADR-parse-memo-failure-and-write-policy)
- **Discard rules**: a memo that is missing, unreadable, not valid UTF-8 JSON, not the expected shape, of another
  `version` or of another `fingerprint` is treated as empty. An entry whose stored result cannot be rebuilt is a miss.
  In both cases the load parses those files as a fresh build would, and the memo is rewritten.
  (ADR-parse-memo-failure-and-write-policy)
- **Non-regular memo path**: a directory or other non-regular file at the memo path is never removed. The load returns
  a fresh build's result and skips the write, with a `-v` log line. (ADR-parse-memo-failure-and-write-policy)
- **Silence**: discarding or failing to write the memo emits no advisory or notice and never changes the exit status;
  each case logs one `logging` line, visible under `-v`. (ADR-parse-memo-failure-and-write-policy)
- **Writers**: only a load that walks the workspace itself (no caller-supplied file list or reader) writes, and only
  when its entries differ from what it read (a new, changed or removed file, or a discarded memo). Its entries are
  exactly the files that load read and decoded, each with its stored result or an "unstorable" marker, so deleted and
  renamed files are pruned and an unstorable document does not count as a change. A file that cannot be read or
  decoded has no entry before or after and is no change either. Loads with a supplied file list or reader, which the
  spec rules use, read the memo and never write it. (ADR-parse-memo-failure-and-write-policy)
- **Write**: `devkit_core.core.atomic_write_bytes` (temporary file, then rename). An `OSError` (read-only file system,
  permissions, full disk) is logged under `-v` and ignored. (ADR-parse-memo-failure-and-write-policy)
- **Concurrency**: no lock. Concurrent writers each write a complete memo of entries that matched the text they read;
  whichever lands last is kept, and an entry that no longer matches its file is a miss on the next load.
  (ADR-parse-memo-failure-and-write-policy)
- The memo is one file under `.devkit/transient/` in JSON with every container tagged, because they meet the ignore,
  per-worktree and safe-load drivers with no new ignore rule, a faithful round trip and a load cost under 10 ms.
  (ADR-parse-memo-location-and-format)
- **Location**: `<root>/.devkit/transient/docs/document-index.json`, `<root>` being the root the load indexes. The memo
  is used only when `<root>/.devkit/transient/` exists as a directory, neither it, `docs/` nor the memo path is a
  symbolic link, and the memo path resolves inside `<root>`; otherwise the load builds without the memo and creates no
  file or directory. `docs/` is created on the first write. (ADR-parse-memo-location-and-format, ADR-document-package)
- **Format**: one UTF-8 JSON object with `version`, `fingerprint` and `entries` (path to digest and stored result).
  Strings, booleans, integers, finite floats and null stay plain; every list, mapping, `datetime` and `date` is a
  one-key tagged object (a mapping as a list of key-value pairs, so any key type survives; `datetime` checked before
  `date`, with its UTC offset). A parse result holding any other value (a non-finite float, another type) is stored as
  an "unstorable" marker with its digest and parsed on each load. (ADR-parse-memo-location-and-format)
- Deleting the file is always safe: the next load rebuilds it. (ADR-parse-memo-location-and-format)

### Kind table

- `Kind` stays a declared enum with one definition row per member, because it is the only option that keeps static
  checking while giving one place per fact and a failing check.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- The table lives in `features/documents/models/` beside `ids.py`, as frozen dataclass rows with no imports above the
  models layer; the governance rules, browse, search and the CLI already import the documents feature.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- A row holds the prefix, the kind, the Living Spec directory or none, whether the directory is area-scoped, whether
  `RULE-spec-format` checks its directory (globally and in namespaces), whether its first H1 carries an ID token, its
  summary requirement (always, anchor file only, never), whether it bears `entrypoints`, its terminal statuses, its
  default status at fix time, and the relation fields that accept it (`usecases` and `related_usecases` accept `UC`,
  and so on). Rows follow the enum order, which `devkit docs list` and the CLI choices use; there is no separate
  position field. (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Each relation field maps to exactly one prefix, checked for uniqueness: `depends_on` sits only on the milestone row,
  and its unit-anchor case (`PROP-`/`SPEC-`) stays code. The use case and capability link pair of
  `RULE-traceability-link` is one explicit pair declaration beside the rows, not row data.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Consumers read the rows through one accessor called at check time, never through constants bound at import; the ID
  regexes (`ID_SOURCE`, `ID_PATTERN`) are the exception and are built from the rows at import.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum) → `CAP-DOCS-document-model` §3.2 (MUST)
- The path-keyed copies of a fact derive from the rows too: `entrypoints/services/paths.py` builds its
  entrypoint-bearing directories from them. (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- `PREFIXES`, `ID_SOURCE`, `ID_PATTERN`, `kind_of` and `is_id` keep their names and signatures and derive from the
  rows. (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Consumers read these facts from the table; the fallbacks between kinds (`MAT-kind-facts-inventory` section 1) are
  replaced by explicit lookups, and a kind without a required fact raises instead of taking another kind's value. The
  values the lookups return reproduce the earlier messages byte for byte.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- Kind-specific behavior stays code: path and stem grammars per kind, spec bundle files, unit anchors and their
  relation rules (`depends_on`, `milestone`, provenance), spec, proposal, feedback and milestone lifecycles
  (`MAT-kind-facts-inventory` section 2). Each Living Spec row needs a path-grammar branch in `RULE-id-convention`, and
  a row without one raises, so no kind is checked under another kind's grammar.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- The table holds no template field: templates stay bundle files, because no code reads them.
  (ADR-kind-definition-table-keyed-on-the-declared-kind-enum) → `CAP-DOCS-document-model` §3.2 (MUST NOT)

---

## 5. Consequences

- **Positive**:
  - One wheel and one executable for SDD; devkit's targeting and snapshot runs apply to the spec rules; a generic
    improvement made in devkit benefits devkit-spec at once. (ADR-rebuild-spec-on-devkit)
  - Every command keeps devkit's output contract (`ARCH-08-cross-cutting`); `devkit spec` is imported only when it
    runs, so built-in commands never pay for it. (ADR-mount-under-the-devkit-command-line)
  - `[GATE_POLICY ...]`, `[STAGE_POLICY ...]` and `[GIT_POLICY ...]` lines reflect exactly what devkit's engines use,
    with `source=config|default`. (ADR-policy-in-the-tool-spec-table)
  - The rule implementation and its tests change together; the managed copy is a stable one-liner and the guide is the
    only rule text a project reads. (ADR-rules-implemented-in-the-package)
  - The skeleton is written once where absent and never updated by later syncs; `glossary.yaml` lives at
    `docs/steering/glossary.yaml` (moved by `ADR-steering-documents`), the synonym list of `devkit docs
    search`. (ADR-docs-skeleton-is-opt-in)
  - The document layer has no import edge to the delivery process, and the architecture declaration enforces that.
    Idea incubation or another process can reuse the document system. (ADR-document-package)
  - Document-only consumers install rule assets, formats and guidance without SDD lifecycle entry assets.
    (ADR-document-and-sdd-bundles)
  - A lookup in an unchanged workspace drops from about 430 ms to about 170 ms on this repository, and spec rule runs
    in a workspace with a memo skip parsing unchanged documents. (ADR-content-keyed-document-parse-memo)
  - Branch switches, `git checkout` of old content, copies that keep timestamps, clock skew and line-ending
    differences between readers cannot produce a stale result; at worst a file is parsed again.
    (ADR-content-keyed-document-parse-memo)
  - A lookup never waits, never fails because of the memo, and writes nothing in the steady state.
    (ADR-parse-memo-failure-and-write-policy)
  - Rule runs on the working tree gain the parse reuse without writing to the workspace.
    (ADR-parse-memo-failure-and-write-policy)
  - No repository `.gitignore` change and no new ignored path; the memo follows the checkout, so worktrees, clones and
    branch switches never share it. (ADR-parse-memo-location-and-format)
  - Adding a kind is a member, a row, a path-grammar branch and a template plus any kind-specific behavior, and a
    forgotten fact or branch fails the exhaustiveness check.
    (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- **Negative / Risks**:
  - devkit is pinned to a minor range (`devkit>=0.1,<0.2`) and devkit-spec moves with it; devkit's `workflow next` and
    `worktree finish` cannot call devkit-spec, so the skills run the scope commands
    (`ADR-worktrees-and-scope`); some earlier features were dropped (derived-data cache, web viewer, per-kind
    listing filters). (ADR-rebuild-spec-on-devkit)
  - The plugin is visible only in the environment devkit-spec is installed in; the `spec` name is reserved for this
    plugin by convention; a broken install surfaces as `COMMAND_PLUGIN_INVALID` on `devkit spec` only.
    (ADR-mount-under-the-devkit-command-line)
  - A malformed `[tool.spec]` is `SPEC_CONFIG_INVALID`. (ADR-policy-in-the-tool-spec-table)
  - A project, its commit gate and its CI must install devkit-spec in the environment that runs `devkit rules check`
    (`ARCH-07-deployment`). (ADR-rules-implemented-in-the-package)
  - Users relearn the skill names. (ADR-skills-named-spec)
  - Improvements to the seed reach existing projects only when they copy them by hand. (ADR-docs-skeleton-is-opt-in)
  - Agents and guidance must use the renamed commands and codes. A malformed `[tool.spec]` no longer fails
    `devkit rules check`; `devkit spec policy`, which SDD work runs before classification, still rejects it. Projects
    with `[[tool.spec.namespaces]]` must move them to `[[tool.docs.namespaces]]`; a leftover entry is rejected as an
    unknown key. Releases build one more wheel. (ADR-document-package)
  - All moved asset citations and tests must track their owning bundle; SDD sessions read two contexts.
    (ADR-document-and-sdd-bundles)
  - Copied seeded READMEs or neutral-looking instructions can retain SDD directives. Semantic review and isolated
    wheel installation smoke cover this risk. Existing consumer seeded files remain project-owned.
    (ADR-document-and-sdd-bundles)
  - Every load still reads every document (8 to 53 ms here), which a stat signature would skip.
    (ADR-content-keyed-document-parse-memo)
  - Two devkit installations with different fingerprints used in one worktree discard each other's memo on every call;
    results stay correct and only the speed-up is lost. (ADR-content-keyed-document-parse-memo)
  - The Non-Goal in `CAP-DOCS-document-model` changes from "no persistent cache" to "no persistent source of truth":
    the memo holds derived parse results only and never decides which files exist.
    (ADR-content-keyed-document-parse-memo)
  - Concurrent writers can drop each other's new entries; the next load parses those files again and writes.
    (ADR-parse-memo-failure-and-write-policy)
  - A process killed between the temporary write and the rename leaves a temporary file in `.devkit/transient/docs/`,
    ignored by Git; `atomic_write_bytes` removes it on every error it sees.
    (ADR-parse-memo-failure-and-write-policy, ADR-document-package)
  - A workspace without `.devkit/transient/` (never synced, or a test fixture) gets no memo. A workspace that installs
    the `spec` bundle has been synced, so the cost falls on bare fixtures only. (ADR-parse-memo-location-and-format)
  - About 1 MB on disk per worktree for this repository's 693 files. (ADR-parse-memo-location-and-format)
  - A project that removes `/transient/` from `.devkit/.gitignore` sees the memo as an untracked file; that edit
    already exposes the sync journal and lock the same way. (ADR-parse-memo-location-and-format)
  - A rule message that was wrong before the kind table stays wrong through it (the milestone path remediation); its
    fix is a separate bugfix. (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
  - The enum and the table are two declarations of the same set; the check keeps them equal.
    (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
  - A fact whose consumers disagree (for example the heading-token set excludes `PROP`, `PADR` and `MAT` while other
    sets include them) must be encoded per consumer, not unified, or a message changes.
    (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
- **Follow-ups**:
  - This repository selects the preset (`docs = ["core", "docs-skeleton"]`) and has replaced the seeded content with
    its own Living Spec. (ADR-docs-skeleton-is-opt-in)
  - `SPEC-document-bundle-split` provides a document-only installation. The viewer hard-codes kind prefixes and
    layout; a change to the kind table must be mirrored there. (ADR-document-package)
  - Incubation runtime policy, orchestration and optional verified SDD adoption stay under `MS-idea-incubation`; the
    bundle split does not satisfy those milestone exits. (ADR-document-and-sdd-bundles)
  - If measurement on larger workspaces shows the read dominating, a stat signature can be added in front of the digest
    as a pure optimization, under a new decision. (ADR-content-keyed-document-parse-memo)
  - `SPEC-ux-documentation` adds its kind through the table once the kind table lands.
    (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)

---

## 6. Confirmation

- `packages/devkit-spec/tests/e2e/package/test_package.py`: the entry points are installed, `spec` is not a built-in
  devkit command and `devkit` mounts the `spec` group, `devkit sync` deploys the default preset and its rules run,
  `devkit config template` writes the spec tables, and the docs skeleton is opt-in and passes the rules.
  (ADR-spec-package-on-devkit)
- `packages/devkit-spec/tests/integration/features/policy/test_cli_policy.py`: `devkit spec policy` reports the
  effective policy. (ADR-spec-package-on-devkit)
- The rule folders under `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/*/tests/` test each rule
  against the package's implementation. (ADR-spec-package-on-devkit)
- `RULE-architecture` checks the `devkit_docs` and `devkit_spec` declarations in `.devkit/architecture.toml`.
  `packages/devkit-docs/tests` covers the commands, codes, `[tool.docs]` and its template. The status overlay is
  covered by `packages/devkit-spec/tests/integration/features/proposals/test_backlog_guard.py`. Each package's
  `tests/integration/package/test_documented_codes.py` requires every code to be documented. (ADR-document-package)
- Development adds bundle inventory/reference assertions and an isolated consumer installation smoke without installed
  devkit-spec. It verifies default SDD selection, explicit spec deselection, opt-in seeding and preservation of
  existing seeded bytes. `devkit sync --check` verifies this repository's projected assets. The feature's acceptance
  scenarios AC-01 through AC-06 define the verification boundary; exact test paths are set in its plan.
  (ADR-document-and-sdd-bundles)
- Tests in `packages/devkit-docs/tests/integration/features/documents/` compare loads with and without a memo after
  edits (including a same-size edit with a restored mtime), renames, deletions, alias and ID changes, malformed and
  non-UTF-8 files, a Git branch switch and back, and a changed fingerprint; and CRLF, lone-CR and BOM documents loaded
  by a walk and by a supplied reader in both orders, including `devkit rules check` reports and `devkit rules fix`
  results. A unit test fails when a module on the read, parse or codec path is missing from the fingerprint.
  (ADR-content-keyed-document-parse-memo)
- Tests: a truncated file, invalid JSON, a wrong `version` or `fingerprint` and a malformed entry each give results
  equal to a fresh build, the same exit code, no advisory without `-v` and a rewritten memo; a directory at the memo
  path and an unwritable `.devkit/transient/docs/` each give a fresh build's result and leave the path as it was. A
  load with no changed file leaves the memo's bytes and modification time unchanged, also with an unstorable document
  and an unreadable file present; a load with a supplied file list never creates or changes it. Several processes
  loading and writing at once all return a fresh build's result. (ADR-parse-memo-failure-and-write-policy)
- Tests: a workspace without `.devkit/transient/` gets no memo file; a symbolic link at `.devkit/transient/`, `docs/`
  or the memo path is not followed; frontmatter with a date, a naive `datetime`, an aware `datetime` (`Z` and
  `+09:00`), nested integer, boolean and null keys and a literal tag-shaped mapping round-trips to equal frontmatter,
  and a non-finite float is stored as unstorable. Review: `CAP-DOCS-document-model` names the path and states that
  deleting it is safe. (ADR-parse-memo-location-and-format)
- A unit test in `packages/devkit-docs/tests/unit/features/documents/` asserts one row per `Kind` member, in enum
  order, and that `PREFIXES` equals the earlier map. A unit test patches the accessor with a table whose use case row
  names another Living Spec directory and whose capability row accepts another relation field, and shows that
  `RULE-id-convention`, `RULE-traceability-link` and `RULE-document-reference` follow the table with no other code
  change; it asserts which files are checked and as which kind, not message text. A unit test asserts that each
  relation field maps to exactly one prefix, and that every Living Spec row has a path-grammar branch. The existing
  suites and the rule tests under `bundles/spec/bundle/rules/*/tests/` pass unchanged; a characterization fixture
  workspace gives identical `devkit rules check` JSON and `devkit rules fix` diffs, and `devkit docs list`,
  `devkit docs search` JSON and their `--help` text are identical before and after (`MAT-kind-facts-inventory`
  section 5). (ADR-kind-definition-table-keyed-on-the-declared-kind-enum)
