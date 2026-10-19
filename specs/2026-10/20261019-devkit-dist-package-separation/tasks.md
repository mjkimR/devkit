---
id: TASKS-devkit-dist-package-separation
spec: SPEC-devkit-dist-package-separation
plan: PLAN-devkit-dist-package-separation
---

# Task Breakdown: `SPEC-devkit-dist-package-separation` Separate asset distribution into independent devkit-dist package

## Phase 1: Package split

- [ ] **Task 1.1**: Create `packages/devkit-dist`, move `core`, `search`, `host`, `distribution`, `advisory_guide`,
  `commits_guide`, `cli.py` and `__main__.py` with their tests, one `py.typed` per area, both `pyproject.toml` files,
  root workspace configuration and `uv.lock`; `distsupport` for the dist test helpers
  - **_Boundary**: packages/devkit-dist/, packages/devkit/pyproject.toml, packages/devkit/src/devkit/,
    packages/devkit/tests/, pyproject.toml, uv.lock
  - _Requirements: AC-08, AC-15_
  - **Verification**: `just test`
- [ ] **Task 1.2**: Root command line in `devkit-dist` with only its own commands, the name-only harness list and
  `HARNESS_COMMAND_UNAVAILABLE`, `--version` from `devkit-dist`; `devkit-agt` mounts its seven commands through
  `devkit.commands` and declares no console script
  - **_Boundary**: packages/devkit-dist/src/devkit/cli.py, packages/devkit-dist/src/devkit/core/errors.py,
    packages/devkit-dist/tests/, packages/devkit/pyproject.toml, packages/devkit/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
- [ ] **Task 1.3**: Per-wheel layering tests: the `devkit-dist` test scanning every module (top-level files, string
  constants, entry points) for `devkit-agt` areas; the `devkit-agt` test with both wheels' group map and the name-only
  list equality
  - **_Boundary**: packages/devkit-dist/tests/test_layering.py, packages/devkit/tests/test_layering.py,
    packages/devkit/tests/test_cli_imports.py
  - _Requirements: AC-13_

## Phase 2: Ownership of formats and bundles

- [ ] **Task 2.1**: Configuration template tables of the harness through `devkit.config_tables` (workflow and worktree
  templates in `devkit-agt`), reserved names kept; receipt `tool.package = "devkit-dist"`, two-sided
  `TOOL_VERSION_CHANGED`; both wheels' bundles built in
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/installation/, packages/devkit-dist/tests/distribution/,
    packages/devkit/src/devkit/workflow/project/config.py, packages/devkit/src/devkit/worktree/config.py,
    packages/devkit/pyproject.toml, packages/devkit/tests/
  - _Requirements: AC-08, AC-10, AC-11_
- [ ] **Task 2.2**: New `harness` bundle (`devkit.harness_guide`) with the moved harness and `devkit run` guidance; the
  `devkit` bundle keeps only distribution guidance and preset `core`; bundle tests on both sides, override of a moved
  asset
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/guide/, packages/devkit-dist/src/devkit/advisory_guide/,
    packages/devkit-dist/tests/distribution/, packages/devkit/src/devkit/harness_guide/, packages/devkit/tests/,
    packages/devkit/pyproject.toml, packages/devkit-spec/src/devkit_spec/bundle/
  - _Requirements: AC-05, AC-07, AC-09, AC-17_
- [ ] **Task 2.3**: `HARNESS_ENGINE_MISSING` notice in `devkit sync` and `devkit status`, detected by `devkit.commands`
  entry point names
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/tests/distribution/,
    packages/devkit/tests/
  - _Requirements: AC-06_
- [ ] **Task 2.4**: Missing-extra directives naming the requirement the project declares
  - **_Boundary**: packages/devkit-dist/src/devkit/search/, packages/devkit-dist/src/devkit/host/,
    packages/devkit-dist/src/devkit/distribution/cli/, packages/devkit-dist/tests/
  - _Requirements: AC-12_

## Phase 3: Wiring and verification

- [ ] **Task 3.1**: Dist-only test environment (`scripts/dist_only.sh`, `just test-dist`) and its CI step;
  standalone-only tests
  - **_Boundary**: scripts/, justfile, .github/workflows/ci.yml, packages/devkit-dist/tests/
  - _Requirements: AC-14_
- [ ] **Task 3.2**: Lockstep release and consumer smoke: `scripts/release.sh`, `scripts/smoke.sh`, `scripts/_lib.sh`,
  lockstep pin test, `devkit-catalog` and `devkit-starter` development dependency
  - **_Boundary**: scripts/, packages/devkit/tests/test_advisory_pin.py, packages/devkit-catalog/pyproject.toml,
    packages/devkit-starter/pyproject.toml, packages/devkit-advisory/, uv.lock
  - _Requirements: AC-15, AC-16_
- [ ] **Task 3.3**: Guides, package READMEs, root README and AGENTS.md, the code reference rows the new codes need,
  and this repository's receipt and `AGENTS.md` block rewritten by `devkit sync`
  - **_Boundary**: guides/, packages/devkit/README.md, packages/devkit-dist/README.md, packages/devkit-advisory/README.md,
    packages/devkit-spec/README.md, packages/devkit-catalog/README.md, packages/devkit-starter/README.md, README.md,
    AGENTS.md, docs/development/, .devkit/installation.json
  - _Requirements: AC-05, AC-07, AC-12_
