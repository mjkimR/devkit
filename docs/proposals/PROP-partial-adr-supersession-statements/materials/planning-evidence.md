# Partial-supersession statements: Planning evidence

## 1. Identity and Boundary

- Inspected: this repository at `b3e4753d` (`plan-partial-adr-supersession-statements`), `docs/decisions/`,
  `RULE-decision-supersession`, the handoff pointer writer, the `devkit docs` commands and the viewer package.
- Inspected on: 2026-11-10.
- Method: two read-only scripts walked `docs/decisions/` with the rule's own masking
  (`devkit_docs.features.documents.models.markdown.visible_lines`) and pointer pattern. To reproduce the counts: for
  each ADR, take each `supersedes` entry that resolves to an ADR whose status is not `superseded` (a pair), then read
  the earlier ADR's visible "Superseded in part by" lines that name the later ADR.
- `envelopes/scout-01.yaml` holds the command and viewer evidence of section 6.
- Correction to `materials/supersession-pointer-attempt.md`: 18 ADRs carry a "Superseded in part by" line at this
  head, not 17.

## 2. Why the earlier spec excluded a structured field (Q1)

`SPEC-partial-adr-supersession` Non-Goal 1 excluded "a structured partial-supersession field
(`superseded_in_part_by`, `status: amended`) or a parsed decision `supersedes` reference graph" with the rationale
"the agreed scope keeps the status and a body line; `supersedes` and `superseded_by` on a decision stay unparsed
metadata". Its plan section 1 adds that nothing changes in the index, search or rules.

- The exclusion bounded that spec's scope. Neither the spec, its plan nor its reconcile record names a defect of a
  structured form.
- Two parts of its premise no longer hold. `SPEC-decision-supersession-check` added `RULE-decision-supersession`,
  which reads a decision's `supersedes`, `superseded_by` and the body pointer.
  `SPEC-proposal-scaffold-and-handoff-pointers` made handoff write the pointer.
- Two parts still hold and constrain this proposal: an ADR partly replaced stays `accepted` (no new status), and the
  document index adds no reference-graph edge for a decision's `supersedes`
  (`packages/devkit-docs/src/devkit_docs/features/documents/models/parse.py:69-70`,
  `CAP-DOCS-document-model` "Decision supersession").

## 3. Statement form options (Q1)

| Criterion | A: frontmatter map (`ADR-<old>: "<clauses>"`) | B: fixed sentence per earlier ADR in Decision Outcome | C: fixed subsection with one list item per earlier ADR |
| --- | --- | --- | --- |
| Reads with existing code | Frontmatter is already parsed; a new key and its shape checks are needed | The rule and handoff already read a fixed body sentence through `visible_lines` (`decision_supersession.py:17,33-34`, `handoff.py:187-189,742-744`) | Same reader as B plus heading detection |
| Text the 26 pairs need | 60 to 400 characters with backticks, double quotes, colons and parentheses inside a YAML string; the decision template already warns that a summary must be quoted for one `": "` | Markdown as written today | Markdown as written today |
| IDs inside the text | Frontmatter strings are outside body reference parsing (`parse.py:183-206` reads the body), so `RULE-document-reference` and alias rewrites do not reach them | Body references: checked and rewritten like any other | Same as B |
| Where a reader finds the replaced scope | Metadata; `decision-writing` requires it in Decision Outcome, so the prose stays and the file holds two copies, or the rendered ADR loses it | In Decision Outcome, where 26 of 26 pairs state it today (25 name the earlier ADR by ID, one says "the old ADR") | In Decision Outcome, under a heading no existing ADR has |
| Symmetry with the pointer | Field on one side, body sentence on the other | Mirror sentences: "Supersedes in part" and "Superseded in part by" | Section on one side, sentence on the other |
| Migration | New field in 16 ADRs; prose kept or removed | Restate one item or paragraph per pair in 16 ADRs | New subsection in 16 ADRs; items moved |
| Cost against `SPEC-partial-adr-supersession` | Adds the structured field that spec excluded | Keeps "the status and a body line" | Keeps the body line; adds template structure |

Recommended: B. It keeps one human-readable place, reuses the reader both tools already have, keeps IDs under the
reference rules and needs no YAML quoting of long prose. A becomes preferable when a tool must read the replaced scope
without reading the body, for example an index-only consumer; none exists (section 6).

