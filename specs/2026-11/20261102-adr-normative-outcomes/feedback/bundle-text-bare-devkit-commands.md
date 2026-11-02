---
id: FB-bundle-text-bare-devkit-commands
title: Bundle bodies name bare devkit commands while the documented agent form is uv run devkit
scope: repo
kind: question
category: instruction-conflict
target: CAP-DIST-context-and-playbooks
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-11-02
---

# [FB-bundle-text-bare-devkit-commands] Bundle bodies name bare devkit commands while the documented agent form is uv run devkit

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-adr-normative-outcomes` restated `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` in
  `CAP-DIST-context-and-playbooks`: the documented agent-facing form MUST be `uv run devkit`.
- **Expectation**: Documented agent-facing commands use `uv run devkit`.
- **Actual**: Skill and reference bodies name bare `devkit ...` commands. Only the spec constitution tells agents to
  run them in the project's documented form.
- **Workaround (or Interpretation Chosen)**: The capability rule covers advisory fixes and output literals, which
  `test_agent_output_contract.py` enforces. It does not claim that bundle prose already complies.
- **Suggestion**: Decide whether bundle prose counts as "documented" under the rule. If it does, either rewrite the
  commands or state the constitution's translation rule in the capability.

## Diagnostic Details

- **Reproduction**: `rg -n '`devkit ' packages/*/src/**/bundle/skills`.
- **Expected / Actual**: Expected `uv run devkit`; observed bare `devkit` in many skill bodies.
- **Versions**: base `fceda9d2`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: none.
- **Related Assets**: the spec bundle constitution (`AGENTS.md.jinja`), `spec-integrate` skill.

## Evidence

```text
spec bundle constitution: "Run a bare `devkit ...` command from bundle text or skills in the project's documented form
(`uv run devkit ...`)."
```

- **Disposition**: `SPEC-retire-stale-integration-clauses`: dismissed by user decision. `CAP-DIST-context-and-playbooks` scopes the `uv run devkit` rule to output-suggested invocations, and the spec bundle's constitution runs bare commands from bundle prose in the documented form, so rewriting bundle prose adds text without changing behavior.
