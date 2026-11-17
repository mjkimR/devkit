# Formal document audit for PROP-formal-doc-padding-trim

Supporting evidence of `SPEC-formal-doc-padding-trim`. Two read-only audits run before Planning, one of the docs
bundle assets and one of the 13 design, domain and operations documents (1,063 lines at the Planning base). Planning
rechecked the items marked "rechecked" against the worktree head; the challenger round checks the rest. Line numbers
are at the Planning base and move with edits. B = `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`.

## Authoring assets

| # | Finding | Status | Action |
| --- | --- | --- | --- |
| A1 | B/instructions/{design,domain,operations}-writing.md steps 3-4, 11/12-12/13 restate checks of `RULE-spec-format`, `RULE-id-convention` and `RULE-code-entrypoints`; steps 1-2, 8/9-10/11, 14-15 repeat across the three and in `living-spec-writing.md` 47-58 and CAP §3.3 | rechecked | Q4 shape |
| A2 | Authority boundary comments: design.md 32-35, domain.md 34-37, operations.md 32-35 ask for a stock disclaimer | rechecked | Q2 |
| A3 | CAP §3.1 rule 5 table (36-51) and rule 7 table (55-69) overlap; `living-spec-writing.md` 25-27 prose copy; equality test `test_formal_doc_checkpoints_guidance.py` 28-33 | rechecked | Q3 |
| A4 | CAP §4 125-127 restates the template layout; §3.2 closing 86-90 repeats `architecture-writing.md` "Responsibility boundary" | rechecked | cut |
| A5 | `templates/capability.md` §4 scaffold 29-33 unused; Summary comment 16 repeats frontmatter `summary` | rechecked (scaffold use count from the Host audit) | drop lines, keep headings |
| A6 | `document-writing.md` 53-54 install note duplicates `YamlBindingUnavailableError.fix` | rechecked | drop bullet |
| A7 | "selected development approach defines" with no action: capability.md 24, usecase-writing.md 70, ux-writing.md 105, milestone.md 15-16 and 31, living-spec-writing.md 13; no test pins them | rechecked | drop; keep decision-writing.md 19, living-spec-writing.md 14 |
| A8 | Lead "at most one question" and datasheet field list in template, instruction and CAP; "delete comments" only in the formal instructions | rechecked | state once (Q4) |
| A9 | domain.md 32 calls the example optional, domain-writing.md 22 requires it; file-path comments capability.md 13, usecase.md 15, ux.md 16; `---` separators in usecase.md and ux.md | rechecked | Q5; drop |
| A10 | "Maintenance and next action" mixes update triggers with next-read pointers | rechecked | Q1 |

## Existing documents

| Document | Edits |
| --- | --- |
| DESIGN-distribution-transactions | Fold the rollback-evidence problem sentence and the `ARCH-05-4-distribution-components` §3 pointer into `DESIGN-distribution-file-directory-replacement`; delete the bundle; alias the old ID on the successor (Q6) |
| `DESIGN-distribution-file-directory-replacement` | Lead: drop "This non-normative detail…" and the orientation sentence; private helpers in words (Q7); example disclaimer line 26 goes; boundary keeps the CAP §3 owner; Update triggers name `apply_changes`, `require_writable`, `recover_locked` |
| `DESIGN-proposal-handoff` | Lines 74-80 restate `CAP-DLV-proposal-lifecycle` §4.2 body classification: keep one sentence and the citation; take over the Q8 mechanism clauses from §4.1 step 5 and §4.3; lines 80-82 (spec rendering, own-path filter) are design-owned and stay in words, as the worked example at 162 relies on them; private helpers in words; line 93 says "sets the accepted status"; boundary keeps the owner list without "settles no rule"; Update triggers keep public names and the `git show` check; the `spec-next` post-handoff pointer moves into the rewriting phase |
| `DESIGN-workflow-stage-evaluation` | Lines 90-93 are a design-owned worked variation: only "because the order is unknown" restates `CAP-DLV-human-interaction` §5; lines 132-134 explain the loop and stay, 135-136 restate §5 Approve gate: cite instead; private helpers in words; boundary without "settles no rule"; Update triggers keep the rerun command; drop "Next read" |
| `DOMAIN-delivery-relationships` | Boundary 46-47 generic text and the owner-per-question lines 52-54 go (table and body name every owner); add `related_capabilities`; "nonexecuted example" and "changes no files" sentences go; the repeated `CAP-DOCS-document-model` §3.3 citations reduced to the table column and one prose citation |
| `DOMAIN-bundle-selection-and-installation` | Lead-ending "This entry relates…" goes; overview prose 17-24 and 39-42 keeps its distinctions (availability is not deployment, auto-selection and opt-out, receipt `selection` is never an input) and loses only the owner citations the table repeats; boundary 46-47 and the owner lines 52-55 go; add `related_capabilities` and `related_designs` (line 55 was its only route to the design) |
| `DOMAIN-feedback-lifecycle` | Table (34-38) vs the actor list (47-66): keep the list for who and when, cut status descriptions the table holds; boundary keeps owners the table does not name; Update triggers 122-123 stay; next-read sentences go |
| `DOMAIN-override-lifecycle` | Prose 40-43 stays or moves into rows (reconciliation is not a state; an `ORPHAN_LEFT` file is not under `files`); boundary keeps owners outside the table (projections, reference, glossary); "copies no [FIX]" disclaimer goes |
| `OPS-distribution-sync` | Lines 45-48 (`RECOVERY_BLOCKED` → `HALT`, no-row fallback) merge into the Routing rows 23-25 they repeat; boundary 35-38 orientation disclaimer goes, line 40 stays as a limit |
| `OPS-assignment-attention-routing`, `OPS-host-hook-dispatch-routing`, `OPS-mcp-runtime-refusals`, `OPS-search-mode-and-model-routing` | Boundary drops "routes evidence and owns no recovery" and owners the routing table's owner column names; the "evidence cannot establish" paragraph stays; the no-row fallback moves under `## Routing` (for `OPS-search-mode-and-model-routing` with its `devkit playbook search` pointer); the advisory `[FIX]` non-repetition disclaimers go |

Kept after checking: use case sections (parsed by rules), operations `## Normal-state observation`, the problem-first
lead, the domain relationship table, the reference template, ADR drivers and confirmation.
