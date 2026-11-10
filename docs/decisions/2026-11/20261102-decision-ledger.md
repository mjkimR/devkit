---
id: ADR-decision-ledger
title: Immutable decisions, editable records and confirm-first playbook discovery
summary: "For the decision ledger and unknown procedures, we keep decisions immutable but let ADRs be edited and consolidated by topic without changing meaning, and let spec offer one matching playbook at intake that confirmation invokes, to keep records current and procedures found, accepting judged edits."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-adr-compaction
  - ADR-immutable-decisions-editable-records
  - ADR-spec-intake-playbook-discovery
  - ADR-group-compaction-by-topic
supersedes: [ADR-document-id-aliases]
---

# [ADR-decision-ledger] Immutable decisions, editable records and confirm-first playbook discovery

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `docs/decisions/`, `capabilities/documents/`, `capabilities/governance/`,
  `capabilities/harness/`, the `adr-consolidation` playbook

---

## 1. Context & Problem Statement

**Decision records.** An append-only ledger, in which an approved ADR is never edited or deleted and any change is a
new ADR linked by `supersedes`, protects the wrong thing: what must not change silently is a decision, not its wording.
No rule enforced append-only; it was stated in the decisions README, the `spec-sync` skill, the `living-spec-writing`
instruction and `CAP-DOCS-document-model`, and `RULE-document-reference` exempted ADRs and PADRs from alias rewrites.
Frozen documents keep stale paths, command names and retired IDs. Fast development produces many fine-grained ADRs, so
the current decision on one topic is spread across several records and supersession chains, and a reader (an agent
first) reassembles it at the cost of context. `ADR-document-id-aliases` lets every ID-bearing document carry `aliases`
resolved through one canonical mapping, so records can be consolidated without breaking references.

**Consolidation groups.** Closing every consolidation group under supersession lets a few bridging supersessions chain
unrelated topics together: in the integration ADRs, one ADR that retires two clauses and one that replaces three
lifecycle rules joined 13 ADRs into a single component, which consolidated as one replacement would hold about 100
clauses and 30 aliases across five topics, a mega-ADR that nobody looks up as one decision. A replacement states only
clauses in effect without closure: the target's replacement can leave out the replaced clauses, and the superseding
statement lives in its own replacement.

**Playbook discovery.** Playbooks run only on explicit invocation (`/devkit-playbook`, a named ID or a failing rule's
remediation), so they stay unused unless the user already knows them. `ADR-playbook-retrieval` §4 stated that
ordinary requests do not authorize discovery, and consolidation's deletions are tied to the user's explicit invocation.
Several playbooks grant file moves, ADR deletions or feedback status updates on that invocation, and search returns
topical candidates for most ordinary requests (88 of 105 spec titles), so discovery needs a bound on what it offers and
on what an offer authorizes.

---

## 2. Decision Drivers

- A decision is never reversed, invalidated or narrowed without a recorded new decision.
  (ADR-immutable-decisions-editable-records)
- Decision records stay current and readable: wording, format and references can be corrected.
  (ADR-immutable-decisions-editable-records)
- Related records can be consolidated without breaking references. (ADR-immutable-decisions-editable-records)
- Every current document, ADRs included, converges on canonical IDs through one `devkit rules fix`.
  (ADR-immutable-decisions-editable-records)
- The current decision on a topic is readable in one record. (ADR-adr-compaction)
- Consolidation reorganizes decisions; it never changes, adds or reverses one. (ADR-adr-compaction)
- No reference breaks: every retired ID keeps resolving. (ADR-adr-compaction)
- Running a consolidation costs no more process than the change itself: no spec unit for an ID-preserving rewrite.
  (ADR-adr-compaction)
