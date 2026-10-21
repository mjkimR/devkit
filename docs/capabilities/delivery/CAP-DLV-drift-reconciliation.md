---
id: CAP-DLV-drift-reconciliation
title: Manual Drift Reconciliation
summary: "An explicitly invoked maintenance playbook reviews a bounded batch of Living Spec, code and guidance, records evidence and coverage gaps, and routes user-decided corrections or deferrals through existing workflows."
area: delivery
status: active
stories:
  - US-keep-the-living-spec-consistent
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/drift-reconciliation.md
---

# [CAP-DLV-drift-reconciliation] Manual Drift Reconciliation

## 1. Summary

The opt-in `maintenance` catalog bundle supplies the independent `drift-reconciliation` playbook
(`CAP-DIST-content-packages`). Explicit manual invocation through `devkit-playbook` loads its procedure on demand
(`CAP-DIST-context-and-playbooks`). It complements per-feature `spec-sync` with accumulated drift review under
`ADR-dual-source-of-truth-and-periodic-reconciliation`; neither ledger automatically decides intended behavior.

## 2. Scope & Boundary

Review documented commands/options, interfaces, terminology, behavior, paths and consumer guidance against the
relevant implementation and tests. Reuse available lookup, references, entrypoints and governance checks.
Scope excluded: a detector, scheduler, standalone skill, report database, automatic rewrite, companion playbooks,
and unrelated structural cleanup. Entrypoints and age are navigation/scope aids, never evidence of semantic drift.

## 3. Review and Reconciliation Contract

1. Intake records repository identity, HEAD and dirty paths, selected contract IDs or area, permitted implementation
   and guidance roots, report destination and prior reports. Clarify missing scope before broad inspection;
   enumerate candidates and split large areas into explicit batches. Record reviewed and excluded candidates.
2. Compare both ledgers and relevant consumer guidance. Each confirmed mismatch has a stable report-local key,
   contract ID and precise citation, code/guidance citation at the recorded revision (including dirty content),
   expected and observed behavior, affected outcome, applicable command/test evidence, proposed disposition and
   `deterministic` or `semantic-assessment` classification. Unsupported suspicions remain investigation gaps.
3. Missing tools, malformed documents, absent entrypoints, unavailable checks and insufficient evidence are named
   coverage gaps with reasons. A deterministic failure proves only its checked condition. A passing check does
   not prove semantic consistency.
4. Present findings together for explicit user dispositions: update documentation/guidance, fix code, defer or
   waive. Record the reason and decision provenance per key. Deferral names an existing or newly authorized
   feedback/proposal destination and restart condition; waiver names the intentional gap and rationale.
   Unanswered findings remain pending. Invocation and automatic integration policy do not arbitrate intent.
5. Apply only decided corrections under applicable development, write-scope and approval boundaries. Code fixes
   require regression evidence; documentation corrections recheck disputed claims, references and applicable
   checks. Outside-scope work is tracked separately. A report authorizes no correction by itself.
6. Search matching open feedback/proposals before creating destinations; repeated runs link earlier keys and
   recheck their dispositions. Revalidate evidence if HEAD or relevant dirty paths change before correction or
   final verification; obtain a new decision when correction intent changes. Preserve unrelated edits.
7. Completion applies only to the declared batch. Record reviewed/excluded candidates, gaps, detected, resolved,
   deferred, waived and pending counts, provenance, verification and follow-ups. Zero findings still needs coverage
   evidence. A completed review may contain explicit gaps/deferrals/waivers, but pending decisions prevent a fully
   reconciled claim. Never claim whole-repository consistency from a batch.

## 4. Report Interface

The artifact is ordinary Markdown under the owning unit's materials, or the repository's existing materials
location without a unit. It contains intake, coverage, findings, decisions, corrections and completion evidence.
Existing commands retain their own output contracts; narrative semantic assessment is not a new checker result.
Isolated seeded exercises label simulated decisions and authorize no real source change.
