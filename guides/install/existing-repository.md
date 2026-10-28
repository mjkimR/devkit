# Route: Existing Repository

For a repository with code, build files, CI or agent configuration: analyze (read-only), present a plan, then
install with a dry run first. Entry point: [Installation Guide](../INSTALL_GUIDE.md).

## 1. Analyze (read-only)

Keep the evidence (file paths, command output) for the plan.

### Python environment

| Finding | Meaning |
| --- | --- |
| `pyproject.toml` and `uv.lock` | uv project: add devkit to its dev group. |
| `[tool.uv.workspace]` in the root `pyproject.toml` | uv workspace: add devkit at the root, never to a member. |
| `pyproject.toml` with `poetry.lock`, `pdm.lock`, `Pipfile` or only `requirements*.txt` | Another manager owns Python dependencies. Ask the user (see section 3). |
| No `pyproject.toml` | Non-Python or unmanaged: devkit gets its own minimal tooling manifest. |
| Several projects below the top level (a monorepo), or a request to install into a subdirectory | See [Monorepo or nested project](#monorepo-or-nested-project). |
| `requires-python` that allows versions below 3.12 (for example `>=3.10`) | `uv add` fails: devkit needs 3.12+. Ask the user (see section 3). |

### Agent configuration

- Which agents are in use: `AGENTS.md` (Codex, Antigravity and others), `CLAUDE.md` or `.claude/` (Claude Code),
  `.codex/` (Codex), `.agents/` (Codex and Antigravity skills). devkit projects for `codex`, `claude-code` and
  `antigravity`; other agents (Cursor, Copilot, Gemini CLI) can still read the `AGENTS.md` block.
- Existing skills and subagents under `.agents/skills/`, `.claude/skills/`, `.claude/agents/`, `.codex/agents/`:
  a bundle asset with the same name stops the sync with `SYNC_CONFLICT`.
- `AGENTS.md`: its size and whether it already has `DEVKIT` markers. A symlinked `AGENTS.md` needs a decision
  (`WORKSPACE_UNSAFE`).
- `CLAUDE.md`: whether it already has an `@AGENTS.md` import line. A Markdown link to `AGENTS.md` is not an import.

### Git hooks

```bash
git config --get core.hooksPath     # set by husky, lefthook and similar tools
ls "$(git rev-parse --git-common-dir)/hooks"
```

- `core.hooksPath` set: devkit leaves it alone and skips its hooks (`GATE_HOOK_INSTALL_SKIPPED`), so commit gates
  do not run; report it, do not change the setting.
- Existing executable hooks (for example from the `pre-commit` framework): devkit keeps running existing hooks before
  its gates; `uv run devkit gate status` shows the installed layout. Tell the user.
- A project that uses the `pre-commit` framework: each teammate runs `pre-commit install` and
  `uv run devkit sync --locked`, in either order. Do not run `pre-commit install -f` (it replaces devkit's dispatcher;
  `uv run devkit gate status` then reports `GATE_HOOK_ENTRY_MISSING`), and remove the hooks with
  `uv run devkit gate uninstall` before `pre-commit uninstall`.

### Verification and conventions

- Verification commands (`justfile`, `Makefile`, `package.json` scripts, `pyproject.toml`, `.github/workflows/`):
  note the fast ones as commit gate candidates.
- `.pre-commit-config.yaml`: list the checks its hooks run. Drop those from the gate candidates, because the existing
  hooks keep running on every commit and the gate would repeat them.
- Commit style: `git log --format=%s -n 50`; mostly `type(scope): subject` means Conventional Commits.
- Agent-authored content: `SKILL.md` files, playbooks, a long root `AGENTS.md` or `CLAUDE.md`.

## 2. Present the plan

Summarize for the user, then wait for approval:

- where devkit is added (`pyproject.toml` dev group, workspace root, or a new minimal manifest at the Git top level);
- target agents for `--agent`;
- what changes in `AGENTS.md` (a managed block appended at the end) and in Git hooks;
- conflicts or decisions found (other Python managers, `requires-python`, `core.hooksPath`, name clashes);
- recommended bundles from [Bundle Recommendations](bundle-recommendations.md), with evidence.

## 3. Decisions that belong to the user

Ask; do not choose for them:

- **Another Python manager**: adding devkit with uv writes `[dependency-groups]` and a `uv.lock` next to the existing
  lock. Offer that, or stop. Never migrate the project to uv on your own.
- **`requires-python` below 3.12**: devkit cannot be added to a project that supports older Python. Options: raise
  the floor to `>=3.12` (a project decision), or stop. Do not create a second project or virtual environment inside
  the repository as a workaround.
- **Commit gate commands**: the `verify-commands` gate runs its commands on every commit. Propose only fast commands
  that `.pre-commit-config.yaml` does not already run, and let the user choose. Put the approved ones in the tracked
  `.devkit/config.toml`:

  ```toml
  [gates.settings.verify-commands]
  commands = ["just lint-check", "uv run pytest -q tests/unit"]
  ```

  The commands run in order with `sh -c` from the Git top level. Call tools through `uv run` or a recipe runner,
  because Git hooks do not have `.venv/bin` on `PATH`.

## 4. Install

In a monorepo, or when asked to install into a subdirectory, first follow
[Monorepo or nested project](#monorepo-or-nested-project); it decides which `pyproject.toml` receives devkit.

No `pyproject.toml` yet (non-Python repository):

```bash
uv init --bare --python 3.12 --no-workspace --name <repository-name>
```

Then, for every route (the harness by default; `devkit-dist` instead only for a distribution-only installation, see
[Installation Guide, step 3](../INSTALL_GUIDE.md#step-3-package-sources)):

```bash
uv add --no-build-package pyyaml --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run python -c "import yaml; assert hasattr(yaml, 'CSafeLoader'), 'PyYAML LibYAML binding is unavailable'"
uv run devkit --version
uv run devkit sync --dry-run --agent <agent>     # plan only: check for SYNC_CONFLICT before any write
uv run devkit sync --agent <agent>
```

- Repeat `--agent` per agent, or omit it for all supported agents.
- Add `.venv/` to the root `.gitignore` when it is not ignored yet.
- On `SYNC_CONFLICT`, nothing was written; show the named paths and ask how to proceed.
- `CLAUDE.md`: when Claude Code is a target and `CLAUDE.md` has no `@AGENTS.md` line, offer to add that line. A
  Markdown link such as `[AGENTS.md](AGENTS.md)` does not import the file into Claude Code, so it does not count. Do
  not rewrite its other content.
- Ignore the native projections in the root `.gitignore` per projected directory, exactly as described in
  [New Repository, section 4](new-repository.md#4-ignore-the-native-projections).

## 5. First rules check

With `devkit-agt` installed (a distribution-only installation has no rules to check; skip to the bundle
recommendations):

```bash
uv run devkit rules check
```

The built-in rules may report findings in existing files. This runs the `linter` phase. Also run the `hygiene` phase
(for example `RULE-file-length`), which no commit gate runs:

```bash
uv run devkit rules check --phase hygiene
```

Report the counts by rule and phase to the user; do not fix them in bulk as part of the installation. The
`rules-check` commit gate refuses a commit that touches a file with an error-severity finding, so offer the choices:
fix the findings, park a rule in the `hygiene` phase or lower its severity in `[rules]`, or set `enabled = false` in
`[gates.settings.rules-check]` until they are resolved.

Then continue with [Bundle Recommendations](bundle-recommendations.md), optionally [MCP onboarding](mcp.md), and
[Installation Guide, step 5](../INSTALL_GUIDE.md#step-5-verify-and-report).

## Monorepo or nested project

devkit has one root per Git repository: the top level that `git rev-parse --show-toplevel` prints.

- devkit's files always live at the top level: `.devkit/`, the root `AGENTS.md`, the agent projections (`.claude/`,
  `.codex/`, `.agents/`), `specs/` and `docs/`, and the Git hooks. A `.devkit/` below the top level stops every command
  with `DEVKIT_ROOT_NESTED`.
- `uv run devkit` uses the environment of the nearest `pyproject.toml` at or above the current directory, and works
  only where that `pyproject.toml` declares devkit.

Install devkit into a root tooling manifest, so every agent and every teammate runs `uv run devkit ...` from the top
level:

1. If the top level has no `pyproject.toml`, create one there:

   ```bash
   uv init --bare --python 3.12 --no-workspace --name <repository-name>
   ```

2. Add devkit to the top-level `pyproject.toml` as a dev dependency, as in [section 4](#4-install). When the top
   level already has a `pyproject.toml` (a uv workspace root or the main project), add devkit there.

Do not add devkit to a subproject's `pyproject.toml`; it is not supported:

- `uv run devkit` from the top level does not find it, so the managed `AGENTS.md` block and every skill that calls
  `uv run devkit` fail there.
- The commit hooks record that subproject's interpreter path when they are installed, a machine-specific path the
  rest of the team does not have.

Repository-wide effects to present in the plan:

- Commit gates apply to the whole repository. `verify-commands` runs every configured command from the top level on
  every commit, whichever package the commit touches.
- With `devkit-spec`, give each package its own Living Spec under `docs/packages/<name>/` by registering it as a
  namespace in the tracked `.devkit/config.toml`, one table per package:

  ```toml
  [[tool.docs.namespaces]]
  name = "api"            # lowercase words joined by -, not "global"
  path = "services/api"   # the package's source directory, relative to the top level
  ```

  Document IDs and references stay repository-wide; `devkit docs list` and `devkit docs search` take
  `--namespace <name>` or `--all-namespaces`.

## Already installed

When `.devkit/` exists, do not reinstall. Diagnose and repair instead:

```bash
uv sync                          # install the locked packages
uv run devkit sync --locked      # restore ignored managed copies without changing committed files
uv run devkit status             # report problems
uv run devkit list               # bundles, their selection state and presets
```

- When the user asked for an upgrade, follow the upgrade commands in
  [Installation Guide, step 3](../INSTALL_GUIDE.md#step-3-package-sources).
- Bundle recommendations still apply: compare `devkit list` against
  [Bundle Recommendations](bundle-recommendations.md) and offer the missing ones.
- Optional: add or diagnose MCP registration with [MCP onboarding](mcp.md); until `devkit-mcp` is installed, sync
  registers nothing.

## Upgrading across the package split

`devkit-agt` releases from before `devkit-dist` existed shipped everything in one wheel. Upgrading from one changes
the following; check each with the user and commit the result together with `pyproject.toml` and `uv.lock`:

- **Packages**: a Git requirement on `devkit-agt` brings `devkit-dist` from the same commit; a release-wheel
  installation names the `devkit-dist`, `devkit-core` and `devkit-cli` wheels next to `devkit-agt` and `devkit-advisory`. A tool installation is
  `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`.
- **The `harness` bundle**: the first `uv run devkit sync` deploys the new auto-selected `harness` bundle (the rules,
  commit gates, workflows and `devkit run` guidance that left the `devkit` bundle), rewrites the `devkit` bundle's
  managed files and records `devkit-dist` as the receipt's tool. A project that opted out with `devkit = false` gets
  `harness` selected and opts out again with `harness = false`.
- **`devkit:run`**: the `run` preset moved to `harness`. A `devkit = ["core", "run"]` (or `"run"`) selection stops the
  sync with `SELECTION_INVALID` until it becomes `harness = "run"`; `devkit = "all"` keeps working but no longer
  deploys the `devkit run` guidance.
- **Overrides**: an override of `devkit:devkit-run` or `devkit:run-pointer` stops applying; re-create it with
  `uv run devkit override create harness:<asset>` and carry the edit over. An override of `devkit:consumption` or of
  the `devkit` constitution keeps applying with an upstream-drift report and still holds the old harness text:
  remove those sections from it (`uv run devkit override diff`, then `accept`).

## Cloud setup

For cloud execution, run `uv run devkit sync --cloud` and use CLI inspection and artifact commands. This saves the checkout-local execution setting and records the actual render environment in the receipt. Optional native-service onboarding is for local execution only; skip it in cloud setup. Cloud mutation still requires a separately authorized CLI/PR route.

`sync --no-save --cloud` renders cloud guidance and records its provenance without changing persisted runtime authorization. The next ordinary sync uses the saved/default environment; status/check reports the pending difference. `sync --local` restores local guidance. Locked sync refuses canonical environment changes; use ordinary sync and commit the resulting tracked output.

For document formats without SDD lifecycle obligations, choose devkit-docs instead of the base harness requirement.
It auto-selects docs:core. For SDD, devkit-spec additionally selects spec:core. The document skeleton is opt-in
through `uv run devkit add docs:docs-skeleton`; existing seeded files remain project-owned.

### Idea incubation entry

When the approved installation is for idea incubation, use devkit-docs plus devkit-catalog and explicitly select
`uv run devkit add incubation`. Configure shared `[development] approach = "incubation"` and inspect
`uv run devkit config show`; the optional independent integration provider is `project`. Follow
[the incubation setup](../INSTALL_GUIDE.md#idea-incubation) for the complete configuration.

Start or resume with `/incubate`. It reuses available answers, implements the next useful flow and verifies actual
usage; the optional clarification/research/usage roles do not create a mandatory sequence. The coordinator keeps
current facts in project-owned `.devkit/incubation.md`, which sync preserves. Asset selection alone changes no
approach, and incubation does not require eventual graduation or reconstructed delivery history.
