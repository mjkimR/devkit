# Agent Asset and Guidance Resource Taxonomy

**Status**: Architecture Specification & Design Blueprint  
**Scope**: Taxonomy, naming standards, and placement decision rules for agent guidance, operational playbooks, governance rules, and runtime assets.  
**Related Documents**: [Unified Agent Asset Distribution Architecture](agent-distribution.md)

---

## 1. Overview and Design Objectives

In modern multi-agent developer environments (e.g., Codex, Claude Code, Antigravity), project guidance and developer tooling take many forms: from natural-language coding standards and multi-step operational checklists to AST-based linters and executable skill directories.

Without a rigorous taxonomy, developer assets suffer from common antipatterns:
- **Context Bloat**: Placing voluminous policies or rules directly into root instruction files (`AGENTS.md` / `CLAUDE.md`), consuming permanent context tokens on every LLM interaction.
- **Fidelity Confusion**: Trying to enforce procedural checklists through static linters, or using prompt instructions to enforce invariants that should be verified deterministically by machine.
- **Naming Ambiguity**: Single-word identifiers (e.g., `entrypoint`, `guide`, `agents`) cause confusion between AI agent personas, Python entry points, and specific filesystem files.

This specification establishes a clean **three-tier classification** and formal, self-describing **kind** naming standards for all distributable agent resources managed by `devkit`.

---

## 2. The Three-Tier Resource Hierarchy

Resources are classified along three dimensions: **Guidance & Context Layer** (natural language), **Mechanized Execution Layer** (code & native tooling), and **Packaging & Selection Layer** (filtering mechanics).

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                       1. Guidance & Context Layer                            │
│  - host-guidance-block  : Host orientation marker (in root AGENTS.md)        │
│  - package-constitution : Package-level constitution (.devkit/.../AGENTS.md) │
│  - package-instruction  : Instruction headers; bodies loaded on demand       │
│  - package-playbook     : Occasional procedures, explicitly requested       │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┴───────────────────────────────────────┐
│                       2. Mechanized Execution Layer                          │
│  - governance-rule      : Deterministic invariant (evaluated by rule engine) │
│  - agent-skill          : Executable tool directory (.agents/skills/, etc.)  │
│  - agent-subagent       : Native agent persona config (.codex/agents/, etc.) │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┴───────────────────────────────────────┐
│                       3. Packaging & Selection Layer                         │
│  - Asset Selectors: Manifest Presets vs. Python Package Extras               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Resource Kinds and Specifications

### A. Guidance & Context Layer (Natural Language)

#### 1. `host-guidance-block`
- **Role**: A concise marker block injected into the consumer repository's root bootstrap file (e.g., `AGENTS.md` or `CLAUDE.md`) between managed delimiters:
  ```markdown
  <!-- DEVKIT:START -->
  ... pointers to installed package constitutions and CLI commands ...
  <!-- DEVKIT:END -->
  ```
- **Consumption**: Read by any agent session upon entering the repository.
- **Token Budget**: Strictly bounded (minimal tokens). Never contains project-specific policies or domain rules; acts purely as an orientation index pointing to installed package constitutions.
- **Target Location**: Host project root `AGENTS.md` / `CLAUDE.md`.

#### 2. `package-constitution`
- **Role**: The foundational architecture guide and constitution for a specific bundle or domain (e.g., repository rules, backend conventions, testing architecture).
- **Consumption**: Before the first skill from the bundle is performed, run `uv run devkit get-context <bundle>`. The response always includes the complete constitution when present. Load once per bundle in the current agent context, shared across all its skills; reload only when the guidance is no longer available, such as after compaction or in a new agent context.
- **Token Budget**: Strictly bounded (~50–100 lines). Summarizes core contracts and points to granular `package-instruction` documents.
- **Target Location**: `.devkit/managed/<bundle>/AGENTS.md`.

#### 3. `package-instruction`
- **Role**: Natural-language coding standards, API design rules, domain constraints, and architectural guidelines that require developer judgment.
- **Consumption**: **Progressive disclosure**, like agent skills: `get-context` exposes the YAML headers and readable file paths of synchronized instructions, never their bodies. The agent uses the names and descriptions to select relevant instructions and reads their full files only when needed. There is no category of instruction bodies eagerly included in the default context.
- **Token Budget**: Headers consume context when the bundle is first used; instruction bodies consume context only when selected.
- **Target Location**: `.devkit/managed/<bundle>/instructions/<name>.md`.
- **Format Requirements**: Single markdown document with English YAML frontmatter specifying `name` and `description` to enable discovery.

#### Bundle context delivery contract

