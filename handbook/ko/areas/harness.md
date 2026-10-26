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
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

하네스(harness)는 devkit-spec 중 AI 에이전트가 직접 읽고 실행하는 핵심 인터페이스 영역입니다. `spec` 번들은 모든 세션에
스펙 주도 전달(spec-driven delivery) 체계가 어떻게 동작하며 각 단계(stage)가 어떤 절차를 따르는지 안내하고, `devkit spec`
명령어 그룹은 해당 절차에서 호출되는 실질적인 CLI 도구를 제공합니다. 두 구성 요소 모두 별도로 설치할 필요가 없습니다.
`spec` 번들은 `devkit sync` 실행 시 자동으로 선택되며, `devkit spec` 명령어는 단일 통합 실행 파일인 `devkit`에 자연스럽게
마운트됩니다. 그 기반이 되는 핵심 모델(Living Spec, 유닛, 워크플로 단계)은 먼저 [개념](../concepts.md)을 참고하십시오.

## 저장소에 배포되는 자산

`devkit sync`를 실행하면 번들이 `.devkit/managed/spec/` 경로로 복사되고, 번들에 포함된 스킬과 역할 계약(role contracts)이
각 에이전트 호스트의 고유 디렉터리(`.claude/`, `.agents/`, `.codex/`)로 프로젝션(projection)되며, 루트 `AGENTS.md` 블록에
정확히 한 줄의 진입 지침이 추가됩니다. 이 한 줄은 모든 에이전트 세션에 대해 개발 작업을 시작하기 전 `uv run devkit get-context spec`을
실행하고, 새로운 요청은 `/spec <intent>`로 시작하며, 작업 맥락 파악 시에는 `/spec-next`를 활용하도록 안내합니다.

| 프리셋 | 선택 방식 | 제공 구성 요소 |
| --- | --- | --- |
| `core` | 자동 활성화 | 에이전트 지침, `AGENTS.md` 포인터, 11개 거버넌스 규칙, 템플릿, 스킬, 워크플로, 역할 계약, 플레이북 |
| `docs-skeleton` | `devkit add spec:docs-skeleton` | 초기 골격이 갖춰진 `docs/` 트리 (미존재 시 1회 생성) |

비활성화하려면 `.devkit/config.toml`에 `[presets] spec = false`를 설정하십시오. 관리 파일(managed files)이나 프로젝션된
파일은 직접 편집하지 마십시오. 필요한 변경은 `devkit override create`나 프로젝트 고유의 번들을 통해 적용해야 합니다.

## 작업 시작하기

1. 에이전트가 `devkit get-context spec`을 실행하여 하네스 헌장을 로드합니다. 여기에는 Living Spec 위치, 작업 분류 체계,
   승인 경계, 완료 판정 기준이 포함되어 있습니다.
2. 사용자가 `/spec <intent>` 형태로 의도를 전달합니다. 새 작업을 접수할 때 `spec` 스킬은 먼저 `devkit playbook search`를
   실행하며, 요청한 작업과 정확히 일치하는 플레이북이 있는 경우에만 이를 추천합니다. 사용자가 승인하기 전까지는 아무것도 임의로
   실행되지 않습니다.
3. 스킬이 `devkit spec policy`를 조회한 후 사용자가 검토하고 확정할 작업 분류를 제안합니다. 여기에는
   `task-kind`(feature, bugfix, refactor), `planning-depth`(`session`, `spec`, `proposal` 중 작업 규모가 아니라 구현 전
   선결 결정 사항의 범위에 따라 결정됨), 그리고 각 활동별 실행 모드와 `activity-effort`가 포함됩니다.
4. 제안된 분류에 매칭되는 워크플로(workflow) `sdd-<planning-depth>[-<task-kind>]`를 진행합니다(`CAP-DLV-delivery-workflows`).
   유닛(Unit) 단위의 깊이에서는 실제 코드 작성 전에 `spec.md`, `plan.md`, `tasks.md`를 반드시 먼저 작성해야 하며, `session`
   수준의 간단한 작업은 별도의 유닛 문서를 생성하지 않습니다.

