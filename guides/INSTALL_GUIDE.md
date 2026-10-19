# devkit Installation Guide (for AI coding agents)

You are an AI coding agent asked to install devkit into the repository you are working in. Follow this guide and
the documents it links in order, run the commands yourself and stop only where a step says to ask the user.

devkit distributes agent assets (instructions, skills, playbooks, rules, commit gates) from installed Python
packages into a repository, records every file it writes in `.devkit/installation.json`, and keeps a managed block
in the root `AGENTS.md`. It runs from the project's own `uv` environment as `uv run devkit ...`. Two packages provide
it: `devkit-dist` (asset distribution: sync, context, playbooks, native hooks, the `devkit` executable) and
`devkit-agt` (the developer harness on top: repository rules, commit gates, delivery workflows, task worktrees and
`devkit run`), which depends on `devkit-dist`.

## Reading these guides

If you were given a GitHub page link, fetch the raw files instead of the rendered HTML:

```text
https://raw.githubusercontent.com/mjkimR/devkit/main/guides/INSTALL_GUIDE.md
https://raw.githubusercontent.com/mjkimR/devkit/main/guides/install/<document>.md
```

Resolve relative links against the same base, and read a linked document only when its step comes up.

## Ground rules

1. **Ask before changing the repository.** Present the plan (route, packages, agents, bundles) and wait for the
   user's approval before the first write. Read-only analysis needs no approval.
2. **Never commit or push.** When the installation is verified, list the files to commit and stop.
3. **Preserve what exists.** Never overwrite or delete files devkit did not create. devkit edits only the block
   between `<!-- DEVKIT:START -->` and `<!-- DEVKIT:END -->` in `AGENTS.md`; leave everything outside it alone.
4. **Act on codes, not prose.** devkit reports problems on stderr as blocks such as `[ERROR]  (SYNC_CONFLICT) ...` with
   `[ACTION]` and `[FIX]` lines. Follow those directives; when a directive says to ask the user, ask.
5. **Do not install tools silently.** If `git` or `uv` is missing, tell the user and ask before installing it.

## Step 1: Preflight

Run from the directory you were asked to install into:

```bash
git rev-parse --show-toplevel   # the repository root; work from there
uv --version                    # uv must be available
git status --porcelain          # uncommitted changes, if any
```

- Not a Git repository: an empty directory follows the new-repository route, which initializes Git after approval;
  for a non-empty one, ask the user whether to run `git init` first (commit gates and `--locked` restores need Git).
- Uncommitted changes: suggest committing or stashing first, so the installation is a separate, reviewable change.
  Continue only with the user's agreement.
- `.devkit/` already exists: devkit is already installed. Follow the maintenance section of the
  [existing-repository route](install/existing-repository.md#already-installed) instead of installing again.

## Step 2: Choose the route

| Situation | Route |
| --- | --- |
| No commits, or only a README, LICENSE, `.gitignore` or other boilerplate, and no source or build files | [New repository](install/new-repository.md) |
| Source code, build files, CI or agent configuration already present | [Existing repository](install/existing-repository.md) |

When unsure, take the existing-repository route: its analysis is read-only and costs nothing.

## Step 3: Package sources

Install from Git. uv resolves `devkit-dist` and `devkit-advisory` from the same commit automatically, and `uv.lock`
pins the commit. Declare exactly one devkit requirement:

```bash
# the full harness (the default): distribution plus rules, commit gates, workflows, worktrees and devkit run
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
# or distribution only, when the user wants agent assets without rules, gates or workflows
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"

uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
```

- `devkit-agt` (the default) brings `devkit-dist`, the CLI and every built-in bundle (`devkit`, `advisory` and the
  auto-selected `harness`); never declare `devkit-dist` next to it. Take `devkit-dist` alone only when the user asks
  for distribution without the harness: it deploys the `devkit` and `advisory` bundles and has no `devkit rules`,
  `devkit gate`, `devkit workflow` or `devkit run` (they fail with `HARNESS_COMMAND_UNAVAILABLE`). Adding the harness
  later replaces the `devkit-dist` requirement with the `devkit-agt` one in the same dependency group.
- `devkit-catalog` (optional) adds opt-in bundles that deploy nothing until selected; add it only when a
  [recommended bundle](install/bundle-recommendations.md) comes from it.
- Both packages require Python 3.12 or newer; the project's `requires-python` must allow 3.12 (the route documents
  cover a project that does not).
