---
id: ADR-autonomy-between-approval-gates
title: Agent autonomy between explicit human decision points
summary: "Concentrates human intervention at defined approval and review points and makes autonomous execution and recovery the default within approved scope. Helper tools provide actionable evidence without introducing incidental human gates."
status: accepted
created_at: 2026-10-20
---

# [ADR-autonomy-between-approval-gates] Agent autonomy between explicit human decision points

- **Status**: Accepted
- **Date**: 2026-10-20
- **Deciders**: Repository owner
- **Involved Capabilities**: `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`

## 1. Context & Problem Statement

The delivery workflow concentrates intent, direction and integration decisions at explicit gates. Native MCP
approval surfaces make those decisions concrete and reviewable. Existing guidance already assigns implementation
choices inside agreed intent to the agent, but leaves the implication for helper commands and routine failures
implicit. Treating every validation finding or failed command as a new human decision undermines autonomous work
and makes users coordinate execution details.

## 2. Decision Drivers

- Human attention belongs at defined approval and review points and at problems that need human judgment or authority.
- Agents need actionable results and actual partial state to choose and execute follow-up work.
- Required checks, reviews, delegated boundaries and host permissions remain effective.

## 3. Considered Options

1. **Autonomous execution within approved scope (selected)**: use existing decision points, let agents resolve
   routine findings and failures, and design helper tools to support that work. Requires clear result reporting and
   escalation boundaries.
2. **Additional confirmations for execution details**: ask before corrective actions or result acceptance. Adds
   human coordination without necessarily improving the evidence at existing gates.

## 4. Decision Outcome

Human intervention is concentrated at the workflow's defined approval and human review points. Within agreed
intent and existing authority, agents SHOULD choose implementation details, execute commands, inspect failures,
correct defects, revalidate and retry autonomously. A routine negative result alone does not require user input.
Automated checks and agent reviews remain execution work; they do not by themselves create a human review point.

Helper commands and validation procedures MUST NOT introduce a human approval or acknowledgment solely to process
routine findings. They SHOULD report completed work, failures or unknown outcomes, stable codes and deterministic
next actions so the responsible agent can continue. A required check may still prevent an invalid transition;
the agent resolves its cause within scope rather than asking the user to manage each step. This principle does
not require an automatic retry engine or background recovery service.

Escalate when a defined human decision is due, agreed goal/scope/contract must change, necessary authority is
missing, an existing explicit stop rule applies, or the responsible agent cannot resolve the problem within the
agreement. In local orchestration, a worker reports to the Host/main agent; that agent resolves matters within its
authority and brings only necessary decisions to the user. Preserve and report actual partial state.

This decision grants no new commit, merge, publication or deletion authority and does not bypass an approval
refusal, sandbox restriction, required check/review, bounded review-loop stop or delegated write boundary.
`ADR-integration-approval-asserted` and effective `CAP-DLV-project-policy` remain in force. Reuse authorization
already given for its approved scope; do not ask again for the same authorized action merely because a helper step
or recoverable failure intervened. An action outside that scope still requires its own authority.

## 5. Consequences

- Agents complete routine execution and recovery without repeated human confirmations.
- Helper-tool design favors concise actionable evidence over incidental human gates.
- Agents must distinguish safe recovery within authority from a changed scope or unresolved outcome; unknown
  outcomes remain unknown until inspected and cannot justify destructive follow-up work.
- Existing required checks and explicit review stops remain; this decision adds no new gate, exception stage or
  approval mechanism. The detailed principle remains in this ADR; Planning discovers applicable decisions through
  the existing ADR search step without adding per-decision references to the constitution.
