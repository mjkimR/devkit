# Context Loading and Playbook Discovery

## 1. Progressive Disclosure

Guidance in startup files costs tokens on every turn and dilutes rarely needed procedures. devkit therefore loads
it in stages:

- The root `AGENTS.md` guidance block holds only orientation ([Workspace Ownership](workspace-ownership.md#2-ownership-categories-and-invariants)).
- `devkit get-context <bundle>` returns a bundle's constitution and instruction headers; the agent reads bodies on
  demand.
- Playbooks stay on disk under `.devkit/managed/<bundle>/` and are searched only when a task explicitly calls for
  one.

## 2. Bundle Context (`devkit get-context`)

`devkit get-context <bundle>` returns the bundle's **context**: its constitution and the header catalog of its
synchronized instructions, so an instruction-only bundle still has one. It runs from the project or a
subdirectory (or with `-w`) and takes the shared project lock, waiting up to ten seconds while a sync writes.

- `constitution`: the full text of the optional UTF-8 `AGENTS.md` at the bundle root, which `devkit sync` always
  deploys to `.devkit/managed/<bundle>/AGENTS.md` whatever the presets; `null` when absent.
- `instructions`: for each synchronized instruction of the selected presets, its YAML `header` (`name`,
  `description`) and absolute `path`. An overridden instruction is read from `.devkit/overrides/<bundle>/...`; every
  other file must still match its receipt hash (`NOT_SYNCHRONIZED` otherwise). Bodies are never returned.

```markdown
---
name: code-style
description: Read before changing Python code. Formatting, typing and naming standards.
---
```

### Skill Prerequisite

For a bundle with a constitution or synchronized instructions, `devkit sync` inserts a context-loading prerequisite
right after the frontmatter of every deployed skill: call `devkit get-context <bundle>` **once per bundle in the
current agent context**, shared by all skills, and again only when that context is gone (compaction, a new
conversation). The CLI keeps no loading state; avoiding duplicate reads is the agent's job. Source skills in the
content package stay untouched; only the managed and projected copies carry the prerequisite.

## 3. Playbook Discovery and Search (`devkit-playbook`)

Instructions are judgment criteria visible in the catalog; playbooks are occasional procedures that `get-context`
never exposes.

### Generated `devkit-playbook` Skill

When playbooks are synchronized, `devkit sync` generates the entry skill
`.devkit/managed/_devkit/skills/devkit-playbook/` and projects it into every selected agent. It is invoked
explicitly, for the current task only: Codex via `policy.allow_implicit_invocation: false` in `agents/openai.yaml`
(`$devkit-playbook <task>`), Claude Code via `disable-model-invocation: true` (`/devkit-playbook <task>`), other
agents through the instructions in the skill body.

The skill runs the search, reads the chosen body from the returned path (loading its bundle's context first when
needed), and when nothing matches, completes the task and asks whether to save a reusable draft into an authoring
source; drafts need explicit approval and never touch installed or generated files.

### Playbook Header

A playbook is a Markdown file or a directory with `SKILL.md`. Its YAML frontmatter has nonempty English `name` and
`description` strings and an optional `aliases` array of nonempty English strings. `x-<name>` extension keys
(`x-[a-z][a-z0-9-]*`, any YAML value) are accepted for tools built on devkit and otherwise ignored: not indexed, not
returned, not interpreted. Any other key (`tags` included) is rejected. The whole header, extension values included,
must be Latin-script text within 4096 bytes.

```markdown
---
name: recover-postgres-replica
description: Recover a PostgreSQL replica after replication has stopped.
aliases: [postgres standby repair, replication failure]
---
```

### Search Engine

`devkit playbook search <query>` ranks an in-memory index rebuilt from receipt-owned files on every call (no
persistent cache) with [`devkit.search`](../search/overview.md). Only `name`, `description` and `aliases` are indexed;
bodies never are.

- **Mode**: `auto` (default) is `hybrid` when the `devkit[search]` extra is installed and `lexical` otherwise;
  `lexical`, `dense` and `hybrid` select one ranking explicitly. `lexical` is BM25 ($k_1=1.5$, $b=0.75$, positive
  IDF, unique query terms; case and Latin accents are normalized and punctuation separates terms), `dense` the cosine
  similarity of the query and header embeddings, and `hybrid` their Reciprocal Rank Fusion
  ([Search Overview](../search/overview.md#2-modes)). An explicit `dense` or `hybrid` without the extra fails with
  `SEARCH_EXTRA_MISSING` or `SEARCH_MODEL_NOT_FOUND` (exit `2`); only `auto` falls back. The result's `mode` names
  the ranking that ran, and each `score` is that ranking's: BM25, cosine similarity or the fused value.

- **Bounds**: `limit` 1–20 (default 5), `min_score` $\ge 0$ (default 0.1, the BM25 floor), `min_similarity` 0–1
  (default 0.35, the cosine floor of `dense` and `hybrid`), `max_bytes` 1024–65536 (default 8192), and `mode`,
  defined once in `installation/config.py` and applied to `[playbooks]` in `.devkit/config.toml` and to the command
  options alike. In `hybrid` each floor applies to its own ranking before the fusion. The default similarity floor
  was measured on English metadata: it drops the long tail of weak similarities and keeps the gain of hybrid ranking. A query is at most 512 UTF-8 bytes. An out-of-range option or a query that is not English Latin
  text is `ARGUMENT_INVALID` (exit `2`), naming the option in `target_files`.
- **Budget**: the JSON output stays within `max_bytes`; whole records that do not fit are omitted and
  `truncated: true` is set.

```bash
uv run devkit playbook search "replica recovery" --limit 3 --min-score 0.2 --max-bytes 4096
```

```json
{
  "query": "replica recovery",
  "mode": "hybrid",
  "results": [
    {
      "bundle": "starter",
      "id": "review-flow",
      "name": "review-flow",
      "description": "Pull request review checklist",
      "aliases": [],
      "path": "/abs/path/.devkit/managed/starter/playbooks/review.md",
      "score": 0.032787
    }
  ],
  "truncated": false
}
```

Results are sorted best first. An overridden playbook is searched and returned from its override.
