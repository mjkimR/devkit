---
id: PADR-namespace-steering-directories
title: Namespace steering directories listed by the working directory's namespace
summary: For a registered namespace that needs package background, we check docs/packages/<name>/steering/ under the root steering contract and list it in a context through a devkit-docs provider selected by the working directory, to keep background visible at bounded cost, accepting one more entry point.
proposal: PROP-namespace-steering
supersedes: [ADR-steering-documents]
status: draft
created_at: 2026-11-04
---

# [PADR-namespace-steering-directories] Namespace steering directories listed by the working directory's namespace

- **Status**: Draft
- **Date**: 2026-11-04
- **Involved Components/Capabilities**: `docs/steering/`, `docs/packages/<name>/steering/`, `CAP-GOV-spec-rules`,
  `CAP-DIST-context-and-playbooks`, `CAP-DIST-manifest-spec`, `CAP-DOCS-namespaces`, `ARCH-05-2-components`

---

## 1. Context & Problem Statement

`ADR-steering-documents` keeps project background in one flat `docs/steering/` directory, lists each file's `title`
and `summary` in every agent context through the `docs` bundle's `context_documents` declaration, and rejected a
per-namespace copy because no registered namespace needed one, recording the reopen condition: a registered namespace
needs package background its package glossary cannot hold. It also rejected an entry-point context provider as "beyond
the need" of listing one fixed directory.

The condition is met by a monorepo of independent products (g-sandbox: four games sharing one platform, each with
`docs/packages/<game>/steering/` holding product concept, world setting and art direction; nine files today). Nothing
checks these files and nothing lists them, so the writing guidance that depends on steering does not reach an agent
working on a game. Listing every package's background in every context is the cost the ADR refused; listing only the
background of the package an agent works in needs the namespace registry (`[[tool.docs.namespaces]]`), which
`devkit-docs` owns and `devkit-dist` may neither read (`[tool.*]` passes through unread,
`CAP-DIST-sync-and-transactions`) nor import (`ARCH-05-2-components`).

---

## 2. Decision Drivers

- Package background reaches the agent working in that package, with the same trigger as the root list.
- The always-loaded cost stays bounded and does not grow with packages the agent does not work in.
- The root steering contract (shape, frontmatter, caps) stays one contract; no new document kind or ID.
- `devkit-dist` keeps no SDD or docs concept and reads no `[tool.*]` table; the registry is read by its owner.
- The list is current at run time, without a sync (`user`, `ADR-steering-documents`).
- A project document or an extension failure never fails a context load.

---

## 3. Considered Options

### Directory

- **`docs/packages/<name>/steering/` of each registered namespace, under the root contract** (selected): the
  namespace layer already maps it (`living_path`, `docs_roots`); the rule checks it per directory with the same caps.
  Cons: one more directory per namespace to check; an unregistered package's directory stays unchecked.
- **A section of the package glossary** (rejected): keeps one file per package, but the glossary is a term table, not
  background prose, and nothing lists package glossaries in a context.
- **Root steering files per package** (`docs/steering/<name>-product.md`; rejected): listed today, but every context
  pays for every package and the root `max_files` cap is reached by the second package.

### Selection

- **The `CAP-DOCS-namespaces` 3.3 default selection** (selected, subject to the Planning question q1): inside a
  package (its source path or docs root) the context lists the global directory and that namespace's; outside every
  package (repository root, `-w`) the global directory and every namespace's. Same rule as `devkit docs list`.
- **Global only outside a package** (rejected unless q1 chooses it): tightest bound, but an agent at the repository
  root never sees package background without changing directory.
- **Every namespace always** (rejected): the cost the ADR refused, paid inside a package too.

### Mechanism

- **A `devkit.context_documents` provider entry point** (selected): `devkit-dist` asks the installed providers for the
  extra directories of a declared one, given the project root and the start directory, and lists each with the read
  rules it already has; `devkit-docs` registers the provider that applies the namespace selection. Cons: package code
  runs inside each context load; one more public entry-point group.
- **A glob in the manifest** (`docs/packages/*/steering`; rejected): lists unregistered directories the rule skips,
  and cannot select by a package's source path without the registry.
- **`devkit-dist` reads `[tool.docs]`** (rejected): breaks the `[tool.*]` pass-through and puts the docs registry
  into the SDD-agnostic package.
- **Sync renders the directories into a managed file** (rejected): stale after a registry edit until the next sync;
  the `user` chose run-time reading.

---

## 4. Decision Outcome

Steering documents of a registered namespace live in `docs/packages/<name>/steering/` under the root contract, and an
agent context lists them by the namespace the working directory selects, through a provider the document system
registers.