에이전트는 자체 판단에 따라 작업 깊이를 상향할 수는 있지만 임의로 하향 조정할 수는 없으며, Development 단계에서 Planning
단계로 되돌아가지 않습니다. 만약 방향이 잘못되었다면 해당 작업을 닫고 새 slug로 다시 시작해야 합니다. 전체 진행 흐름은
[개발 요청 라우팅하기](../journeys/route-development-intent.md)를 참고하십시오. 실행 단계가 실패하거나 예외 처리가 필요한
경우는 [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)에서 다룹니다.

## 제공 스킬 목록

| 스킬 | 주요 역할 |
| --- | --- |
| `spec` | 모든 개발 의도 라우팅: 작업 분류, Backlog 등록, 인라인 Planning, 워크플로 진행 |
| `spec-next` | 현재 상황 파악: 진행 중인 작업 또는 다음에 착수할 대기 초안 확인 |
| `spec-specify`, `spec-plan`, `spec-tasks` | `spec.md`, `plan.md`, `tasks.md` 문서 작성 |
| `spec-review` | 작업 완료 선언 전 코드 diff, 수락 기준 및 검증 결과 검증 |
| `spec-sync` | 구현 변경 사항을 Living Spec에 반영하고 `reconcile.md` 완료 처리 |
| `spec-integrate` | 베이스 브랜치를 병합하고 재검증을 거쳐 사용자 승인 후 최종 통합 |
| `spec-delegate`, `spec-orchestrate` | 격리된 작업 워크트리에서 작업하는 리뷰어나 일회성 워커에게 작업 위임 |
| `spec-review-proposal` | 제안 수락 전 커밋된 제안서 및 관련 PADR 검토 |
| `spec-rule` | 프로젝트 거버넌스 규칙 작성([거버넌스 규칙](governance.md)) |
| `spec-feedback` | 도구와 에셋에 대한 관찰 기록 작성 또는 일괄 정리 |
| `spec-entrypoints` | 스펙 번들로부터 기능 및 유스케이스 진입점 도출 |

각 스킬은 현재 수행 단계에 필요한 지침과 참고 자료만을 선별 로드하며, 각 참고 자료에는 참조해야 하는 적절한 시점이
명시되어 있습니다. 효율적인 작업 위임을 위해 6가지 역할 계약(`challenger`, `scout`, `code-reviewer`, `reconcile-reviewer`,
`planning-worker`, `development-worker`)이 함께 배포됩니다.

## 규칙 준수 문서 작성법

새 문서는 `.devkit/managed/spec/templates/<kind>.md`(capability, use case, decision, proposal, milestone) 템플릿을
기반으로 시작합니다. 문서를 작성하기 전에 에이전트는 해당 문서 종류에 맞는 작성 지침을 먼저 숙지합니다.

| 작성 지침 | 확인 시점 |
| --- | --- |
| `document-writing` | 모든 문서 공통: 문장 단위의 기본 작성 원칙 |
| `living-spec-writing` | `docs/` 또는 `specs/` 편집 시: 현재 상태 기술, ID 체계, 요약(summary), 용어집 규칙 |
| `contract-authoring` | 스펙, 수락 기준, 정책, 규칙, 워크플로 정의 작성 시 |
| `capability-writing`, `usecase-writing`, `architecture-writing`, `decision-writing` | 각 세부 문서 종류별 작성 시 |

번들에 포함된 거버넌스 규칙들은 이 지침에서 설명하는 규약을 자동으로 검증합니다. 자세한 내용은
[거버넌스 규칙](governance.md)의 spec 규칙 목록을 참고하십시오.

## 기존 문서가 존재하는 저장소에 도입하기

devkit은 이미 존재하는 `docs/` 트리에 임의로 템플릿을 덮어쓰지 않습니다. `brownfield-adoption` 플레이북을 실행하면
안전하게 devkit을 설치하고 기준선을 설정한 뒤, 기존 레거시 Markdown 문서를 `docs/materials/_legacy/` 아래로 격리하고
사용자가 결정한 보류 사항들을 기록합니다. 자세한 내용은
[기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)를 참고하십시오. 번들에는
`feedback-hygiene`(열린 피드백 일괄 분류)과 `adr-compaction`(결정 변경 없이 관련 ADR 통합 정리) 플레이북이 추가로 제공됩니다.

