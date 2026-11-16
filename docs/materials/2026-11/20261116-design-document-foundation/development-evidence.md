# Foundation Development evidence

## Source and method

Development starts at handoff `db9d230adfe2c8bd221996e9c5f910e67d3c3151`; accepted Planning landed at
`6aaddb58a48aa81c6a0c23417801e9b4542f758a`. The premise comparison found no changed agreement: existing identity,
namespace and transaction contracts retain their owners. Handoff skeletons were promoted to AC-01–AC-06/F1–F6.
`sync --check` before the first edit passed exit 0 (no preexisting drift). No base checkout or disabled-change
runtime experiment was used. The recorded Planning R1/V1 contract-only trials supply the before outcome: no direct
route to the implementation detail. This turn measures the after route qualitatively; it makes no speed or
whole-corpus claim. Historical direction, target-docs and pilot evidence remain unchanged.

Boundaries are emulated: absolute assigned-worktree cwd/read scopes, exact write scope, quiesced author writes
and SHA-256 content snapshots of tracked plus nonignored untracked files substitute for native isolation.
Independent readers reported no outside-worktree reads or mutations. Generated managed copies remain ignored;
`.devkit/installation.json` is the only tracked sync output and is annotated in task 3.

## F1: Ownership case audit

All twelve target-docs routing cases are represented in `CAP-DOCS-documentation-ownership` §3.1: capability,
domain/glossary, architecture, design/source, use case, UX, ADR, materials, reference, development guide,
operations composition and executable action owner. Its §3.2 addresses strategy/ADR, building blocks/algorithm,
runtime/actor goal, technical/domain/observable contracts, deployment/operations and existing quality/risk cases.

Every pilot ledger passage retains its previous authority:

| Pilot passages | Retained owner and foundation treatment |
| --- | --- |
| Domain opening and relationships 1–4, next steps, terminology/evidence boundary | Existing availability/manifest/projection/selection/receipt capabilities and glossary; historical domain entry unchanged, no new validity rule |
| Design question, mechanism, authority/context and next step | Capability §3 safety; ARCH component/system context; source behavior. Adapted entry is current explanation with optional context and useful next detail |
| Detail preflight, shape examples and forward application | Capability eligibility/safety stays §3; source `require_writable`, `_ordered`, `apply_changes`, directory helpers explain method |
| Reverse application and maintenance seam | Capability Recovery retains decisions/stop conditions; source `recover_locked` explains ordering; conditional updates do not transfer architecture ownership |
| Operations four classifications, action boundary, normal-state and evidence boundary | Capability/advisory/reference retain actions/readiness; no-journal drift remains not-ready; historical operations entry unchanged |

No normative transfer, copied recovery procedure, rigid authoring DAG, numeric/length routing, all-pairs links,
reciprocal registry, whole-layer prerequisite or fixed hop cap appears. No glossary term was introduced; the new
shared capability defines responsibilities. Generic source guidance implements that shared contract without citing
repository IDs or adding a second matrix.

## F2/F3: Actual global route

Fresh independent reader received only the transaction capability path and original question: “How can one managed
path become a directory or the reverse without losing rollback information?” No fork history, entry names, diff,
spec/materials or inventory was supplied. Opened in order:

1. Response-style instruction (role setup).
2. Transaction capability: first whole-file attempt truncated, then heading/question-word search and §3.
3. §3 ordinary link → `docs/designs/distribution-transactions.md`: question, authority/context, next detail,
   maintenance touchpoints.
4. Entry link → `distribution-transactions/file-directory-replacement.md`: preflight, forward/reverse application,
   maintenance seam.
5. Detail source link → transaction.py: symbol lookup and lines 96–237, 280–420.

Observed result: deletion-first application plus before/after content and directory evidence explains both
replacement directions and reverse restoration. `_ordered`, `require_writable`, `apply_changes`, `recover_locked`,
`_swapped_directory`, `_prune_created` matched the description. Entry works alone for overview/next action; detail
works directly. The source destination exists. Actual operational decisions route to capability Recovery.
Architecture/runtime were not opened because they were unnecessary for this question. No document returns or
indexed lookup were needed. Avoidable read: initial whole capability; its §3 could be selected first. After the
trial the implementer removed an unnecessary evaluative sentence about absent datasheets, preserving all route
links/mechanism text. Author tracked/nonignored snapshots before/after reader both:
`7609f68fbbcf382676279065608534a71ea94388116a636ad86049bcb6e60337`.