- `get-context <bundle>` returns the full constitution (when present) and an instruction header catalog with paths. It returns content; the agent reads that output into its context.
- During sync, bundles with a constitution or selected instructions receive a generated prerequisite at the beginning of each deployed skill body, after YAML frontmatter. Managed and native skill copies receive the same prerequisite. Source files and authoring ZIP exports remain unchanged.
- The prerequisite explicitly requires **one command execution per bundle per current agent context**, not one per skill or turn. Other package entry points may explicitly request the same context using this command and the same deduplication rule.
- The command is stateless and always returns the complete response. It does not record that an agent has loaded it or suppress later output. Context deduplication is the agent's responsibility; automatic injection and exactly-once runtime enforcement are not guaranteed.
- Installation, listing, and skill discovery do not load this context. Instruction bodies remain on demand even after `get-context` runs. Presets restrict the instruction catalog; the constitution is included independently of presets.
- Playbook headers and bodies are excluded from `get-context`. An ordinary task request does not trigger playbook search.

#### 4. `package-playbook`
- **Role**: Procedures for occasional tasks, retrieved for reuse and extended through experience. Explicit, recurring execution flows belong to workflows; frequency alone does not turn a policy or judgment criterion into a playbook.
- **Consumption**: Search and use only after the user explicitly invokes the shared `devkit-playbook` skill for a task. Individual playbooks are not exposed in the default context or native skill catalog. References from instructions or other skills do not bypass this entry condition.
- **Format Requirements**: English YAML frontmatter with required `name` and `description`, plus an optional `aliases` string array. The body contains explicit `Prerequisites`, numbered `Step N` actions, and unambiguous completion conditions.
- **Target Location**: `.devkit/managed/<bundle>/playbooks/<slug>/SKILL.md`.

#### Instruction and playbook consumption boundaries

| Concern | `package-instruction` | `package-playbook` |
| --- | --- | --- |
| Purpose | Rules, constraints, and judgment criteria for the current work | Procedures for occasional tasks |
| Default disclosure | Headers and paths in the bundle's `get-context` response | No individual headers or bodies |
| Entry condition | The agent determines relevance from the instruction catalog | The user explicitly invokes `devkit-playbook` for the requested task |
| Full text | Read when relevant, before the affected action | Read after selecting a search candidate, before executing its procedure |
| Example | Compatibility requirements for database changes | Recovery steps for a particular database failure |

The explicit invocation applies to the requested task, not all future tasks in the
conversation. For example, "recover the database" alone does not initiate playbook
search; "use devkit-playbook to recover the database" does. Selected playbooks do
not replace package guidance: load their bundle's context if it is not already
available, then apply the constitution and any relevant instructions. The
once-per-bundle rule concerns context loading, not the procedure's execution state.

#### `devkit-playbook` entry point and search contract

Sync generates the shared entry skill when selected playbooks exist. Search and
metadata validation are implemented. Codex and Claude Code projections use their
native explicit-invocation settings; other runtimes rely on the skill's body
instructions until native support is verified. The search CLI itself does not
inspect conversation history to enforce user-only invocation.

1. Generate one shared `devkit-playbook` skill for the consumer project, rather
   than one skill per playbook. Its instructions require explicit user invocation;
   use native invocation controls where supported by the target runtime. Codex
   uses `agents/openai.yaml` with `policy.allow_implicit_invocation: false`; Claude
   Code uses `disable-model-invocation: true`. Removing the last selected playbook
   removes the generated skill. The managed copy lives under
   `.devkit/managed/_devkit/skills/devkit-playbook/`.
2. After invocation, convert the user's task into an English search query. User
   requests and conversation may use any language; search queries must be English.
3. Search synchronized playbooks across bundles, respecting asset selection.
   Implement BM25 within devkit without an additional search package. Initially
   index only `name`, `description`, and `aliases`, not procedure bodies. The
   command is `uv run devkit playbook search "<English query>"`; it returns parsed
   metadata and paths. Rebuild its in-memory index from receipt-owned entry files
   on each invocation. Directory playbooks index only their root `SKILL.md`, not
   supporting resources.
4. Return only candidate metadata and readable paths above a configurable minimum
   score, capped at top N and a total header-output budget. Scores rank lexical
   matches, not execution suitability; allow an empty result and calibrate the
   threshold with representative queries rather than treating it as confidence.
   Defaults: `--limit 5`, `--min-score 0.1`, `--max-bytes 8192`. The byte budget
   covers the complete JSON response and final newline; omit entire candidates
   rather than truncating individual headers. BM25 uses k1=1.5, b=0.75, positive
   IDF, and unique query terms; normalize case, Latin accents, and punctuation.
   Use aliases for alternate terms; no stemming or semantic expansion is applied.
5. Select an applicable candidate from its metadata, read the full procedure, and
   check prerequisites before executing it. A search match does not grant extra
   permission or make the procedure automatically applicable.
