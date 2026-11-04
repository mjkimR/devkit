---
id: PROP-namespace-steering
title: Namespace steering documents checked and listed beside the global ones
summary: "Recognizes docs/packages/<name>/steering/ as steering documents of a registered namespace, checked by the steering rule and listed in the context of the namespace an agent works in, within the bounded-context caps."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
namespace: global
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-monorepo-namespace-support
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-docs/src/devkit_docs/features/documents/services/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/
    - packages/devkit-docs/pyproject.toml
    - packages/devkit-docs/tests/
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/
    - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/
    - packages/devkit-dist/src/devkit_dist/features/distribution/models/
    - packages/devkit-dist/src/devkit_dist/features/distribution/cli/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/tests/integration/bundles/spec/test_steering_guidance.py
    - docs/capabilities/governance/
    - docs/capabilities/distribution/
    - docs/capabilities/documents/
    - docs/architecture/ARCH-05-2-components.md
    - docs/decisions/2026-11/20261102-steering-documents.md
    - docs/steering/glossary.md
  excludes:
    - .devkit/managed/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-namespace-steering] Namespace steering documents checked and listed beside the global ones

## 1. Background & Hypothesis

`ADR-steering-documents` chose one flat `docs/steering/` directory and rejected a per-namespace copy because "no
registered namespace needs it today", recording the reopen condition: a registered namespace needs package background
its package glossary cannot hold. `RULE-steering-documents` checks only the root directory ("there is no namespace
copy", `steering_documents.py`), and the `docs` bundle lists one directory in every context through its
`context_documents = "docs/steering"` manifest field (`CAP-DIST-context-and-playbooks`,
`devkit_dist.features.distribution.services.bundles.context_documents`).

The condition is met. g-sandbox keeps `docs/packages/<game>/steering/` for four games, two or three files each:
`product.md` plus world setting and art direction. Nothing rejects these files, but nothing reads them either: they
pass no shape check and never reach an agent's context, so the writing guidance that depends on steering (read the
body before a wording, naming or content decision its summary covers) does not apply to them.

Hypothesis: a namespace steering directory can follow the root contract unchanged (flat, ID-free, `title` and
`summary`, the size caps) and be listed with the same progressive loading, if the list is narrowed to the namespace the
agent works in. `living_path` already maps `docs/packages/<name>/steering/X` to `docs/steering/X`, and
`CAP-DOCS-namespaces` 3.3 already defines the namespace of the current directory, so the selection rule exists; what is
missing is applying it to the steering rule and to context assembly.

## 2. Technical Spike Questions

Settled in Planning; the inventory, measurements and option tables are in `materials/namespace-steering-design.md`,
the decision in `PADR-namespace-steering-directories`, the criticism in `envelopes/challenger-01.yaml`.

- **Q1**: How does the steering list stay bounded? The caps stay per directory (`max_files`, default 10, and the
  summary length), and the context lists only the directories the working directory selects by the
  `CAP-DOCS-namespaces` 3.3 default rule: inside a package, the global directory and that namespace's (at most
  `2 × max_files` entries); outside every package (the repository root, `-w`), the global directory only, with the
  registered namespaces' steering directories named as a hint (directory path and file count, one line each, no titles)
  under a separate result key (q1, decided by the `user`: option c). `devkit get-context` gains a generic `--for <dir>`
  option naming the working directory the context is for, so an agent at the repository root requests a package's
  context (`uv run devkit get-context docs --for packages/<name>`) without changing directory; it takes a directory,
  never a namespace name. Today the CLI hands `GetContext` only the resolved project root (`resolve_root`), so the
  selection needs a second input: the CLI passes the working directory (`--for`, else the cwd, else the `-w` root)
  beside the root, and the provider selects by it.
- **Q2**: What declares the namespace directories to `devkit-dist`? A `devkit.context_documents` provider entry
  point: `devkit-dist` asks the installed providers for the extra directories of a declared `context_documents`
  directory, given the project root, the working directory and the declared directory, and lists each with the read
  rules it already has; `devkit-docs` registers the provider that reads `[[tool.docs.namespaces]]` and applies
  `detect` and returns two lists, the directories to list and the directories to mention. `devkit-dist` reads no
  `[tool.docs]` and imports no application package, so `ARCH-05-2-components` holds;
  the provider loader follows the `devkit.config_template` pattern (one warning per failed entry, never a failure),
  and the warning reaches the agent as a `notices` entry of the JSON object and a stderr advisory block with the code
  `CONTEXT_DOCUMENTS_EXTENSION_FAILED` (exit `1` only under `--strict`). A manifest glob was rejected because it cannot
  select by a package's source path and would list unregistered directories; a registry read in `devkit-dist` because
  `[tool.*]` passes through unread; a sync-rendered list because the `user` chose run-time reading.
