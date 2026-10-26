---
sources:
  ADR-host-cli-lifecycle-authority: null
  ADR-local-and-pull-request-integration: null
  CAP-DLV-project-policy: null
  CAP-INT-mcp-services: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
title: 통합
translated_from: en/areas/integration.md@0c0496869a6a9123
---

# 통합

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
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

통합(integration)은 작업의 마지막 단계입니다. 활동 브랜치에 커밋된 작업이 베이스 브랜치에 반영되고, 작업
워크트리(task worktree)와 브랜치가 정리됩니다. `devkit integration`(`CAP-INT-mcp-services`)은 이를 prepare와
integrate의 두 단계로, 로컬 병합이나 풀 리퀘스트 중 하나를 통해 수행합니다.
[개발을 통합까지 진행하기](../journeys/drive-development-to-integration.md)(`UC-drive-development-to-integration`)
여정이 끝나는 곳이 여기입니다. 브랜치, 워크트리, 게이트가 어떻게 맞물리는지는 [개념](../concepts.md)을 참고하세요.

## 누가 결정하나요

통합은 업무상의 결정이며, 누가 결정하는지는 프로젝트 정책이 정합니다(`CAP-DLV-project-policy`의 `dev-integration`).

- **`ask`**: Host(오케스트레이션하는 에이전트 세션)가 정확한 소스, 대상, 보고서, 정리 효과를 보여 주고, 여러분이
  대화에서 결정합니다. 그 다음 Host가 명령을 호출합니다. CLI는 stdin으로 묻지 않고 승인 플래그나 토큰도 받지 않으며,
  작업을 다시 검증하지만 대화를 인증하지는 않습니다.
- **`auto`**: 권한은 베이스 브랜치 자체에 커밋된 정책에서 나오며 로컬 경로만 다룹니다. 결과에는
  `authority: policy`가 보고됩니다.

워커는 이 승인을 결코 요청하지 않으며, 다른 무엇도 이 승인을 대신하지 않습니다. 호출자의 `--claims`, 로컬 설정
오버레이, 호스트 도구 권한은 업무상의 권한이 아닙니다. 그 근거는 `ADR-host-cli-lifecycle-authority`에 기록되어 있습니다.

## prepare 후 integrate

```text
devkit integration prepare <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request]
devkit integration integrate <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--expected-digest <digest>]
```

1. `prepare`는 커밋된 소스, 대상, 프로젝트 정책, 준비 상태 제공자, 정확한 정리 범위를 검증합니다. 아무것도 바꾸지
   않으며 `request.digest`가 담긴 `[INTEGRATION_PREPARED: ...]`를 출력합니다.
2. Host가 그 결과를 보여 줍니다. `ask`에서는 여러분이 대화에서 승인합니다.
3. `integrate --expected-digest <digest>`는 새 요청을 만들고, 무엇이든 바꾸기 전에 모든 검사를 반복합니다. `ask`에서는
   다이제스트가 필수이며, 다이제스트가 묶는 것(소스, 대상, 정책, 준비 상태, 정리 범위) 중 하나라도 바뀌었다면 명령은
   `INTEGRATION_REQUEST_STALE`로 거부합니다. `auto`에서는 다이제스트가 선택이지만, 제공했다면 여전히 일치해야 합니다.

다이제스트는 자격 증명이 아니라 동시성 전제 조건입니다. 요청이 여러분이 본 바로 그 요청임을 증명할 뿐, 여러분이
승인했음을 증명하지는 않습니다.

종료 코드는 일반적인 에이전트 계약을 따릅니다. `0` 성공, `1` 부정적이거나 부분적인 결과, `2` 거부입니다.

## 경로 고르기

- **로컬**(`--route local`): devkit은 베이스 체크아웃 밖에서 병합 커밋을 만들고, 검사한 뒤 베이스를 fast-forward하고,
  범위가 정해진 정리를 실행합니다. fetch, push, 원격 브랜치 삭제는 결코 하지 않습니다. `devkit worktree finish`와 같은
  병합 기구를 쓰며([워크트리](worktree.md) 참고), `[worktree] merge = "ff-only"`를 따릅니다.
