---
id: ADR-separate-unit-prerequisites-from-milestone-themes
title: Separate unit prerequisites from milestone themes
summary: "Defines typed unit prerequisite edges, conservative base readiness and explicit lifecycle retargeting while milestones remain coarse grouping documents."
proposal: SPEC-unit-dependencies-and-milestone-scope
status: accepted
supersedes: ADR-milestone-documents
created_at: 2026-10-21
---

# [ADR-separate-unit-prerequisites-from-milestone-themes] Separate unit prerequisites from milestone themes

- **Status**: Accepted
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`ADR-milestone-documents` restricts dependency edges to milestones. Fine-grained sequencing therefore
encourages milestones that duplicate a single delivery unit. `CAP-DOCS-document-model` and
`CAP-DLV-proposal-incubation` already provide anchor identity and handoff rewriting.

## 2. Decision Drivers

Keep milestones as long-term multi-unit themes, express explicit unit ordering, preserve history resolution,
and avoid conflating scheduling with verified delivery. Existing authority over pickup and milestone transitions
must remain intact.

## 3. Considered Options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Continue milestone-only ordering | No model changes | Single-unit milestones remain necessary for sequencing |
| Typed unit edges with frontmatter authoring | Reuses indexing and handoff; separates grouping and order | Requires mixed-unit graph validation and lifecycle guidance |
| New scheduling CLI and automatic lineage resolution | Centralized execution | Adds authority and provenance mechanisms beyond the requested ordering outcome |

## 4. Decision Outcome

Choose typed direct PROP/SPEC anchor edges alongside the unchanged MS graph. Completed SPEC history is a
terminal target, not a source of transitive readiness obligations. No decomposition/supersession graph is stored. Supersede
`ADR-milestone-documents` only in its milestone-only dependency restriction and clarify coarse authoring;
retain its unaffected transition authority and milestone dependency readiness decisions. Milestone membership
becomes direct PROP-only; handoff does not carry milestone metadata into SPECs. Ignore legacy SPEC membership
metadata without rewriting historical specs. Remove the direct-spec creation `--milestone` flag and API
parameter in place, with no compatibility shim; proposal milestone authoring remains available. User and agent review milestone themes and decomposition together.

Carry and rewrite edges at handoff after projected-graph preflight. Other retirements require explicit incoming
edge disposition; provenance never silently redirects an edge. Status completed on the selected local base
satisfies a direct SPEC prerequisite for scheduling only. Unknown evidence blocks recommendation. Unit
readiness filters critical drafts too, while existing milestone ranking exceptions remain intact. User-directed
out-of-order starts remain available; structural validation remains mandatory.

Author optional frontmatter through existing document editing and templates, with no new CLI flag or evaluator.
No milestone member-count rule is added. A theme may initially have one member while describing broader scope.
No persistent milestone delivery lineage is introduced. Downstream status can be investigated from code/Git
on demand. `SPEC-deterministic-milestone-completion` remains independent and supplies no assumed contract here.

## 5. Consequences

Authors must maintain explicit dependency edges during lifecycle changes, for live incoming direct edges when a target is removed; completed history remains unchanged. No automatic selection of decomposed children or superseding proposals is safe.
The base status signal can be weaker than verified completion; it intentionally grants no delivery certification.
Development must test mixed cycles, history targets, handoff projection and conservative base recommendation.
This accepted decision governs the typed dependency and direct proposal membership contracts.

## Superseding decision disposition

`ADR-milestone-closure-confirmations` replaces only the inherited milestone closure/branch-enumeration procedure
with a focused two-confirmation Backlog review and explicit planned-to-done/reopen cases. This decision remains
in force for typed unit prerequisites, conservative readiness, lifecycle edge disposition and direct PROP-only
membership; unaffected MS readiness, activation/drop authority, history and roadmap review reminders remain.