6. If no suitable playbook was found, complete the requested task using the
   applicable guidance. After completion, ask whether to add the reusable
   procedure as a playbook, presenting a draft and proposed bundle/source path.
   Do not persist it without the user's approval or write into generated managed
   copies; an authoring location must be available for the approved addition.

All frontmatter prose must be English. `aliases` provide
alternative English terms, abbreviations, and phrases that users may search for.
Product names and technical identifiers retain their canonical spelling. For
example:

```yaml
---
name: recover-postgres-replica
description: Recover a PostgreSQL replica after replication has stopped.
aliases: [postgres standby recovery, repair replica, replication failure]
---
```

Validate required fields and field types mechanically, reject duplicate/unknown
fields, and cap frontmatter at 4096 UTF-8 bytes. The supported fields are exactly
`name`, `description`, and `aliases`; classification tags are not supported.
English authoring is also an authoring/review requirement. Reject non-Latin letters
in headers and queries as a practical guard, without claiming this proves English
language use. Queries must contain search terms and fit within 512 UTF-8 bytes.
Playbooks may be single Markdown files or directories containing `SKILL.md` and
supporting resources. Validate metadata at bundle load and again when searching
synchronized files; preserve receipt ownership, hash checks, and transaction checks.

#### Follow-up TODO: optional query for bundle context

- Evaluate whether to support `devkit get-context <bundle> [query]` in the future;
  this is a review item, not an implemented command signature or a commitment.
- Consider using the optional English query to narrow instruction header exposure
  as catalogs grow. Preserve the full constitution in every response when present
  and keep instruction bodies on demand. Keep the existing no-query behavior.
- Review relevance, omitted-instruction risks, output budgets, and whether a new
  query should refresh the catalog despite the once-per-context loading rule.
- Preserve the explicit `devkit-playbook` entry boundary. Adding a context query
  must not silently enable playbook discovery during ordinary task handling.

---

### B. Mechanized Execution Layer (Code & Native Tooling)

#### 5. `governance-rule`
- **Role**: Invariants that **can and must be 100% mechanically verified** via AST parsing, regex, or static analysis without LLM hallucinations.
- **Consumption**: Evaluated out-of-band by `agent-rule-engine` during `just rules-check`, `agent-rules check`, or CI gates.
- **Token Budget**: Zero LLM context consumption unless violations are reported.
- **Target Location**: `.devkit/managed/<bundle>/rules/<category>/<rule>.py`.

#### 6. `agent-skill`
- **Role**: Reusable external capability packaged as an actionable tool directory containing a `SKILL.md` manifest, executable scripts (`0755`), references, and operational templates.
- **Consumption**: Projected into vendor-neutral or agent-specific tool roots (`.agents/skills/<name>/`, `.claude/skills/<name>/`) and invoked as functions/tools.
- **Target Location**: Native agent skill directories.

#### 7. `agent-subagent`
- **Role**: Standalone agent persona definition configuring system prompts, permissions, and tool access for delegated subagent tasks.
- **Consumption**: Read by agent runtimes when spawning child tasks.
- **Format Requirements**: Vendor-native format (`.toml` for Codex in `.codex/agents/<name>.toml`, `.md` for Claude Code in `.claude/agents/<name>.md`).
- **Target Location**: Native agent persona directories.

---

## 4. Placement Decision Matrix

When authoring new project guidance or developer tooling, follow this decision tree to select the appropriate resource kind:

```text
Q1: Can this invariant be 100% deterministically verified by machine code?
 ├─ YES ──> [ governance-rule ] (Python rule for agent-rule-engine)
 └─ NO  ──> Q2

Q2: Is it a reusable tool or executable script directory for the agent?
 ├─ YES ──> [ agent-skill ] (Projected into .agents/skills/ or .claude/skills/)
 └─ NO  ──> Q3

Q3: Is it an agent persona definition or subagent configuration file?
 ├─ YES ──> [ agent-subagent ] (Projected into .codex/agents/ or .claude/agents/)
 └─ NO  ──> Q4

Q4: Is it a task procedure rather than a rule or judgment criterion?
 ├─ YES, recurring explicit flow ──> [ workflow ] (Separate workflow design)
 ├─ YES, occasional procedure ──> [ package-playbook ] (Explicit devkit-playbook entry)
 └─ NO  ──> Q5

Q5: Is it a global orientation pointer required in root bootstrap files?
 ├─ YES ──> [ host-guidance-block ] (Injected into root AGENTS.md / CLAUDE.md)
 └─ NO  ──> Q6

Q6: Is it a high-level package constitution loaded before the first bundle skill?
 ├─ YES ──> [ package-constitution ] (Stored in package AGENTS.md)
 └─ NO  ──> [ package-instruction ] (Default for policies, coding standards, and judgment criteria)
```

---

