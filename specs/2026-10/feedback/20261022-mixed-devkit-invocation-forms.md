---
id: FB-mixed-devkit-invocation-forms
title: Bundle text mixes uv run devkit and bare devkit
scope: repo
kind: suggestion
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-mixed-devkit-invocation-forms] Bundle text mixes uv run devkit and bare devkit

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: Agent-facing bundle text names devkit commands two ways. The managed `AGENTS.md` block,
  the `devkit-workflow` entry skill and the `devkit` and `harness` bundle instructions write `uv run devkit ...`;
  the `spec` bundle skills, references and subagent contracts mostly write bare `devkit ...` (about 267 mentions),
  sometimes in the same file (`scout.md` line 33 uses both).
- **Proposed Procedure**: State once, in the guidance every agent reads first, that a bare `devkit ...` in bundle
  text means the project's documented form (`uv run devkit ...`), or normalize the frequent entry points to one
  form. Keep the prose short; do not rewrite every mention.
- **Expected Benefit**: An agent whose shell has no `devkit` on `PATH` stops guessing whether a bare command is
  meant literally; fewer failed first calls.
- **Cost & Risk**: A blanket rewrite adds about 9 characters to hundreds of lines read every session; a single
  convention line costs one line.
- **Attempted**: Hypothesis. In this run the bare form was not runnable; `uv run devkit` was used throughout.

## Diagnostic Details

- **Reproduction**: In the Planning worktree shell, `which devkit` printed `devkit not found`; `uv run devkit ...`
  worked.
- **Expected / Actual**: Expected one invocation form across bundle text; found two.
- **Versions**: Worktree revision 6f0d4600; uv 0.12.8.
- **Conditions**: Claude Code planning worker; the shell inherited `VIRTUAL_ENV` from another project.
- **Workarounds Attempted**: Prefixed every bare command with `uv run`; it worked.
- **Related Assets**: ~~`PROP-direct-devkit-invocation`~~ (`materials/invocation-forms.md`, Git `4672a101eec0`), `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`, the `spec` bundle skills.

## Evidence

```text
rg count of bare `devkit (spec|workflow|rules|get-context|run) ` in the spec bundle: 267
rg count of `uv run devkit` in bundle sources: about 56
which -a devkit -> devkit not found
VIRTUAL_ENV=<other project>/.venv
```