- A registered namespace MAY keep steering documents in `docs/packages/<name>/steering/`; `RULE-steering-documents`
  checks that directory as it checks `docs/steering/`: flat, `*.md` and `glossary.yaml` only, UTF-8, frontmatter
  closed within 4096 bytes, no `id`, a `title`, an English `summary` within `max_summary_length`, a body within
  `max_body_bytes`, `max_files` Markdown files per directory, `README.md` neither checked nor counted. → `CAP-GOV-spec-rules` 3.14 (MUST), `CAP-DOCS-namespaces` 3.4 (MUST)
- A `steering/` directory of an unregistered `docs/packages/<name>/` is neither checked nor listed, as its other
  documents are plain `docs/` files. → `CAP-GOV-spec-rules` 3.14 (MUST)
- The caps are per directory and stay rule settings; `devkit-dist` caps nothing itself. → `CAP-GOV-spec-rules` 3.14 (MUST)
- `devkit get-context <bundle>` lists, for a bundle declaring `context_documents`, the declared directory and the
  directories the installed `devkit.context_documents` providers return for the project root, the start directory
  and the declared directory, each with the existing read rules, de-duplicated and sorted by path; entries keep
  `path`, `title` and `summary`. → `CAP-DIST-context-and-playbooks` 2 (MUST), `CAP-DIST-manifest-spec` Context documents (MAY)
- A provider that fails to load, raises or returns anything but safe workspace-relative directories is reported as a
  warning notice naming the entry point and never fails the context load; `devkit-dist` reads no `[tool.docs]` and
  imports no application package for it. → `CAP-DIST-context-and-playbooks` 2 (MUST), `ARCH-05-2-components` entry-point groups
- The `devkit-docs` provider returns the namespace mirror of a `docs/`-rooted declared directory: that of the
  namespace the start directory selects (`CAP-DOCS-namespaces` 3.3, rule 3), or of every registered namespace when it
  selects none; nothing without registered namespaces or for another directory. → `CAP-DOCS-namespaces` 3.3 and 4.5 (MUST)
- The `docs` bundle's constitution line names both directories with the same read-before-deciding trigger. → `CAP-DIST-context-and-playbooks` 2
- A namespace steering file MAY hold the package's goals as prose; how a namespace milestone cites them is
  `PROP-namespace-roadmap`'s decision. Package glossaries stay at `docs/packages/<name>/glossary.md`.
- Replaces in `ADR-steering-documents`: the Directory clause "no subdirectories and no namespace copy" and its
  rejected option "A per-namespace copy as well" (a registered namespace may now keep one); the Listing mechanism's
  rejection of an entry-point provider as beyond the need (a provider now supplies the namespace directories beside
  the manifest-declared one, which stays). Every other clause stands.
- The provider is selected over the glob and the registry read because only the registry owner can select by a
  package's source path, and the pattern already exists for `devkit.config_template` and `devkit.docs.status_overlay`.

---

## 5. Consequences

- **Positive**:
  - Package background reaches the agent working in that package at about 260 bytes per file; the root list is unchanged.
  - One contract and one rule for every steering directory; a project tunes `max_files` once.
  - A generic way for any bundle's context documents to gain namespace-selected directories.
- **Negative / Risks**:
  - At the repository root a monorepo pays `max_files × (1 + N)` entries at most; a project with many packages keeps
    fewer steering files per package or lowers `max_files`.
  - Provider code runs in every context load; a `DOCS_CONFIG_INVALID` registry degrades the list to the root directory
    with a warning instead of failing, so a broken registry is noticed through `devkit rules check`, not here.
  - Steering files of an unregistered package are silently plain files until the package is registered.
- **Follow-ups**:
  - A namespace copy of `docs/steering/ux-objects.md` for the UX rules work of `MS-monorepo-namespace-support`.
  - The asymmetry between the root glossary (`docs/steering/glossary.md`) and package glossaries
    (`docs/packages/<name>/glossary.md`).

---

## 6. Confirmation

`RULE-steering-documents` fixtures with a registered namespace directory (clean, nested file, over cap, missing
summary, non-Latin title with an English summary) and an unregistered one; `devkit-dist` tests for the provider
contract with a test double (directories merged and sorted, a failing provider warns, an unsafe path is dropped, no
provider lists the declared directory only), passing without `devkit-docs` and `devkit-agt` (`just test-dist`);
`devkit-docs` tests for the provider from a package source directory, its docs root, the repository root, a directory
outside every package and a workspace without namespaces; the `spec` bundle guidance test keeps one constitution line
naming `docs/steering/`; a monorepo fixture whose `devkit get-context docs` from a package directory lists that
package's steering files beside the global ones and no other package's.
