---
sources:
  ARCH-08-1-agent-output: null
  CAP-DLV-delivery-workflows: null
  CAP-GOV-spec-rules: null
  CAP-HARN-agent-guidance: null
  CAP-HARN-command-mount: null
  UC-adopt-in-an-existing-repository: null
  UC-handle-delivery-problems-and-exceptions: null
  UC-resolve-stale-activity-branches: null
  UC-route-development-intent: null
title: 하네스
translated_from: en/areas/harness.md@e0badba6a0ab65b1
---

# 하네스

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [어드바이저리](advisory.md)
- [에이전트 우선 CLI 도구 키트](cli.md)
- [협업](collaboration.md)
- [컴팩트 명령 출력](compact.md)
- [전달](delivery.md)
- [배포](distribution.md)
- [문서](documents.md)
- [커밋 게이트](gate.md)
- [생성 파일](generated.md)
- [거버넌스 규칙](governance.md)
- [호스트](host.md)
- [통합](integration.md)
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

하네스(harness)는 devkit-spec 가운데 에이전트가 읽고 실행하는 부분입니다. `spec` 번들은 모든 세션에 스펙 주도 전달이
어떻게 동작하고 각 단계(stage)가 어떤 절차를 따르는지 알려 주며, `devkit spec` 명령 그룹은 그 절차가 호출하는 명령을
제공합니다. 둘 다 따로 설치하지 않습니다. `spec` 번들은 `devkit sync`에서 자동으로 선택되고, `devkit spec`은 하나뿐인
`devkit` 실행 파일에 붙습니다. 그 바탕이 되는 모델(Living Spec, 유닛, 워크플로 단계)은 먼저 [개념](../concepts.md)을
읽어 보세요.

## 저장소에 들어오는 것

`devkit sync`는 번들을 `.devkit/managed/spec/`에 복사하고, 그 스킬과 역할 계약을 각 에이전트 호스트의 고유
디렉터리(`.claude/`, `.agents/`, `.codex/`)에 프로젝션(projection)하며, 루트 `AGENTS.md` 블록에 정확히 한 줄을
추가합니다. 그 줄은 모든 세션에 개발 작업 전 `uv run devkit get-context spec`을 한 번 실행하고, `/spec <intent>`로
시작하며, `/spec-next`로 현재 위치를 파악하라고 알려 줍니다.

| 프리셋 | 선택 방식 | 가져오는 것 |
| --- | --- | --- |
| `core` | 자동 | 지침, `AGENTS.md` 포인터, 열한 개의 규칙, 템플릿, 스킬, 워크플로, 역할 계약, 플레이북 |
| `docs-skeleton` | `devkit add spec:docs-skeleton` | 초기 내용이 채워진 `docs/` 트리로, 없는 곳에 한 번만 씁니다 |

`.devkit/config.toml`에 `[presets] spec = false`를 두면 선택을 해제합니다. 관리 파일(managed files)이나 프로젝션된
파일은 절대 직접 편집하지 마세요. `devkit override create`나 프로젝트 자체 번들을 통해 바꿉니다.

## 작업 시작하기

1. 에이전트가 `devkit get-context spec`으로 헌장을 불러옵니다. Living Spec의 위치, 작업 분류 방식, 승인 경계,
   완료 검사가 담겨 있습니다.
2. 여러분이 `/spec <intent>`로 의도를 밝힙니다. 새 작업을 접수하면 `spec` 스킬은 먼저 `devkit playbook search`를 한
   번 실행하고, 요청한 작업을 정확히 가리키는 플레이북이 있을 때만 이를 제안합니다. 여러분이 확인하기 전에는 아무것도
   실행되지 않습니다.
3. 스킬이 `devkit spec policy`를 읽고 여러분이 확인할 분류를 제안합니다. `task-kind`(feature, bugfix, refactor),
   `planning-depth`(`session`, `spec` 또는 `proposal`로, 크기가 아니라 구현 전에 무엇을 정해야 하는지로 고릅니다),
   그리고 활동별 모드와 `activity-effort`입니다.
