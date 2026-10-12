# Context Loading and Playbook Discovery

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)
- [Evaluations: Hybrid Binary Search Engine](../architecture/evaluations/hybrid-binaries.md)

---

## 1. Problem Statement: Context Bloat vs. Progressive Disclosure

AI coding agents operate under finite context token windows. Dumping all repository guidelines, coding rules, and procedural checklists into startup prompt files (`AGENTS.md`, `CLAUDE.md`) leads to two antipatterns:
1. **Permanent Token Bloat**: Thousands of tokens consumed on every single agent query, degrading performance and increasing costs.
2. **Attention Dilution**: Crucial procedural playbooks (e.g., release checklists, database migrations) are diluted by noise during routine coding tasks.

To solve this, `devkit` implements **Progressive Context Disclosure**:
- Only host orientation headers live in the repository bootstrap instructions (`<!-- DEVKIT:START -->...<!-- DEVKIT:END -->`).
- Bundle constitutions and instruction headers are discovered via `devkit get-context`.
- Procedural playbooks and deep instructions remain on disk under `.devkit/managed/<bundle>/`.
- Agents query playbooks on demand through the shared `devkit-playbook` skill or CLI search when an explicit task requires them.

---

## 2. Bundle Constitution and Context Loading (`devkit get-context`)

The response of `devkit get-context <bundle>` is the bundle's **context**: the constitution when the bundle ships one, plus the header catalog of its synchronized instructions. Instruction-only bundles therefore still deliver a context; the catalog is what the agent reads to decide which bodies to open.

### Bundle Constitution (`AGENTS.md`)
An optional UTF-8 `AGENTS.md` at the bundle root serves as its constitution. `devkit sync` always extracts it into `.devkit/managed/<bundle>/AGENTS.md`, independently of presets.

### Instruction Catalog
Instruction sources (`kind = "instruction"`) are Markdown files with YAML frontmatter containing `name` and `description`:

```markdown
---
name: code-style
description: Python formatting, typing, and naming standards.
---

## Coding Standards
...
```

### Context Loading Protocol
```bash
uv run devkit get-context <bundle>
```
- **Execution**: Run from the synchronized consumer project or a subdirectory (or specify `-w/--workspace-root <dir>`). The command takes the shared project lock, so parallel agents can load context at the same time; while a sync is writing it waits up to ten seconds.
- **Response**: Returns JSON containing:
  - `constitution`: Full markdown string of the bundle's `AGENTS.md` (or `null` when absent).
  - `instructions`: Catalog array of YAML `header` strings and absolute file `path` values for synchronized instructions selected by presets. An overridden instruction is read from `.devkit/overrides/<bundle>/...`; every other file must still match its receipt hash.
- **On-Demand Body Loading**: Instruction bodies are never returned by `get-context`. The agent inspects headers to identify relevant policies and reads those files on demand.

### Skill Body Prerequisite Injection
For bundles declaring a constitution or synchronized instructions, `devkit sync` prepends a context loading prerequisite to every deployed skill body, immediately after frontmatter:
- **Contract**: Requires calling `devkit get-context <bundle>` **only once per bundle in the current agent context**, shared across all skills, not once per skill or turn.
- **Reload Policy**: Reload only when context is no longer available (such as after context window compaction or in a fresh conversation turn).
- **Stateless CLI**: The CLI keeps no agent loading state; following the prerequisite and avoiding duplicate reads is the agent's responsibility.
- **Source Isolation**: Source skills in content packages remain pristine. Managed copies in `.devkit/managed/` and projected copies in native agent directories are generated afresh on each sync.

---

## 3. Playbook Discovery and Search (`devkit-playbook`)

Instructions expose headers through `get-context` so agents can select relevant judgment criteria during normal coding. In contrast, playbooks hold occasional task procedures and expose neither headers nor bodies through `get-context`.

