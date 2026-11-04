# Namespace steering: inventory, evidence and option comparison (Planning spike, Q1 to Q3)

Everything that reads, checks or names the root steering directory today, the evidence for a namespace copy, and the
options weighed for the three spike questions. Function names refer to the Planning branch head.

## 1. Inventory: what touches `docs/steering/` today

### Code

| Location | Today | Change the namespace copy needs |
| --- | --- | --- |
| `packages/devkit-docs/src/devkit_docs/features/governance/usecases/steering_documents.py` (`DIRECTORY`, `SteeringDocumentsRule.check`) | One literal `docs/steering`; messages, remediation and the `max_files` count name that directory; the module docstring states "there is no namespace copy" | Iterate `docs_roots(registered)` (`namespaces.py`) and check `<root>/steering/` per directory with the same checks and caps, each directory only when a file in it is targeted (the early return and the over-cap report become per directory, challenger-01 #6); messages name the actual directory; `glossary.yaml` stays root-only and a `glossary.md` or `glossary.yaml` in a namespace directory is reported (challenger-01 #5). An unregistered `docs/packages/<name>/steering/` is skipped, as `living_path` skips it for the other rules. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/steering_documents/` (`rule.py`, `guide.md`, `tests/test_rule.py`) | Loader, guide and fixtures for the root directory only | Guide gains the namespace directory; fixtures gain a registered namespace (clean, nested file, over cap, missing summary, Korean title with an English summary) and an unregistered one. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/context_documents.py` (`declared_directory`, `list_documents`) | Lists one declared directory; read rules of `ADR-steering-documents` (the listing mechanism) | Unchanged read rules; called once per directory. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/context.py` (`GetContext.execute(start, bundle)`) | `start` is only used to find the project root; lists `list_documents(root, directory)` | Takes the working directory as a second input, collects the directories the `devkit.context_documents` providers return for `(root, working directory, directory)`, lists each, merges, de-duplicates and sorts by path; a failing provider becomes a `notices` entry. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/cli/context.py` (`context`) and `packages/devkit-dist/src/devkit_dist/adapters/cli.py` (`resolve_root`) | The CLI passes `resolve_root(workspace_root)`: the `-w` root, else `find_project_root(Path.cwd())`, the devkit root. The cwd never reaches the use case (challenger-01 #1) | Passes the working directory (`Path.cwd()`, or the `-w` root) beside the resolved root; the command is wired through `_json_command`, which prints only the result. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/models/results.py` (`ContextResult`) and `cli/output.py` (`_report`) | `ContextResult` has no `notices`; `_report` (sync) is the pattern that prints the result, then `echo_notices` and `exit_on_warnings` | `ContextResult` gains `notices`, carried in the JSON object; the CLI prints the stderr advisory blocks (`CONTEXT_DOCUMENTS_EXTENSION_FAILED`) and exits `1` only under `--strict`. |
| `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py` (`STEERING`, `_is_steering`, the steering citation pass) | Checks the IDs cited in the root steering files only (`CAP-GOV-spec-rules`, steering files paragraph) | Generalized over `docs_roots(registered)`, so an alias or stale ID in a namespace steering file is reported and fixed as in the root ones (challenger-01 #4). |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config_template.py` (`_load_templates`) | The entry-point loading pattern devkit-dist already uses: load, validate, one warning per failed entry | Reused as the pattern for the provider loader. |
| `packages/devkit-docs/src/devkit_docs/features/documents/services/namespaces.py` (`detect`, `living_path`, `docs_roots`) | The selection rule of `CAP-DOCS-namespaces` 3.3 and the root mapping | Unchanged; the provider composes them (the inverse of `living_path` for the detected namespace). |
| `packages/devkit-docs/src/devkit_docs/features/documents/repositories/config.py` (`read_docs_config`) | Reads `[[tool.docs.namespaces]]`; devkit passes `[tool.*]` through unread (`CAP-DIST-sync-and-transactions`) | Unchanged; the provider reads the registry through it. |
| `packages/devkit-docs/pyproject.toml` | Entry points `devkit.bundles`, `devkit.commands`, `devkit.config_template` | Gains the `devkit.context_documents` provider entry. |
| `packages/devkit-docs/src/devkit_docs/features/documents/usecases/browse.py` (`OVERLAY_GROUP`, `_overlays`) | The `devkit.docs.status_overlay` provider pattern with a `DOCS_OVERLAY_FAILED` warning per failed overlay | Reference for the failure semantics (warn, never fail). |

### Tests

| Location | Content |
| --- | --- |
| `packages/devkit-dist/tests/integration/features/distribution/test_context_documents.py` | Field grammar, read rules, the bounded default size. Gains: provider directories listed and merged, a failing provider warns, a provider returning an unsafe path is ignored, no provider installed lists the declared directory only. Runs without `devkit-docs` and `devkit-agt` (`just test-dist`), so the provider is a test double registered through `importlib.metadata`. |
| `packages/devkit-docs/tests/` | The provider: from a package source directory, from its docs root, from the repository root, from a directory outside every package, with `-w`, without registered namespaces, with a malformed `[tool.docs]`. |
| `packages/devkit-spec/tests/integration/bundles/spec/test_steering_guidance.py` (`test_the_constitution_names_the_list_and_its_trigger`) | Asserts exactly one constitution line names `docs/steering/`; the extended line must keep that count. |
| `packages/devkit-dist/tests/integration/features/distribution/test_context.py:58-64` | Asserts the result from a nested directory equals the root result; narrowed to the constitution and instructions once the working directory selects documents. |
| `packages/devkit-dist/tests/integration/features/distribution/test_context_documents.py:176-185` | Asserts the `documents` payload at the default caps stays within 4096 bytes for one directory; gains the `(1 + N) × 4096` bound for a fixture of `N` namespaces (challenger-01 #7). |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/` | Gains an alias ID cited in a namespace steering file. |

### Documents and bundle text

| Location | Text to generalize |
| --- | --- |
| `docs/capabilities/governance/CAP-GOV-spec-rules.md` 3.14 | "Only the root `docs/steering/` is checked" becomes the per-directory rule over the root and every registered namespace. |
| `docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md` 2 (`documents`) | Adds the provider directories, the failure semantics and the unchanged read rules. |
| `docs/capabilities/distribution/CAP-DIST-manifest-spec.md` (Context documents) | Names the providers beside the field. |
| `docs/capabilities/documents/CAP-DOCS-namespaces.md` 3.4 and 4.5 | `steering/` joins the directories a namespace mirrors; the library section names the provider. |
| `docs/architecture/ARCH-05-2-components.md` (entry-point groups) | The public group list gains `devkit.context_documents`. |
| `docs/decisions/2026-11/20261102-steering-documents.md` | "Superseded in part by" pointers (Development writes them). |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/AGENTS.md` line "`docs/steering/` holds project-wide background" | Names the namespace directory in the same line. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md` (steering paragraph) | Package background goes to the namespace steering directory; package glossaries stay where they are. |
| `docs/capabilities/governance/CAP-GOV-spec-rules.md` `RULE-document-reference` steering files paragraph (lines ~119-123) | The steering files whose IDs are checked include those of registered namespace directories. |
| `docs/capabilities/documents/CAP-DOCS-document-model.md` rule 9 | "There is no namespace copy" becomes the registered namespace directory. |
| `docs/capabilities/distribution/CAP-DIST-workspace-ownership.md` 7 | "a bundle's declared context document directory may list ..." also covers provider directories. |
| `docs/steering/glossary.md` row **Steering document** | "directly in `docs/steering/`" names the namespace directory too. |

## 2. Evidence: the motivating repository

`/Users/mj/workspace/playground/g-sandbox` keeps `docs/packages/<game>/steering/` for four of its five packages
(`platform` has none). It is **not a devkit project yet**: it has no `.devkit/config.toml`, so no namespace is
registered there today; the proposal's premise ("a registered namespace needs it") describes the state after it adopts
devkit. The acceptance fixture therefore has to be a monorepo fixture in this repository's tests, not g-sandbox itself.

| File | Listing entry (bytes, local path) | File size (bytes) | Summary length |
| --- | --- | --- | --- |
| `caravan-trade/steering/art-direction.md` | 239 | 3702 | 72 |
| `caravan-trade/steering/product.md` | 236 | 5112 | 66 |
| `scavenger-crew/steering/future-directions.md` | 276 | 879 | 101 |
| `scavenger-crew/steering/product.md` | 260 | 1801 | 92 |
| `wasteland-gunsmith/steering/product.md` | 288 | 2446 | 113 |
| `wasteland-gunsmith/steering/setting-and-art.md` | 295 | 1328 | 111 |
| `workshop-mercenary/steering/art-direction.md` | 249 | 2047 | 77 |
| `workshop-mercenary/steering/product.md` | 246 | 1923 | 71 |
| `workshop-mercenary/steering/world-setting.md` | 242 | 4879 | 77 |

Nine files, 2331 bytes of listing entries in all (about 260 bytes each; absolute paths add their prefix). Every file
has a Korean `title`, an English `summary` and no `id`; most carry extra `status` and `updated` keys, which the root
contract tolerates (it rejects `id` and checks `title` and `summary`; a Latin-script requirement applies to `summary`
only). So the root contract applies unchanged: every file would pass `RULE-steering-documents` as written, with
`max_files` 10 and `max_body_bytes` 24576 far above the measured sizes.

## 3. Q1: what the context lists, and the cost

Per-entry cost is about 260 bytes locally, about 400 bytes with an absolute path (`steering-design.md` D2). The root
directory lists at most `max_files` entries. Options for the namespace directories, `N` registered namespaces:

| Option | Inside a package (source path or docs root) | Outside every package (repository root, `-w`) | Worst case per context | Consistency |
| --- | --- | --- | --- | --- |
| a. The `CAP-DOCS-namespaces` 3.3 default selection (Planning's first recommendation) | global + that namespace | global + every namespace | `max_files × (1 + N)` entries at the root; `2 × max_files` inside a package | Same rule as `devkit docs list` without options; no new concept |
| b. Global only outside a package | global + that namespace | global only | `2 × max_files` | Tightest bound; an agent at the repository root (the usual Claude Code working directory) never sees package background unless it changes directory or reads `docs/packages/<name>/steering/` itself |
| **c. Global plus a hint, with `--for <dir>`** (the `user`'s decision, `envelopes/answer-01.yaml`) | global + that namespace; the other namespaces' directories as path and file count | global only; every namespace's directory as path and file count | `2 × max_files` entries plus `N` hint lines of about 60 bytes | The `documents` list stays as small as b; the hint (`documents_elsewhere`) tells the agent what exists, and `uv run devkit get-context docs --for packages/<name>` fetches a package's list from the root; one more call for package background |
| d. Every namespace always | global + every namespace | global + every namespace | `max_files × (1 + N)` | The cost `ADR-steering-documents` rejected, paid even inside a package |

For g-sandbox at the repository root, option a would list 9 namespace entries (about 2.3 KB locally) beside the root
ones; option c lists none and names 4 directories (about 240 bytes); inside `caravan-trade`, both list two. A monorepo with many packages lowers `max_files` or keeps fewer steering files per
package; the rule caps each directory, and the number of namespaces is the project's own choice. The cap stays a rule
setting (`CAP-GOV-spec-rules` 3.14) because `devkit-dist` caps nothing itself (`ADR-steering-documents` (the listing mechanism)).

**Selection input**: `devkit get-context` takes no `--namespace <name>` (a docs concept devkit-dist could not
validate). The selection follows the working directory, the same input `devkit docs list` uses; today the CLI hands
the use case only the resolved project root (`resolve_root`, challenger-01 #1), so the CLI passes a second input,
`--for <dir>` (an existing directory inside the project, `ARGUMENT_INVALID` otherwise), else the cwd, else the `-w`
root (which is "outside every package"), and `GetContext.execute` gains that parameter; its only production caller is
the CLI. `--for` lets an agent at the repository root request a package's context without changing directory. A namespace concept in the `devkit-dist` CLI would contradict the SDD-agnostic rule, and an agent working
across packages runs the command from the repository root (option a) or reads the other directory by path.

## 4. Q2: who tells `devkit-dist` which directories to list

`devkit-dist` reads no `[tool.docs]` table (`CAP-DIST-sync-and-transactions`: devkit passes `[tool.*]` through
unread) and imports no application package (`ARCH-05-2-components`). The registry it would need lives in
`devkit-docs` (`read_docs_config`, `detect`).

| Option | Mechanism | Pros | Cons | Verdict |
| --- | --- | --- | --- | --- |
| **B. Provider entry point** (selected) | Group `devkit.context_documents`; a provider `(root, start, directory) -> directories` returns extra workspace-relative directories for a declared one; `devkit-docs` returns the namespace mirror(s) of a `docs/`-rooted directory by the 3.3 selection | `devkit-dist` keeps no docs concept; the registry is read by its owner; cwd selection uses the existing `detect`; the pattern (`config_template`, `status_overlay`, `post_finish`) exists, including warn-never-fail loading | One more entry-point group; package code runs inside every context load (the ADR's objection); needs a test double in `devkit-dist` tests | Selected: the objection was "beyond the need" when no selection was needed; a namespace-aware selection cannot be computed without the registry |
| A1. Glob in the manifest | `context_documents = ["docs/steering", "docs/packages/*/steering"]`; `devkit-dist` expands the glob and lists a globbed directory only when `start` is under its parent | No new group; no registry | Unregistered `docs/packages/<name>/steering/` is listed although the rule skips it; selection by a package's **source** path (`services/api` → `api`) is impossible without the registry, so an agent in a package source directory gets nothing; a wildcard enters the seeded `target` grammar | Rejected |
| A2. `devkit-dist` reads `[tool.docs]` | A namespace-aware pattern resolved against the registry | Smallest code | Breaks the documented pass-through of `[tool.*]` and puts the docs registry into the SDD-agnostic package | Rejected |
| D. Sync renders the directories | A `post_sync` extension of `devkit-docs` writes the namespace directories into a managed data file that `get-context` reads | No run-time plugin call | Stale between syncs after a registry edit; the `user` chose run-time reading (`steering-design.md` D1, option D) | Rejected |

Provider contract (Development writes the exact signature and code name):

- Called for every bundle whose managed `bundle.toml` declares `context_documents`, with the project root, the
  working directory and the declared directory; returns two sequences of workspace-relative directories, those to
  list and those to mention, each validated with the seeded `target` grammar (`manifest.seed_target`); an invalid item
  is dropped with a warning.
- The directories to mention appear under a new result key `documents_elsewhere`: the absolute `path` and `files`
  (the count of Markdown files other than `README.md`, by the same read rules), existing directories only, sorted by
  path, `[]` when none (q1 option c).
- A provider that fails to load, raises (including `DOCS_CONFIG_INVALID`) or returns something else is reported as a
  warning (one per provider, naming the entry point): `ContextResult.notices`, carried in the JSON object, and a
  stderr advisory block `CONTEXT_DOCUMENTS_EXTENSION_FAILED`, as `devkit sync` reports its notices; the context lists
  the declared directory alone and exits `0` (`1` under `--strict`). `_json_command` prints only the result today,
  so the `get-context` command adopts the `_report` pattern (challenger-01 #3).
- The declared directory and the returned ones are listed with the same read rules, de-duplicated, and `documents`
  stays sorted by absolute path; entries keep `path`, `title` and `summary` only. `docs/packages/<name>/steering/X`
  sorts before `docs/steering/X`, which puts package background first.
- The `devkit-docs` provider: without registered namespaces, or for a directory not under `docs/`, it returns
  nothing; otherwise it returns `docs/packages/<name>/<rest>` to list for the namespace `detect` selects and the other
  registered namespaces' mirrors to mention; when `detect` selects none, nothing to list and every registered
  namespace's mirror to mention (q1 option c).

## 5. Q3: goals and the glossary

- `ADR-roadmap-and-milestones-ledger` keeps goals as prose in `ARCH-01-introduction-and-goals` and names "goals per
  namespace" as its reopen condition; `MS-monorepo-namespace-support` already states that goals stay prose "in
  `ARCH-01-introduction-and-goals` or a namespace steering file". A namespace steering file is ID-free, so a milestone
  body can cite it only by path (`RULE-document-reference` forbids relative links to ID-bearing documents only).
- Decision for this proposal: a namespace steering file MAY hold the package's goals as prose (g-sandbox's
  `product.md` files already do), and nothing in this proposal cites it mechanically. How a namespace milestone
  cites a goal, and the "Superseded in part" pointer on the roadmap ADR, belong to `SPEC-namespace-roadmap`, which owns
  that ADR; a namespace milestone may cite the global goals meanwhile, so neither proposal depends on the other.
- A namespace steering directory holds Markdown files only: `glossary.yaml` is read from the root file alone
  (`search.py`), so a namespace copy would be silently unused, and a `steering/glossary.md` would be a second place
  for the package glossary; both are reported by the rule (challenger-01 #5).
- The package glossary stays at `docs/packages/<name>/glossary.md` (`living-spec-writing`; a declared non-goal):
  moving it would change `living_path`'s mapping of `glossary.md` and every consumer's path, for no listing gain
  (the root glossary is listed only because it lives in `docs/steering/`). The asymmetry (root glossary in
  `steering/`, package glossary at the docs root) is recorded as a follow-up, not changed here.
- `ux-writing` names one root `docs/steering/ux-objects.md`; a namespace copy of that register is a follow-up for the
  UX rules work of the milestone, not this proposal.
