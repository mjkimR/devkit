---
id: FB-smoke-response-style-skill-path
title: Consumer smoke still checks the response-style instruction path after the bundle moved to a skill
scope: repo
kind: friction
category: docs-mismatch
target: scripts/smoke.sh (just smoke, response-style section)
skill: spec-review
agent: claude-code
origin: agent
severity: blocked
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-smoke-response-style-skill-path] Consumer smoke still checks the response-style instruction path after the bundle moved to a skill

## 1. Friction / Question (friction, question)

- **Context**: Verifying `SPEC-advisory-unique-code`; `AGENTS.md` lists `just smoke` as the consumer smoke for
  packaging, CLI wiring and hooks.
- **Expectation**: `just smoke` passes on the base branch, so a failure points at the change under test.
- **Actual**: `just smoke` fails on the base commit `8fc64ef` and on the task branch alike, at the response-style
  step: the script reads `.devkit/managed/response-style/instructions/response-style.md`, but since the response-style
  bundle deploys a templated skill the managed copy holds `bundle.toml`, `guidance/` and `skills/` only.
- **Workaround (or Interpretation Chosen)**: Ran `just smoke` on the base checkout to show the failure is
  pre-existing, reported it as unrelated, and relied on the other checks.
- **Suggestion**: Point the smoke assertions at the rendered skill
  (`.devkit/managed/response-style/skills/response-style/SKILL.md`) and its projection, matching the bundle's current
  assets.

## Diagnostic Details

- **Reproduction**: `just smoke` in a clean checkout of `8fc64ef`.
- **Expected / Actual**: exit 0 / `FileNotFoundError` for `.devkit/managed/response-style/instructions/response-style.md`,
  recipe `smoke` failed with exit code 1.
- **Versions**: base commit `8fc64ef` (feat: Introduce templated response-style skill deployment).
- **Conditions**: macOS host; the failure is independent of this spec's diff.
- **Workarounds Attempted**: none beyond confirming on the base checkout.
- **Related Assets**: `scripts/smoke.sh` (response-style block after `devkit add response-style`), the
  `response-style` bundle in `devkit-catalog`.

## Evidence

```text
scripts/smoke.sh:
    path = Path(".devkit/managed/response-style/instructions/response-style.md")
    assert "Use ko as the default" in path.read_text()
just smoke (base and branch):
    FileNotFoundError: [Errno 2] No such file or directory: '.devkit/managed/response-style/instructions/response-style.md'
    error: recipe `smoke` failed on line 62 with exit code 1
<worktree>/.devkit/managed/response-style/: bundle.toml  guidance/  skills/
```

- **Disposition**: scripts/smoke.sh (commit c05b3c5): the smoke now checks the rendered response-style skill and its AGENTS.md pointer instead of the removed instruction path.
