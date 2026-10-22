---
id: ADR-usecases-replace-stories
title: Use Cases Replace User Stories in the Living Spec
summary: "For a Living Spec that is the durable source of truth, we replace user stories with use cases that state a main success scenario, step-keyed extensions and postconditions, to make every branch and guarantee explicit, accepting a breaking rename across documents, rules and CLI."
status: accepted
created_at: 2026-10-22
---

# [ADR-usecases-replace-stories] Use Cases Replace User Stories in the Living Spec

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `capabilities/documents/`, `capabilities/governance/`, `capabilities/traceability/`, `usecases/`

---

## 1. Context & Problem Statement

`docs/` is the current contract, but its actor-level documents were user stories: an "As a / I want / So that"
narrative, a background paragraph and a flat list of Given/When/Then scenarios. A user story is a request that
expires once delivered, so the format has no place for the flow itself, for the branch a scenario belongs to or for
what the system guarantees afterwards. The existing stories carried their flow in background prose and their refusals
as unordered scenarios, so a missing failure path was invisible. Agent-first output makes every refusal a stable code
with a directive, which is exactly what a use case's extensions enumerate.

---

## 2. Decision Drivers

- The actor-level document is a durable contract, maintained in place like a capability.
- Every refusal and alternative path is attached to the step it branches from and names its stable code.
- Capabilities keep the detailed contracts; the actor-level document does not duplicate them.
- No external consumer exists yet, so a breaking rename costs only this repository.

---

## 3. Considered Options

### Option 1: Use cases with their own kind, prefix and directory (Selected)
- **Overview**: `UC-<slug>` under `docs/usecases/<area>/`, kind `usecase`, capability back-links in `usecases:`.
- **Pros**: the name states the format; nothing reads as a backlog item. **Cons**: renames across rules, CLI, viewer and guides.

### Option 2: Keep `US-` IDs and restructure only the template
- **Pros**: no rule or CLI change. **Cons**: the name keeps promising a story while the body is a use case.

### Option 3: Keep user stories
- **Cons**: flows stay in prose and branches stay unkeyed.

---

## 4. Decision Outcome

We adopt **Option 1**.

- **Kind and location**: document kind `usecase`, ID `UC-<slug>`, file `docs/usecases/<area>/UC-<slug>.md` (and
  `usecases/` under a namespace docs root). `US-` is no longer an ID prefix.
- **Format**: frontmatter `primary_actor` and `supporting_actors`; sections Goal (goal, scope, trigger,
  preconditions), Main Success Scenario, Extensions keyed to steps, Postconditions (success and minimal guarantee) and
  Acceptance Criteria whose scenarios name what they cover (`usecase-writing`).
- **Traceability**: a use case lists `capabilities:`; a capability lists `usecases:` (formerly `stories:`), checked
  in both directions by `RULE-traceability-link`. A spec's `related_stories` becomes `related_usecases`.
- **Feature specs**: `spec.md` keeps user stories as the statement of intent; `spec-sync` folds a completed spec's
  behavior into use cases.
- **History**: completed specs and dated materials keep their `US-` text unchanged; it no longer resolves as an ID.

---

## 5. Consequences

- **Positive**: each use case shows its flow, every keyed branch with its code and the guarantees that hold on failure.
- **Negative / Risks**: `US-` references in completed specs no longer resolve; a use case takes longer to write than a
  story.
- **Follow-ups**: none.

---

## 6. Confirmation

- `RULE-id-convention` (path, ID and heading of `UC-` documents), `RULE-spec-format` (frontmatter),
  `RULE-traceability-link` (`capabilities` and `usecases` in both directions).
- Section structure: review only.