### Generated `devkit-playbook` Skill
When synchronized playbooks exist, `devkit sync` generates a shared entry skill under `.devkit/managed/_devkit/skills/devkit-playbook/` and projects it into active native skill directories:
- **Codex Native Control**: Configured with `policy.allow_implicit_invocation: false` in `agents/openai.yaml` (`$devkit-playbook <task>`).
- **Claude Code Native Control**: Configured with `disable-model-invocation: true` in frontmatter (`/devkit-playbook <task>`).
- **Antigravity / Other Agents**: Follows explicit-invocation instructions in the skill body.
- **Invocation Scope**: Scoped to the current requested user task, not future conversation turns.

### Playbook Authoring Contract
Playbooks can be Markdown files or directories containing `SKILL.md` and supporting resources:
- **Frontmatter Fields**: Must be YAML frontmatter with nonempty English `name` and `description` strings, plus an optional `aliases` array of nonempty English strings.
- **Extension Keys**: Keys of the form `x-<name>` (`x-[a-z][a-z0-9-]*`, any YAML value) are accepted for tools built on devkit and ignored by devkit: they are not indexed by search, not returned in results and not interpreted. They remain in the managed copy for the tool that owns them.
- **Strict Validation**: Other fields (including `tags`) are strictly rejected. The whole header, extension values included, must still use Latin letters and fit in 4096 bytes.
- **Size & Language Limits**: Headers are limited to 4096 bytes. The parser verifies that header text uses Latin characters (English).
- **Example**:
  ```markdown
  ---
  name: recover-postgres-replica
  description: Recover a PostgreSQL replica after replication has stopped.
  aliases: [postgres standby repair, replication failure]
  ---

  ## Recovery Procedure
  ...
  ```

---

## 4. Embedded BM25 Search Engine

`devkit` contains an embedded lexical search engine based on BM25:
- **Zero C-Dependencies**: Implemented purely using the Python standard library.
- **Dynamic In-Memory Index**: Rebuilt from receipt-owned files for each search, avoiding stale persistent caches.
- **Indexed Fields**: Indexes only `name`, `description`, and `aliases` with parameters $k_1=1.5$, $b=0.75$, positive IDF, and unique query terms. Playbook bodies are never indexed.
- **Normalization**: Normalized case and Latin accents; punctuation separates terms. (Aliases provide alternate terminology).
- **Configuration & Defaults** (`.devkit/config.toml`):
  ```toml
  [playbooks]
  min_score = 0.1
  limit = 5
  max_bytes = 8192
  ```
- **Bounds**: `limit` (1–20), `min_score` ($\ge 0$), `max_bytes` (1024–65536), defined once in `installation/config.py` and checked for `[playbooks]` and for the command's options alike. Query length is limited to 512 UTF-8 bytes. An out-of-range option or a query that is not English Latin text is `ARGUMENT_INVALID` (one `{"error": ...}` JSON document, exit `2`), naming the option in `target_files`.
- **Budgeting**: Serialized JSON outputs stay within `max_bytes`. When candidates exceed the budget, whole records are omitted and the `truncated: true` flag is emitted.

---

## 5. Playbook Discovery Workflow and CLI

### 1. Search Query Execution
```bash
uv run devkit playbook search "replica recovery" --limit 3 --min-score 0.2 --max-bytes 4096
```
The search returns the query and the matching candidates (bundle, asset id, frontmatter `name`, `description` and `aliases`, absolute file path and score), best first:
```json
{
  "query": "replica recovery",
  "results": [
    {
      "bundle": "starter",
      "id": "review-flow",
      "name": "review-flow",
      "description": "Pull request review checklist",
      "aliases": [],
      "path": "/abs/path/.devkit/managed/starter/playbooks/review.md",
      "score": 0.85
    }
  ],
  "truncated": false
}
```
An overridden playbook is searched and returned from its override (`/abs/path/.devkit/overrides/<bundle>/...`).

### 2. On-Demand Procedure Reading
Once a matching candidate is identified, the agent loads its procedure body directly from the returned absolute file path. If the playbook belongs to a bundle whose context has not yet been loaded in the current session, the agent calls `devkit get-context <bundle>` first.

### 3. Draft Saving Workflow
If an agent searches for a task procedure and finds no matching playbook, it completes the user request and asks whether to save a reusable draft into an authoring source. Writing drafts requires explicit user approval and authoring paths; it never mutates installed wheel resources or generated projections.