- **풀 리퀘스트**(`--route pull-request`): devkit은 GitHub 어댑터를 통해 원격 쓰기를 미리 밝히고 수행하며, 저장소
  바인딩과 head 고정을 유지하고, 필수 검사를 기다리고, 반영을 확인한 뒤 로컬 정리 전에 임대한 원격 브랜치를 제거합니다.
  자동으로 실행되는 일은 없으며, `[worktree] pull_request = "required"` 정책은 로컬 경로를 거부합니다.

어느 경로도 호스트 도구 권한, 파일 시스템 권한, 신뢰, 게시 정책을 바꾸지 않습니다. 병합 커밋 구성과 경로 보호 장치는
`ADR-local-and-pull-request-integration`에 설명되어 있습니다.

## 문제가 생겼을 때

모든 결과는 완료된 단계, 실패한 작업, 안정적인 코드, 관찰된 Git 상태를 나열합니다. 호출 사이에 보관되는 것은
없습니다. 요청 ID, 승인, 복구 저널 어느 것도 남지 않으므로, 상태를 살펴보고 다시 prepare하는 방식으로 복구합니다.

| 코드 | 할 일 |
| --- | --- |
| `INTEGRATION_NOT_READY` | 보고된 완료 조건을 해결한 뒤 다시 prepare합니다. |
| `INTEGRATION_AUTHORITY_REQUIRED` | 베이스 정책과 경로를 확인합니다. `ask`에서는 통합 전에 결정을 받습니다. |
| `INTEGRATION_REQUEST_STALE` | 이미 일어난 일을 살펴보고, 남은 범위를 prepare한 뒤 다시 결정합니다. |
| `INTEGRATION_TARGET_MOVED` | 현재 베이스를 브랜치에 병합하고 검사를 다시 실행한 뒤 다시 결정합니다. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | 남은 정리를 마칩니다(아래 참고). |
| `INTEGRATION_LANDED_UNCHECKED` | 작업을 통합되었다고 하기 전에 제공자의 반영 대상 검사를 실행합니다. |
| `INTEGRATION_CONFIG_INVALID`, `INTEGRATION_PROVIDER_FAILED` | 준비 상태 제공자를 설치하거나 복구하거나, 지원되는 경로를 사용합니다. |

전형적인 복구 방법은 다음과 같습니다.

- 병합이 반영되지 않았을 때: 소스와 대상을 살펴본 뒤, 다시 시도하기 전에 새로 결정을 받습니다.
- 병합은 반영되었지만 정리가 실패했을 때: `devkit worktree status`를 확인합니다. 워크트리가 남아 있으면
  `devkit worktree finish <branch> --merge --local-only`를 실행합니다. 이 명령은 남은 보호된 정리만 수행합니다. 완료 후
  작업이 실패했다면 보고된 대상에 그 작업 고유의 명령을 실행합니다. 예를 들어 `devkit spec proposal prune <slug>`입니다.
- 풀 리퀘스트 경로에서 원격 브랜치 삭제가 실패했거나 결과를 알 수 없으면 로컬 워크트리와 브랜치가 유지됩니다. 걸림돌을
  해결한 뒤 남은 범위를 prepare하고 integrate하세요. 이미 병합된 PR은 검증될 뿐, 두 번 병합되지 않습니다.
- 결과를 알 수 없을 때는 먼저 Git이나 풀 리퀘스트를 확인합니다. 결과를 모르는 원격 쓰기를 결코 다시 실행하지 마세요.

## 통합 확장하기

패키지는 `devkit_agt.features.integration`을 통해 연결됩니다. `ReadinessProvider`는 작업이 완료되었는지 판단하고,
`ScopedCleanup`은 묶인 정리 대상을 추가합니다(devkit-spec은 이를 이용해 범위 기록을 제거하고 제안 디렉터리를 정리합니다.
[협업](collaboration.md) 참고). 공개 API는 `IntegrationService`, `IntegrationRequest`, `IntegrationResult`와 타입이
지정된 오류도 내보냅니다.

이전 설계의 수명 주기 MCP 도구(`integration_prepare`, `integration_integrate`, ...)는 등록되지 않습니다. MCP 런타임은
공유 아티팩트와 보고서 게시를 위해 남아 있습니다([MCP](mcp.md) 참고).

## 출처

- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문):
  CLI 계약, 권한, 경로, 복구와 코드.
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-drive-development-to-integration.md).
- [ADR-host-cli-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md),
  [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261022-local-and-pull-request-integration.md).
- 관련 문서: [워크트리](worktree.md)(`CAP-WT-task-worktrees`).
