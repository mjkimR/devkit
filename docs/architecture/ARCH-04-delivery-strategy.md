---
id: ARCH-04-delivery-strategy
title: Delivery Strategy
summary: "Macro delivery architecture, Backlog-Planning-Development lifecycle, three-axis classification, execution modes, and decision boundaries."
status: active
created_at: 2026-10-21
---

# [ARCH-04-delivery-strategy] Delivery Strategy

- **arc42**: §4 Solution Strategy
- Boundaries: `ARCH-04-1-ecosystem-boundaries`. Policy: `ARCH-04-2-delivery-policy`.
- Living Spec: `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`. Stories: `US-route-development-intent`, `US-drive-development-to-integration`.

---

## 1. Delivery Lifecycle

Every software change in `devkit` traverses three high-level activities: **Backlog → Planning → Development**.

```mermaid
flowchart LR
    subgraph BL["Backlog — direct mode"]
        direction TB
        B1([Intake Request]):::human --> B2[Classify axes & manage drafts / milestones]:::host
    end
    subgraph PL["Planning"]
        direction TB
        PI[Inline Planning<br/>intent agreement<br/>direct mode]:::host
        PP[Proposal Planning<br/>draft → reviewing → accepted<br/>three modes]:::host
    end
    subgraph DV["Development — three modes"]
        direction TB
        D1[(Agreed Intent Unit)]:::store --> D2[Workflow progression<br/>develop, review, verify<br/>spec Unit includes reconcile]:::host
        D2 --> D3([dev-integration]):::human
        D3 --> D4[(Merge & cleanup)]:::store
    end
    B2 -->|session / start now| PI
    B2 -->|spec / start now| PI
    B2 -->|proposal / queue| PP
    PI -->|spec new / record intent| D1
    PI -->|session / no Unit| D2
    PP -->|handoff / carried approvals| D1
    D2 -.->|blocker / close & draft| B2

    classDef human fill:#fde68a,stroke:#b45309,color:#111
    classDef host fill:#bfdbfe,stroke:#1d4ed8,color:#111
    classDef store fill:#f5f5f4,stroke:#78716c,color:#111
```

| Activity | Input | Output | Applicable Modes | Key Decisions |
| :--- | :--- | :--- | :--- | :--- |
| **Backlog** | User requests, open feedback | Tentative classification, draft proposals, milestone anchors | `direct` | Classification confirmation, draft intake |
| **Planning** | Classified request | Agreed intent in conversation (`session`), spec Unit (`spec`), or accepted proposal (`proposal`) | Inline: `direct`<br/>Proposal: `direct`, `local-orchestrated`, `cloud-pr` | `plan-intent`, `plan-accept` (proposal) |
| **Development** | Agreed intent (Unit or session agreement) | Verified changes, reports, Living Spec & reconcile updates | `direct`, `local-orchestrated`, `cloud-pr` | `proposal-handoff`, `dev-integration` |

Development always starts from agreed intent. Unit-bearing paths evaluate stage exit conditions with `devkit workflow next`, while `session` tasks complete within conversation context without durable envelopes or reconcile files.

---

## 2. Classification Axes

Tasks are classified across three orthogonal axes:

```mermaid
flowchart LR
    subgraph CLS["Task Classification — determined in Backlog"]
        direction TB
        K[task-kind<br/>feature · bugfix]:::host
        D[planning-depth<br/>session · spec · proposal]:::host
        K --> D
    end
    subgraph RUN["Activity Execution — chosen per activity"]
        direction TB
        M[Execution Mode<br/>direct · local-orchestrated · cloud-pr]:::host
        E[activity-effort<br/>low · medium · high]:::host
    end
    subgraph POL["Policy — .devkit/config.toml"]
        direction TB
        P1[(worktree.pull_request<br/>auto · required)]:::store
        P2[(workflow.approvals<br/>ask · auto)]:::store
        P3[(tool.spec.worktree<br/>auto · required)]:::store
    end
    CLS -->|per activity| RUN
    POL -.->|applies across combinations| CLS
    POL -.->|effort does not lower policy| RUN

    classDef host fill:#bfdbfe,stroke:#1d4ed8,color:#111
    classDef store fill:#f5f5f4,stroke:#78716c,color:#111
```

### 2.1 `task-kind`
- `feature` (default): New behavior or intentional modifications to existing capabilities.
- `bugfix`: Defect violating an agreed contract. Requires characterization (current, expected, preserved behavior) and reproduction evidence (Red → Green).

### 2.2 `planning-depth`
- `session`: No contract or Living Spec changes required; fully verifiable within one session without durable artifacts.
- `spec`: Contract changes with an already clear direction; bound to a spec Unit via inline Planning.
- `proposal`: Uncertain direction requiring multi-option exploration, spikes, or architectural PADRs.

