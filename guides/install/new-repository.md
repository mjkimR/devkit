# Route: New Repository

For an empty directory or a repository with only boilerplate (README, LICENSE, `.gitignore`). There is no code to
analyze, so the user's intent replaces the analysis. Entry point: [Installation Guide](../INSTALL_GUIDE.md).

## 1. Ask the user

Ask these in one message, with the defaults stated so the user can answer "defaults":

1. **Agents**: which coding agents will work here? devkit projects skills and subagents for `codex`,
   `claude-code` and `antigravity`. Default: the agent you are, plus any others the user names.
2. **Project kind**: what will the repository hold (language, a library or a service, documentation only)? This
   decides whether the root `pyproject.toml` is only devkit's tooling manifest or the project's own. Default: a
   tooling manifest only (`uv init --bare`); the project's own files come later.
3. **Practices**: should commits follow Conventional Commits? Will the repository author agent skills or a large
   `AGENTS.md`? Will work follow spec-driven delivery (`devkit-spec`)? The answers feed
   [Bundle Recommendations](bundle-recommendations.md). Default: no opt-in bundles and no `devkit-spec`; the
   automatically deployed bundles only.

Then present the plan (the steps below with the chosen values) and wait for approval.

## 2. Initialize

```bash
git init -b main                                      # only when the directory is not a Git repository
uv init --bare --python 3.12 --no-workspace --name <repository-name>
```

- `uv init --bare` writes only a minimal `pyproject.toml`, devkit's tooling manifest. For a Python project the user
  wants scaffolded, use the layout they ask for (`uv init --lib` or `--app`) with `--python 3.12` or newer instead.
- `--no-workspace` keeps the new project out of a uv workspace that happens to contain the directory.

Create or extend the root `.gitignore` with at least:

```gitignore
.venv/
__pycache__/
```

## 3. Install devkit

```bash
uv add --no-build-package pyyaml --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run python -c "import yaml; assert hasattr(yaml, 'CSafeLoader'), 'PyYAML LibYAML binding is unavailable'"
uv run devkit --version
uv run devkit sync --agent <agent> [--agent <agent> ...]
```

- For a distribution-only installation, add `devkit-dist` instead, never both
  ([Installation Guide, step 3](../INSTALL_GUIDE.md#step-3-package-sources)).
- Omit `--agent` to project into every supported agent; the choice is recorded as `agents` in
  `.devkit/config.toml`.
- The first sync creates `.devkit/config.toml`, `.devkit/installation.json`, `.devkit/.gitignore`, the root
  `AGENTS.md` with its managed block and, with `devkit-agt` in a Git repository, the commit hook dispatchers.
- Claude Code reads `CLAUDE.md`, which devkit never writes: when it is among the agents, offer to create a
  `CLAUDE.md` containing the single line `@AGENTS.md`.

## 4. Ignore the native projections

`devkit sync` prints a `[CHANGE: create <path>]` line per file. Paths under `.agents/`, `.claude/` and `.codex/` are
native projections that `devkit sync --locked` rebuilds in every clone; keep them out of Git by adding each
projected directory to the root `.gitignore`, for example:

```gitignore
# devkit native projections (rebuilt by `uv run devkit sync --locked`)
.agents/skills/devkit-playbook/
.claude/skills/devkit-playbook/
```

List the directories that actually appeared in the sync output; do not ignore whole `.claude/` or `.codex/`
directories, which also hold project settings. The base installation projects nothing; bundles with skills or
playbooks do (playbooks bring the generated `devkit-playbook` skill), so do this after selecting bundles too.

## 5. Continue

1. Select bundles with [Bundle Recommendations](bundle-recommendations.md), using the user's answers to question 3.
2. Optional: the `rules-check` commit gate (on by default) already runs `devkit-agt`'s built-in rules on every
   commit (Markdown links, secrets, committed binaries and logs, `devkit` command citations); rules from selected bundles
   join it. When the project has fast verification commands, offer to run them before every commit too:

   ```toml
   # .devkit/config.toml
   [gates.settings.verify-commands]
   commands = ["just lint-check"]
   ```

   Call tools through `uv run` or a recipe runner; Git hooks do not have `.venv/bin` on `PATH`.
3. Optional: connect native service tools with [MCP onboarding](mcp.md).
4. Verify and report as in [Installation Guide, step 5](../INSTALL_GUIDE.md#step-5-verify-and-report). Suggest adding
   the fresh-clone setup (`uv sync`, then `uv run devkit sync --locked`) to the project's README or setup recipe.

## Cloud setup

For cloud execution, run `uv run devkit sync --cloud` and use CLI inspection and artifact commands. This saves the checkout-local execution setting and records the actual render environment in the receipt. Optional native-service onboarding is for local execution only; skip it in cloud setup. Cloud mutation still requires a separately authorized CLI/PR route.

`sync --no-save --cloud` renders cloud guidance and records its provenance without changing persisted runtime authorization. The next ordinary sync uses the saved/default environment; status/check reports the pending difference. `sync --local` restores local guidance. Locked sync refuses canonical environment changes; use ordinary sync and commit the resulting tracked output.

For document formats without SDD lifecycle obligations, choose devkit-docs instead of the base harness requirement.
It auto-selects docs:core. For SDD, devkit-spec additionally selects spec:core. The document skeleton is opt-in
through `uv run devkit add docs:docs-skeleton`; existing seeded files remain project-owned.

### Adaptive development entry

When the approved installation is for adaptive development, use devkit-docs plus devkit-catalog and explicitly select
`uv run devkit add adaptive-dev`. Configure shared `[development] approach = "adaptive-dev"` and inspect
`uv run devkit config show`; the optional independent integration provider is `project`. Follow
[the adaptive development setup](../INSTALL_GUIDE.md#adaptive-development) for the complete configuration.

Start or resume with `/adaptive-dev`. Product iteration and optional roles impose no mandatory team sequence. The
coordinator keeps current facts in project-owned `.devkit/adaptive-dev.md`, which sync preserves. Asset selection
alone changes no approach, and adaptive development does not require eventual graduation or reconstructed delivery
history.
