---
id: ADR-opt-in-maintenance-history
title: Explicit opt-in maintenance history composition
summary: "For maintenance playbooks, we keep history as an explicitly requested companion workflow, to preserve independent default execution, accepting separate composition steps."
status: accepted
created_at: 2026-11-04
supersedes: [ADR-history-branch-publication]
---

# [ADR-opt-in-maintenance-history] Explicit opt-in maintenance history composition

- **Status**: Accepted
- **Date**: 2026-11-04
- **Deciders**: repository owner
- **Involved Components/Capabilities**: `CAP-DLV-maintenance-history`, maintenance catalog playbooks

## 1. Context & Problem Statement

History commands are useful independently of maintenance playbooks. Command installation must not change a playbook's report handling or completion criteria. `ADR-history-branch-publication` section 4 first clause broadly says each maintenance run publishes; its root and publication decisions do not require default lifecycle integration.

## 2. Decision Drivers

- Driver 1: default maintenance execution remains independent of installed history commands.
- Driver 2: users can explicitly compose durable history without changing publication authority or immutable evidence.

## 3. Considered Options

### Option 1: Standalone explicit composition (Selected)

Keep the default playbooks unchanged and put optional history steps in a separate reference. This preserves Driver 1 and requires deliberate composition for Driver 2.

### Option 2: Availability-guarded lifecycle commands

Automatically start and finish history when commands are installed. This reduces composition work but changes default playbook behavior and report lifecycle, failing Driver 1.

## 4. Decision Outcome

We selected Option 1.

- History commands run only after the user explicitly requests a companion history run; installation or playbook invocation alone never opts in or triggers a recurring offer. → `CAP-DLV-maintenance-history` rule 13 (MUST).
- Default playbooks retain their report, outcome and completion procedures independently of history availability. → `CAP-DLV-maintenance-history` rule 14 (MUST).
- Frozen evidence and append-only integration amendments apply only to the selected history run. → `CAP-DLV-maintenance-history` rules 3, 10 and 14 (MUST).
- This decision supersedes only the blanket applicability of section 4 first clause in `ADR-history-branch-publication`: its publication semantics apply to explicitly selected history runs. All other branch, root, publication, authority and identity decisions remain in force.

## 5. Consequences

- **Positive**: installing history does not alter maintenance execution; explicit composition retains the standalone feature.
- **Negative / Risks**: agents must read the separate reference when a user chooses history.
- **Follow-ups**: reconsider default composition only after an explicit user request to change that policy.

## 6. Confirmation

`packages/devkit-catalog/tests/integration/bundles/test_maintenance_history.py` verifies the four default playbooks contain no history lifecycle commands or availability probes and preserve local outcome handling. `UC-record-a-maintenance-run` states the explicit request precondition. Review checks the separate composition reference and absence of recurring offers; standalone command tests enforce the frozen evidence and publication contracts.
