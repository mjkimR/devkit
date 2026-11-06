# Multi-Agent Swarm Architectures and Role Catalogs for Adaptive Development

## 1. Overview and Intent

This reference material investigates multi-agent architectures, role-catalog frameworks, and subagent orchestration patterns
to inform the design of an autonomous agent-swarm rapid development mode under `adaptive-dev`. While devkit's primary
delivery model—Spec-Driven Development (SDD)—provides high governance, traceability, and zero phantom completion through
strict sequential stages (`spec` → `plan` → `tasks` → `develop` → `review` → `sync`), developers frequently require a rapid,
high-throughput development mode ("agent swarm") for prototypes, exploratory features, and rapid spikes without heavy ceremony.

Because this development capability is repository-wide and impacts everyday engineering workflows, strict skill isolation
(as applied to narrow single-utility skills like `deep-research`) is not the only viable approach. A spectrum of structural
models—ranging from pure skill-local roles to archetype-subagent hybrids—warrants comparative evaluation.

This survey compares six upstream open-source references, evaluates four concrete subagent/role structuring models, and defines
how devkit's native primitives (git worktrees, `just test-affected`, and execution isolation) solve the primary failure modes
of multi-agent swarms.

---

## 2. Upstream Reference Survey

The following repositories were examined on 2026-11-06 as architectural and operational references:

### 2.1 FoundationAgents/MetaGPT: SOP-Driven Multi-Agent Framework
- **Repository**: [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)
- **Core Philosophy**: "Code = SOP(Team)". Encodes Standard Operating Procedures into LLM-based agent roles.
- **Key Mechanics**:
  - Roles: Product Manager (generates PRD), Architect (generates system design and API interfaces), Project Manager (decomposes tasks into a dependency graph), Engineer (writes source code and unit tests), and QA Engineer (designs test cases and runs execution).
  - Environment & Message Pool: Agents share an environment where messages carry typed payloads. Roles observe (`_watch`), evaluate relevance (`_observe`), and trigger actions (`_react`).
- **Strengths**:
  - Clear sequential-to-parallel progression: Waterfall analysis flows cleanly into concurrent module implementation.
  - Interface-first design: Architect specifies API signatures and data structures before Engineers write implementation code, minimizing interface mismatches.
- **Limitations & Friction Points for devkit**:
  - Monolithic Python runtime dependency: MetaGPT requires a heavy Python daemon, API servers, and complex orchestration libraries that conflict with devkit's lightweight CLI-driven packaging.
  - High token cost and pipeline latency: Running every role end-to-end for small-to-medium changes introduces substantial token overhead.
  - Weak filesystem-level collision control: Relies primarily on prompt instructions to avoid file overwrite conflicts rather than filesystem/git isolation.

### 2.2 code-yeongyu/oh-my-openagent & Yeachan-Heo/oh-my-codex: Coding Agent Harnesses
- **Repositories**: [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent), [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex)
- **Core Philosophy**: Practical developer harnesses and command wrappers for LLM coding environments (OpenAgent, OpenAI Codex, Antigravity, Claude Code).
- **Key Mechanics**:
  - Modular persona prompts and system instructions categorized by task kind (planner, implementer, reviewer, refactorer).
  - Shortcut slash commands and streamlined prompt injection.
  - Lead agent / orchestrator pattern: A primary agent interacts with the user, decomposes requirements, and invokes targeted sub-prompts.
- **Strengths**:
  - Low friction: Operates directly within existing coding agent interfaces without external daemons.
  - High developer ergonomics: Pragmatic commands focused on shipping code fast.
- **Takeaways for devkit**:
  - Keep the invocation interface as a natural slash command/skill (`/adaptive-dev` or `/adaptive-swarm`).
  - Maintain an orchestrator that stays in continuous dialogue with the user while dispatching background workers.

