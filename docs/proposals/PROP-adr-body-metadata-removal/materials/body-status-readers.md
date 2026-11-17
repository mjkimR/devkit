# Readers of the ADR body metadata block

Evidence for Q1 and Q2, taken at worktree HEAD `f329111c7` (base `main` `2d247d824`).

## Searches

All searches use `rg` over the worktree with `.git`, `docs/decisions/`, `docs/proposals/` and `specs/` excluded, so
only code, rules, guidance and Living Spec prose remain:

- `Status\*\*`, `\*\*Status`, `\*\*Date\*\*`, `Deciders`, `Involved Components`: the body block.
- `superseded (in part )?by` (case-insensitive) in non-Markdown files: supersession readers.
- `Status:` and `status` in the viewer frontend sources and the built bundle under `devkit_viewer/static/`.

## Writers and pinned tests

| Location | Role |
| --- | --- |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md:15-18` | template block |
| `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py:489-490` | PADR scaffold writes `- **Status**: Draft`, `- **Date**` and a `---` |
| `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py:176,859-871` | `_DRAFT_BODY_STATUS`, `_accept_status` body pass |
| `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py:115-117,436-475` | pin the body rewrite: plain, fenced example, HTML comment, trailing comment |
| `packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py:222` | pins the scaffold line |
| `docs/capabilities/delivery/CAP-DLV-proposal-planning.md:290-291` (§4.4) | states the scaffold body |
| `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md:73` (handoff step 4) | states the body rewrite |
| `docs/designs/delivery/DESIGN-proposal-handoff/design.md:156` | observed run: "`- **Status**: Accepted`" |

## Readers (Q2): none parse the block

| Candidate | Finding |
| --- | --- |
| Viewer frontend | `features/document/supersession.ts` reads `meta.status` and the "Supersedes in part" / "Superseded in part by" lines; `KnowledgeViews.svelte`, `BundleHeader.svelte`, `api/roadmap.ts` read `meta.status`. No `**Status**` match in the sources or the built bundle. |
| `devkit docs` index, list, search | `features/documents/models/parse.py` takes `status` from the frontmatter; `cli/search.py` prints `status=` from the indexed document. No body pattern. |
| Supersession tooling and rules | `governance/usecases/decision_supersession.py` and `documents/models/supersession.py` read `status`, `supersedes`, `superseded_by` and the partial pointer lines. The `handoff.py` pointer writer inserts below the first H1 (`_insert_pointer`, ~:775). |
| Release handbook script | `scripts/handbook.py:249` takes `status` from the frontmatter. |
| Other rules, playbooks, guidance | No match outside the template. `adr-consolidation` reads the partial pointers, not the block. |
| Body references (indirect) | `devkit-docs` `features/documents/models/parse.py` (`body_references`, ~:88, :208-231) and the viewer `api/documents.ts:163-173` and `features/document/references.ts:48,102-135` index every backticked ID in the body, Involved Components lines included. `devkit docs refs CAP-DLV-project-policy` lists `ADR-document-system` and `ADR-worktrees-and-scope` only through those lines. About 20 ADRs mention some IDs only there (challenger-01; a local count found 18 files, 45 mentions). |

## Corpus (Q1)

- 94 ADR files under `docs/decisions/` (the draft's "95" counted `README.md`); 71 carry `- **Status**`.
- Block shapes: Status+Date+Deciders+Involved 27 (`ADR-dual-source-of-truth-and-periodic-reconciliation` adds a
  `- **Follow-up**` item; `ADR-roadmap-and-milestones-ledger` also has an unrelated `- **Status**:` milestone-lifecycle
  item at line 235); Status+Date 25 (`ADR-ux-screens` carries three "Superseded in part by" list items inside the
  same list); Status+Date+Involved 18; Status only 1. About 30 ADRs wrap Involved Components onto indented lines.
- `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` records its provenance only in its Deciders line.
- `ADR-orchestration-workers` has a prose paragraph between the block and its `---`.
- Every Status agrees with frontmatter `status` (and names `superseded_by` when superseded); every Date equals
  `created_at`.
- Partial-supersession pointers mostly sit as paragraphs above the block, directly below the H1 (for example
  `ADR-roadmap-and-milestones-ledger` lines 23-25); `ADR-ux-screens` is the exception with list items inside the
  block. Removing only the field items leaves every pointer where it is.
- 64 ADRs use `---` separators beyond the frontmatter; the template change does not require editing them.
- No PADR under `docs/proposals/` carries the block at this HEAD; the sibling plan branch
  `plan-formal-doc-padding-trim` has no PADR yet.