4. 스킬이 해당 워크플로(workflow) `sdd-<planning-depth>[-<task-kind>]`를 진행합니다(`CAP-DLV-delivery-workflows`).
   유닛(Unit)을 만드는 깊이에서는 프로덕션 코드 전에 `spec.md`, `plan.md`, `tasks.md`를 쓰고, `session` 작업은 유닛을
   만들지 않습니다.

에이전트는 스스로 판단해 깊이를 올릴 수 있지만 혼자서 낮추지는 않으며, Development는 Planning으로 되돌아가지
않습니다. 방향이 잘못되었다면 닫고 새 slug로 다시 시작합니다. 전체 흐름은
[개발 의도 라우팅](../journeys/route-development-intent.md)에 있으며, 단계가 실패하거나 예외가 필요할 때는
[전달 문제와 예외 처리](../journeys/handle-delivery-problems-and-exceptions.md)를 참고하세요.

## 스킬

| 스킬 | 용도 |
| --- | --- |
| `spec` | 모든 개발 의도를 라우팅합니다: 분류, Backlog, 인라인 Planning, 워크플로 진행 |
| `spec-next` | 현재 위치 파악: 진행 중인 작업이나 다음에 집어 들 대기 초안 |
| `spec-specify`, `spec-plan`, `spec-tasks` | `spec.md`, `plan.md`, `tasks.md` 작성 |
| `spec-review` | 작업 완료를 선언하기 전에 diff, 기준, 검사를 확인 |
| `spec-sync` | 변경을 Living Spec에 반영하고 `reconcile.md`를 해결 |
| `spec-integrate` | 베이스를 병합하고 다시 검증한 뒤, 승인을 받아 통합 |
| `spec-delegate`, `spec-orchestrate` | 각자의 워크트리에서 일하는 리뷰어나 일회성 워커에게 작업을 넘김 |
| `spec-review-proposal` | 수락 전에 커밋된 제안과 그 PADR을 리뷰 |
| `spec-rule` | 프로젝트 규칙 작성([거버넌스 규칙](governance.md)) |
| `spec-feedback` | 도구와 에셋에 대한 관찰을 기록하거나 일괄 정리 |
| `spec-entrypoints` | 스펙 번들에서 capability와 use case의 진입점을 도출 |

스킬은 현재 단계의 지침과 참고 자료만 불러오며, 각 참고 자료는 언제 읽어야 하는지 밝힙니다. 위임을 위해 여섯 개의
역할 계약(`challenger`, `scout`, `code-reviewer`, `reconcile-reviewer`, `planning-worker`, `development-worker`)이
배포됩니다.

## 규칙이 기대하는 방식으로 문서 쓰기

새 문서는 `.devkit/managed/spec/templates/<kind>.md`(capability, use case, decision, proposal, milestone)에서
시작합니다. 쓰기 전에 에이전트는 해당 종류의 지침을 읽습니다.

| 지침 | 읽는 시점 |
| --- | --- |
| `document-writing` | 모든 문서: 문장 수준의 기준 |
| `living-spec-writing` | `docs/`나 `specs/`를 편집할 때: 현재 상태 서술, ID, 요약, 용어집 |
| `contract-authoring` | 스펙, 수락 기준, 정책, 규칙, 워크플로 |
| `capability-writing`, `usecase-writing`, `architecture-writing`, `decision-writing` | 각 문서 종류 |

번들의 규칙은 이 지침들이 설명하는 내용을 검사합니다. [거버넌스 규칙](governance.md)의 스펙 규칙을 참고하세요.

## 이미 문서가 있는 저장소에 도입하기

