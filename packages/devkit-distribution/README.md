# devkit-distribution

Install the CLI and content packages into the same uv project dev environment:

```bash
uv add --dev devkit-distribution devkit-starter
uv run devkit sync
uv run devkit list
```

Package names above require a published index or configured local/Git sources.
In this monorepo, `uv sync --all-packages` installs the example content wheel.
Run `uv run --package devkit-distribution devkit sync --target <existing-directory>`.
The CLI does not install dependencies. Use uv to update/remove packages, then sync.

## Content wheel contract

Register a resource module, not a callable, in the entry point group:

```toml
[project.entry-points."devkit_distribution.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

```text
src/package_b_playbooks/
  __init__.py               # No side effects; content module only
  bundle/
    bundle.toml
    AGENTS.md                # Optional bundle constitution
    playbooks/review.md
    instructions/development.md
    skills/review/SKILL.md
```

Include the full resource tree in the wheel. Non-Python producer repositories can
map their existing content into this tree at build time using Hatch force-include.
Discovery reads `importlib.metadata` entry points and `importlib.resources`; it does
not execute rule implementations. Loading a resource module executes its ordinary
Python initialization, so keep it empty. Bundle names must be unique across packages.

`bundle.toml` schema 1 declares a lowercase slug `name`, an `X.Y.Z` `version`, and
nonempty `[[assets]]`. Assets have a unique `id`, a `kind` (`skill`, `subagent`,
`instruction`, `playbook`, `rule`), and exactly one `source` or `variants` table.
Sources are relative POSIX files/directories. A skill is a directory with `SKILL.md`.
Optional `[presets.<name>]` tables select asset IDs through `assets = ["id", ...]`.
Unknown manifest keys, missing sources, path escapes and symlinks are errors.
Native content is copied verbatim except for the generated skill context prerequisite
described below, with modes normalized to 0644 or 0755.

```toml
schema = 1
name = "team"
version = "0.1.0"

[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/codex/reviewer.toml"
claude-code = "native/claude-code/reviewer.md"

[presets.daily]
assets = ["reviewer"]
```

## Sync behavior

```bash
uv run devkit sync --dry-run
uv run devkit sync --agent codex --preset team:daily
uv run devkit sync --check
uv run devkit sync --all-assets
uv run devkit recover
```

Sync deploys all registered packages into `.devkit/managed/<bundle>/` by default.
Repeated `--preset bundle:name` restricts that bundle's selected assets. Agent and
preset choices persist in `.devkit/installation.json`; `--all-assets` clears
preset restrictions. `--no-agents` clears native agent selections and removes
unchanged native copies. Shared skills project into `.agents/skills/` for Codex and
`.claude/skills/` for Claude Code. Subagents require an explicit native variant:
Codex `.toml` into `.codex/agents/`, Claude `.md` into `.claude/agents/`.
No field filtering or conversion is performed. Without `--agent`, the first sync
only installs managed resources. `list` shows installed metadata and synchronized
asset paths, including instruction/playbook/rule paths.

The receipt records package and bundle versions, selection, asset paths, and file
hashes/modes. Existing unowned files and edited deployed files cause sync to fail
before writing. Removed packages/assets delete only unchanged owned files. Missing
owned files are restored. A no-op preserves receipt bytes. Dry-run changes no project
files; check exits 1 when changes are needed. All commands output JSON on success.

Writes use a per-project advisory lock, atomic file replacement and a durable
journal. An interrupted operation must be recovered before further sync. Recovery
checks every recorded file for subsequent edits before rollback. Empty directories
may remain after rollback/removal. Runtime support is currently POSIX (Linux/macOS).

Commit the receipt. Ignore managed/transient and generated native files using your
project's own `.gitignore`; devkit does not edit ignore rules or the Git index.

## Bundle context and progressive disclosure

An optional UTF-8 `AGENTS.md` at the bundle root is its constitution. Sync always
includes it, independently of presets. Instruction sources should be Markdown
files with YAML frontmatter containing `name` and `description`.

```bash
uv run devkit get-context team
```

Run from the synchronized consumer project or a subdirectory; `--target` can
select another project. The command uses the nearest installation receipt and
returns JSON containing the full `constitution` (or null when absent) and an
`instructions` catalog of YAML `header` strings and absolute file `path` values.
Only synchronized instructions selected by presets appear. Instruction bodies
are never included: the agent selects relevant entries from their headers and
reads those files on demand, just as with skill discovery. Missing frontmatter,
unclosed headers, and missing or modified context files produce errors.

For bundles with a constitution or selected instructions, sync prepends a context
loading prerequisite to every deployed skill body, immediately after frontmatter.
It requires `get-context` **only once per bundle in the current agent context**,
shared across all skills, not once per skill or turn. Reload only when context
is no longer available, such as after compaction or in a new agent context.
Package entry points may also explicitly request context using the same rule.
The CLI always returns the full response and keeps no agent loading state;
following the prerequisite and avoiding duplicate reads are agent responsibilities.

Source skills are unchanged. Managed and native copies are generated afresh, so
repeated sync does not accumulate prerequisites. ZIP exports preserve authoring
sources, including the constitution; prerequisites are added when synchronized.

## Local authoring and export

```bash
uv run devkit bundle validate examples/bundles/starter
uv run devkit plan examples/bundles/starter --preset daily
uv run devkit bundle build examples/bundles/starter --output /tmp/starter.zip
```

ZIP build is an optional deterministic local export, not the sync transport.
`plan` previews a local source's managed inventory without inspecting a consumer.
The example source is `packages/devkit-starter/src/devkit_starter/bundle/`;
`examples/bundles/starter/` is its local authoring demonstration.

Still pending: local/override merging, agent trust/config/instruction integration,
agent version/runtime verification, and rule plugin discovery/execution. Installed
Python rule dependencies use the uv environment, but syncing code does not activate
rules automatically. See the [design](../../docs/architecture/agent-distribution.md).
