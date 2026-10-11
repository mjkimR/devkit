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
│  - package-playbook     : Multi-step procedural checklist (workflows)       │
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
- **Format Requirements**: Single markdown document with YAML frontmatter specifying `name` and `description` to enable semantic discovery.

#### Bundle context delivery contract

- `get-context <bundle>` returns the full constitution (when present) and an instruction header catalog with paths. It returns content; the agent reads that output into its context.
- During sync, bundles with a constitution or selected instructions receive a generated prerequisite at the beginning of each deployed skill body, after YAML frontmatter. Managed and native skill copies receive the same prerequisite. Source files and authoring ZIP exports remain unchanged.
- The prerequisite explicitly requires **one command execution per bundle per current agent context**, not one per skill or turn. Other package entry points may explicitly request the same context using this command and the same deduplication rule.
- The command is stateless and always returns the complete response. It does not record that an agent has loaded it or suppress later output. Context deduplication is the agent's responsibility; automatic injection and exactly-once runtime enforcement are not guaranteed.
- Installation, listing, and skill discovery do not load this context. Instruction bodies remain on demand even after `get-context` runs. Presets restrict the instruction catalog; the constitution is included independently of presets.

#### 4. `package-playbook`
- **Role**: Multi-step operational workflows that require state tracking, ordered execution steps, and verification checkpoints (e.g., database migration, release checklist, triage procedures).
- **Consumption**: Triggered intentionally when executing a designated operational task.
- **Format Requirements**: Structured checklist containing explicit `Prerequisites`, numbered `Step N` actions, and unambiguous termination conditions.
- **Target Location**: `.devkit/managed/<bundle>/playbooks/<slug>/SKILL.md`.

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

Q4: Is it a multi-step operational procedure with an ordered checklist?
 ├─ YES ──> [ package-playbook ] (Stored in playbooks/<slug>/SKILL.md)
 └─ NO  ──> Q5

Q5: Is it a global orientation pointer required in root bootstrap files?
 ├─ YES ──> [ host-guidance-block ] (Injected into root AGENTS.md / CLAUDE.md)
 └─ NO  ──> Q6

Q6: Is it a high-level package constitution loaded before the first bundle skill?
 ├─ YES ──> [ package-constitution ] (Stored in package AGENTS.md)
 └─ NO  ──> [ package-instruction ] (Default for policies, coding standards, and judgment criteria)
```

---

## 5. Selection and Packaging Mechanics (Presets vs. Extras)

Selecting which assets to install from a package requires an ergonomic selection mechanism. Two design options are currently evaluated:

### Option 1: Manifest Presets (`bundle.toml`)
- **Mechanism**: Bundles declare named subsets in their manifest:
  ```toml
  [presets.daily]
  assets = ["development", "review-flow", "review"]
  ```
- **CLI Workflow**:
  ```bash
  uv run devkit sync --preset team:daily
  ```
- **Strengths**:
  - Fine-grained control within a single content wheel.
  - Native authoring ergonomics; does not require multiple Python distribution wheels.
  - Allows consumer repositories to combine assets dynamically without package reinstallation.

### Option 2: Python Package Extras (`package[feature]`)
- **Mechanism**: Leverage Python packaging standards via `pyproject.toml`:
  ```toml
  [project.optional-dependencies]
  daily = ["package-b-playbooks", "package-b-rules"]
  ```
- **CLI Workflow**:
  ```bash
  uv add --dev "team-bundle[daily]"
  uv run devkit sync
  ```
- **Strengths**:
  - Aligns with standard Python packaging (`uv.lock` natively locks feature sets).
  - Eliminates custom preset filtering syntax in `bundle.toml`.
- **Considerations**:
  - Python wheels traditionally bundle all static resource files within the package directory; omitting files based on extras requires either multiple separate sub-packages or dynamic wheel inspection.

### Current Position
Both options remain open architectural alternatives. The core resource taxonomy defines **what** can be distributed, while selection mechanics (`presets` vs. `extras`) govern **how** subsets are filtered.

---

## 6. Summary Comparison Table

| Resource Kind | Tier / Layer | Typical File Form | Consumption Timing | Token / Context Impact | Physical Destination |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`host-guidance-block`** | Guidance | Injected Marker Block | Session bootstrap | Minimal pointer index | Root `AGENTS.md` / `CLAUDE.md` |
| **`package-constitution`** | Guidance | Markdown (~50–100 lines) | Before first bundle skill | Bounded (~100 lines) | `.devkit/managed/<bundle>/AGENTS.md` |
| **`package-instruction`** | Guidance | Markdown (`instructions/*.md`) | Headers on first bundle use; bodies on demand | Header catalog plus selected bodies | `.devkit/managed/<bundle>/instructions/` |
| **`package-playbook`** | Guidance | Checklist (`playbooks/<slug>/SKILL.md`) | Workflow command trigger | On-demand workflow | `.devkit/managed/<bundle>/playbooks/` |
| **`governance-rule`** | Mechanized | Python (`rules/*.py`) | Linters / `just rules-check` | **0 tokens** (pure code) | `.devkit/managed/<bundle>/rules/` |
| **`agent-skill`** | Mechanized | Directory (`skills/<slug>/`) | Tool/function invocation | Tool registry metadata | Projected (`.agents/skills/`, etc.) |
| **`agent-subagent`** | Mechanized | Config (`agents/<slug>.{toml,md}`) | Subagent delegation | Persona config on load | Projected (`.codex/agents/`, etc.) |
