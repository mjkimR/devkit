---
id: PLAN-embed-local-wheel
spec: SPEC-embed-local-wheel
---

# Technical Plan: `SPEC-embed-local-wheel` Commit devkit-embed Wheel to Repository

## 1. Architecture Overview & Invariant Review

The `devkit.search` capability provides dense and hybrid retrieval using `numpy`, `tokenizers`, and `devkit-embed` (`CAP-SRCH-document-search`). Previously, `packages/devkit-dist/pyproject.toml` referenced `devkit-embed` via a GitHub release asset URL in `[tool.uv.sources]`.

This plan replaces the remote URL source with a local file path pointing to a repository-committed wheel at `models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl`.

### Invariants & Boundaries
- Layering and workspace rules: `models/devkit-embed` remains outside the uv workspace members list (`packages/*`, `tools/*`); `devkit-dist` continues to consume it as an optional extra (`search`) via its prebuilt wheel.
- Clean offline execution: Running `uv run` inside a network-isolated environment must never trigger DNS lookups or HTTP requests.

## 2. Component Breakdown & Impact

### 1) Committed Artifact
- `models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl`:
  - 14,277,264 bytes, SHA-256 `2b8534b60d85e36c2027e2c0d13d110289fa877b9c0b2639b8c4daedbe461f38`.
  - Added to Git tracking (verifying `.gitignore` does not exclude `models/**/wheels/`).

### 2) Dependency Configuration
- `packages/devkit-dist/pyproject.toml`:
  - Change `[tool.uv.sources.devkit-embed]` from `{ url = "https://..." }` to `{ path = "../../models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl" }`.
- Root `pyproject.toml`:
  - Add `devkit-embed = { path = "models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl" }` to `[tool.uv.sources]`.
- `uv.lock`:
  - Regenerate via `uv lock` so lockfile records the local path source and its hash.

### 3) Workspace Scripts
- `scripts/_lib.sh`:
  - Replace `model_wheel_url()` with `model_wheel_path()` that returns the path to `models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl`.
- `scripts/smoke.sh` and `scripts/release.sh`:
  - Update consumer installation steps to use `model_wheel_path()` instead of `model_wheel_url()`.

### 4) Documentation & Living Spec
- `docs/capabilities/search/CAP-SRCH-document-search.md`:
  - Update packaging section to document that the wheel is committed under `models/devkit-embed/wheels/` and resolved via local path.
- `README.md`:
  - Update installation examples that reference the release URL.
- `FB-planning-context-command-can-trigger-unavailable-sync.md`:
  - Mark status as `resolved` with disposition documenting the committed wheel resolution.

## 3. Failure Modes & Rollback

- **Path Resolution in Worktrees**: In Git worktrees (e.g., `devkit-wt-...`), relative paths like `models/devkit-embed/wheels/...` and `../../models/devkit-embed/wheels/...` resolve within the worktree checkout correctly because all tracked files exist in the worktree.
- **Rollback**: If reverted, restoring the URL in `pyproject.toml` and re-locking returns the repository to the previous release-wheel URL.

## 4. Verification & Test Plan

1. **Offline Resolution**:
   - `unshare -r -n uv run python -c "import devkit_embed; print(devkit_embed.__file__)"` must pass without network access.
2. **Package & Dist Checks**:
   - `just check` (Pyright static analysis)
   - `just lint-check` (Ruff formatting and lint)
   - `just test-dist` (devkit-dist standalone environment)
3. **Consumer Smoke**:
   - `just smoke` to verify full consumer packaging and dense search retrieval.
