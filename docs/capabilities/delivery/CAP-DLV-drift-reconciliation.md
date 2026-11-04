---
id: CAP-DLV-drift-reconciliation
title: Manual Drift Reconciliation
summary: "An explicitly invoked or confirmed maintenance playbook reviews a bounded batch of Living Spec, code and guidance, records evidence and coverage gaps, and routes user-decided corrections or deferrals through existing workflows."
area: delivery
status: active
usecases:
  - UC-reconcile-living-spec-drift
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/drift-reconciliation.md
---

# [CAP-DLV-drift-reconciliation] Manual Drift Reconciliation

## 1. Summary

The opt-in `maintenance` catalog bundle supplies the independent `drift-reconciliation` playbook
(`CAP-DIST-content-packages`). Explicit manual invocation through `devkit-playbook`, its exact ID or the user's confirmation
of a `spec` intake offer loads its procedure on demand (`CAP-DIST-context-and-playbooks`). It complements per-feature `spec-sync` with accumulated drift review under
`ADR-dual-source-of-truth-and-periodic-reconciliation`; the playbook MUST NOT treat either ledger as automatically
deciding intended behavior.
Rules that bind an agent, a host or a playbook step are checked by review only unless they name a check.

## 2. Scope & Boundary

The playbook MUST review documented commands/options, interfaces, terminology, behavior, paths and consumer guidance
against the relevant implementation and tests. It SHOULD reuse available lookup, references, entrypoints and
governance checks. Scope excluded: a detector, scheduler, standalone skill, report database, automatic rewrite,
companion playbooks, and unrelated structural cleanup. The playbook MUST NOT treat entrypoints or age as evidence of
semantic drift; they are navigation/scope aids.

## 3. Review and Reconciliation Contract

1. Intake MUST record repository identity, HEAD and dirty paths, selected contract IDs or area, permitted
   implementation and guidance roots, report destination and prior reports. The playbook MUST clarify missing scope
   before broad inspection and MUST enumerate candidates. It SHOULD split large areas into explicit batches. It MUST
   record reviewed and excluded candidates.
2. The playbook MUST compare both ledgers and relevant consumer guidance. Each confirmed mismatch MUST have a stable
   report-local key, contract ID and precise citation, code/guidance citation at the recorded revision (including
   dirty content), expected and observed behavior, affected outcome, applicable command/test evidence, proposed
   disposition and `deterministic` or `semantic-assessment` classification. Unsupported suspicions MUST remain
   investigation gaps.
3. Missing tools, malformed documents, absent entrypoints, unavailable checks and insufficient evidence MUST be
   recorded as named coverage gaps with reasons. The playbook MUST NOT treat a deterministic failure as proof of more
   than its checked condition. It MUST NOT treat a passing check as proof of semantic consistency.
4. The playbook MUST present findings together for explicit user dispositions: update documentation/guidance, fix
   code, defer or waive. It MUST record the reason and decision provenance per key. A deferral MUST name an existing
   or newly authorized feedback/proposal destination and restart condition. A waiver MUST name the intentional gap
   and rationale. Unanswered findings MUST remain pending. The playbook MUST NOT treat invocation or automatic
   integration policy as arbitrating intent.
5. The playbook MUST apply only decided corrections, under applicable development, write-scope and approval
   boundaries. Code fixes MUST carry regression evidence. Documentation corrections MUST recheck disputed claims,
   references and applicable checks. Outside-scope work MUST be tracked separately. The playbook MUST NOT treat a
   report by itself as authorizing a correction.
6. The playbook MUST search matching open feedback/proposals before creating destinations. Repeated runs MUST link
   earlier keys and recheck their dispositions. IF HEAD or relevant dirty paths change before correction or final
   verification, THEN the playbook MUST revalidate evidence. WHEN correction intent changes, the playbook MUST
   obtain a new decision. The playbook MUST preserve unrelated edits.
7. Completion MUST apply only to the declared batch. The report MUST record reviewed/excluded candidates, gaps,
   detected, resolved, deferred, waived and pending counts, provenance, verification and follow-ups. A zero-finding
   completion MUST still carry coverage evidence. A completed review MAY contain explicit gaps/deferrals/waivers.
   IF any decision is pending, THEN the playbook MUST NOT claim the batch fully reconciled. The playbook MUST NOT
   claim whole-repository consistency from a batch.

## 4. Report Interface

The artifact MUST be ordinary Markdown under the owning unit's materials, or the repository's existing materials
location without a unit. It MUST contain intake, coverage, findings, decisions, corrections and completion evidence.
Existing commands retain their own output contracts; the playbook MUST NOT present narrative semantic assessment as a
new checker result. Isolated seeded exercises MUST label simulated decisions. They MUST NOT authorize a real source
change.

## Maintenance history integration

WHERE `devkit maintenance history` is installed, the playbook MUST use the run identity and companion record of `CAP-DLV-maintenance-history`, starting after fixing the report path and finishing after report verification. Publication and amendments MUST retain separate explicit user authority. Without the command, this capability's local record procedure applies. The separate history backend belongs to `CAP-DLV-maintenance-history`.