devkit은 기존 `docs/` 트리에 스스로 초기 내용을 채우지 않습니다. `brownfield-adoption` 플레이북이 설치하고, 기준선을
잡고, 레거시 Markdown을 `docs/materials/_legacy/` 아래에 격리하고, 여러분이 결정한 보류 사항을 기록합니다.
[기존 저장소에 도입하기](../journeys/adopt-in-an-existing-repository.md)를 참고하세요. 번들에는 플레이북이 두 개 더
있습니다. `feedback-hygiene`(열린 피드백을 한 번에 분류)와 `adr-compaction`(결정을 바꾸지 않고 관련 ADR을 통합)입니다.

## 지침이 따르는 정책

- **피드백**: `spec-feedback`은 `devkit spec policy`의 `FEEDBACK_POLICY`를 따릅니다. 관찰을 자동으로 수집할지 요청이
  있을 때만 수집할지, 업스트림 도구도 포함할지, 기록을 얼마나 자세히 남길지가 정해집니다.
- **검증**: 계획, 리뷰, 통합은 저장소 자체의 검증 정책을 따릅니다. 예를 들어 전체 테스트 대체 실행이 있는 영향
  범위 테스트 선택입니다.
- **통합**: 검사, 리뷰, reconcile을 마친 뒤 에이전트는 대화에서 여러분에게 묻고, 그 다음에야
  `devkit integration integrate`를 실행합니다. 승인은 결코 추론되지 않습니다.
- **Backlog와 마일스톤**: 지금 시작하지 않는 요청은 초안 제안이 되며, 선택적으로 마일스톤 주제 아래에 묶입니다.
  `spec-next`는 하나의 로컬 베이스 스냅샷에서 초안을 직접 선행 조건으로 걸러 낸 뒤 순위를 매깁니다.
- **오래된 브랜치**: 남아 있는 `plan-*`와 `dev-*` 브랜치는
  [오래된 활동 브랜치 정리](../journeys/resolve-stale-activity-branches.md)에 따라 처리합니다.
- **세션 가로채기 금지**: 에이전트는 여러분의 지시 없이 세션이나 진행 중인 작업을 멈추지 않습니다.

## `devkit spec` 명령

`devkit spec`에는 자체 실행 파일이 없습니다. devkit의 루트 그룹이 실행 시점에만 `devkit.commands` 진입점을 통해 이를
임포트합니다. `devkit spec --version`은 패키지 버전을 출력합니다(`devkit --version`은 devkit 자체를 보고합니다).

| 명령 | 용도 |
| --- | --- |
| `devkit spec resolve`, `refs`, `list`, `search` | 문서 찾기 |
| `devkit spec new`, `devkit spec proposal new`, `accept`, `handoff` | 스펙 번들 생성과 제안 숙성 |
| `devkit spec policy` | 프로젝트 정책 읽기 |
| `devkit spec entrypoints` | 코드 진입점 도출 |
| `devkit spec scope register`, `query`, `update`, `release` | 공유 작업 범위 레지스트리 |

모든 하위 명령은 `-w/--workspace-root`, `--format text|json`, `-q`, `-v`, `--strict`를 받고,
`ARCH-08-1-agent-output`이 설명하는 대로 센티널이나 JSON 객체 하나를 출력하며, `SPEC_` 접두사가 붙은 어드바이저리를
발생시킵니다([어드바이저리](advisory.md)). 목록은 `--limit`과 `--offset`으로 페이지를 나누며, 항목이 더 남아 있으면
`[NEXT_CMD: ...]` 줄이 다음 페이지를 위한 정확한 명령을 알려 줍니다. 종료 코드 `0`은 알림 유무와 관계없이 성공, `1`은
`--strict`에서의 경고, `2`는 실행할 수 없었거나 거부된 명령입니다.

## 출처

- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문):
  번들의 프리셋, 헌장, 지침, 스킬, 플레이북, 템플릿과 정책.
- [CAP-HARN-command-mount](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-command-mount.md):
  `devkit spec`이 붙는 방식과 하위 명령이 공유하는 규약.
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md):
  스킬이 진행하는 워크플로와 역할 계약.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  번들이 배포하는 규칙.