### 2.3 msitarzewski/agency-agents: Domain Persona Catalog
- **Repository**: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
- **Core Philosophy**: A comprehensive, modular library of specialized agent personas (50+ markdown files) spanning Engineering, Design, Testing, Marketing, and Operations.
- **Key Mechanics**:
  - Each persona is a standalone Markdown document specifying identity, core strengths, thinking style, boundaries, and concrete output deliverables.
  - Roles can be mixed and matched to form dynamic virtual agencies (e.g., UX Architect + Frontend Dev + Reality Checker).
- **Strengths**:
  - Prompt modularity: Adding or updating a role requires editing only a single Markdown file.
  - Strong behavioral boundaries: Prompts explicitly instruct roles on what *not* to do (e.g., reality checker does not write production code).
- **Takeaways for devkit**:
  - Persona modularity maps directly to devkit's bundle `roles/*.md` pattern.
  - Roles should be behavioral contracts loaded dynamically rather than monolithic hardcoded agent classes.

### 2.4 VoltAgent/awesome-codex-subagents & wshobson/agents: Developer Subagent Libraries
- **Repositories**: [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents), [wshobson/agents](https://github.com/wshobson/agents)
- **Core Philosophy**: Curated subagent prompt templates specifically optimized for AI coding assistants.
- **Key Mechanics**:
  - Task-specific subagents: `refactoring-specialist`, `test-automator`, `security-auditor`, `api-designer`, `bug-hunter`.
  - Precise boundary definitions: Each subagent template defines strict input parameters, expected file touch boundaries, and exact output formats (e.g., unified diffs, test logs).
- **Strengths**:
  - Clear separation of concerns: Testing agents focus exclusively on breaking code; refactoring agents focus on structural cleanliness without changing behavior.
  - Ready-to-use prompt patterns for coding tasks.

---

## 3. Comparative Evaluation of Subagent & Role Architecture Models

Because rapid development is a core, repository-wide activity rather than a narrow one-off tool, we evaluate four
architectural models balancing global footprint, execution specialization, and catalog packaging:

```mermaid
flowchart TD
    subgraph Model1 ["Model 1: Pure Skill-Local Roles"]
        M1_Coord["Coordinator"] -->|"Reads on demand"| M1_Roles["roles/*.md<br/>(architect, builder, qa)"]
        M1_Coord -->|"Spawns"| M1_Gen["General Subagent<br/>(self / inherit)"]
    end

    subgraph Model2 ["Model 2: Archetype Subagents + Role Overlay (Hybrid A)"]
        M2_Coord["Coordinator"]
        M2_Arch["Registered Archetype Subagents<br/>• swarm-planner (Read-only, Pro)<br/>• swarm-worker (Write tools, Flash)<br/>• swarm-verifier (Exec/Bash, Flash)"]
        M2_Coord -->|"Dispatches with role.md payload"| M2_Arch
        M2_Arch -->|"Loads role context"| M2_Roles["roles/*.md library"]
    end

    subgraph Model3 ["Model 3: Core Global + Long-Tail Catalog (Hybrid B)"]
        M3_Coord["Coordinator"]
        M3_Core["Registered Core Subagents<br/>• architect<br/>• builder<br/>• qa-tester"]
        M3_LongTail["roles/*.md (Catalog Library)<br/>• security-auditor<br/>• db-migrator<br/>• ui-polisher"]
        M3_Coord -->|"Direct invocation"| M3_Core
        M3_Coord -->|"On-demand delegation"| M3_LongTail
    end

    subgraph Model4 ["Model 4: Fully Registered Static Subagents"]
        M4_Coord["Coordinator"]
        M4_All["Registered Subagents (All 10+ Roles)<br/>• architect, builder, qa, reviewer,<br/>refactorer, doc-writer, security, etc."]
        M4_Coord -->|"Invokes by TypeName"| M4_All
    end
```

### Detailed Trade-Off Matrix

| Evaluation Dimension | Model 1: Pure Skill-Local | Model 2: Archetype Subagent + Role Overlay (Hybrid A) | Model 3: Core Global + Long-Tail Catalog (Hybrid B) | Model 4: Fully Registered Static Subagents |
| :--- | :--- | :--- | :--- | :--- |
| **Global Prompt Token Overhead** | **Zero**: No subagent metadata injected into unrelated sessions. | **Minimal**: Only 2~3 functional archetypes registered (e.g. `swarm-worker`, `swarm-verifier`). | **Moderate**: 3~4 core subagents registered globally. | **High / Severe**: 10+ subagent descriptions injected into every session prompt. |
| **Native Tool Sandboxing** | None: General subagents inherit all parent tools; boundaries are prompt-only. | **High**: Archetypes have native tool restrictions (e.g. `swarm-planner` has no write tools). | **High**: Core subagents have tailored tool allocations. | **High**: Every subagent has dedicated native permissions. |
| **Model Profile Specialization** | Limited: Subagents inherit the coordinator's model tier. | **High**: Archetypes map to optimal models (e.g., Pro for Planner, Flash for high-speed Builders). | **High**: Core subagents declare default models. | **High**: Granular model selection per persona. |
| **Persona Extensibility & Library Growth** | **Unlimited**: Drop any Markdown file into `roles/` without modifying global config. | **Unlimited**: Archetypes load any specialized role contract dynamically at runtime. | **Hybrid**: Core roles fixed; long-tail roles expanded via `roles/`. | **Rigid**: Every new persona requires modifying global agent config / projections. |
| **Cross-Platform Portability** | **Complete**: Plain Markdown files loadable by any agent runner. | **Good**: Requires only basic host subagent archetype configuration. | **Moderate**: Requires host subagent registration for core roles. | **Poor**: Highly coupled to platform-specific subagent config syntax. |
| **Direct User Ergonomics** | Coordinator-mediated only; user cannot invoke child roles directly in chat. | Coordinator-mediated; archetypes invoke with role payload. | **High**: User can invoke `@architect` or `@qa-tester` directly in any chat session. | **High**: Direct single-agent invocation supported. |

### Architectural Insights

1. **Why Pure Skill-Local (Model 1) Can Be Overly Constrained for Daily Development**:
   While Model 1 was optimal for `deep-research` (a specialized, bounded research tool), development work benefits greatly from
   running high-speed parallel coders on faster/cheaper models (e.g., `flash`) while keeping planning on reasoning models (`pro`).
   Pure inheritance forces all child workers to run on the parent agent's model tier.
2. **The Power of Archetype Subagents + Role Overlays (Model 2)**:
   By registering only 3 functional capability archetypes (`planner`, `worker`, `verifier`), devkit preserves global prompt cleanliness
   while gaining native tool gating (read-only planning vs. write-enabled workers) and cost-effective model routing. The infinite variety
   of domain personas from `agency-agents` or `awesome-codex-subagents` can be injected as runtime role overlays.
3. **The Pragmatism of Core Global + Long-Tail Catalog (Model 3)**:
   Developers often want to trigger a quick `@qa-tester` or `@architect` review directly in chat without launching a full swarm workflow.
   Registering the 3 primary roles globally while managing specialized personas via `roles/` offers high daily ergonomics.

---

## 4. The Core Failure Mode of Multi-Agent Swarms & devkit's Solution

### 4.1 Why Pure Prompt-Based Swarms Fail in Real Projects
1. **Concurrent File Write Collisions (Race Conditions)**: When 3+ agents write code simultaneously in the same working directory, they overwrite each other's edits, produce syntax errors, and create git merge chaos.
2. **Interface Drift**: Agent A assumes an API returns JSON; Agent B implements it returning a string or different field names because no binding interface contract was established before implementation.
3. **Phantom Completion & Test Rot**: Workers report "all tasks completed" without running local compilers, type checkers, or test suites, leaving broken builds on the main branch.

### 4.2 devkit's Architectural Countermeasures
devkit possesses unique primitives that turn theoretical swarms into reliable development engines:

```mermaid
flowchart TD
    User["User Intent / Feature Request"] --> Lead["Swarm Lead (Coordinator)"]
    
    subgraph Planning ["1. Sprint Decomposition"]
        Lead --> Architect["Role: System Architect"]
        Architect --> Contract["Sprint Contract<br/>• Interface Signatures<br/>• File Touch Boundaries (_Boundary)"]
    end
    
    subgraph Execution ["2. Parallel Swarm Build (Worktree Isolated)"]
        Contract --> Worker1["Builder 1 (Worktree A)<br/>packages/core/..."]
        Contract --> Worker2["Builder 2 (Worktree B)<br/>packages/cli/..."]
        Contract --> Worker3["Builder 3 (Worktree C)<br/>tests/..."]
    end
    
    subgraph Verification ["3. Adversarial QA & Integration"]
        Worker1 --> Merge["Merge to Swarm Branch"]
        Worker2 --> Merge
        Worker3 --> Merge
        Merge --> QA["Role: QA Tester / Challenger"]
        QA --> TestRun["Run: just test-affected<br/>Run: just check<br/>Run: just lint"]
        TestRun -- "Failures Found" --> Worker1
        TestRun -- "All Pass" --> Reviewer["Role: Reviewer / Integrator"]
    end
    
    Reviewer --> Commit["Landed Commit + .devkit/adaptive-dev.md"]
```

1. **Explicit File Boundaries (`_Boundary`)**:
   - The Architect role partitions the work such that parallel builders operate on strictly disjoint file sets (e.g., Builder A owns `packages/pkg-a/src/`, Builder B owns `packages/pkg-b/src/`).
2. **Git Worktree Isolation (`devkit worktree`)**:
   - Where file overlap is unavoidable, builders run in dedicated git worktrees created via `devkit worktree create`. Changes are integrated systematically rather than written concurrently to a single working tree.
3. **Deterministic Local Verification (`just test-affected`)**:
   - Instead of trusting LLM assertions of correctness, the QA Tester executes devkit's native verification pipeline (`just test-affected`, `just check`, `just lint-check`). If tests fail, the failure logs are routed back to the specific Builder responsible.
4. **Lightweight Context Retention**:
   - Rather than creating heavy SDD artifacts (`spec.md`, `plan.md`, `tasks.md`, `reconcile.md`, `envelopes/*.yaml`), the swarm records its state in `.devkit/adaptive-dev.md` with active facts, completed changes, and open questions.

---

## 5. Synthesis and Recommendations

1. **Retain Open Evaluation of the Hybrid Models**:
   Proposal `PROP-adaptive-swarm-development` must not prematurely lock into Model 1 (pure skill-local). Planning should evaluate
   Model 2 (Archetype Subagents + Role Overlay) and Model 3 (Core Global + Long-Tail Catalog) alongside Model 1 during spike execution.
2. **Adopt MetaGPT's SOP Flow without its Heavy Runtime**:
   Use a 4-stage pipeline: (1) Architecture & Boundary Contract, (2) Parallel Builder Implementation, (3) QA & Affected Test Execution, (4) Integration & Context Record.
3. **Core Role Set**:
   - `swarm-coordinator` (Skill entrypoint)
   - `roles/architect.md` (Interface & Boundary Designer)
   - `roles/builder.md` (Implementation Worker)
   - `roles/qa-tester.md` (Test Execution & Edge Case Attacker)
   - `roles/reviewer.md` (Code Quality & Diff Sanity Reviewer)
4. **Retain Clear Separation from SDD**:
   Adaptive swarm development is an accelerator for iteration and exploratory builds; SDD remains canonical for durable, highly governed systems. A swarm-built prototype can graduate into SDD at any point via the standard adoption procedure.
