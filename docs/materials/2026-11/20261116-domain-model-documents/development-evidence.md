# Domain Development evidence

Source under test: `970fa15cb336703ff60e9d4e8796be0b37d867dc`.
Accepted Planning materials remain historical. Baseline is their recorded supplied-entry pilot: explanation was
useful, but independent discovery without entry names was not demonstrated. The head demonstrates the bounded
routes below. No independent base route measurement was recorded; the Host retains that limitation. No timing,
read-count improvement or universal discovery claim follows.

## D1: statement-to-owner and glossary audit

| Maintained entry statements | Normative owner checked |
| --- | --- |
| Proposal/spec anchors, handoff carries prerequisites and relocates live incoming targets; membership not carried; origin is not fulfillment | `CAP-DLV-proposal-lifecycle` §4.1 |
| Milestone membership versus Unit prerequisite versus provenance, separate MS/Unit graphs and provenance excluded from refs | `CAP-DOCS-document-model` §3.3 |
| Direct spec has no proposal or milestone membership | `CAP-DLV-spec-bundles` §3 rule 7 |
| Package installation/dependencies make bundles available | `CAP-DIST-content-packages` §§1–3 |
| Preset/auto-selection/configuration determine requested selection; receipt selection is audit evidence | `CAP-DIST-sync-and-transactions` §§1–2 |
| Conceptual asset identity, preset membership and seeded-document semantics | `CAP-DIST-manifest-spec` §§2–3 |
| Managed/native paths represent assets according to kind and agents | `CAP-DIST-agent-projections` |
| Receipt assets, file hashes/modes and separate seeded evidence | `CAP-DIST-sync-and-transactions` §1 |

Both entries independently state question, relationship overview, authority boundary and next useful owner.
Delivery includes a nonexecuted membership-change walkthrough; changing a grouping alone neither completes nor
removes a prerequisite and creates no origin. Every substantive summary cites its existing owner. Normative
transfer count is zero. Glossary definitions, owners, synonyms and code identifiers remain unchanged; only two
ordinary links beside the relevant groups were added. Entries require no class/schema catalog or authoring order.

## D2: fresh global readers

Each reader began in the assigned worktree, receiving only the owner ID and conceptual question before discovering
entry names. They received no materials, inventory or other reader output. Read-only scopes were explicit;
confinement was emulated, with no native read-only guarantee. Author HEAD and all tracked plus
nonignored-untracked bytes were frozen throughout all three reader calls. Before/after SHA-256 matched
`477423d6f4b24c8c4b31c7703c0813eea3f35b8c2088e9d0f8683f76422f932f`; HEAD stayed at the source above.
Readers reported no outside-worktree document reads or writes. Hash snapshots read file bytes for comparison.

Delivery reader actual commands (cwd worktree):

```text
.venv/bin/devkit --help
.venv/bin/devkit docs --help
cat .agents/skills/response-style/SKILL.md
git -C <worktree> status --short
git -C <worktree> rev-parse HEAD
.venv/bin/devkit docs resolve CAP-DLV-proposal-lifecycle
cat docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
cat docs/domain/delivery-relationships.md
.venv/bin/devkit docs resolve CAP-DOCS-document-model
```

It additionally used Python to hash tracked paths before/after and extract only document-model §3.3, from heading
`### 3.3` to the next `###`. Opened lifecycle §4.1 → linked entry all sections → document-model §3.3.
PASS: membership groups proposed work; prerequisite is a separate Unit graph; provenance records origin outside
current refs. Validity is document-model §3.3; handoff transformations are lifecycle §4.1. Direct-spec owner was
unnecessary for this question. Avoidable reads: two help calls and whole lifecycle owner output (truncated).
No loop, unclear next step or wrong-owner answer.

Distribution reader actual commands (cwd worktree):

```text
.venv/bin/devkit docs --help
.venv/bin/devkit docs resolve CAP-DIST-sync-and-transactions
cat docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
cat docs/domain/bundle-selection-and-installation.md
cat .agents/skills/response-style/SKILL.md
```

Opened receipt §1 and selection §2 → selected entry Question, overview/table/example, authority/next steps.
PASS: installed packages supply availability; configuration/defaults select assets and agents; `(bundle, kind, id)`
identifies the conceptual asset; paths are representations; receipt records applied evidence. Recorded selection
is never another input. The entry names availability, manifest, projection and transaction owners correctly.
No extra owner read was needed because the requested selection/receipt authority was already open.
Avoidable reads: help and whole transaction owner output (truncated). No loop, unclear next step or wrong owner.

## D3: real registered namespace fixture

