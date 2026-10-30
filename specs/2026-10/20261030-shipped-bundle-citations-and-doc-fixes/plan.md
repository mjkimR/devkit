---
id: PLAN-shipped-bundle-citations-and-doc-fixes
spec: SPEC-shipped-bundle-citations-and-doc-fixes
---

# Technical Plan: `SPEC-shipped-bundle-citations-and-doc-fixes` Forbid repository document IDs in shipped bundle text and fix two contract gaps

## 1. Constitution & Invariant Review

None. The change adds one repository test, rewords bundle guidance and aligns two Living Spec documents with
behavior that `CAP-DLV-proposal-planning`, `CAP-DIST-context-and-playbooks` and the code already define. No `MUST`
of `docs/architecture/` changes.

- `ARCH-05-2-components` (test layout): package tests cover package ownership; a check over every package's bundles
  is repository-wide, so it joins the repository's existing workspace scans in `tools/devkit-dev/tests/integration/`
  (`test_architecture.py` scans `packages/*/src`). It imports only public modules of the scanned packages and
  `devkit_docs` document models; no product runtime depends on it.
- `ARCH-08-1-agent-output`: untouched; no command output changes.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `tools/devkit-dev/tests/integration/test_bundle_citations.py` (new) | The citation test (AC-01 to AC-03) |
| `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md` | Self-Containment states the convention for every document kind; completion `rg` widened (AC-04) |
| `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/guide.md` | Drops the `CAP-GOV-rule-authoring` citation (AC-06) |
| `docs/capabilities/distribution/CAP-DIST-content-packages.md` | One rule in section 1 with the test path (AC-05) |
| `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md` | The `CONFIG_LOCAL_RENDER_STALE` remedy (AC-07) |
| `docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md` | Extensions 6a and 7g, scenarios 24 and 25 (AC-08) |
| `AGENTS.md` managed block, `.devkit/installation.json` | `devkit sync` outputs of the two bundle source edits (the advisory bundle and the authoring bundle are selected here) |

No new dependency: the workspace environment already holds every imported package.

## 3. Component & Interface Design

The test, in outline:

```python
SHIPPING = (devkit_agt.bundles, devkit_catalog, devkit_dist.bundles, devkit_docs.bundles, devkit_spec.bundles,
            devkit_starter)  # static imports: a change to their sources selects the test in `just test-affected`

def shipped_bundles() -> list[Path]  # bundle.toml parents under each module's directory
def seeded_ids(bundles) -> set[str]  # frontmatter `id` of documents under `seeded = true` document sources
def repository_ids(root) -> set[str]  # DocumentIndex over docs/ and specs/: IDs and aliases
def citations(bundle, forbidden) -> list[str]  # "<path>:<line>: <ID>" per backticked forbidden ID
```

- A citation is an ID matching the document ID grammar (`devkit_docs` `ID_SOURCE`, every indexed kind) inside a
  backticked span on one line, not preceded by a word character, `<` or `-`. Placeholders (`ADR-<slug>`) never match
  the grammar; examples (ADR-example, a numbered use case example) match it but resolve to nothing.
- Forbidden IDs are the repository's IDs and aliases minus the IDs a shipped bundle seeds.
- `DocumentIndex.load` receives an explicit file list (`docs/**/*.md`, `specs/**/*.md`), so the test reads the parse
  memo but never writes it into the checkout.
- Discovery completeness: the set of collected manifests equals `ROOT.glob("packages/*/src/**/bundle.toml")`; a new
  shipping package fails the test until its module joins `SHIPPING`.

Decided choices, each the recommended option:

- **Backticked spans only** (not every ID-shaped token): the spec skill's convention makes a backtick the citation
  marker, and rule test fixtures use real-looking IDs as plain strings.
- **Seeded by any shipped bundle**: `ARCH-01-introduction-and-goals` in the spec bundle's roadmap reference names a
  document the auto-selected `docs` bundle seeds; `devkit-spec` requires `devkit-docs`. Rewording it would lose the
  exact target with no consumer benefit.
- **Import-based selection** instead of a `scripts/affected_tests.py` data entry: the script is outside the agreed
  scope, and static imports of the shipping modules already map their source changes to this test. A `docs/` change
  that newly resolves a cited example does not select it; nightly CI covers that.

UC changes: extension **6a** (moved base refused before the acceptance commit: `SPEC_PROPOSAL_APPROVAL_NOT_READY`
for a failing CI rule on the prospective result or a base change to the proposal directory, `WORKTREE_MERGE_CONFLICT`
for a conflict; recovery merges the base into `plan-<slug>`, runs `devkit rules fix` on the proposal, commits and
reruns; resumes at step 6) and **7g** (conflict-free moved base lands without a merge into `plan-<slug>`: moved base
first parent, acceptance commit second, result fields `target_sha`, `landed_sha`, `disclosure`; resumes at step 8),
each with a scenario. Wording follows `CAP-DLV-proposal-planning` and the e2e tests in
`packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`.

## 4. Error Handling & Edge Cases

- A non-UTF-8 bundle file (none today) is skipped; bundles hold text assets.
- `__pycache__` directories under bundle sources are skipped.
- An ID followed by `.md` in a backticked path (`docs/architecture/ARCH-03-context.md`) is still a citation of that
  document and is reported unless seeded.

## 5. Verification & Test Plan

- `uv run pytest tools/devkit-dev/tests/integration/test_bundle_citations.py` (AC-01 to AC-03; AC-02 through a
  synthetic bundle under `tmp_path`); before the guide rewording it fails on `CAP-GOV-rule-authoring`.
- AC-03 selection: `scripts/affected_tests.py` `select()` on a changed bundle file of each shipping package lists the
  test (checked once, recorded in the review).
- `uv run devkit rules check --phase hygiene packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`
  (AC-04).
- `uv run devkit rules check` on the whole workspace (AC-05, AC-07, AC-08 document structure and references).
- `just lint-check`, `just check devkit-dev` and `just test-affected` (keeping its `mode=full` fallback).
