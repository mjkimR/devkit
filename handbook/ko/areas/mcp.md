---
sources:
  CAP-COLL-shared-artifacts: null
  CAP-HOST-lifecycle-observation: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
  UC-drive-development-to-integration: null
title: MCP
translated_from: en/areas/mcp.md@c219778a793807d2
---

# MCP

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
- [하네스](harness.md)
- [호스트](host.md)
- [통합](integration.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

`devkit-mcp`는 Model Context Protocol(stdio)로 에이전트 호스트에 devkit의 도구를 제공하고, 프로젝트의 로컬 MCP 등록을
맞춰 두는 선택형 패키지입니다(`CAP-MCP-runtime-registration`). devkit을 쓰는 데 이 패키지가 꼭 필요하지는 않습니다.
통합을 포함한 모든 수명 주기 작업은 CLI로 실행됩니다. 이번 릴리스에서 주된 용도는 공유 아티팩트(shared artifact)
도구입니다([협업](collaboration.md) 참고).

워크플로에서 Host와 승인이 맡는 역할은 [개념](../concepts.md)과
[개발을 통합까지 진행하기](../journeys/drive-development-to-integration.md) 여정을 참고하세요.

## 설치와 등록

`devkit-mcp`는 유지되는 런타임(retained runtime)에 설치합니다. 베이스 체크아웃의 환경이나 도구 설치가 그런 곳이며,
작업 워크트리의 `.venv`나 편집 가능 모드로 연결된 워크트리 소스에는 절대 설치하지 않습니다. 그 다음 sync가 등록하게
하거나, 명시적으로 등록합니다.

| 하려는 일 | 실행 |
| --- | --- |
| 어떤 런타임이 쓰일지 확인 | `devkit mcp status --descriptor --format json` |
| 프로젝트 항목 등록 | `devkit mcp setup [--host codex\|claude]` |
| 원하는 등록, 기록된 등록, 프로젝트 등록 확인 | `devkit mcp status --format json` |
| devkit 자신의 항목 제거 | `devkit mcp remove` |

런타임이 설치되어 있으면 일반적인 `devkit sync`가 선택된 각 에이전트의 프로젝트 파일에 있는 devkit 항목을 맞춥니다.
Codex는 `.codex/config.toml`, Claude Code는 `.mcp.json`, Antigravity는 `.agents/mcp_config.json`입니다.
`[mcp] register = false`로 설정하면 선택을 해제합니다. 새 작업 워크트리는 잠긴 에셋 복원 직후
`devkit sync --registrations-only`를 통해 항목을 얻습니다([워크트리](worktree.md) 참고). 호스트별 단계적 설정은
[MCP setup](https://github.com/mjkimR/devkit/blob/v0.1.4/guides/install/mcp.md) (영어 원문) 가이드에 있습니다.

## 등록이 건드리는 것과 건드리지 않는 것

등록은 자신의 것이 아닌 파일을 조심스럽게 다룹니다.

- 추적되지 않는 파일에만, 그리고 무시되는 원장 `.devkit/transient/mcp/registrations.json`에 devkit의 것으로 기록된
  항목에만 씁니다. 추적되는 파일과 눈에 보이는 외부 파일은 바뀌지 않습니다.
- 대상 파일이 없으면 기존 무시 규칙이 필요하거나, devkit이 연결된 모든 워크트리에서 가리게 될 파일이 없는지 확인한 뒤
  좁은 범위의 클론 로컬 제외 규칙을 하나 추가합니다.
- 소유한 항목이 없거나, 편집되었거나, 중복되면 충돌(`MCP_REGISTRATION_CONFLICT`)입니다. devkit이 소유하지 않은 동일한
  항목을 넘겨받는 일은 결코 없습니다.
- 호스트 신뢰, 권한, 전역 설정은 호스트에 남습니다. 사용자 설정이나 관리 설정에 있는 같은 이름의 선언은 읽기 전용으로
  충돌로 보고됩니다.
- 중단된 변경은 다음 변경 전에 복구됩니다. `--dry-run`과 `--check`는 쓰지 않고 계획만 하며, 잠긴 sync는 호스트 파일을
  바꾸지 않고 검증합니다.

등록되었다고 연결된 것은 아닙니다. status는 실제 연결, 폼 지원, 신뢰, 권한을 알 수 없음(unknown)으로 보고합니다.

## 서버가 여러분을 보호하는 방법

`devkit mcp serve`는 모든 호출을 세 위치에 묶습니다. 유지되는 런타임, 실행자 체크아웃, 소유 설정 작업 공간(설정이
적용되는 체크아웃)입니다. 도구 입력으로는 작업 공간을 바꿀 수 없습니다.

- **실행 등급.** 각 도구는 자신을 `read_only`, `bounded_write`, `preflight`, `interactive`, `approved_resume` 중 하나로
  선언하며, 선언하지 않은 도구는 `interactive`로 취급합니다. 네이티브 확인은 여러분이 수락과 승인을 모두 했을 때만
  유효합니다. 거절, 취소, 연결 끊김, 폼을 지원하지 않는 호스트는 아무것도 허용하지 않습니다.
- **클라우드 환경**은 읽기 전용 도구만 노출하고 폼과 쓰기를 거부합니다. 보호 장치는 대기 후와 효과 발생 전에 반복됩니다.
- **오래된 코드.** 서버는 자신이 불러온 devkit 코드의 해시를 기록합니다. 디스크의 코드가 바뀌었다면 읽기 전용이 아닌
  모든 호출이 `MCP_RUNTIME_STALE`로 거부됩니다. 서비스를 다시 시작하거나 다시 연결하세요. 읽기 전용 도구는 계속
  동작합니다.
- **사라진 작업 공간.** 소유 작업 공간이 없거나 형식이 잘못되었으면 닫힌 상태로 실패합니다(`MCP_WORKSPACE_UNAVAILABLE`).

## 업무 승인은 대화에 남습니다

수명 주기 변경(통합, 정리)은 MCP 도구가 아닙니다. Host가 작업을 확인하고, 정확한 보고서, 대상, 효과를 보여 주고,
`ask`에서 여러분의 결정을 받은 뒤 CLI를 호출합니다(`CAP-INT-mcp-services`, [통합](integration.md) 참고). 호스트 신뢰,
도구, 샌드박스 프롬프트는 그 결정과 별개의 문제입니다.

폼 텍스트가 표시될 때 그 언어는 소유 작업 공간의 설정을 따릅니다. 이는 보호 장치나 등록을 결코 바꾸지 않습니다.

## 공유 아티팩트 도구

공유 아티팩트 서비스는 `shared_put`(승인 폼이 필요 없는 제한된 쓰기)과 읽기 전용인 `shared_get`, `shared_list`를
제공합니다. 이 도구들은 `devkit shared` CLI와 같은 정체성, 보존, 어댑터 규칙을 따릅니다(`CAP-COLL-shared-artifacts`).
클라우드 환경에서는 쓰기 도구가 목록에 나오지도 않고 받아들여지지도 않습니다.

## 자주 보는 코드

| 코드 | 할 일 |
| --- | --- |
| `MCP_RUNTIME_UNAVAILABLE` | 서비스 패키지가 일치하는 유지 런타임을 설치하거나 선택한 뒤 다시 맞춥니다. |
| `MCP_RUNTIME_STALE` | 서비스를 다시 시작하거나 다시 연결한 뒤 다시 호출합니다. |
| `MCP_REGISTRATION_CONFLICT` | 편집되었거나 소유하지 않은 항목을 살펴보고, 동기화 전에 정확한 소유 상태를 복원합니다. |
| `MCP_REGISTRATION_UNAVAILABLE` | 호스트 파일은 그대로 두고, 호스트 설정이나 CLI 경로를 사용합니다. |
| `MCP_INTERACTIVE_UNAVAILABLE` | 로컬 대화형 Host나 CLI 경로를 사용합니다. |

## 출처

- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/mcp/CAP-MCP-runtime-registration.md) (영어 원문):
  런타임 계약, 등록, Host 워크플로와 공유 아티팩트 서비스.
- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/host/CAP-HOST-lifecycle-observation.md)
  (프로젝트 MCP 등록 경계)과
  [host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/host.md#mcp-services).
- 관련 문서: [호스트](host.md), [협업](collaboration.md), [통합](integration.md).
