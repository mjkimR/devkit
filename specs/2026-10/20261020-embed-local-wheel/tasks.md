---
id: TASKS-embed-local-wheel
spec: SPEC-embed-local-wheel
plan: PLAN-embed-local-wheel
---

# Task Breakdown: `SPEC-embed-local-wheel` Commit devkit-embed Wheel to Repository

- [ ] **Task 1**: Commit prebuilt wheel and configure local path sources in pyproject.toml and uv.lock
  - **_Boundary**: `models/devkit-embed/wheels/devkit_embed-0.1.0-py3-none-any.whl`, `packages/devkit-dist/pyproject.toml`, `pyproject.toml`, `uv.lock`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `unshare -r -n uv run python -c "import devkit_embed; print(devkit_embed.__file__)"`

- [ ] **Task 2**: Update workspace helper scripts to resolve local model wheel
  - **_Boundary**: `scripts/_lib.sh`, `scripts/smoke.sh`, `scripts/release.sh`
  - _Requirements: AC-04_
  - **Verification**: `just smoke`

- [ ] **Task 3**: Update Living Spec documents, README, and resolve source feedback
  - **_Boundary**: `docs/capabilities/search/CAP-SRCH-document-search.md`, `README.md`, `specs/2026-10/20261020-local-config-execution-environment/feedback/planning-context-command-can-trigger-unavailable-sync.md`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit rules check`
