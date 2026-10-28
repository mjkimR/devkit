---
reconcile_id: REC-incubation-sdd-baseline
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md
    resolution: modified
  - file: docs/usecases/delivery/UC-adopt-sdd-from-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/harness/UC-adopt-in-an-existing-repository.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-adopt-sdd-through-an-evidenced-baseline-playbook.md
    resolution: modified
---

# Reconciliation

The baseline capability and actor use case describe the explicit playbook, actual evidence threshold and exact-effects
activation. Harness inventory and existing-repository adoption distinguish this path from legacy debt containment.
The accepted ADR has wording/provider-effect clarification only, without changing its chosen design.

Package README and the focused installation guide explain staging assets while incubation remains active, preserving
an existing spec provider and explicitly authorizing a necessary project-to-spec switch.
`CAP-DLV-drift-reconciliation` is unchanged: evidence practices are reused without changing its maintenance entry.
`CAP-DLV-project-policy` is unchanged: its implemented setting and runtime contract are consumed, not redefined.

The source includes separately reviewed prerequisite policy and stacked guidance assets. Baseline review covers its
own entire feature, not a new review of those prerequisite implementations. Guidance final integration still precedes
Host baseline integration. Actual commands and simulated decisions are distinguished in materials/scenario-evidence.md.

No concrete baseline requirement is deferred to another feature. Full milestone closure remains a Host/user decision
after all three integrated results are compared with MS-idea-incubation.

## Entrypoint review

Keep the existing exact sdd-baseline/SKILL.md doorway for the new capability and actor use case.
Reject receipt, broad package/guides directories and test files from derived candidates: they do not start this
behavior. Existing harness/adoption entrypoints remain valid; their changes are inventory and routing references.

## Verification boundary

The final policy snapshot is present; eight real CLI/app scenario/asset checks passed, plus twelve affected
document checks and the use-case parser regression. Source/scenario evidence is labelled synthetic product inputs
and simulated user decisions. Autonomous product-scope inference is not claimed. Guidance final source/main
incorporation and sequential integration remain the Host's next verification boundary.

The focused installation guide follows canonical package-source replacement in the consumer's actual group/source/ref,
retains optional catalog, prevents a duplicate direct base requirement and checks the required PyYAML binary binding.
It deliberately does not prescribe a universal remove command or silently alter another dependency group.