Compared with recorded R1/V1, the added owner link now provides the observed route. This establishes the selected
question-specific path, not universal discovery, index support or timing improvement. No recovery was executed.

## F4: Isolated package validation

Ignored fixture root: `.venv/spec-probes/foundation-development/namespace`, with registered fixture-alpha at
`packages/alpha` and unrelated fixture-beta at `packages/beta`. Initial commands rejected the nested root with
ARGUMENT_INVALID exit 2 because it belonged to the outer Git tree. Host initialized separate disposable `.git`
roots for namespace and consumer; no actual repository config or branch changed. Successful reruns below use
existing `.venv/bin/devkit`, `--workspace-root <fixture>` and package source cwd `packages/alpha`, with JSON format:

| Command after `docs` | Actual outcome |
| --- | --- |
| `list capability` | exit 0, alpha owner and global owner only |
| `search replacement` | exit 0, alpha replacement owner |
| `resolve CAP-FIX-replacement` | exit 0, package owner path |
| `refs CAP-FIX-replacement` | exit 0, indexed global owner reference only |
| `list capability --namespace global` | exit 0, global owner only |
| `list capability --all-namespaces` | exit 0, global, alpha and unrelated beta owners |
| `search shape-change` | exit 0, linked capability hit; no design document node |
| `resolve shape-change` / `refs shape-change` | exit 2, expected DOCS_ID_UNRESOLVED |

Independent second reader received only fixture root, package source cwd, owner ID CAP-FIX-replacement and original
replacement question; no entry names/results. It ran `docs resolve`, opened owner §3, ordinary mechanism link,
linked ordering detail and linked `packages/alpha/mechanism.txt`. No avoidable reads or returns occurred; every
next step was clear, explanation and fixture sequence agreed. It did not run recovery or inspect unrelated package
content. Tracked/nonignored snapshots before/after both:
`2a3792091125cb96e15c820ae1955205ae5d79c73739a65dad84116d7f36df2f`.
The fixture's example names/content validate format/discovery, not actual package demand or production runtime.
The beta owner is unchanged; all-namespace output still includes it and package selection excludes it.

## F5: Consumer distribution

Separate ignored consumer fixture selects docs core and invokes `devkit sync --workspace-root <consumer>
--no-agents`, then `sync --workspace-root <consumer> --check`: both exit 0. Existing auto-selected bundles also
arrive; MCP_RUNTIME_UNAVAILABLE warns about optional registration, with no docs delivery failure. Delivered
living-spec/architecture instructions and design-template match source bytes exactly. Inspection finds no real
repository document ID, template frontmatter/identity/status schema or generated `docs/designs/` scaffold.
The existing `templates` asset supplies the file; manifest unchanged. Managed/projected copies were generated only.
Initial affected test run caught the exact five-template assertion (2590 pass, one failure). Host authorized its
adjacent test mirror to add the new template while preserving all existing inventory/assertions and add consumer
byte/ID-free checks. This is an implemented required F5 update, not weakened coverage.

## F6: Verification scope

Ordinary links from capability → entry → detail → source and detail → entry resolve at their actual depth.
The two maintained files have no identity metadata. Source-symbol agreement is read-based, not runtime recovery.
Namespace fixture negative controls prove no design identity/refs node; search can find an indexed owner's link text.
Native check results and final reviewed source SHAs are retained in the unit's envelopes. No new runtime, UI,
identity grammar, namespace configuration, dependency, domain/operations home or unrelated ARCH correction is made.

Executed native checks before implementation commit:

- Scoped document/source-asset rules: 22 rules, zero errors/warnings.
- Source hygiene rules: included in scoped checks; no agent-asset wording warning.
- Post-sync `sync --check`: exit 0, zero drift.
- `pytest packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py -q`: 2 passed.
- `just lint-check devkit-docs`: ruff check passed, 155 files already formatted.
- `just check devkit-docs`: pyright zero errors/warnings/information.
- `just test-affected --base 6aaddb58a48aa81c6a0c23417801e9b4542f758a`: final PASS 2591;
  mode partial, 37 changed paths selecting 157 paths, reason devkit_docs/docs/specs/tests, default unit-integration.
  Full fallback remained enabled and was not selected. Initial run before test inventory correction failed as above.
- Selective built-wheel E2E `pytest packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py -q`:
  1 passed, real isolated wheel consumer with docs lookup/search/refs/rules/sync and no spec lifecycle package.
- No frontend files changed, so no frontend check applies. Product runtime code remains unchanged; lint/type checks
  cover the authorized Python test mirror. Native verification ran in the assigned worktree, not a Host exec checkout.