## 하네스 지침이 준수하는 기본 정책

- **피드백 수집**: `spec-feedback`은 `devkit spec policy`에 정의된 `FEEDBACK_POLICY`를 따릅니다. 관찰 사항을 자동
  수집할지 요청 시에만 수집할지, 업스트림 도구까지 수집 대상에 포함할지, 기록의 상세 수준을 어느 정도로 유지할지 등을 결정합니다.
- **검증 정책**: 기획, 검토, 통합 단계는 각 저장소 자체의 검증 정책을 따릅니다(예: 영향 범위 기반 테스트 선택 실행 및
  풀 스위트 폴백).
- **최종 통합**: 각종 검사, 리뷰, Living Spec 조정을 마친 후, 에이전트는 반드시 대화를 통해 사용자에게 승인을 구한 뒤에만
  `devkit integration integrate`를 실행합니다. 사용자의 승인을 임의로 추론하여 진행하지 않습니다.
- **Backlog 및 마일스톤**: 즉시 착수하지 않는 요청은 초안 제안서로 보관되며, 필요에 따라 마일스톤 테마별로 그룹화할 수
  있습니다. `spec-next`는 로컬 베이스 스냅샷을 기준으로 직접적인 선행 조건 충족 여부를 확인한 후 초안들의 우선순위를 정렬합니다.
- **방치된 브랜치 정리**: 작업 후 남겨진 `plan-*` 및 `dev-*` 브랜치는
  [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md) 지침에 따라 체계적으로 정리합니다.
- **세션 가로채기 금지**: 에이전트는 사용자의 명시적인 지시 없이 현재 세션이나 진행 중인 작업을 일방적으로 중단하지 않습니다.

## `devkit spec` 명령어 체계

`devkit spec`은 별도의 단독 실행 바이너리를 두지 않고, `devkit` 루트 명령어 그룹이 실행 시점에 `devkit.commands` 진입점을
통해 동적으로 임포트합니다. `devkit spec --version`을 실행하면 해당 패키지 버전을 출력합니다(`devkit --version`은 devkit
코어 자체 버전을 출력).

| 명령어 | 주요 용도 |
| --- | --- |
| `devkit spec resolve`, `refs`, `list`, `search` | Living Spec 문서 탐색 및 색인 조회 |
| `devkit spec new`, `devkit spec proposal new`, `accept`, `handoff` | 스펙 번들 생성 및 제안 문서 숙성/이관 |
| `devkit spec policy` | 프로젝트 정책 조회 |
| `devkit spec entrypoints` | 코드 진입점 도출 |
| `devkit spec scope register`, `query`, `update`, `release` | 공유 작업 범위 레지스트리 관리 |

모든 하위 명령은 `-w/--workspace-root`, `--format text|json`, `-q`, `-v`, `--strict` 공통 옵션을 지원하며,
`ARCH-08-1-agent-output` 규약에 따라 한 줄 센티널 또는 단일 JSON 객체를 출력하고, `SPEC_` 접두사가 붙은 에이전트
어드바이저리를 발생시킵니다([어드바이저리](advisory.md)). 목록 조회는 `--limit`과 `--offset`으로 페이징되며, 추가 항목이
남아 있는 경우 다음 페이지 조회를 위한 `[NEXT_CMD: ...]` 명령어가 함께 안내됩니다. 종료 코드는 알림(notice) 유무와 관계없이
정상 성공 시 `0`, `--strict` 모드에서 경고 발생 시 `1`, 실행 불가 또는 요청 거부 시 `2`를 반환합니다.

## 관련 자료

- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문):
  번들의 프리셋, 헌장, 지침 문서, 스킬, 플레이북, 템플릿 및 정책 규약.
- [CAP-HARN-command-mount](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-command-mount.md):
  `devkit spec` 마운트 방식 및 하위 명령어 공통 규약.
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md):
  스킬이 실행하는 워크플로 및 역할 계약 정의.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  번들이 배포하는 거버넌스 규칙 명세.