- Each replacement is one decision area a reader looks up. (ADR-group-compaction-by-topic)
- A replacement still states only the clauses in effect. (ADR-group-compaction-by-topic)
- No reference breaks, and no decision changes. (ADR-group-compaction-by-topic)
- `RULE-decision-supersession` keeps checking the metadata that remains. (ADR-group-compaction-by-topic)
- Surface a fitting procedure without the user knowing it exists. (ADR-spec-intake-playbook-discovery)
- Grant no authority beyond what the user confirms; never run a granting clause on a guess.
  (ADR-spec-intake-playbook-discovery)
- Keep the user-visible offer rare and the cost of a false positive to one line. (ADR-spec-intake-playbook-discovery)
- Keep `devkit-dist` spec-neutral for consumers without the `spec` bundle. (ADR-spec-intake-playbook-discovery)
- Keep exact receipt-backed retrieval and external execution unchanged. (ADR-spec-intake-playbook-discovery)

---

## 3. Considered Options

### Decision records
- **Immutable decisions, editable records** (selected in `ADR-immutable-decisions-editable-records`): a change of
  decision needs a new ADR; an edit that keeps every decision's meaning is allowed in place. Pros: records stay
  current; consolidation is an ordinary edit; references in ADRs are fixed like any other. Cons: whether an edit changes
  meaning is a judgment, not a mechanical check.
- **Append-only with consolidation as the only exception** (rejected in `ADR-immutable-decisions-editable-records`; the
  rule of `ADR-adr-compaction`): stale wording and references stay in every ADR; each other kind of cleanup needs its
  own exception.
- **Freely editable ADRs** (rejected in `ADR-immutable-decisions-editable-records`): a decision could change without a
  record.

### Consolidation
- **Consolidation by replacement with aliases** (selected in `ADR-adr-compaction`): replace a group of related approved
  ADRs with one new ADR whose `aliases` lists the retired IDs and whose considered options keep the alternatives the
  retired ADRs weighed; delete the retired files in the same commit. Pros: one record per topic; references resolve
  through the alias; the full text stays in Git. Cons: retired files leave the working tree.
- **Tombstones** (rejected in `ADR-adr-compaction`): keep each retired ADR as a stub pointing at the replacement. No
  deletion, but the ledger keeps every file and an alias can never resolve while the old ID is still declared.
- **Keep the strict ledger** (rejected in `ADR-adr-compaction`): supersession only; fragmentation keeps growing.

### Consolidation groups
- **Topic groups; partial supersession may cross groups** (selected in `ADR-group-compaction-by-topic`): group by
  topic; a wholly superseded ADR joins its superseder's group; a partial supersession may cross groups. Pros: coherent
  replacements; a bridging ADR no longer drags unrelated topics together. Cons: a reader follows a superseding
  statement into another replacement.
- **Keep the closure; split the replacement into sections** (rejected in `ADR-group-compaction-by-topic`): one
  replacement per closure, sectioned by topic. No rule change, but mega-ADRs whenever a few supersessions bridge
  topics.
- **Keep the closure; leave such components uncompacted** (rejected in `ADR-group-compaction-by-topic`): compact only
  closures that form one topic. No rule change, but the most fragmented part of the ledger stays fragmented.

### Playbook discovery
- **Discover at intake, confirm first** (selected in `ADR-spec-intake-playbook-discovery`): one line per offer,
  uniform authority, rare offers under the selection rule.
- **Keep explicit-only discovery** (rejected in `ADR-spec-intake-playbook-discovery`): no new cost, but procedures stay
  undiscovered.
- **Discover at intake, apply directly** (rejected in `ADR-spec-intake-playbook-discovery`): no extra question, but an
  ambiguous request runs a status-update or deletion procedure the user never asked for.
- **Discover at intake, apply directly except granting clauses** (rejected in `ADR-spec-intake-playbook-discovery`):
  fewer questions, but each playbook needs a per-clause authority split and the rule differs by playbook.
- **A separate `spec-playbook` skill** (rejected in `ADR-spec-intake-playbook-discovery`): either model-invocable,
  which bypasses the skip table, or user-only, which `spec` cannot route to.

---

## 4. Decision Outcome

