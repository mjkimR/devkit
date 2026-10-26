---
id: CAP-DIST-context-and-playbooks
title: "Context Loading & Playbooks"
summary: "On-demand context loading, playbook discovery and exact receipt-backed retrieval with effective content identity and external execution boundaries."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/playbook_get.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/reading.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/status.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/context.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/context_documents.py
created_at: 2026-10-17
usecases:
  - UC-reconcile-living-spec-drift
  - UC-review-and-refactor-accumulated-slop
---

# [CAP-DIST-context-and-playbooks] Context Loading and Playbook Discovery

## 1. Progressive Disclosure

Guidance in startup files costs tokens on every turn and dilutes rarely needed procedures. devkit therefore loads
it in stages:

- The root `AGENTS.md` guidance block holds only orientation (`CAP-DIST-workspace-ownership`).
- `devkit get-context <bundle>` returns a bundle's constitution, instruction headers and the titles and summaries of
  its declared context documents; the agent reads bodies on demand.
- Playbooks stay on disk under `.devkit/managed/<bundle>/` and are searched only when the user invokes
  `devkit-playbook` for the task, a failing rule's remediation names one, or an installed entry skill runs its own
  bounded intake search (the `spec` skill's, `CAP-HARN-agent-guidance`); a candidate found that way runs only after
  the user confirms it.

## 2. Bundle Context (`devkit get-context`)

`devkit get-context <bundle>` returns the bundle's **context**: its constitution, the header catalog of its
synchronized instructions and the list of its context documents, so an instruction-only bundle still has one. It runs from the project or a
subdirectory (or with `-w`) and takes the shared project lock, waiting up to ten seconds while a sync writes; where
the file system is read-only for it, it reads without the lock (`CAP-DIST-sync-and-transactions`).

- `constitution`: the full text of the optional UTF-8 constitution, literal `AGENTS.md` or rendered `AGENTS.md.jinja`, at the bundle root, which `devkit sync` always
  deploys to `.devkit/managed/<bundle>/AGENTS.md` whatever the presets; `null` when absent.
- `instructions`: for each synchronized instruction of the selected presets, its YAML `header` (`name`,
  `description`) and absolute `path`. An ordinary overridden instruction is read from
  `.devkit/overrides/<bundle>/...`. A template instruction is read from rendered managed `.md` output, including
  when its raw `.md.jinja` source is overridden; source or variable changes require a sync. Every file read outside
  the override tree must match its canonical receipt hash or validated personal render evidence. Missing or stale
  personal evidence is `CONFIG_LOCAL_RENDER_STALE`; other unsynchronized files are `NOT_SYNCHRONIZED`. Both direct
  the caller to sync. Bodies are never returned; see `CAP-DIST-sync-and-transactions`.
- `documents`: always present, `[]` when the bundle declares no context document directory
  (`context_documents` in `bundle.toml`, `CAP-DIST-manifest-spec`) or the directory is absent
  (`ADR-bundle-context-lists-project-documents`). The declaration is read from the receipt-verified managed
  `bundle.toml`; the directory's files are project-owned and read from the workspace at run time, under the same lock,
  without a hash check. Each entry has the absolute `path`, `title` and `summary` of one Markdown file, sorted by
  path. Only regular, non-symlink `*.md` files other than `README.md` directly inside the directory are listed, and
  only when no component of the directory path is a symlink. At most the first 4096 bytes of a file are read, and only
  the frontmatter block in them is decoded; a value that cannot be read (an unreadable file, a non-UTF-8 block, no
  frontmatter or frontmatter that does not close within those bytes, malformed YAML, a non-string value) is `null`,
  never an error. `devkit-dist` caps nothing
  itself; the bundle's own rules bound the directory (the `spec` bundle's `RULE-steering-documents`,
  `CAP-GOV-spec-rules`).

```markdown
---
name: code-style
description: Read before changing Python code. Formatting, typing and naming standards.
---
```

