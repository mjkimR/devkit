---
id: PLAN-affected-frontend
spec: SPEC-affected-frontend
---

# Technical Plan: `SPEC-affected-frontend` Frontend changes in affected test selection

## 1. Constitution & Invariant Review

None. The change extends the selection rules of `scripts/affected_tests.py` and their description; the new stdout
line is a one-line sentinel result like the existing `[TEST_SELECTION: ...]` and `[TEST_PATH: ...]` lines, and no
advisory code changes (`CAP-ADV-agent-advisory-protocol`).

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `scripts/affected_tests.py`: `FRONTEND_PREFIXES` and `FRONTEND_CHECK`; `Selection.frontend`; the rule in
    `select()`; the extra line in `main()`.
  - `packages/devkit/tests/test_affected_tests.py`: AC-01 to AC-06.
  - `docs/development/ci-cd.md` §2 and `AGENTS.md` Verification: AC-07.
- **New Dependencies**: None.

## 3. Component & Interface Design

```python
FRONTEND_PREFIXES = ("packages/devkit-viewer/frontend/", "scripts/viewer.sh")
FRONTEND_CHECK = "just viewer install && just viewer lint && just viewer check && just viewer test && just viewer pack && just viewer build"

@dataclass(frozen=True)
class Selection:
    mode: Literal["full", "partial", "none"]
    paths: tuple[str, ...]
    reason: str
    frontend: bool = False  # a frontend path changed: print the frontend line
```

- `select()` computes `frontend` from all changed paths before the full-trigger scan, so a `full` selection carries it
  too (AC-03). In the per-path loop a frontend path adds the cause `frontend` and nothing else, ahead of the
  untested/unmapped fallback (AC-01, AC-04). With no path kept, the reason is `frontend` when a frontend path changed,
  else `untested`.
- `main()` prints `[FRONTEND_CHECK: <FRONTEND_CHECK>]` right after the selection line when `selection.frontend`, then
  the `[TEST_PATH: ...]` lines under `--list`, then hands over or exits as before (AC-02, AC-05).
- The rebuilt page under `src/devkit_viewer/static/` stays a package source change of `devkit_viewer` (AC-06).

## 4. Verification & Test Plan

- **Unit**: `select()` cases for AC-01 to AC-06 against the real tree; the command through `CliRunner` for the line
  order of AC-01 and AC-02 and the absence of the line (AC-05).
- **Manual**: `just test-affected --list` on this branch (no frontend change), and `select()` probes for a frontend
  file, `scripts/viewer.sh` and a mixed change.
- **Checks**: `just test-affected` during development, `just lint-check`, `just check`, `just rules-check`, the full
  `just test` once before integration.
