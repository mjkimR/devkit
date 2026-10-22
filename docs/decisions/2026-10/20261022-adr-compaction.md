---
id: ADR-adr-compaction
title: ADR Compaction as the Only Exception to the Append-Only Ledger
summary: "For a fragmented decision ledger, we allow compaction into replacement ADRs that alias the retired IDs as the only exception to the append-only rule, to keep current decisions readable in one place, accepting that retired texts live only in Git history."
status: accepted
created_at: 2026-10-22
---

# [ADR-adr-compaction] ADR Compaction as the Only Exception to the Append-Only Ledger

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `docs/decisions/`, `capabilities/documents/`, `capabilities/harness/`

---

## 1. Context & Problem Statement

`docs/decisions/` is an append-only ledger: an approved ADR is never edited or deleted, and a change of direction is a
new ADR linked by `supersedes` and `superseded_by`. Fast development produced many fine-grained ADRs, so the current
decision on one topic is spread across several records and supersession chains, and a reader (an agent first)
reassembles it at the cost of context. `ADR-document-id-aliases` lets every ID-bearing document carry `aliases`
resolved through one canonical mapping, so records can be consolidated without breaking references.

---

## 2. Decision Drivers

- The current decision on a topic is readable in one record.
- Compaction reorganizes decisions; it never changes, adds or reverses one.
- No reference breaks: every retired ID keeps resolving.
- Running a compaction costs no more process than the change itself: no spec unit for an ID-preserving rewrite.

---

## 3. Considered Options

### Option 1: Compaction by replacement with aliases (Selected)
- **Overview**: replace a group of related approved ADRs with one new ADR whose `aliases` lists the retired IDs and
  whose considered options keep the alternatives the retired ADRs weighed; delete the retired files in the same commit.
- **Pros**: one record per topic; references resolve through the alias; the full text stays in Git.
- **Cons**: retired files leave the working tree.

### Option 2: Tombstones
- **Overview**: keep each retired ADR as a stub pointing at the replacement.
- **Pros**: no deletion.
- **Cons**: the ledger keeps every file; an alias can never resolve while the old ID is still declared.

### Option 3: Keep the strict ledger
- **Overview**: supersession only.
- **Cons**: fragmentation keeps growing.

---

## 4. Decision Outcome

We adopt **Option 1**. The append-only rule stays the default; compaction is its only exception.

- **Replacement**: a compaction replaces two or more approved ADRs with one new ADR (a new slug naming the topic,
  dated the compaction day, `status: accepted`, `proposal` unset) and deletes the source files in the same commit.
  The replacement's `aliases` lists every source ID and every alias a source declared. No `supersedes` is written.
- **No new decision**: the replacement's outcome holds exactly the statements in effect in the group, each citing its
  source ID. Wording may be consolidated; no driver, option, scope or consequence is added, dropped or changed in
  meaning. Superseded parts are left out; rejected alternatives stay in the considered options, labelled by the
  source that weighed them. The retired texts are read from Git (`git log --diff-filter=D -- docs/decisions/`).
- **Out of compaction**: a contradiction between in-effect ADRs, a statement that no longer matches the code or the
  Living Spec, or any other needed change is not resolved by compaction. The affected ADR stays out of the group and
  the finding goes to feedback or a proposal.
- **Supersession closure**: a group contains every ADR a member's `supersedes` or `superseded_by` names, and every ADR
  whose supersession field names a member, transitively.
- **Later changes**: a later ADR that changes any part of a replacement supersedes the whole replacement by its
  canonical ID and restates the parts that stay in effect; a new `supersedes` never names a retired alias. A
  replacement may itself be compacted again; its aliases carry over.
- **Authority and depth**: compaction runs only when the user explicitly invokes the `adr-compaction` playbook; that
  invocation is the authorization for the run's deletions. It runs at `session` depth: the replacement ADRs and the
  ID rewrites `devkit rules fix` makes in current documents do not raise it to `spec`.
- **Checks**: no dedicated rule. A run is complete when `devkit rules fix` then `devkit rules check` pass, every
  deleted ADR ID resolves through `devkit spec resolve` to a replacement that lists it in `aliases`, and a fidelity review
  of each replacement against its sources finds no changed decision.

---

## 5. Consequences

- **Positive**: the ledger shrinks to one record per topic; retired IDs keep resolving.
- **Negative / Risks**: a careless consolidation could change a decision's meaning; the fidelity review and the
  per-statement source citations are the guard. Retired texts are read through `git log --diff-filter=D`.
- **Follow-ups**: the `adr-compaction` playbook in the `spec` bundle carries the procedure.

---

## 6. Confirmation

Review only: the `adr-compaction` playbook's completion checks.
