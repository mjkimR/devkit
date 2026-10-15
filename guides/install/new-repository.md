# Route: New Repository

For an empty directory or a repository with only boilerplate (README, LICENSE, `.gitignore`). There is no code to
analyze, so the user's intent replaces the analysis. Entry point: [Installation Guide](../INSTALL_GUIDE.md).

## 1. Ask the user

Ask these in one message, with the defaults stated so the user can answer "defaults":

1. **Agents**: which coding agents will work here? devkit projects skills and subagents for `codex`,
   `claude-code` and `antigravity`. Default: the agent you are, plus any others the user names.
2. **Project kind**: what will the repository hold (language, a library or a service, documentation only)? This
   decides whether the root `pyproject.toml` is only devkit's tooling manifest or the project's own.
3. **Practices**: should commits follow Conventional Commits? Will work be planned with GitHub Milestones and
   Issues? Will the repository author agent skills or a large `AGENTS.md`? The answers feed
   [Bundle Recommendations](bundle-recommendations.md).

Then present the plan (the steps below with the chosen values) and wait for approval.

## 2. Initialize

```bash
git init -b main                                      # only when the directory is not a Git repository
uv init --bare --python 3.12 --no-workspace --name <repository-name>
```

- `uv init --bare` writes only a minimal `pyproject.toml` (no build system, no sample code). It serves as devkit's
  tooling manifest; for a non-Python project that is all it is.
- For a Python project the user wants scaffolded, use the uv layout they ask for (`uv init --lib` or `uv init --app`)
  with `--python 3.12` or newer instead.
- `--no-workspace` keeps the new project out of a uv workspace that happens to contain the directory.

Create or extend the root `.gitignore` with at least:

```gitignore
.venv/
__pycache__/
```

## 3. Install devkit

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit --version
uv run devkit sync --agent <agent> [--agent <agent> ...]
```

- Omit `--agent` to project into every supported agent; the choice is recorded as `agents` in
  `.devkit/config.toml`.
- The first sync creates `.devkit/config.toml` (commented template), `.devkit/installation.json`,
  `.devkit/.gitignore`, the root `AGENTS.md` with its managed block, and, in a Git repository, the commit hook
  dispatchers.
- When Claude Code is among the agents, Claude Code reads `CLAUDE.md`, not `AGENTS.md`, and devkit never writes
  `CLAUDE.md`. Offer to create a `CLAUDE.md` containing the single line `@AGENTS.md`.

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
2. Optional: the commit gate already checks the rules (`rules-check`, on by default). When the project has fast
   verification commands, offer to run them before every commit too:

   ```toml
   # .devkit/config.toml
   [gates.settings.verify-commands]
   commands = ["just lint-check"]
   ```

   Call tools through `uv run` or a recipe runner; Git hooks do not have `.venv/bin` on `PATH`.
3. Verify and report as in [Installation Guide, step 5](../INSTALL_GUIDE.md#step-5-verify-and-report). Suggest adding
   the fresh-clone setup (`uv sync`, then `uv run devkit sync --locked`) to the project's README or setup recipe.
