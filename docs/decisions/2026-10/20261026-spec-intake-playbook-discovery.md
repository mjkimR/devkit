---
id: ADR-spec-intake-playbook-discovery
title: Discover playbooks at spec intake with confirm-first invocation
summary: For procedures nobody invokes explicitly, we let spec run one bounded playbook search at new task intake and offer a matching playbook in one line that the user's confirmation invokes, to surface procedures without granting authority, accepting one search per intake.
proposal: SPEC-spec-playbook-discovery
status: accepted
created_at: 2026-10-26
---

# [ADR-spec-intake-playbook-discovery] Discover playbooks at spec intake with confirm-first invocation

- **Status**: Accepted
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Playbooks run only on explicit invocation (`/devkit-playbook`, a named ID or a failing rule's remediation), so they
stay unused unless the user already knows them. `ADR-external-playbook-execution` §4 states that ordinary requests do
not authorize discovery, and `ADR-immutable-decisions-editable-records` §4 ties `adr-compaction`'s deletions to the
user's explicit invocation. Several playbooks grant file moves, ADR deletions or feedback status updates on that
invocation, and search returns topical candidates for most ordinary requests (88 of 105 spec titles), so discovery
needs a bound on what it offers and on what an offer authorizes.

## 2. Decision Drivers

- Surface a fitting procedure without the user knowing it exists.
- Grant no authority beyond what the user confirms; never run a granting clause on a guess.
- Keep the user-visible offer rare and the cost of a false positive to one line.
- Keep `devkit-dist` spec-neutral for consumers without the `spec` bundle.
- Keep exact receipt-backed retrieval and external execution unchanged.

## 3. Considered Options

- **Keep explicit-only discovery**: no new cost, but procedures stay undiscovered.
- **Discover at intake, apply directly**: no extra question, but an ambiguous request runs a status-update or
  deletion procedure the user never asked for.
- **Discover at intake, apply directly except granting clauses**: fewer questions, but each playbook needs a
  per-clause authority split and the rule differs by playbook.
- **Discover at intake, confirm first** (chosen): one line per offer, uniform authority, rare offers under the
  selection rule.
- **A separate `spec-playbook` skill**: either model-invocable, which bypasses the skip table, or user-only, which
  `spec` cannot route to.

## 4. Decision Outcome

Chosen: discovery at `spec` intake with confirm-first invocation, because it surfaces procedures while keeping
authority with the user and the offer rare.

- **Trigger**: `spec` runs one `devkit playbook search` at new task intake, before classification, under the skip
  cases and the selection rule of `SPEC-spec-playbook-discovery` §3a. No match and search errors stay silent.
- **Invocation**: a candidate is named in one line with the classification statement of intake step 1. The user's
  confirmation is the explicit invocation of that playbook; without it nothing of the playbook runs. A declined
  candidate is not offered again in the conversation.
- **Ownership**: `spec` owns trigger and search; the post-selection procedure is a `spec` reference file read only on
  a match. No `spec-playbook` skill exists.
- **Generic entry**: the generated `devkit-playbook` skill stays the spec-neutral explicit entry, with the draft offer
  for explicit discovery only and without the statement that references from other skills do not authorize discovery.
- **Partial replacement of `ADR-external-playbook-execution`**: this replaces its §4 statement "Ordinary requests do not
  authorize discovery" and the §5 consequence that the no-unsolicited-discovery rule remains. Its exact retrieval, its
  external scheduling and execution boundary and the statement that no invocation grants extra permission for gated
  operations stay in force.
- **Partial replacement of `ADR-immutable-decisions-editable-records`**: in its §4 "Compaction" statement, the user's
  confirmation of a discovered `adr-compaction` candidate counts as explicit invocation and authorizes its deletions.
  The rest of the statement stays in force.
- Each affected statement gets a one-line pointer to the ADR this PADR becomes.

## 5. Consequences

- **Positive**: procedures are offered when the request names their operation; authority stays uniform and explicit.
- **Negative / Risks**: one search per new intake (about 0.3 s, at most 4096 bytes); the selection rule is agent
  judgment, so a topical false positive costs one declined line; each new playbook's `description` must name one
  operation and its scope.
- **Follow-ups**: `PROP-review-refactor` and `SPEC-release-handbook` state their entry conditions in this form when
  they land; a recorded offer rate above the acceptance bound triggers a review of the selection rule.

## 6. Confirmation

- `devkit-spec` text-contract tests for the intake step, the skip table, the selection rule and confirm-first wording;
  `devkit-dist` tests for the reworded generated skill and guidance line.
- Review step: the recorded manual run in the proposal's `intake-frequency.md` §6 shows 0 offers on the 16 ordinary
  intents and one offer per positive control.