| Depth × Kind | `feature` | `bugfix` |
| :--- | :--- | :--- |
| **`session`** | `sdd-session-feature` | `sdd-session-bugfix` |
| **`spec`** | `sdd-spec-feature` | `sdd-spec-bugfix` |
| **`proposal`** | `sdd-proposal` → `sdd-spec-feature` | `sdd-proposal` → `sdd-spec-bugfix` |

```mermaid
flowchart LR
    S["session<br/>in-memory / conversation"]:::host -->|contract or doc changes discovered| SP["spec<br/>spec Unit on dev-slug"]:::host
    SP -->|direction unclear / architectural tradeoffs| P["proposal<br/>proposal Unit on plan-slug"]:::host
    S -->|direction unclear / architectural tradeoffs| P
    P -->|accepted & handed off| SP

    classDef host fill:#bfdbfe,stroke:#1d4ed8,color:#111
```

Depth may escalate during Development (`session → spec`) when contract or documentation changes are discovered. Lowering depth is prohibited, with the sole exception of session reclassification of unreviewed draft proposals at pickup (`ADR-session-reclassification-of-a-queued-draft`).

### 2.3 `activity-effort`
Determines the thoroughness of inspection and review per activity (`low`, `medium`, `high`, default `medium`):
- `low`: Self-review and self-verification by the working actor.
- `medium`: Mandatory initial `code-reviewer` subagent execution. Conditional self-verification for `reconcile-reviewer` only when contracts and diff coverage are provably unambiguous.
- `high`: Bounded re-review loop (`ADR-bounded-high-effort-review-loop`) reviewing whole batches, stopping when rounds find no issues or only minor fixes. Mandatory independent `reconcile-reviewer`.

---

## 3. Unit Model and Boundaries

A **Unit** is an isolated directory containing an anchor file bound to a delivery workflow:
- **Proposal Unit**: `docs/proposals/PROP-<slug>/` anchored by `proposal.md` bound to `sdd-proposal`.
- **Spec Unit**: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` anchored by `spec.md` bound to `sdd-spec-<task-kind>`.

```mermaid
flowchart LR
    subgraph BASE["Base Branch"]
        direction TB
        P0[(proposal Unit<br/>draft)]:::store
        P2[(proposal Unit<br/>accepted)]:::store
        S2[(spec Unit<br/>completed history)]:::store
    end
    subgraph PLAN["plan-slug Branch"]
        P1[(proposal Unit<br/>reviewing)]:::store
    end
    subgraph DEV["dev-slug Branch"]
        S1[(spec Unit<br/>proposal deleted on handoff)]:::store
    end
    P0 -->|Start Planning| P1
    P1 -->|Accept & merge| P2
    P2 -->|Start Development<br/>handoff = replace unit| S1
    S1 -->|dev-integration & merge<br/>reconciled to base| S2

    classDef store fill:#f5f5f4,stroke:#78716c,color:#111
```

A slug identifies the line of work across activities, while each activity runs in its respective Unit and branch. Units never nest, and `session` tasks operate without a Unit.

---

## 4. Decision Boundaries and Gates

The four decision gates represent explicit authorization boundaries in `[workflow.approvals]`:

| Gate | Scope | Authority & Delegation |
| :--- | :--- | :--- |
| `plan-intent` | Authorizes initial scope, goal, and classification | Explicit instruction satisfies `plan-intent` without duplicate prompting; supports `ask` or `auto`. |
| `plan-accept` | Accepts proposal direction and merges Planning branch | Defaults to `ask`; supports policy delegation (`auto`). Supports direct acceptance in Backlog. |
| `proposal-handoff`| Authorizes starting Development and Unit transition | Defaults to `ask`; supports policy delegation (`auto`). Schedulable independently of `plan-accept`. |
| `dev-integration` | Authorizes merging verified Development changes | Evaluated by `approvals.dev-integration` (`ask` or `auto`). Requires passing verification and reconcile. |

Unrecoverable failures (retry caps, tool crashes, semantic conflicts) transition to the `exception` workflow stage (`exception: true`). Unlike decision gates, `exception` is a workflow stage requiring explicit human handling and cannot be delegated or configured in `[workflow.approvals]`.

---

## 5. Core Architectural Principles

1. **State lives in branches**: Workers are one-shot entities; incoming workers resume execution purely from committed branch state, Unit files, and envelopes.
2. **The working actor records its own evidence**: Subagents are read-only; the invoking actor records envelope findings and decision records.
3. **Autonomous progression within agreed boundaries**: Actors proceed on recommended choices within agreed intent; non-blocking improvements become feedback, while agreement breaches halt as structured problems.
4. **Nested execution**: Host delegates to workers, and workers nest delegated review subagents (depth 2). Environments incapable of nesting use `direct` mode.

