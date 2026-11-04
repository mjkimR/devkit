---
id: FB-skill-local-role-authoring
title: Document skill-local role selection in shared authoring guidance
scope: repo
kind: suggestion
category: token-cost
target: packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md
origin: user
severity: noise
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-skill-local-role-authoring] Document skill-local role selection in shared authoring guidance

## 2. Suggestion / Change Request

- **Current Procedure**: Shared authoring guidance covers skill and playbook structure, but does not distinguish internal role instructions from globally registered subagents.
- **Proposed Procedure**: Include subagent authoring in the common instruction's applicability and state when a role belongs inside a skill. Link the criterion from the skill-authoring playbook when delegation is needed.
- **Expected Benefit**: Avoid exposing skill-only role metadata globally and avoid repeating the placement decision for every bundle.
- **Cost & Risk**: General guidance must preserve native role settings when they are needed; internal Markdown is no substitute for enforced tool or sandbox restrictions.
- **Attempted**: Applied skill-local roles to deep research; a general authoring-policy change remains outside this spec.

## Diagnostic Details

- **Reproduction**: Inspect the shared instruction and deep-research manifest before and after `SPEC-research-local-roles`.
- **Expected / Actual**: Role instructions can be packaged inside a skill, while the previous bundle registered four global subagents.
- **Versions**: devkit-catalog 0.1.5.
- **Conditions**: Explicit-only research skill with four optional role procedures.
- **Workarounds Attempted**: Moved role documents into the skill and verified supported-host distribution.
- **Related Assets**: Shared agent-asset-writing instruction and skill-authoring playbook.

## Evidence

The shared instruction's description names skills, playbooks and instructions, but not subagents. Its structure
section addresses conditional references without a role-registration criterion. The deep-research bundle now
selects only one skill asset and packages four role documents under its `roles/` directory; 112 affected tests pass.
