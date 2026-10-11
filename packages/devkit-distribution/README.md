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

## Playbook discovery and reuse

Instructions expose headers through `get-context` so the agent can select relevant
rules and judgment criteria during normal work. Playbooks hold occasional task
procedures and expose neither headers nor bodies through that command. Recurring,
explicit execution flows belong to workflows.

When selected playbooks exist, sync generates one shared `devkit-playbook` skill
under `.devkit/managed/_devkit/skills/devkit-playbook/` and projects it to selected
native skill directories. It is removed when no selected playbooks remain. Source
skills using the same native name cause a destination collision. Generated files
are receipt-owned and protected from overwriting user edits, like other assets.
Without an agent selection, only the managed entry skill is generated. Local
`plan` previews bundle source assets; project `sync --dry-run` also shows this
shared generated skill.

Invoke `$devkit-playbook <task>` in Codex or `/devkit-playbook <task>` in Claude
Code. Codex receives `policy.allow_implicit_invocation: false` in
`agents/openai.yaml`; Claude Code receives `disable-model-invocation: true` in
frontmatter. These use the documented [Codex invocation policy](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code invocation control](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill).
Other consumers of the shared skill, including Antigravity, must follow the
explicit-invocation instruction in its body; native enforcement is not verified.
Invocation is scoped to the current requested task, not future conversation turns.

```bash
uv run devkit playbook search "postgres standby repair"
uv run devkit playbook search "replica recovery" --limit 3 --min-score 0.2 --max-bytes 4096
```

The search CLI is read-only and does not verify conversational authorization;
the generated skill and supported native invocation controls govern agent use.
Run from the consumer project or a subdirectory, or use `--target`. Search uses
synchronized playbooks across bundles and honors presets. Old receipts without
playbook entrypoints require another sync. Missing/modified entry files or a
pending transaction cause an error.

Playbooks can be Markdown files or directories with `SKILL.md` and supporting
resources. Bundle validation requires YAML frontmatter with nonempty English
`name` and `description` strings, plus an optional `aliases` array of nonempty
English strings. Other fields, including `tags`, are rejected. Headers are limited
to 4096 bytes. YAML parsing uses PyYAML; the BM25 implementation uses only the
Python standard library and has no search-package dependency.

```yaml
---
name: recover-postgres-replica
description: Recover a PostgreSQL replica after replication has stopped.
aliases: [postgres standby repair, replication failure]
---
```

The skill translates requests into English queries; the CLI rejects non-Latin
letters and empty search terms. Validation cannot establish that Latin prose is
English, so English remains an authoring/review and skill instruction requirement.
Case and Latin accents are normalized; punctuation separates terms. Search has
no stemming or semantic matching: use aliases for alternate terms. BM25 indexes
only `name`, `description`, and `aliases`, with k1=1.5, b=0.75, positive IDF, and
unique query terms. Bodies and supporting resources are never indexed or returned.
The index is rebuilt from receipt-owned files for each search, avoiding stale
persistent indexes.

Results contain bundle/asset identity, metadata, score, and an absolute file path.
Defaults are top 5, minimum score 0.1, and 8192 bytes for the serialized JSON output
including its final newline. Bounds are configurable (limit 1–20, finite
nonnegative minimum score, output 1024–65536 bytes). Only positive matches meeting
the threshold appear; results may be empty. Whole candidates are omitted when
the output budget is reached, and `truncated` reports omitted qualifying matches.
Scores are lexical ranks, not applicability confidence; calibrate the threshold
with real tasks. Queries are limited to 512 UTF-8 bytes.

After choosing a playbook, the agent loads its bundle's context once if needed,
reads relevant instructions, and reads the selected procedure body. If no suitable
procedure exists, it completes the task and asks whether to save a reusable draft
into an authoring source. Saving requires user approval and an available source;
the skill never writes into generated copies or installed wheel resources. See
the [consumption and search contract](../../docs/architecture/resource-taxonomy.md#devkit-playbook-entry-point-and-search-contract).

**TODO:** Evaluate `devkit get-context <bundle> [query]` for filtering instruction
headers in larger catalogs. This optional argument is not implemented. Any future
design must preserve full constitution delivery, on-demand instruction bodies, and
the explicit user entry boundary for playbooks.

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