Fixture: `.venv/spec-probes/domain-development/namespace/`, a Host-initialized independent Git root.
Only ignored fixture configuration/content was authored. It registers alpha → `packages/alpha`, beta →
`packages/beta` through actual `[[tool.docs.namespaces]]`, with global, alpha and unrelated beta owners and domain
entries. No production package document/configuration was created.

Fresh reader received alpha source cwd, CAP-FIX-alpha-relationships and the grouping/prerequisite question only.
Actual commands, cwd `<fixture>/packages/alpha`:

```text
<worktree>/.venv/bin/devkit docs resolve CAP-FIX-alpha-relationships
cat docs/packages/alpha/capabilities/fixture/CAP-FIX-alpha-relationships.md
cat <fixture>/docs/packages/alpha/capabilities/fixture/CAP-FIX-alpha-relationships.md
cat <fixture>/docs/packages/alpha/domain/grouping.md
```

The relative `cat` failed once because resolve returns repository-relative paths; anchoring to the known fixture
root succeeded. Owner Summary/Validity contract → selected `../../domain/grouping.md` → Question/Overview/Authority.
PASS: grouping says which milestone; prerequisite says work needed first; changing grouping alone does not remove
or complete a prerequisite. Fixture owner §2 retains validity authority. No navigation loop, unclear conceptual
next step, wrong owner or outside-fixture/worktree read. Resolver path anchoring was the only friction.

Actual controls from alpha source cwd, using `<worktree>/.venv/bin/devkit`:

```text
docs list capability
docs list capability --namespace global
docs list capability --all-namespaces
docs search navigationprobe
docs search navigationprobe --namespace global
docs search navigationprobe --all-namespaces
```

All exit 0. Default list/search returned global+alpha, global-only returned global, all-namespaces returned
alpha+beta+global. Ordinary selected links resolve at actual package depth. Fixture entry filenames and controls
were withheld from the fresh reader until completion.

## D4: identity and ordinary navigation controls

Ran actual CLI via Python subprocess, cwd worktree: `docs list --limit 0 --history --format json` contained 1,407
indexed documents and no `docs/domain/` path. `docs search delivery-relationships --format json` and
`docs search bundle-selection-and-installation --format json` returned no domain node. For each bare slug,
`docs resolve <slug>` and `docs refs <slug>` exited 2 with the existing exact-ID remediation.
For both lifecycle and transaction owner IDs, `docs resolve <ID>`, `docs refs <ID>` and `docs search <ID>` exited 0.
Python checked every ordinary Markdown destination in the two entries, two ingress capabilities and glossary;
all exist. The entries have no frontmatter ID and borrow no ARCH/MAT identity. Search finds indexed owners,
not independent domain nodes. No runtime change was used.

## D5: actual consumer delivery

Ran `.venv/bin/devkit sync -w <worktree>/.venv/spec-probes/domain-development/consumer` against the Host-initialized
independent Git root, then compared the existing source instruction asset with the managed consumer bytes.
PASS: byte equality, SHA-256 `f35ba865a4daed31a7b52445cfc5f437f44b34b692b84a2a1da0bfc3bf6d7f24`;
consumer wording contains the domain convention, no repository-specific ID, and no `docs/domain/` scaffold.
Default available bundles were auto-selected; sync emitted MCP-runtime-unavailable and unselected-bundle notices.
Those optional integrations were not exercised. This is asset delivery evidence, not isolated document-only
runtime evidence; the separate existing built-wheel consumer E2E supplies that check.

## D6: source checks

Initial `uv run devkit sync --check`: PASS exit 0, no drift.
After source instruction edit, `uv run devkit sync` updated managed instruction, receipt and ignored local render.
Only tracked output is `.devkit/installation.json`, admitted in task 2 as `(sync output)`.
Post-source `sync --check`: PASS. Scoped document/source-asset rules: zero errors/warnings.
`just lint-check devkit-docs`: PASS, Ruff and formatting (155 files). First sandbox attempt could not create Ruff
cache; an operation-specific escalation reran the same command successfully. `just check devkit-docs`: PASS,
Pyright zero errors/warnings. Remaining check results are recorded in the review and worker envelopes.

At source `970fa15cb336703ff60e9d4e8796be0b37d867dc`, `just test-affected --base
19baca429e39d691c9ceee1b1b7b7b67ee738634` selected partial mode (157 paths, unit/integration, full fallback retained):
2,591 passed in 31.35s. `uv run --no-active --no-sync pytest
packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py -q`: 1 passed in 17.52s, disjoint selected
built-wheel consumer E2E. `uv run devkit rules check --ci --base main`: zero errors/warnings at retained
main `19baca429e39d691c9ceee1b1b7b7b67ee738634`. `git diff --check` passed.
No executable/test source was changed; no new test tier or frontend check applies.