Context reads the actual recorded render mode when validating personal evidence, including a no-save cloud render under persisted local runtime settings. An unrecorded receipt can still validate canonical bytes without claiming an environment; mode-bound personal evidence requires sync. Render provenance never replaces effective configuration as runtime authority.

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
source; drafts need explicit approval and never touch installed or generated files. The draft offer belongs to this
explicitly requested discovery only. The skill names no other bundle's asset: it states generically that a user's
confirmation of a playbook another installed entry skill offered is the explicit invocation of that playbook.

### Playbook Header

A playbook is a Markdown file or a directory with `SKILL.md`. Its YAML frontmatter has nonempty English `name` and
`description` strings and an optional `aliases` array of previous asset IDs of the playbook in the same bundle
(`ADR-playbook-aliases-as-identifiers`): each matches the manifest slug grammar `[a-z][a-z0-9-]*` (not frontmatter
`name`), no item repeats, and no alias equals a playbook asset ID of the bundle (its own included) or another
playbook's alias; bundle validation refuses a violation (`BUNDLE_INVALID`). Aliases are identifiers, not search
keywords: a renamed playbook keeps its published `<bundle>/<old-id>` selectors working. `x-<name>` extension keys
(`x-[a-z][a-z0-9-]*`, any YAML value) are accepted for tools built on devkit and otherwise ignored: not indexed, not
returned, not interpreted. Any other key (`tags` included) is rejected. The whole header, extension values included,
must be Latin-script text within 4096 bytes.

```markdown
---
name: recover-postgres-replica
description: Recover a PostgreSQL replica after replication has stopped.
aliases: [standby-repair]
---
```

### Search Engine

`devkit playbook search <query>` ranks an in-memory index rebuilt from receipt-owned files on every call (no
persistent cache) with `CAP-SRCH-document-search`. Only `name` and `description` are indexed; aliases are
returned as identity metadata and never ranked, and bodies never are.

- **Mode**: `auto` (default) is `hybrid` when the `search` extra (`devkit-dist[search]`, or `devkit-agt[search]`)
  is installed and `lexical` otherwise;
  `lexical`, `dense` and `hybrid` select one ranking explicitly. `lexical` is BM25 ($k_1=1.5$, $b=0.75$, positive
  IDF, unique query terms; case and Latin accents are normalized and punctuation separates terms), `dense` the cosine
  similarity of the query and header embeddings, and `hybrid` their Reciprocal Rank Fusion
  (`CAP-SRCH-document-search`). An explicit `dense` or `hybrid` without the extra fails with
  `SEARCH_EXTRA_MISSING` or `SEARCH_MODEL_NOT_FOUND` (exit `2`); only `auto` falls back. The result's `mode` names
  the ranking that ran, and each `score` is that ranking's: BM25, cosine similarity or the fused value.

- **Bounds**: `limit` 1–20 (default 5), `min_score` $\ge 0$ (default 0.1, the BM25 floor), `min_similarity` 0–1
  (default 0.35, the cosine floor of `dense` and `hybrid`), `max_bytes` 1024–65536 (default 8192), and `mode`,
  validated for shared configuration, restricted local configuration and command options alike. Search reads
  effective `[playbooks]` preferences: local values override shared values, and explicit command options override
  both. In `hybrid` each floor applies to its own ranking before the fusion. The default similarity floor
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


## 4. Exact Playbook Retrieval (`devkit playbook get`)

`devkit playbook get <bundle>/<playbook> [-w <workspace>]` accepts exactly two case-sensitive
manifest slugs matching `[a-z][a-z0-9-]*`, separated by one slash. It performs no trimming,
case folding, extension removal, path interpretation, ranking or fallback.
The second component is the manifest asset ID, not frontmatter `name`, or a declared alias of one: an exact asset
ID always wins; otherwise the alias resolves only when exactly one effective playbook header of that bundle
(overrides included) declares it. A declared alias is the playbook's own identity, not fallback selection.

The command returns one JSON object and exits 0. It exposes no `--format` option;
unsupported options and missing/extra arguments are Click usage errors (exit 2).
Libraries return data without printing. The normative result fields are:

- `bundle`, `id`: canonical manifest identity (the asset ID, also when the request named an alias).
- `alias`: the alias the request named, or `null` for an exact asset ID.
- `name`, `description`, `aliases`: validated effective header metadata; extension keys are ignored.
- `body`: complete decoded UTF-8 text after the closing frontmatter delimiter line, preserving
  whitespace/newlines without truncation, interpolation, resource expansion or execution.
- `source`: `{path, sha256}` with the absolute effective entrypoint and SHA-256 of the exact
  bytes read including frontmatter. Overrides name their override path; other playbooks name
  the managed path. This identifies content, not package provenance or execution attestation.
- `context`: `{bundle, argv, policy}` with the same bundle, argv
  `["devkit", "get-context", "<bundle>"]` and policy `"once-per-agent-context"`.

Run the context argv in the same resolved workspace (or pass its `-w`) before following the
procedure unless already loaded in this agent context; reload after loss. Apply the full
constitution and read relevant instruction bodies, including when the bundle context is empty.
Retrieval loads no context and tracks no execution state. Resolve relative body resources
against the parent of `source.path`, reading only needed resources under existing permissions;
no resource bytes or directory inventory are returned.

Resolution validates the selector, resolves the synchronized project and takes its existing
shared lock, then validates the runtime receipt, bundle presence, exact playbook match (when it misses, the alias
match over every effective playbook header of the bundle, each validated as below; an exact ID is served without
this step), entrypoint ownership, effective file and content, in that order. The match must have exactly
one entrypoint in its recorded paths and its bundle's managed or override prefix. Only receipt
assets are read; no installed-package discovery, source-tree lookup, lazy sync or fallback occurs.
Ordinary overrides are read as currently edited. Selection edits do not change the deployment
snapshot before sync. Playbook templates remain unsupported; shared runtime validation still
checks personal-render evidence for other eligible kinds. Existing lock transient-file behavior
and read-only filesystem fallback remain unchanged. Retrieval mutates no content or selection.

All domain failures use the existing JSON error envelope, advisory action and exit 2, without
partial results. Existing transaction, lock, unsafe-path and configuration advisories pass through.

| Condition | Code | Action |
| --- | --- | --- |
| Malformed selector | `ARGUMENT_INVALID` | Correct `<bundle>/<playbook>`; target `PLAYBOOK_ID` |
| Absent synchronized bundle or playbook (unknown, wrong kind or unselected, and no effective header declares the alias) | `SELECTION_INVALID` | Inspect `devkit list` and explicit bundle/preset selection |
| Alias declared by more than one effective playbook header of the bundle | `PLAYBOOK_ALIAS_AMBIGUOUS` | Name the playbook by its exact asset ID, or keep the alias on one playbook; target the declaring playbooks |
| No receipt, missing effective entrypoint or modified managed content | `NOT_SYNCHRONIZED` | `devkit sync` |
| Stale/missing personal-render evidence, including unrelated assets | `CONFIG_LOCAL_RENDER_STALE` | `devkit sync` |
| Invalid receipt or zero/multiple/unowned/wrong-bundle entrypoints | `RECEIPT_INVALID` | Existing receipt repair advisory |
| Invalid effective UTF-8 or frontmatter | `BUNDLE_INVALID` | Fix the named effective source; sync managed-source changes |

Unknown and unselected identities share a code because the deployed receipt cannot distinguish them.

## 5. Explicit Invocation and Execution Ownership

A user naming the exact playbook for the current task, or explicitly configuring an external
schedule naming that exact ID, authorizes retrieval and interpretation within that task's scope. A request or
schedule naming a declared alias is explicit invocation of the canonical playbook `get` reports.
Retrieval cannot verify authorization and grants none. Ordinary task wording alone never selects or
runs a playbook: an entry skill may run one bounded search at its intake and offer a candidate, and the user's
confirmation of that offer is the explicit invocation (`ADR-spec-intake-playbook-discovery`). Explicit discovery and
rule remediation remain supported.
Each run starts fresh procedure progress, checks prerequisites and obeys project workflow gates,
permissions and user constraints. Schedules do not provide future gated approvals, and unavailable
approval UI is not approval. External systems own cadence, launch, retries, overlap control and
execution history; devkit supplies instructions and context requirements (`ADR-external-playbook-execution`).
