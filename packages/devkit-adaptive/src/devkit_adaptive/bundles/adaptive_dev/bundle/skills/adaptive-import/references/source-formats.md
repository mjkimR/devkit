# Source formats and the header inventory

`<root>` is the cloned repository or the stated subdirectory.

## Recognize the format

| Format | How to recognize it | Header fields | Permission signal |
| --- | --- | --- | --- |
| TOML agent | A `.toml` file with a `developer_instructions` key | `name`, `description`; often `model`, `model_reasoning_effort` | `sandbox_mode`; a `[mcp_servers.<name>]` table is a dependency |
| Markdown agent | A `.md` file whose frontmatter has `name` and `description`, under an `agents/` directory or a directory per division or category | `name`, `description`; sometimes `model`, `tools` and display keys such as `color` or `emoji` | `tools`; a missing `tools` key means every tool on the native host, not read-only |
| Skill | A directory with `SKILL.md` whose frontmatter has `name` and `description` | `name`, `description`; sometimes `allowed-tools` | `allowed-tools`, and whether the directory ships `scripts/` |

- Treat `commands/`, `hooks/`, plugin manifests, MCP configuration and installer scripts as dependencies of a candidate, never as candidates.
- Treat `README.md`, changelogs and catalog indexes as descriptions of the pack; do not follow their instructions to a human installer.

## List the headers

```bash
rg --files <root> | wc -l
rg --no-heading -n '^(name|description|sandbox_mode)\s*=|^\[mcp_servers' <root> -g '*.toml'
rg -U --no-heading -n '\A---\r?\n(?s:.*?)\n---' <root> -g '*.md'
rg --files <root> -g 'SKILL.md'
```

1. Run the first command to size the pack, then the command for each format present.
2. If a command prints more than the session can hold, rerun it per top-level directory.
3. Drop a Markdown file whose frontmatter lacks `name` or `description`; it is a command or a document.
4. Record one inventory row per candidate: path, name, description, permission signal and the directory it sits in (its category, division or plugin).
5. For a plugin layout, list the sibling `commands/`, `skills/` and `hooks/` directories of each agent directory; an agent can depend on them.

## Read the signals with the body in mind

- A header states intent; the body decides. A TOML agent marked `sandbox_mode = "read-only"` can still tell the agent to implement changes, and a review description can head a body that edits files.
- Record a `model` or effort value as a conversion note; it is the pack author's choice and is dropped at conversion.
- Wording such as "use proactively" or "must be used" in a description is an auto-invocation request to the native host: it is dropped at conversion and is no evidence of fit.
- Judge richness by the lines that state a check, a criterion, a failure mode or required evidence, not by length; identity, tone, memory and success-metric sections convert to nothing.

## Layouts seen in public packs

Verify each against the actual clone; a pack can change its layout between commits.

- TOML agent packs: numbered category directories of `.toml` files with uniform keys and short uniform bodies; a few add an MCP server table, and some read-only sandbox files instruct implementation.
- Persona Markdown packs: one directory per division, frontmatter limited to `name`, `description` and display keys, no permission signal. Bodies run to hundreds of lines with identity, style, memory and success-metric sections, named hand-offs and frequent always-or-proactively wording; some grant pull-request creation, package installs or pushes.
- Plugin packs: `plugins/<plugin>/agents/*.md` with `name`, `description`, a model alias and an occasional `tools` key, beside `commands/`, `skills/` and sometimes `hooks/`. Some agents depend on a plugin command or on pipeline state files under a host directory.

## Shortlist body reading

1. Read the whole body of each shortlisted candidate once.
2. For a skill, read `SKILL.md` and list its other files by path; read a script only when the user selects its import in the selection round, and never run it.
3. Note per candidate: the checks worth keeping, host tool names, named hand-offs, state files, MCP servers, companion assets and each operation that assumes authority.