Decisions are immutable and decision records are editable and consolidable without changing meaning, because that
keeps every decision change recorded while records stay current and consolidated. Consolidation groups are formed by
topic, because each replacement stays one decision area while every replacement still states only clauses in effect.
Playbooks are discovered at `spec`
intake with confirm-first invocation, because it surfaces procedures while keeping authority with the user and the
offer rare.

### Decision records

- **Decision changes**: reversing, invalidating, narrowing or widening a decision, or changing its scope, drivers'
  weight or consequences, is a new ADR. (ADR-immutable-decisions-editable-records)
  → `CAP-DOCS-document-model` §Decision supersession (MUST)
- When a decision change replaces a whole ADR, it names it in `supersedes`, and the replaced ADR gets
  `status: superseded` and `superseded_by`. When it replaces only part of an ADR, it names that ADR and the part in its
  outcome, and the earlier ADR's affected statement gets a one-line pointer to the new ADR.
  (ADR-immutable-decisions-editable-records)
- **Editorial edits** may be made in place on accepted ADRs and need no new ADR: wording and format, the template's
  current sections, stale paths, command, code and file names, references rewritten to canonical IDs, and metadata
  (`status`, `superseded_by`, `aliases`). An edit that would change what a statement decides is a decision change.
  (ADR-immutable-decisions-editable-records) → `CAP-DOCS-document-model` §Decision supersession (MAY)
- **References in decision records**: `RULE-document-reference` reports an alias reference in an ADR or PADR like one
  in any current document, and `devkit rules fix` rewrites it to the canonical ID. This replaces the decision-record
  exemption of `ADR-document-id-aliases` (its "References" outcome). Historical files (completed spec bundles, done or
  dropped milestones) stay as written. (ADR-immutable-decisions-editable-records)
- **Checks**: no rule detects a decision change; review of the diff does. A consolidation run is complete when
  `devkit rules fix` then `devkit rules check` pass, every deleted ADR ID resolves through `devkit docs resolve`, and a
  fidelity review finds no changed decision. (ADR-immutable-decisions-editable-records)

### Consolidation

- **Consolidation**: related ADRs may be consolidated into one replacement ADR whose `aliases` lists the retired IDs and
  every alias they declared; the retired files are deleted in the same commit. The replacement's outcome holds exactly
  the statements in effect, each citing its source ID; superseded parts are left out, rejected alternatives stay in the
  considered options. A contradiction or a statement that no longer matches the code or the Living Spec is not
  resolved by consolidation; it goes to feedback or a proposal. A consolidation runs when the user explicitly invokes the
  `adr-consolidation` playbook, which authorizes its deletions, at `session` depth.
  (ADR-immutable-decisions-editable-records)
- A consolidation group is formed by topic and holds two or more members. (ADR-group-compaction-by-topic)
  → `CAP-DOCS-document-model` §Decision supersession (MUST)
- A wholly superseded ADR joins the group of its superseder. (ADR-group-compaction-by-topic)
  → `CAP-DOCS-document-model` §Decision supersession (MUST)
- When a partially superseding member and its target land in different groups, the target's replacement leaves out
  the replaced clauses. The superseding replacement states what it replaced, and it cites the target's replacement
  ID. (ADR-group-compaction-by-topic) → `CAP-DOCS-document-model` §Decision supersession (MUST)
- An ADR kept outside the run whose `supersedes` names a consolidated member names the member's replacement instead. That
  replacement carries the matching "Superseded in part by" line. (ADR-group-compaction-by-topic)
  → `CAP-DOCS-document-model` §Decision supersession (MUST)
- A consolidated member that partially supersedes an ADR kept outside the run passes that entry on: its replacement lists
  the kept ADR in `supersedes`, the one exception to a replacement having none, and the kept ADR's pointer names the
  replacement. (ADR-group-compaction-by-topic) → `CAP-DOCS-document-model` §Decision supersession (MUST)
- The user's confirmation of a discovered `adr-consolidation` candidate counts as explicit invocation and authorizes its
  deletions. (ADR-spec-intake-playbook-discovery)

