# devkit Installation Guide (for AI coding agents)

You are an AI coding agent asked to install devkit into the repository you are working in. This guide and the
documents it links are written for you: follow them in order, run the commands yourself and stop only where a step
says to ask the user.

devkit distributes agent assets (instructions, skills, playbooks, rules, commit gates) from installed Python
packages into a repository, records every file it writes in `.devkit/installation.json`, and keeps a managed block
in the root `AGENTS.md`. It runs from the project's own `uv` environment as `uv run devkit ...`.

## Reading these guides

If you were given a GitHub page link, fetch the raw files instead of the rendered HTML:

```text
https://raw.githubusercontent.com/mjkimR/devkit/main/guides/INSTALL_GUIDE.md
https://raw.githubusercontent.com/mjkimR/devkit/main/guides/install/<document>.md
```

Resolve every relative link in these guides against the same base. Read a linked document when its step comes up,
not all of them up front.

## Ground rules

1. **Ask before changing the repository.** Present the plan (route, packages, agents, bundles) and wait for the
   user's approval before the first write. Read-only analysis needs no approval.
2. **Never commit or push.** When the installation is verified, list the files to commit and stop.
3. **Preserve what exists.** Never overwrite or delete files devkit did not create. devkit edits only the block
   between `<!-- DEVKIT:START -->` and `<!-- DEVKIT:END -->` in `AGENTS.md`; leave everything outside it alone.
4. **Act on codes, not prose.** devkit reports problems on stderr as blocks such as `[ERROR: SYNC_CONFLICT]` with
   `[ACTION]` and `[FIX]` lines. Follow those directives; when a directive says to ask the user, ask.
5. **Do not install tools silently.** If `git` or `uv` is missing, tell the user and ask before installing it.

## Step 1: Preflight

Run from the directory you were asked to install into:

```bash
git rev-parse --show-toplevel   # the repository root; work from there
uv --version                    # uv must be available
git status --porcelain          # uncommitted changes, if any
```

- Not a Git repository: an empty directory follows the new-repository route, which initializes Git after approval.
  A non-empty directory without Git: ask the user whether to run `git init` first. devkit works without Git, but
  commit gates and `--locked` restores need it.
- Uncommitted changes: tell the user and suggest committing or stashing first, so the installation is a separate,
  reviewable change. Continue only with their agreement.
- `.devkit/` already exists: devkit is already installed. Follow the maintenance section of the
  [existing-repository route](install/existing-repository.md#already-installed) instead of installing again.

## Step 2: Choose the route

| Situation | Route |
| --- | --- |
| No commits, or only a README, LICENSE, `.gitignore` or other boilerplate, and no source or build files | [New repository](install/new-repository.md) |
| Source code, build files, CI or agent configuration already present | [Existing repository](install/existing-repository.md) |

When unsure, take the existing-repository route: its analysis is read-only and costs nothing.

## Step 3: Package sources

Install from Git. uv resolves `devkit-advisory` from the same commit automatically, and `uv.lock` pins the commit:

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv add --dev "devkit-catalog @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-catalog"
```

- `devkit-agt` (required) is the CLI with its built-in bundles. `devkit-catalog` (optional) adds opt-in bundles
  that deploy nothing until selected; add it only when a [recommended bundle](install/bundle-recommendations.md)
  comes from it.
- `devkit-agt` requires Python 3.12 or newer. uv downloads a suitable interpreter when needed, but the project's
  `requires-python` must allow 3.12; the route documents say how to handle a project that does not.
- Release wheels are an alternative only when the latest release lists `devkit_agt-*.whl` (and `devkit_catalog-*.whl`
  when needed): check with `gh release view --repo mjkimR/devkit`. Do not mix Git and wheel sources for these packages.
- Upgrading later: `uv lock --upgrade-package devkit-agt --upgrade-package devkit-advisory`
  (plus `--upgrade-package devkit-catalog`), then `uv sync` and `uv run devkit sync`.

## Step 4: Recommend bundles

After the base installation, follow [Bundle Recommendations](install/bundle-recommendations.md): match the repository
against each opt-in bundle, present the recommendations with their evidence, and select the approved ones.

## Optional: MCP connection

When Codex native integration tools are wanted, follow [MCP onboarding](install/mcp.md) after bundle selection.
Include its optional dependency and user-scoped registration in the approved installation plan. Asset sync does
not register MCP. Report registration, client connection and visible approval UI as separate observations.

## Step 5: Verify and report

```bash
uv run devkit sync --check   # exit 0: the workspace matches the selection
uv run devkit status         # exit 0: no problems in the installed state
uv run devkit gate status    # hooks installed (Git repositories only)
git status --short           # what the installation changed
```

Then report to the user:

- the route taken and anything you skipped or that needs their decision;
- installed packages and selected bundles with presets;
- every warning devkit printed (`[WARN: ...]`) and what it means for them;
- the files to commit: `pyproject.toml`, `uv.lock`, `.devkit/config.toml`, `.devkit/installation.json`,
  `.devkit/.gitignore`, `AGENTS.md`, `.gitignore` changes and any seeded files;
- how a fresh clone restores the generated files: `uv sync`, then `uv run devkit sync --locked`.

Ask whether to commit. Do not commit on your own.

## Troubleshooting

| Code or symptom | Meaning | What to do |
| --- | --- | --- |
| `SYNC_CONFLICT` | A file devkit must write already exists with other content | List the named paths to the user; never delete them yourself. Move or rename only with approval, then sync again. |
| `GUIDANCE_BLOCK_INVALID` | `AGENTS.md` has broken or duplicate `DEVKIT` markers | Show the markers to the user and fix them together. |
| `WORKSPACE_UNSAFE` | `AGENTS.md` is a symlink | Ask the user: make `AGENTS.md` the real file, or set `guidance_block = false`. |
| `GATE_HOOK_INSTALL_SKIPPED` | Hooks were not installed (custom `core.hooksPath`, foreign hook layout) | Report it; the installation is otherwise complete. See the existing-repository route. |
| `GATE_HOOKS_PATH_SET` from `devkit gate status` | `core.hooksPath` sends Git to another hooks directory, so no devkit gate runs | Report it with its `[FIX]`; change the setting only once the user agrees. |
| `GATE_HOOK_ENTRY_MISSING` from `devkit gate status` | An enabled gate's stage has no installed devkit hook entry, so its gates do not run | Run `uv run devkit gate install` (or `uv run devkit sync`), then `uv run devkit gate status` again. If hooks were skipped (`GATE_HOOK_INSTALL_SKIPPED`), report that instead. |
| `SELECTION_INVALID` | A selected bundle's package is not installed | Run `uv sync`, or remove the bundle with `uv run devkit remove <bundle>`. |
| `RECEIPT_STALE` from `devkit sync --locked` | The committed receipt does not match the installed packages | Run a plain `uv run devkit sync` and include its changes in the commit. |
| uv reports `requires-python` incompatible | The project allows Python below 3.12 | Stop and ask the user (see the route document). |