## 5. Selection and Packaging Mechanics (Manifest Presets & Configuration)

Selecting which assets to install from a package requires an ergonomic and deterministic selection mechanism. During architectural evaluation, two approaches were compared: Python Package Extras (`package[feature]`) and Manifest Presets (`bundle.toml`) paired with declarative project configuration (`.devkit/config.toml`).

### Architecture Decision: Rejection of Python Package Extras

Python package extras (`[project.optional-dependencies]`) were evaluated and **formally rejected** for asset selection due to fundamental ecosystem impedance mismatches:

1. **Wheel Immutability & Asset Bundling**: Python wheels are static ZIP archives that unpack their entire contents into the environment. Package extras control external dependency resolution; they cannot selectively extract or omit static resource files within a single wheel.
2. **Missing Runtime Introspection**: Standard Python packaging metadata (`importlib.metadata`) does not expose which extras the consumer project requested for top-level dev dependencies. Resolving activated extras at runtime requires brittle, ad-hoc inspection of consumer `pyproject.toml` or `uv.lock` files.
3. **Micro-Package Explosion**: Achieving true selective installation through extras would require fracturing cohesive domain bundles into fragmented micro-wheels (e.g., `pkg-core`, `pkg-git-commits`, `pkg-skill-authoring`), dramatically increasing authoring friction, CI overhead, and cross-package version synchronization complexity.

### Adopted Architecture: Manifest Presets & Project Configuration

Asset filtering is governed by **bundle-level manifest presets** and **project-level declarative configuration**:

#### 1. Bundle Manifest Presets (`bundle.toml`)
Content bundles declare cohesive, purpose-specific asset subsets directly in their manifest (analogous to `specrig`'s modular preset bundles such as `git-commits` or `skill-authoring`):

```toml
# bundle.toml (Content Wheel)
schema = 1
name = "starter-workflow"
version = "0.1.0"

[[assets]]
id = "development"
kind = "instruction"
source = "instructions/development.md"

[[assets]]
id = "review-flow"
kind = "playbook"
source = "playbooks/review.md"

[[assets]]
id = "review"
kind = "skill"
source = "skills/review"

[presets.daily]
assets = ["development", "review-flow", "review"]
```

#### 2. Declarative Consumer Configuration (`.devkit/config.toml`)
Consumer repositories declare their desired baseline presets and agents in a Git-tracked project configuration file:

```toml
# .devkit/config.toml (Consumer Project, Git-tracked)
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter-workflow = "daily"
```

Running `uv run devkit sync` automatically converges the workspace to the declared configuration without requiring developers or CI pipelines to pass manual CLI flags.

#### 3. Configuration Precedence Matrix
Selections are resolved using a clear three-tier hierarchy:

1. **CLI Overrides**: Explicit CLI flags (`--preset bundle:name`, `--all-assets`, `--agent name`, `--no-agents`) take highest priority for ad-hoc experimentation and scripting.
2. **Project Configuration (`.devkit/config.toml`)**: Repository-level baseline committed to Git; governs clean checkouts and default `devkit sync` runs.
3. **Installation Receipt (`.devkit/installation.json`)**: Preserves previously synchronized selections when neither CLI flags nor `config.toml` specify restrictions.

---

## 6. Summary Comparison Table

| Resource Kind | Tier / Layer | Typical File Form | Consumption Timing | Token / Context Impact | Physical Destination |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`host-guidance-block`** | Guidance | Injected Marker Block | Session bootstrap | Minimal pointer index | Root `AGENTS.md` / `CLAUDE.md` |
| **`package-constitution`** | Guidance | Markdown (~50–100 lines) | Before first bundle skill | Bounded (~100 lines) | `.devkit/managed/<bundle>/AGENTS.md` |
| **`package-instruction`** | Guidance | Markdown (`instructions/*.md`) | Headers on first bundle use; bodies on demand | Header catalog plus selected bodies | `.devkit/managed/<bundle>/instructions/` |
| **`package-playbook`** | Guidance | Metadata and checklist (`playbooks/<slug>/SKILL.md`) | Explicit user invocation of `devkit-playbook`, then search and selection | Bounded candidate headers; selected body only | `.devkit/managed/<bundle>/playbooks/` |
| **`governance-rule`** | Mechanized | Python (`rules/*.py`) | Linters / `just rules-check` | **0 tokens** (pure code) | `.devkit/managed/<bundle>/rules/` |
| **`agent-skill`** | Mechanized | Directory (`skills/<slug>/`) | Tool/function invocation | Tool registry metadata | Projected (`.agents/skills/`, etc.) |
| **`agent-subagent`** | Mechanized | Config (`agents/<slug>.{toml,md}`) | Subagent delegation | Persona config on load | Projected (`.codex/agents/`, etc.) |
