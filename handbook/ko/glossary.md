---
generated: true
---
# 용어집

<!-- handbook:provenance -->
> 소스 커밋 `f115e96c8059` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-11에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated page -->
devkit 문서가 쓰는 용어이며 Living Spec 용어집에서 생성됩니다.

### 1. Distribution and Packaging

| 용어 | 번역어 | 정의 | 출처 |
| :--- | :--- | :--- | :--- |
| **Release version** | 릴리즈 버전 | One human-selected X.Y.Z assigned to changed distributions and their exact-pin dependents; excludes unchanged package and bundle identities. | `ADR-selective-package-versions` |
| **Package version** | 패키지 버전 | A distribution's actual static version, retained when its shipped payload is unchanged; excludes the newest release number. | `ADR-selective-package-versions` |
| **Release inventory** | 릴리즈 인벤토리 | Completed artifact provenance and compatible actual package versions for one release; excludes an unpublished preparation plan. | `ARCH-07-deployment` |
| **devkit bundle** | devkit 번들 | devkit's unit of distributable agent assets, declared in `bundle.toml`. Bundles ship instructions, playbooks, rules, workflows, subagents, gates, and guidance fragments. | `CAP-DIST-manifest-spec` |
| **Bundle source snapshot** | 번들 소스 스냅샷 | Repository-committed source copy of a complete supported content provider, with provenance and explicit refresh through an ordinary local package; excludes governance Snapshot run evaluation and runtime-package vendoring. | `CAP-DIST-in-repo-bundles` |
| **Subagent model level** | 서브에이전트 모델 수준 | Distribution-owned preset (minimal, compact, lean, standard, deep or maximal) selecting native model family and supported effort for a common role contract, with inherit as the default; excludes delivery activity-effort and runtime model routing. | `CAP-DIST-agent-projections` |
| **Preset** | 프리셋 | A named asset selection of a bundle (e.g. `core`, `default`). | `CAP-DIST-manifest-spec` |
| **Managed files** | 관리 파일 | Pristine synchronized copies under `.devkit/managed/<bundle>/`; never edited by hand. | `CAP-DIST-workspace-ownership` |
| **Projections** | 프로젝션 | Native agent files projected into `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, etc. | `CAP-DIST-agent-projections` |
| **Receipt** | 설치 기록 | `.devkit/installation.json`: records every deployed file, checksum, and origin bundle in one transaction. | `CAP-DIST-sync-and-transactions` |
| **Project override** | 프로젝트 오버라이드 | Local adaptation of an upstream asset placed under `.devkit/overrides/`, tracked against an upstream baseline. | `CAP-DIST-workspace-ownership` |
| **Alias** | 별칭 | A previous or alternate identifier of a document (`aliases` in its frontmatter) or of a playbook (a previous asset ID in its header's `aliases`). It resolves to the canonical document or playbook and counts as a declaration; it is identity, not a reference. | `CAP-DOCS-document-model` |

### 2. Governance and Verification

| 용어 | 번역어 | 정의 | 출처 |
| :--- | :--- | :--- | :--- |
| **Governance rule** | 거버넌스 규칙 | A deterministic invariant evaluated by `devkit rules check` with optional automatic repair (`devkit rules fix`). | `CAP-GOV-rules-engine` |
| **Per-file rule facts** | 파일별 규칙 팩트 | Immutable rule-owned syntax extracted from one logical Python path; persistent reuse is keyed by cached source bytes, explicit extraction context and executing-source fingerprint. Excludes shared AST objects and cross-file judgments. | `CAP-GOV-rule-authoring` |
| **Rule phase** | 규칙 페이즈 | Execution category of a rule: `syntax`, `hygiene`, `linter`, `contract`. | `CAP-GOV-rules-engine` |
| **Snapshot run** | 스냅샷 실행 | Rule execution against an exact Git snapshot: staged tree (`devkit rules check --staged`) or base commit comparison (`--ci --base <ref>`). | `CAP-GOV-rules-engine` |
| **Steering document** | 스티어링 문서 | An ID-free Markdown file directly in `docs/steering/` (project-wide background: the glossary, product, style) or in a registered namespace's `docs/packages/<name>/steering/` (package background), one per topic, with only `title` and `summary` frontmatter; `devkit get-context docs` lists the root ones in each agent context and a namespace's when the working directory is inside that package, and an agent reads a body when a decision concerns its summary. Excludes contracts (capabilities, use cases, architecture, decisions), evidence (materials) and package glossaries. | `ADR-steering-documents`, `ADR-namespace-steering-directories` |
| **UX document** | UX 문서 | A Living Spec document (`UX-<slug>`, kind `ux`) describing one interface element a person sees and operates, a screen, modal or panel, by purpose, content tree, states and interactions; use case steps cite it and each interaction names the step it serves. Excludes visual style and the wireframe medium. | `ADR-ux-screens` |
| **UX object register** | UX 객체 목록 | The steering file `docs/steering/ux-objects.md` listing each object's representations and calls to action per role, for the objects the use cases with UX documents touch; created with a project's first UX document, never seeded. | `ADR-ux-screens` |

### 3. Delivery Workflows and Tasks

| 용어 | 번역어 | 정의 | 출처 |
| :--- | :--- | :--- | :--- |
| **Development approach** | 개발 방식 | Shared project choice of `sdd` or `adaptive-dev`, independent of installed packages and selected assets; excludes clone-local execution environment and publication authority. | `CAP-DIST-sync-and-transactions` |
| **Adaptive development** | 적응형 개발 | The development approach (`adaptive-dev`) that iterates a product through clarification, research, implementation and usage verification without per-change SDD records, and may remain a project's approach; SDD adoption is the explicit `sdd-baseline` procedure. Excludes SDD Units, envelopes and immutable experiment history. | `CAP-DLV-adaptive-development` |
| **Adaptive-dev current context** | 적응형 개발 현재 컨텍스트 | Mutable current product facts used to resume adaptive development: goal, retained choices versus assumptions, run/check evidence, uncertainty and next useful action; excludes SDD Units/envelopes, transcripts and immutable experiment history. | `CAP-DLV-adaptive-development` |
| **Deep research** | 심층 조사 | An explicitly invoked, approach-neutral team investigation (`/deep-research`) retained as one indexed material under `docs/materials/` and cited by its `MAT-<slug>` ID; excludes product iteration, approach policy, delivery records and committing the result. | `CAP-DLV-deep-research` |
| **Work scope observation** | 작업 범위 관찰 | Invocation-local evidence from one snapshot, pinned branch tree or accessible worktree, with task attribution, provenance and missing layers; excludes a persistent registry revision or write authority. | `CAP-COLL-work-scope-registry` |
| **Workflow** | 워크플로 | A multi-stage delivery procedure declared as data (`kind = "workflow"`): ordered stages with entry/exit checks, approval gates, and returns. | `CAP-DLV-workflow-orchestration` |
| **Proposal Planning** | 제안 계획 | The SDD activity that settles a proposal's direction on its `plan-<slug>` branch, from draft through the user's `plan-accept` to handoff to a spec bundle. Excludes Development and adaptive development. | `CAP-DLV-proposal-planning` |
| **Unit** | 유닛 | A directory driven by a workflow, tracked by its anchor file (e.g. `spec.md` or `proposal.md`). | `CAP-DLV-workflow-orchestration` |
| **Stage** | 단계 | A discrete step in a workflow (`intent`, `specify`, `build-verify`, `handoff`); evaluates whether checks are met. | `CAP-DLV-workflow-definitions` |
| **Segment** | 세그먼트 | The execution span during which a Unit is bound to a single workflow definition; reset upon workflow handoff. | `CAP-DLV-workflow-orchestration` |
| **Gate** | 게이트 | A workflow stage that pauses for an explicit human or automated decision. | `CAP-DLV-workflow-definitions` |
| **Envelope** | 엔벨로프 | A structured YAML file recording the findings, questions, problems, or resolution of a workflow stage. | `CAP-DLV-workflow-envelopes` |
| **Shared artifact** | 공유 아티팩트 | Immutable expiring report content shared by exact generation reference; excludes scope coordination and approval authority. | `CAP-COLL-shared-artifacts` |
| **Task worktree** | 작업 워크트리 | An isolated Git worktree created on an activity branch (`plan-<slug>`, `dev-<slug>`) for parallel task execution. | `CAP-WT-task-worktrees` |
| **Source feedback** | 출처 피드백 | Explicit FB IDs whose observations and received scope an authorized task addresses; recorded in the proposal/spec body or session agreement. Excludes unrelated observations captured during the task. | `ADR-feedback-lifecycle-ledger` |
| **Direct acceptance** | 직접 수락 | The user's `plan-accept` of an eligible draft given on sight in Backlog and recorded on the base checkout, without a Planning branch or run. Excludes any `activity-effort`, Planning `worker` envelope or acceptance without the user. | `ADR-proposal-acceptance` |
| **Session reclassification** | 세션 재분류 | Deleting a queued draft without PADRs on the user's explicit decision at pickup, preserving its open feedback, to do the work as a `session` task under a new slug; the one lowering of depth besides a proposal's handoff. Excludes proposals in review or accepted and spec Units. | `ADR-delivery-classification` |
| **Feedback promotion** | 피드백 승격 | Closing feedback by routing an observation to identified follow-up work, which owns subsequent tracking. Excludes any claim that the observation has been fixed or verified. | `ADR-feedback-lifecycle-ledger` |
| **Feedback resolution** | 피드백 해결 | Closing an explicitly linked open observation through a direct verified fix without promotion, in a session or spec task. Excludes promoted sources, handoff alone, partial fixes and any claim of integration. | `ADR-feedback-lifecycle-ledger` |

### 4. Gates, Host and Integration

| 용어 | 번역어 | 정의 | 출처 |
| :--- | :--- | :--- | :--- |
| **Host** | Host | The main agent of the user's local session: it drives Backlog, inline Planning, scheduling, worker acceptance and lifecycle decisions, and carries the user's conversational decisions to Host-authorized CLI operations; in local-orchestrated mode it delegates exact lifecycle execution to git-operator. Excludes delegated workers and subagent roles, and the agent host product (Codex, Claude Code, Antigravity) that `--host` and host hooks name. | `ARCH-04-1-ecosystem-boundaries` |
| **git-operator** | Git 작업 실행자 | Reusable lifecycle executor for one Host conversation and repository, operating exact current Host-authorized jobs through guarded CLI operations. Excludes production authoring, semantic decisions, approval grants, persistent services and global locking. | `CAP-DLV-delivery-workflows` |
| **Commit gate** | 커밋 게이트 | Git hook wrapper installed by `devkit gate install` enforcing policy prior to commit. | `CAP-GATE-commit-gates` |
| **Consolidation** | 통합 정리 | Merging related closed records into one replacement that keeps every retired ID as an alias without changing any decision or outcome: the `adr-consolidation` and `feedback-consolidation` playbooks and the `FB-consolidated-<area>-<status>` records. Distinct from Compact output and from shortening a document. | `ADR-consolidation-terminology` |
| **Compact output** | 컴팩트 출력 | Bounded command execution for AI agents (`devkit run`), capturing full logs to disk while streaming bounded summaries to stdout. | `CAP-CMP-bounded-execution` |
| **Agent advisory** | 에이전트 어드바이저리 | Structured error, warning, or notice adhering to the Agent Advisory Protocol (`[ERROR]`, `[WARN]`, `[NOTICE]`) with machine-actionable directives. | `CAP-ADV-agent-advisory-protocol` |
| **Host hook** | 호스트 훅 | Mechanized execution resource registering an installed service at a native host event (`kind = "hook"`). | `CAP-HOST-lifecycle-observation` |
| **Scoped CLI integration** | 범위 지정 CLI 통합 | The Host-authorized `devkit integration prepare` and `integrate` commands that land committed work through the local or pull-request route after revalidating policy, readiness, source identity and cleanup scope; no MCP tool performs integration. | `CAP-INT-mcp-services` |
| **Playbook run** | 플레이북 실행 | One bounded maintenance playbook execution, independent of its report or publication. | `CAP-DLV-maintenance-history` |
| **Run record** | 실행 기록 | Canonical maintenance evidence, outcome and local publication metadata; excludes report bytes. | `CAP-DLV-maintenance-history` |
| **Publication destination** | 게시 대상 | Credential-free repository and dedicated history branch selected for run publication. | `CAP-DLV-maintenance-history` |
| **Source SHA** | 소스 SHA | HEAD commit inspected at intake; excludes content trees and history commit SHAs. | `CAP-DLV-maintenance-history` |
<!-- /handbook:generated -->
