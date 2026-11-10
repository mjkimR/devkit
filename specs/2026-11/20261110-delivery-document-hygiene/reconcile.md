---
reconcile_id: REC-delivery-document-hygiene
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-roles.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-document-id-aliases.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-orchestration-workers.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-proposal-handoff.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-ux-screens.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-namespace-milestone-roots.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-partial-supersession-statements.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
---

# Living Spec reconciliation

The four delivery capabilities partition existing contracts; preservation-map.md and relocated-sections.json
account for every moved block and the retained core policy. All original H2/H3 portal headings survive for
fragment compatibility. New capabilities use three existing doorway entrypoints each.

Other capability, use-case and accepted-decision edits redirect only current contract ownership/section traces
and symmetric backlinks. Decision outcomes, statuses and aliases keep their meaning. The Development use case
retains every scenario body and corrects the repeated Scenario 32 number. No domain concept, screen, runtime,
agent asset, dependency or feature edge changed.

The distribution reference removes a duplicated engine/search configuration sample, retains a practical
selection example and its unique diagnostics/public snapshot subset, and links canonical configuration detail.
The baseline line-budget warning remains justified at 414 lines; no rule or threshold changes here.

No required work is deferred. Deliberately retained sync/ADR/history detail is outside this editorial scope,
not an unmet acceptance criterion. There is no linked source feedback to resolve. Host owns landed verification.