- **Q3**: A namespace steering file MAY hold the package's goals as prose (g-sandbox's `product.md` files already do);
  how a namespace milestone cites them is `PROP-namespace-roadmap`'s decision, which owns the roadmap ADR, and a
  namespace milestone may cite the global goals meanwhile, so neither proposal depends on the other. Package
  glossaries stay at `docs/packages/<name>/glossary.md`: a namespace steering directory holds Markdown files only, and
  a `glossary.md` or `glossary.yaml` in it is reported (the package glossary has its place; synonyms are read from the
  root `docs/steering/glossary.yaml` only). The asymmetry with the root glossary is a recorded follow-up.

## 3. Proposed Design & Impact

- **Rule**: `RULE-steering-documents` checks `docs/packages/<name>/steering/` of each registered namespace as it checks
  `docs/steering/`, one directory at a time, each only when the run targets a file in it: flat, Markdown only (plus
  `glossary.yaml` in the root directory only), UTF-8, closed frontmatter within 4096 bytes, no `id`, `title` and
  Latin-script `summary`, `max_body_bytes`, `max_files` per directory with the over-cap files reported only for a
  targeted directory, `README.md` neither checked nor counted; a `glossary.md` or `glossary.yaml` in a namespace
  directory is reported with the package glossary's path as the remediation; messages name the directory checked. A
  file under an unregistered `docs/packages/<name>/steering/` is not checked, as its other documents are not. The rule
  iterates `docs_roots(registered)` (`devkit_docs.features.documents.services.namespaces`). `RULE-document-reference`
  checks the IDs cited in a namespace steering file as it checks the root ones (`_is_steering` generalized over the
  same roots).
- **Listing**: `GetContext.execute` takes the working directory beside the project root; the CLI passes `--for <dir>`
  (an existing directory inside the project), else the cwd, else the `-w` root. `devkit get-context <bundle>` lists,
  under `documents`, the files of the declared directory and of the directories the `devkit.context_documents`
  providers return to list for (root, working directory, declared directory), each with `path`, `title` and
  `summary`, merged, de-duplicated and sorted by path (a namespace file sorts before the root ones); the directories
  the providers return to mention appear under `documents_elsewhere` as `path` (absolute) and `files` (the count of
  Markdown files other than `README.md`), sorted by path, `[]` when none. The `devkit-docs` provider lives in
  `devkit_docs.features.documents.services` and is registered in `packages/devkit-docs/pyproject.toml`; for a
  `docs/`-rooted declared directory it returns the namespace mirror of the namespace `detect` selects to list and the
  other registered namespaces' mirrors to mention; when `detect` selects none, nothing to list and every registered
  namespace's mirror to mention; nothing without registered namespaces. A mentioned directory that does not exist is
  dropped.
  A provider that fails to load, raises (`DOCS_CONFIG_INVALID` included) or returns an unsafe path is reported as a
  warning: `ContextResult` gains `notices`, the JSON object carries them and the CLI prints the stderr advisory blocks
  (`CONTEXT_DOCUMENTS_EXTENSION_FAILED`) as `sync` does; the context lists the declared directory alone and exits `0`
  (`1` under `--strict`).
- **Guidance**: the `docs` bundle's constitution line that names `docs/steering/` also names the namespace
  directory with the same trigger and tells the agent to request a package's context with `--for <dir>` when
  `documents_elsewhere` names it; `living-spec-writing` sends package background there and keeps package glossaries
  where they are; the rule guide names both directories; the glossary row **Steering document** and
  `CAP-DOCS-document-model` rule 9 drop "no namespace copy"; `CAP-DIST-workspace-ownership` 7 covers provider
  directories as it covers the declared one. The `spec` bundle guidance test keeps asserting one constitution line
  naming `docs/steering/`.
