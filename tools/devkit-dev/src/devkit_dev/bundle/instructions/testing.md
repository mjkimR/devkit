---
name: testing
description: Read before authoring, moving or organizing workspace tests across unit, integration and e2e tiers.
---

# Testing tiers and boundaries

Workspace tests belong in each package's `tests/{unit,integration,e2e}/` tiers, with shared test helpers in
`tests/support/`. Only create the tiers a package actually needs. Deployed governance rule tests travel beside their
rule (`rules/<rule>/tests/`), and installed-wheel cross-package checks remain under `scripts/`.

Classify every test by its execution boundary and isolation level, not by whether the package is an application:

## 1. Unit Tests (`tests/unit/`)

- **Scope:** Pure domain logic, dataclass/model validations, parsing algorithms, lexical/fusion calculations, formatters,
  and isolated in-memory transformations.
- **Boundaries:**
  - **Zero disk I/O, zero Git binaries, zero subprocesses, and zero network calls.**
  - Tests run entirely in-memory using pure Python objects, in-memory mocks, or test doubles.
  - Fast execution: hundreds of tests must complete in 1–2 seconds without parallel worker overhead.
- **Examples:**
  - `devkit-core`: `test_frontmatter.py` (markdown frontmatter parsing), `test_usecase.py` (base usecase contract).
  - `devkit-dist`: `test_lexical.py`, `test_fusion.py` (search score algorithms), `test_config_template.py`.
  - `devkit`: `test_scan.py` (compact output text regex matching), `test_evaluator.py` (in-memory rule engine).
  - `devkit-spec`: `test_parse.py` (document AST/markdown parsing), `test_status.py` (proposal lifecycle states).

## 2. Integration Tests (`tests/integration/`)

- **Scope:** In-process collaboration between layers (UseCase + Service + Repository + Transport Adapter) within or
  across features.
- **Boundaries:**
  - **Single in-process Python execution.**
  - May interact with the real local filesystem using `tmp_path` (e.g. reading/writing config files, receipts, envelopes).
  - May invoke CLI command handlers through `click.testing.CliRunner().invoke()`.
  - **MUST NOT spawn out-of-process subprocesses (`subprocess.run`), run OS Git hooks, or invoke external Python
    interpreters.**
  - If Git operations are needed, keep them confined to minimal, lightweight in-process commands rather than full repository
    lifecycles.
- **Examples:**
  - Verifying a Repository persists and retrieves receipts or configuration from `tmp_path`.
  - Testing that a UseCase orchestrates services and returns structured output dictionaries or notices.
  - Testing in-process CLI option parsing and error boundary formatting via `CliRunner`.
  - Testing workflow envelope creation, state transitions, and frontmatter updates on disk.

## 3. End-to-End Tests (`tests/e2e/`)

- **Scope:** Out-of-process execution, operating system environment interactions, Git hooks, multi-interpreter dispatch,
  and full user/agent lifecycles across subsystems.
- **Boundaries:**
  - **Spawns independent subprocesses** (`subprocess.run(["devkit", ...])`, `python -m ...`).
  - **Exercises OS Git Hooks** (e.g. `.git/hooks/commit-msg` executing via a separate interpreter process during `git commit`).
  - **Full multi-branch worktree lifecycles** (locate -> start -> sync -> merge/rebase -> conflict resolution -> gate run).
  - **End-to-end SDD workflows** (`devkit spec new` -> template scaffold -> governance rules audit -> workflow binding).
  - **MCP protocol & client confirmation** (native plan accept, handoff, JSON-RPC communication).
- **Examples:**
  - `devkit`: `test_hooks.py` (real Git commit triggers Python commit-msg hook), `test_lifecycle.py` (real worktree sync & lock).
  - `devkit-spec`: `test_plan_accept_mcp.py` (MCP acceptance with real Git branches), `test_integration.py` (native handoff),
    `test_spec_new.py` (full proposal creation and rule check).
  - `devkit-dist`: `test_standalone.py` (subprocess execution verifying lazy-loading in fresh Python process).

---

# Directory layout and conventions

- **Mirroring:** Under each tier (`unit`, `integration`, `e2e`), directory structure SHOULD mirror source package
  ownership (e.g. `tests/{unit,integration,e2e}/features/<feature>/`, `tests/integration/package/`, `tests/unit/core/`).
  Do not create empty category directories.
- **Shared Helpers:** Package-specific test fixtures and utilities belong in that package's `tests/support/`
  (e.g. `packages/devkit-spec/tests/support/spec_support/`). Reusable helpers shared across packages may reside in
  `devkit_dev.testing` when a concrete cross-package need arises.
- **Rule Tests:** A governance rule's tests remain embedded beside the rule in `rules/<rule>/tests/test_rule.py`.

---

# Developer loop and test execution

- **Fast development feedback (`just test-affected`):** Selects affected Unit and Integration tests by default from
  the git diff against base. Heavy E2E tests are excluded unless an E2E test itself was modified or `--e2e` is passed.
- **E2E verification (`just test-e2e [module]` or `just test-affected --e2e`):** Runs the heavy out-of-process E2E suites
  when validating end-to-end flows, before integration approval or in CI.
- **Full test suite (`just test [module]`):** Runs all test tiers across the workspace with parallel xdist execution.