### Playbook discovery at spec intake

- **Trigger**: `spec` runs one `devkit playbook search` at new task intake, before classification, under the skip
  cases and the selection rule of `SPEC-spec-playbook-discovery` §3a. No match and search errors stay silent.
  (ADR-spec-intake-playbook-discovery)
- **Invocation**: a candidate is named in one line with the classification statement of intake step 1. The user's
  confirmation is the explicit invocation of that playbook; without it nothing of the playbook runs. A declined
  candidate is not offered again in the conversation. (ADR-spec-intake-playbook-discovery)
- **Ownership**: `spec` owns trigger and search; the post-selection procedure is a `spec` reference file read only on a
  match. No `spec-playbook` skill exists. (ADR-spec-intake-playbook-discovery)
- **Generic entry**: the generated `devkit-playbook` skill stays the spec-neutral explicit entry, with the draft offer
  for explicit discovery only and without the statement that references from other skills do not authorize discovery.
  (ADR-spec-intake-playbook-discovery)
- **Partial replacement of `ADR-playbook-retrieval`**: this replaces its §4 statement "Ordinary requests do
  not authorize discovery" and the §5 consequence that the no-unsolicited-discovery rule remains. Its exact retrieval,
  its external scheduling and execution boundary and the statement that no invocation grants extra permission for gated
  operations stay in force. The §4 statement and its consequence are retired from `ADR-playbook-retrieval`.
  (ADR-spec-intake-playbook-discovery)

---

- Supersedes in part `ADR-document-id-aliases`: the decision-record exemption from alias rewrites in the References outcome; historical files retain their existing treatment.

## 5. Consequences

- **Positive**:
  - ADRs carry current names and canonical IDs; consolidation is routine. (ADR-immutable-decisions-editable-records)
  - Procedures are offered when the request names their operation; authority stays uniform and explicit.
    (ADR-spec-intake-playbook-discovery)
  - Bridging supersessions no longer force mega-ADRs; the integration ADRs can be consolidated by topic.
    (ADR-group-compaction-by-topic)
- **Negative / Risks**:
  - An editorial edit could change meaning unnoticed; the edit's diff review is the guard.
    (ADR-immutable-decisions-editable-records)
  - One search per new intake (about 0.3 s, at most 4096 bytes); the selection rule is agent judgment, so a topical
    false positive costs one declined line; each new playbook's `description` must name one operation and its scope.
    (ADR-spec-intake-playbook-discovery)
  - The fidelity review must check cross-group supersession explicitly: replaced clauses left out of one replacement
    and stated in another. (ADR-group-compaction-by-topic)
- **Follow-ups**:
  - None for the decision records. (ADR-immutable-decisions-editable-records)
  - The `adr-consolidation` playbook follows the topic-group rule. (ADR-group-compaction-by-topic)
  - `SPEC-review-refactor` and `SPEC-release-handbook` state their entry conditions in this form when they land; a
    recorded offer rate above the acceptance bound triggers a review of the selection rule.
    (ADR-spec-intake-playbook-discovery)

---

## 6. Confirmation

- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`
  (`test_alias_references_in_decision_records_are_fixed`, `test_alias_references_in_history_stay`).
  (ADR-immutable-decisions-editable-records)
- Diff review for decision changes; the `adr-consolidation` playbook's completion checks.
  (ADR-immutable-decisions-editable-records)
- `RULE-decision-supersession` checks the remaining `supersedes` metadata and pointer lines; the playbook's fidelity
  review checks the replaced clauses. Otherwise review only. (ADR-group-compaction-by-topic)
- `devkit-spec` text-contract tests for the intake step, the skip table, the selection rule and confirm-first wording;
  `devkit-dist` tests for the reworded generated skill and guidance line. (ADR-spec-intake-playbook-discovery)
- Review step: the recorded manual run in the proposal's `intake-frequency.md` §6 shows 0 offers on the 16 ordinary
  intents and one offer per positive control. (ADR-spec-intake-playbook-discovery)
