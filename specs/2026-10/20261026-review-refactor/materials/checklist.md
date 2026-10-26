# Spec-review checklist: agreed design to playbook sections

`SPEC-review-refactor` AC-05. `S` is `playbooks/review-refactor/SKILL.md`, `C` its `references/criteria.md`, `A` its
`references/applying.md` (all under `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/`).

| Agreed item (spec §6) | Playbook location |
| --- | --- |
| Entry condition: invoked or confirmed, exact `devkit playbook get maintenance/review-refactor` | S, opening paragraph |
| Invocation and external runners authorize no change; unattended run stops at the decision round | S, opening paragraph |
| Contract mismatch deferred to drift reconciliation; never invokes another playbook | S, second paragraph |
| Consolidation and reduction as primary outcomes | S, opening paragraph; C §2 first item |
| Kind: merge duplicated logic into a shared module | C §2; C §1 Code "Duplicated behavior" |
| Kind: fold repeated technical helpers into a utility | C §2; C §1 Code "Repeated technical helpers" |
| Kind: remove unneeded code, guidance, options and commands | C §2; C §1 Code "Unused code", Guidance, CLI "Unneeded" |
| Shared implementation needs two current callers with the same behavior | C §2 second item |
| Compatibility-path removal is a contract change unless the declared policy exception; names inputs no longer accepted | C §2 third item; A §8 exception |
| Command, option or interface removal, rename or consolidation never behavior-preserving | C §2 fourth item; A §8 |
| Reduction ground: derivable | C §3 item 1 |
| Reduction ground: duplicated with a named canonical copy | C §3 item 2 |
| Reduction ground: enforced mechanically elsewhere | C §3 item 3 |
| Reduction ground: recorded check (code: verification plus reachability; guidance: representative-task run); unavailable without the record | C §3 item 4 |
| Line or token delta reported, never the justification | C §3 last line; S §6 change record |
| Intake: run ID, identity, HEAD, dirty paths, prior reports, destination | S §1 step 1 |
| Intake: user selects surfaces and roots; missing scope clarified first | S §1 step 2 |
| One batch per surface, one decision round each | S §1 step 3 |
| Cross-surface finding cites both sides, lands in the batch of its landing surface | S §1 step 4 |
| Unselected landing surface: deferred with a follow-up, not applied | S §1 step 4 first sub-item |
| User's scope addition: own batch, roots clarified, own decision round, recorded | S §1 step 4 second sub-item |
| Following edits stay with the change; call sites, imports, re-exports are source edits | S §1 step 5 |
| Following edits never touch receipt-owned files; source bundle, upstream follow-up or `devkit override` | S §1 step 6 |
| Subagent review when useful and supported; fallback in the playbook's agent | S §2 step 3 |
| Subagent result validated at the cited location; unconfirmed claim dropped or a coverage gap | S §2 step 3 first sub-item |
| Verification and negative-reachability claims re-run before recording | S §2 step 3 second sub-item |
| Root covered only when the result lists what was read | S §2 step 3 third sub-item |
| Subagents have no decision authority and write no records | S §2 step 3 fourth sub-item; A §3 last item |
| Tool output is a candidate list; install nothing without asking | S §2 step 2 |
| Finding cites location and named cost; dropped otherwise and counted | S §3; C opening paragraph |
| Code review questions | C §1 Code |
| Guidance review questions and preserved constraints | C §1 Guidance |
| CLI review questions (inventory, overlap, unneeded, fragmented, grouping, help and docstrings) | C §1 CLI |
| Findings and changes as separate records; commit per change; follow-ups without duplication | S §3 last paragraph; S §6 |
| Dispositions: consolidate/reduce/remove, contract change, defer, keep | S §4 table |
| Decision-round approval is the routed intent, never integration approval | S §4 second bullet; A §7 |
| Route: cross-area refactor workflow (`sdd-overall-refactor` with `spec`) | A §1 step 3 first sub-item |
| Single-module test with following edits left out; examples per surface | A §1 step 2 |
| Single-module route: feature workflow at the repository's own depth | A §1 step 3 second sub-item |
| Route stated in the decision round; never split or merge to change it; undeclared layout settled by approval | A §1 steps 3-4; S §4 opening |
| Batch write scope: edited paths stated in the round, following edits included | A §1 step 5 |
| Direct mode: no workers and no Unit; edit tasks; general subagents or own steps; procedure without a refactor workflow | A opening paragraph; A §1 last line; A §2 step 2 |
| Branch: own branch, never the base branch | A §2 step 1 |
| Subagent write scopes: subset of the batch scope, disjoint from concurrent subagents | A §3 first item |
| Sequential changes on the previous checkpoint | A §3 second item |
| Diff check against assigned paths and agreed change | A §3 third item |
| Hunk-by-hunk revert; never reset another scope; redo or return to the round | A §3 fourth item |
| One commit per change on a tree holding only committed work plus the change | A §4 steps 2 and 3 |
| Verification before and after per change | A §4 step 1 |
| Full verification on a clean tree at the final head | A §4 step 4 |
| Independent review by a fresh reviewer, or a recorded self-review; repository review effort | A §5 |
| Report with breaking changes in the final response and commit body | A §6 |
| Integration after the report through the repository path and its own approval (`overall-refactor` session path with `spec`) | A §7 |
| Contract-removal work item through the normal development workflow, contract and docs updated | A §8 |
| Preservation: static and dynamic reachability with named searches and results | C §4 first item |
| Preservation: verification before and after | C §4 second item |
| Preservation: characterization test only for an untested merged caller | C §4 third item |
| Preservation: retained-constraint map for guidance, plus representative-task run when relied on | C §4 fourth item |
| Helper placement: lowest common owner; new cross-package or foundation module is a decision | C §5 |
| Helper placement order example (feature-local, `utils` or `base`, foundation) | C §5 second paragraph |
| Recurrence prevention: delete or consolidate first; new rule needs evidenced recurrence and benefit | C §6 |
| HEAD or dirty paths moved: revalidate; changed intent back to the round | S §5 |
| Report fields: run ID, identity, revision, dirty state, scope, outcome, commit per change | S §6 |
| Exercise rule: decisions simulated, change only the fixture | S §4 last bullet |
| Batch completion only with no pending decision; never the whole repository | S §6 last paragraph |