- **Decision record**: the "no namespace copy" clause and the rejected namespace-copy option of
  `ADR-steering-documents`, and its rejection of an entry-point provider, are superseded in part by
  `PADR-namespace-steering-directories`; Development writes the pointer. `ARCH-05-2-components` adds the new group to
  the public entry-point names. No new feature edge in `.devkit/architecture.toml`: the provider uses the documents
  feature's existing dependency on `devkit_dist.features.project`, and `devkit-dist` loads it generically.
- **Tests**: rule fixtures with a registered namespace directory (clean, nested file, over cap, missing summary,
  non-Latin title with an English summary, a `glossary.md`, an over-cap root with an untargeted namespace directory)
  and an unregistered one; `RULE-document-reference` fixtures with an alias ID cited in a namespace steering file;
  `devkit-dist` tests with a provider test double (a nested working directory and `--for <dir>` reach the provider,
  `--for` outside the project or a non-directory is `ARGUMENT_INVALID`, listed directories merged and sorted,
  mentioned directories under `documents_elsewhere` with their counts, a failing provider yields the notice and exit
  `0`, an unsafe path is dropped, no provider lists the declared directory only with `documents_elsewhere` empty, the
  `documents` payload of a fixture with `N` namespaces at the default caps stays within `2 × 4096` bytes and
  `documents_elsewhere` within `N` entries), passing without `devkit-docs` and `devkit-agt`; `devkit-docs` provider
  tests from a package source directory, its docs root, the repository root, a directory outside every package, with
  `--for` and with `-w`, without registered namespaces and with a malformed registry. `test_context.py` narrows its "nested equals root" assertion to
  the constitution and instructions.

Expected affected contracts: `CAP-GOV-spec-rules` (3.14, the steering pass of `RULE-document-reference`),
`CAP-DIST-context-and-playbooks` (context documents, `notices`), `CAP-DIST-manifest-spec` (Context documents),
`CAP-DIST-workspace-ownership` (7), `CAP-DOCS-namespaces` (3.4, 4.5), `CAP-DOCS-document-model` (rule 9),
`ARCH-05-2-components` (entry-point groups), `ADR-steering-documents` (superseded in part).

## Planning decisions

- Root steering contract reused for the namespace directories with two deltas: Markdown only (no `glossary.yaml`) and
  `glossary.md` reported; caps and targeting per directory (Host, within scope).
- Selection by the working directory the CLI passes beside the root: `--for <dir>`, else the cwd, else the `-w` root
  (Host for the input; the option's name and shape are the Host's recommendation the `user` accepted).
- q1 (`user`, `envelopes/answer-01.yaml`): outside every package the context lists the global directory only and
  names the registered namespaces' steering directories as a hint (`documents_elsewhere`: path and file count); a
  package's context is requested with `--for <dir>`. Chosen over listing every namespace at the root (cost
  `max_files × (1 + N)` entries) and over a bare global list with no hint.
- Mechanism: the `devkit.context_documents` provider entry point; failures surface as `notices` and
  `CONTEXT_DOCUMENTS_EXTENSION_FAILED` (`PADR-namespace-steering-directories`).
- Goals as prose in a namespace steering file; citation and the roadmap ADR pointer left to `PROP-namespace-roadmap`;
  package glossaries unchanged (Host, within scope and non-goals).
- The acceptance fixture is a monorepo fixture in this repository: g-sandbox has no `.devkit/config.toml` yet, so no
  namespace is registered there today (assumption recorded for `plan-accept`).
- Challenger round 1 (`envelopes/challenger-01.yaml`) folded: the CLI selection input, the notices channel, the
  `RULE-document-reference` pass, the glossary and document-model wording, the glossary files, per-directory
  targeting and the payload bound; its `Decision needed` finding is q1.
- `dev_effort` stays `medium`: two packages and one new entry-point contract, each covered by existing patterns.

## 4. Lifecycle & Retirement Criteria

Planning settled Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the rule, provider
and context tests above, the synchronized guidance and a monorepo fixture whose `devkit get-context docs` from a
package directory (and from the root with `--for` that directory) lists that package's steering files beside the
global ones and no other package's, names the other packages' directories under `documents_elsewhere`, and from the
root without `--for` lists the global ones only, with the payload bounds asserted.

Non-goals: loading steering bodies by default; a steering directory for an unregistered package; moving package
glossaries; changing the root directory's contract or caps; a `--namespace` option on `devkit get-context` (the
option takes a directory); titles or summaries in the hint; a namespace copy of `docs/steering/ux-objects.md`;
namespace search synonyms.