- Release wheels are an alternative only when `gh release view --repo mjkimR/devkit` lists `devkit_dist-*.whl` and
  `devkit_agt-*.whl` (and `devkit_catalog-*.whl` when needed); a `devkit-agt` wheel installation also names the
  `devkit-dist` and `devkit-advisory` wheels of that release. Never mix Git and wheel sources for these packages.
- Upgrading later: `uv lock --upgrade-package devkit-agt --upgrade-package devkit-dist --upgrade-package devkit-advisory`
  (plus `--upgrade-package devkit-catalog`), then `uv sync` and `uv run devkit sync`. The first upgrade from a
  `devkit-agt` that predates `devkit-dist` follows
  [Upgrading across the package split](install/existing-repository.md#upgrading-across-the-package-split).

## Step 4: Recommend bundles

After the base installation, follow [Bundle Recommendations](install/bundle-recommendations.md): match the repository
against each opt-in bundle, present the recommendations with their evidence, and select the approved ones.

## Optional: MCP connection

When Codex or Claude Code native service tools are wanted, now or on an existing installation, follow
[MCP onboarding](install/mcp.md) after bundle selection, with its optional dependency and user-scoped registration
in the approved plan. Sync never registers MCP.

## Step 5: Verify and report

```bash
uv run devkit sync --check   # exit 0: the workspace matches the selection
uv run devkit status         # exit 0: no problems in the installed state
uv run devkit gate status    # hooks installed (devkit-agt in Git repositories only)
git status --short           # what the installation changed
```

Then report to the user:

- the route taken and anything you skipped or that needs their decision;
- installed packages and selected bundles with presets;
- every warning devkit printed (`[WARN]   (<CODE>) ...`) and what it means for them;
- the files to commit: `pyproject.toml`, `uv.lock`, `.devkit/config.toml`, `.devkit/installation.json`,
  `.devkit/.gitignore`, `AGENTS.md`, `.gitignore` changes and any seeded files;
- how a fresh clone restores the generated files: `uv sync`, then `uv run devkit sync --locked`.

Ask whether to commit. Do not commit on your own.

## Troubleshooting

| Code or symptom | Meaning | What to do |
| --- | --- | --- |
| `SYNC_CONFLICT` | A file devkit must write already exists with other content | List the named paths to the user; never delete them yourself. |
| `GUIDANCE_BLOCK_INVALID` | `AGENTS.md` has broken or duplicate `DEVKIT` markers | Show the markers to the user and fix them together. |
| `WORKSPACE_UNSAFE` | `AGENTS.md` is a symlink | Ask the user: make `AGENTS.md` the real file, or set `guidance_block = false`. |
| `GATE_HOOK_INSTALL_SKIPPED`, `GATE_HOOKS_PATH_SET` | `core.hooksPath` or a foreign hook layout keeps devkit's hooks out, so no gate runs | Report it; the installation is otherwise complete. |
| `GATE_HOOK_ENTRY_MISSING` from `devkit gate status` | An enabled gate's stage has no devkit hook entry | Run `uv run devkit gate install`, then `uv run devkit gate status` again. |
| `SELECTION_INVALID` | A selected bundle's package is not installed, or a selected preset does not exist (`devkit:run` became `harness:run`) | Run `uv sync`, or remove the bundle with `uv run devkit remove <bundle>`; replace a `devkit` `run` preset with `harness = "run"` under `[presets]`. |
| `HARNESS_COMMAND_UNAVAILABLE`, `HARNESS_ENGINE_MISSING` | A harness command, or deployed rule, gate or workflow assets, with `devkit-dist` only | Tell the user; apply the `[FIX]` (switch to `devkit-agt`) only once they agree. |
| `RECEIPT_STALE` from `devkit sync --locked` | The committed receipt does not match the installed packages | Run a plain `uv run devkit sync` and include its changes in the commit. |
| uv reports `requires-python` incompatible | The project allows Python below 3.12 | Stop and ask the user (see the route document). |