## 4. Inventory of existing pairs (Q3, Q4)

Counts at `b3e4753d`: 65 ADRs; 26 pairs from 16 partly superseding ADRs to 18 earlier ADRs; no ADR has
`status: superseded`.

- Every pair has one pointer before the earlier ADR's first second-level heading. 23 are paragraphs of their own;
  the three in `ADR-ux-screens` are list items.
- Five pairs have further pointers at the affected statements (ten lines), with local text such as "the next item".
- Six pointers repeat the later ADR's `summary` (whitespace normalized, final sentence mark ignored).
- One pointer uses "for" instead of a colon after the ID (`ADR-selective-package-versions` in
  `ADR-package-ownership-and-release-version`).
- The later ADRs state the replaced scope in several wordings: "This replaces `ADR-<old>` …", "Replaces in
  `ADR-<old>`: …", "From `ADR-<old>`, … is retired", "This decision supersedes only …", "This replaces, in part, the
  clause of `ADR-<old>` …". No two ADRs written independently share a wording a pattern could extract.
- One open PADR names `supersedes` (`PADR-adaptive-dev-distribution` in `PROP-adaptive-package-extraction`,
  accepted); its Decision Outcome states the replaced parts in prose.

"Summary copy" marks the six pointers. "Extra pointers" counts the pointers at affected statements. "Outcome items"
counts the Decision Outcome list items or paragraphs of the later ADR that name the earlier ADR by ID.

| Later ADR | Earlier ADR | Summary copy | Extra pointers | Outcome items |
| --- | --- | --- | --- | --- |
| `ADR-decision-ledger` | `ADR-document-id-aliases` | no | 1 | 1 |
| `ADR-explicit-ux-coverage-exception-notation` | `ADR-ux-screens` | no | 0 | 1 |
| `ADR-impeccable-session-authority` | `ADR-uiux-improvement-workflow-boundary` | no | 0 | 1 |
| `ADR-local-and-pull-request-integration` | `ADR-configuration-language-and-rendering` | no | 3 | 1 |
| `ADR-namespace-milestone-roots` | `ADR-roadmap-and-milestones-ledger` | no | 0 | 1 |
| `ADR-namespace-steering-directories` | `ADR-steering-documents` | yes | 0 | 1 |
| `ADR-namespace-steering-registers` | `ADR-namespace-steering-directories` | no | 0 | 1 |
| `ADR-namespace-steering-registers` | `ADR-ux-screens` | no | 0 | 1 |
| `ADR-opt-in-maintenance-history` | `ADR-history-branch-publication` | no | 0 | 1 |
| `ADR-post-merge-verification` | `ADR-adaptive-development-and-research` | no | 0 | 1 |
| `ADR-post-merge-verification` | `ADR-delivery-approval-and-lifecycle-authority` | yes | 0 | 1 |
| `ADR-post-merge-verification` | `ADR-local-and-pull-request-integration` | yes | 0 | 1 |
| `ADR-post-merge-verification` | `ADR-proposal-acceptance` | yes | 0 | 1 |
| `ADR-post-merge-verification` | `ADR-test-selection-and-ci` | yes | 0 | 1 |
| `ADR-recorded-adjacent-path-extensions-for-development-workers` | `ADR-orchestration-workers` | yes | 0 | 1 |
| `ADR-retire-native-approval-and-moved-ownership-clauses` | `ADR-document-system` | no | 2 | 1 |
| `ADR-retire-native-approval-and-moved-ownership-clauses` | `ADR-mcp-runtime-and-shared-artifacts` | no | 0 | 1 |
| `ADR-retire-native-approval-and-moved-ownership-clauses` | `ADR-proposal-acceptance` | no | 2 | 3 |
| `ADR-retire-native-approval-and-moved-ownership-clauses` | `ADR-steering-documents` | no | 2 | 1 |
| `ADR-role-authoring-reference` | `ADR-shared-role-authoring` | no | 0 | 1 |
| `ADR-selective-package-versions` | `ADR-document-system` | no | 0 | 1 |
| `ADR-selective-package-versions` | `ADR-mcp-runtime-and-shared-artifacts` | no | 0 | 1 |
| `ADR-selective-package-versions` | `ADR-package-ownership-and-release-version` | no | 0 | 0 |
| `ADR-skill-local-research-roles` | `ADR-adaptive-development-and-research` | no | 0 | 1 |
| `ADR-skill-local-swarm-roles` | `ADR-adaptive-development-and-research` | no | 0 | 1 |
| `ADR-ux-coverage-step-targeting` | `ADR-ux-screens` | no | 0 | 1 |

