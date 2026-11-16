# Independent reader trials

## Identity and method

Reader: nested agent pilot_reader, independent of the draft author. Source HEAD:
`a448f4ef5726039e7ddf61b72cef3bdc722dce19`. The four drafts were untracked working files at that HEAD;
the subsequent build commit retains the same text. The reader modified no files, opened no ledger/evidence/unit
documents and executed no recovery. Each supplied-entry trial had only its question and named entry as starting
information. The design discovery trial ran first, before any entry filename was supplied.

Native boundaries were not enforced. Explicit worktree cwd, read-only commands and reported opened-path ledgers
substituted for enforcement. No external repository was read.

## R1: contract-only design discovery

Starting input: `CAP-DIST-sync-and-transactions` §3 and the question “How can one managed path become a directory
or the reverse without losing rollback information, and where is its detailed implementation explanation?”

Opened only that contract. First extraction sought an absent next-section delimiter and overread into later
Shared development approach and Source snapshot boundary material. A second extraction used the next H2 boundary;
§3 includes many unrelated subsections, so output truncated. The reader used numbered items 3, 5 and 6 to answer
the guarantee: journal prior evidence, delete to free paths, restore previous content, reject unsafe contents,
and stop on subsequent edits.

Result: direct contract-to-design discovery GAP. No relevant design entry is offered at the numbered transaction
steps; the unavailable hop is transaction guarantees → detailed path-shape mechanism explanation.
No corpus search or draft-filename knowledge filled that hop. The contract overview answers the guarantee,
but supplies no next step to this pilot's detailed explanation. Two extraction reads were unnecessary round trips;
there was no whole-layer prerequisite. Truncation limits any claim that the reader inspected all of broad §3.
This direct-reference result does not establish failure of lexical search or reverse references.

## R2: supplied design entry to detail to source

Starting input: same file/directory question plus [design entry](design-entry.md).

| Opened document/section | Necessity |
| --- | --- |
| design-entry.md, all | Supplied mechanism overview and next step |
| replacement-detail.md, all | Ordinary link explains preflight, journal and rollback |
| transaction.py, symbol-location read | Locate named implementation symbols |
| transaction.py lines 96–205 and 291–407 | Inspect directory planning, ordering, eligibility and recovery/application code |

Answer: preflight recognizes owned paths freed by the change set; before/after file content and created/replaced
directories are recorded; deletion precedes writes; reverse application removes created content before restoring
prior content and prunes empty recorded directories. Detail sections: Preflight and the change set, Forward
application, Reverse application. Source: `require_writable`, `missing_directories`, `_ordered`, `apply_changes`,
`recover_locked`, `_swapped_directory`, `_prune_created`. Safety stays with `CAP-DIST-sync-and-transactions` §3.

Result: useful supplied-entry path. The entry explains overview and next step; no architecture/runtime prerequisite
or return to entry was needed. The symbol-location read was useful, with no unnecessary document return.
The reader did not separately inspect the `atomic_write`/`replace_file` delegation statement. This success proves
no contract-only discovery path.

## R3: domain concept to contract

Starting input: “How does an available bundle become selected assets and projected paths, and what does a receipt
record?” plus [domain entry](domain-entry.md).

| Opened document/section | Necessity |
| --- | --- |
| domain-entry.md, all | Relationship overview and owner map |
| `CAP-DIST-content-packages` §§1–3 | Discovery, installation and dependency/availability boundary |
| `CAP-DIST-manifest-spec` §3 | Presets, default and auto-selection |
| `CAP-DIST-agent-projections` §1 | Projected kinds and destinations |
| `CAP-DIST-sync-and-transactions` §§1–2 | Receipt evidence and effective selection |

Answer: Python installation makes bundles available; explicit project presets or auto-selection determine asset
selection; host projection maps projected kinds to paths; receipt records the applied selection and installed
versions/path/hash/mode evidence. Its selection is an audit record, not an input. The cited capability sections
remain the authorities. No design or implementation prerequisite was needed.

Result: useful supplied-entry path. Overview separates availability, requested selection and recorded installation;
next steps serve unexpected-selection and path questions. No document returns. Extraction included unnecessary
manifest syntax, lifecycle examples and subagent policy in §2; combined output truncated during unrelated policy.
Needed selection/receipt passages were visible. This is an extraction-efficiency limit, not proof that whole-layer
reading is required. The mandatory reviewer repeats narrower extracts.

## R4: operations symptom to owner, four documented states

Starting input: “What does TRANSACTION_PENDING mean and which recovery owner applies to later-edited
RECOVERY_BLOCKED, a legacy journal lacking directories, and no journal with desired-state drift; how is readiness
decided?” plus [operations entry](operations-entry.md).

| Opened document/section | Necessity |
| --- | --- |
| operations-entry.md, all | Symptom/evidence/owner map |
| `CAP-DIST-sync-and-transactions` §3 item 6 | Recovery authority and stop conditions |
| Same contract, Readiness Gate | Desired-state normal-state criterion |
| distribution reference heading/code-row search | Locate supplied anchors and relevant action rows |
| Reference lines 203–227 and 260–277 | Installed-state diagnostics and error action mappings |

| Documented state | Reader conclusion and owner |
| --- | --- |
| Interrupted sync/pending journal | `TRANSACTION_PENDING`; capability §3 item 6 owns recovery; reference maps PendingTransactionError to AUTO/recover |
| Subsequent edit blocks rollback | `RECOVERY_BLOCKED`, HALT; agent cannot decide retained content; capability item 6/reference RecoveryError |
| Legacy journal lacks directories | `RECOVERY_BLOCKED`, HALT; actual advisory owns version-specific/manual fix; same owners |
| No journal, desired-state drift | Not ready; capability Readiness Gate owns sync --check interpretation |

The reader identifies exit 0 as ready and exits 1/2 as not ready; status alone is insufficient. These are paper
conclusions, not executed recovery/readiness evidence. Overview and next owner were explicit, with no domain/design
prerequisite or return to entry. Neighboring reference error rows were unnecessary extraction. No actual error
advisory was generated. Exact recovery instructions remain with the existing owners.
