---
id: TASKS-adaptive-package-extraction
spec: SPEC-adaptive-package-extraction
plan: PLAN-adaptive-package-extraction
---
<!-- devkit:skeleton -->

# Task Breakdown: `SPEC-adaptive-package-extraction` Extract adaptive development into a devkit-adaptive distribution

## Phase 1: Implementation
- [ ] **Task 1.1**: Core Implementation
  - **_Boundary**: packages/, packages/devkit-catalog/src/devkit_catalog/adaptive_dev/, packages/devkit-catalog/pyproject.toml, packages/devkit-catalog/README.md, packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py, packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev_documents.py, packages/devkit-catalog/tests/integration/bundles/test_adaptive_import.py, packages/devkit-catalog/tests/integration/bundles/test_adaptive_behavior_scorer.py, packages/devkit-catalog/tests/integration/bundles/test_deep_research.py, packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/, packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py, tools/devkit-dev/tests/integration/test_bundle_citations.py, tests/e2e/smoke.sh, scripts/_lib.sh, scripts/releases/prepare.py, packages/devkit/tests/integration/package/test_selective_releases.py, pyproject.toml, uv.lock, .devkit/architecture.toml, .github/workflows/ci.yml, AGENTS.md, README.md, guides/INSTALL_GUIDE.md, guides/install/, docs/capabilities/delivery/CAP-DLV-adaptive-development.md, docs/capabilities/harness/CAP-HARN-agent-guidance.md, docs/usecases/delivery/UC-advance-an-idea.md, docs/usecases/delivery/UC-import-third-party-agent-assets.md, docs/architecture/ARCH-05-1-containers.md, docs/architecture/ARCH-05-2-components.md, docs/architecture/ARCH-07-deployment.md, docs/decisions/2026-11/20261102-adaptive-development-and-research.md, docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06, AC-07, AC-08_
  - **Verification**: <command that verifies the task>