## 5. Pointer derivation and rule evidence (Q2, Q3)

- Handoff takes the pointer text from the promoted ADR's `summary`, else its `title`, else its slug
  (`handoff.py:747-757`), writes one paragraph below the earlier ADR's first heading (`handoff.py:760-804`) and
  writes nothing when a visible pointer already names the promoted ADR.
- `RULE-decision-supersession` is an error rule without a fixer. It requires a pointer naming the later ADR for each
  `supersedes` entry whose target is not `superseded`, and a reciprocal `supersedes` for each pointer
  (`decision_supersession.py:98-114`). It skips every document whose ID does not start with `ADR-`, so a PADR is not
  checked. It checks only targeted files, so a staged run that holds one ADR of a pair evaluates only that side.
- The evaluator gives every finding its rule's severity (`materials/supersession-pointer-attempt.md` section 3), and
  the per-finding severity model is a non-goal. A check added to this rule is therefore an error on `main` and at
  every commit gate, and the existing ledger has to satisfy it in the change that adds it.
- `SPEC-decision-supersession-check` Non-Goal 1 excluded automatic rewriting and PADR validation from the rule.
- Options for keeping the two texts consistent after handoff:

| Option | What keeps them equal | Cost |
| --- | --- | --- |
| Equal texts checked by the rule | The rule compares the statement with the earlier ADR's pointers, whitespace normalized; a repair edits both in one commit | Two copies; a one-line manual copy per repair |
| Equal texts restored by `devkit rules fix` | A fixer rewrites the pointer from the statement | A fixer in a rule that is report-only by its spec; it has to choose among several pointers of one pair |
| Pointer without text | Nothing to keep equal | The earlier ADR no longer says what was replaced, against the proposal's second hypothesis |

## 6. Command and viewer evidence (Q5)

From `envelopes/scout-01.yaml`:

- `devkit docs` has four subcommands (`resolve`, `refs`, `list`, `search`). `refs` lists a pointer as one body
  reference among the others: `devkit docs refs ADR-test-selection-and-ci --direction in` returns 19 documents, all
  `fields=body`. The text line carries no sentence, and JSON carries line and column only.
- `refs` is defined on the reference graph, and a decision's `supersedes` is deliberately outside it. An option on
  `refs` would have to add ADR `supersedes` edges or classify body lines inside a reference command; a sibling
  subcommand reads frontmatter and body text as the rule does. Either touches about four source files,
  `test_cli_documents.py` and `CAP-DOCS-document-lookup`. No MCP tool or generated listing mirrors `refs`.
- The viewer backend does not use devkit-docs (`packages/devkit-viewer/pyproject.toml:7-10`). The document page
  parses frontmatter in the browser and shows `id`, `status`, `priority`, `milestone`, `target_area` and the title;
  it shows no `supersedes` and has no incoming-reference list.
- Showing which later ADRs replace parts of a decision in the viewer needs a cross-document index in the frontend or
  a new endpoint; an endpoint that reuses devkit-docs adds a package dependency that does not exist. The built page
  is committed (100 tracked files under `packages/devkit-viewer/src/devkit_viewer/static/`), so a frontend change
  adds `just viewer lint`, `check`, `test` and `build` and changes `CAP-VIEW-repository-viewer` section 4.
- No UX document exists, and the repository text does not settle whether `ADR-ux-screens` requires drafted screens
  for a viewer change.

## 7. Where the post-handoff clarification is stated (Q6)

- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py:14-17` and `:748-749`: "Development
  replaces the summary with the replaced clauses."
- `CAP-DLV-proposal-planning` section 4.5 step 4: "`<clause>` is the PADR's `summary`, else its `title`, as one
  sentence, and Development replaces it with the replaced clauses at `living-spec-draft`."
- The `spec-next` post-handoff reference: its opening paragraph ("partial-supersession pointer clarifications … as a
  later Host commit") and step 4.
- The decision template, the `decision-writing` instruction, the seeded and the repository `docs/decisions/README.md`,
  the PADR scaffold's commented `supersedes` line and the rule guide describe the pointer; none describes a fixed
  statement.
