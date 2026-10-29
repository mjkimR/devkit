---
sources:
  ADR-host-cli-lifecycle-authority: null
  ADR-local-and-pull-request-integration: null
  CAP-DLV-project-policy: null
  CAP-GOV-evaluation-lifecycle: null
  CAP-INT-mcp-services: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
title: 통합
translated_from: en/areas/integration.md@12a4fcf57f7a357e
---

# 통합

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
integrate의 두 단계로 나누어, 로컬 병합이나 풀 리퀘스트 중 한 가지 경로로 수행합니다.
[개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)(`UC-drive-development-to-integration`)
여정이 바로 이 단계에서 마무리됩니다. 브랜치, 워크트리, 게이트가 상호 작용하는 전체 구조는 [개념](../concepts.md)을 참고하세요.

## 결정 주체

통합은 비즈니스 차원의 결정이며, 프로젝트 정책에서 결정 주체를 정의합니다(`CAP-DLV-project-policy`의 `dev-integration`).

- **`ask`**: Host(전체 과정을 조율하는 에이전트 세션)가 정확한 소스, 대상, 보고서 및 정리 작업의 영향을 제시하면, 사용자가
  대화에서 승인 여부를 결정합니다. 승인이 이루어지면 Host가 명령을 실행합니다. CLI는 표준 입력(stdin)으로 대화형 입력을
  요구하지 않으며, 승인 플래그나 토큰도 받지 않습니다. 즉, 작업의 유효성을 다시 검증할 뿐 대화 세션 자체를 인증하지는 않습니다.
- **`auto`**: 베이스 브랜치 자체에 커밋된 정책에서 권한이 부여되며, 로컬 경로에만 적용됩니다. 결과에는
  `authority: policy`가 보고됩니다.

워커는 이 승인을 직접 요청하지 않으며, 다른 어떤 방법으로도 권한을 대신할 수 없습니다. 호출자의 `--claims`, 로컬 설정
오버레이, 호스트 도구 권한 등은 비즈니스 승인 권한에 해당하지 않습니다. 이러한 설계 근거는 `ADR-host-cli-lifecycle-authority`에
기록되어 있습니다.

## prepare 후 integrate

```text
devkit integration prepare <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>]
devkit integration integrate <branch> --task-kind unit|session --task-id <id> [--unit <dir>] [--route local|pull-request] [--claims <json>] [--expected-digest <digest>]
```

두 명령 모두 통합이 제거할 작업 워크트리 안이 아니라 베이스 체크아웃에서 실행합니다. 워크트리 안에서 실행하면
`WORKTREE_RUN_FROM_BASE`로 거부되며, 해결 방법은 `-w`로 베이스 체크아웃을 지정해 같은 명령을 실행하는 것입니다.

1. `prepare`는 커밋된 소스, 대상, 프로젝트 정책, 준비 상태 제공자(readiness provider), 정확한 정리 범위를 검증합니다.
   실제 변경은 전혀 발생하지 않으며, 다이제스트·경로·네트워크 사용 여부가 담긴 `[INTEGRATION_PREPARED: ...]`와 함께,
   워크트리와 브랜치 제거 여부, 실행될 확장 정리 작업, 준비 상태 제공자의 공개 내용을 알려 주는 `[INTEGRATION_SCOPE: ...]`
   줄을 출력합니다. `--format json`은 같은 승인 범위와 계획된 단계를 반환합니다.
2. Host는 이 결과를 사용자에게 안내합니다. `ask` 정책에서는 사용자가 대화에서 이를 승인합니다.
3. `integrate --expected-digest <digest>`는 요청을 새로 구성하여, 실제 변경을 적용하기 전에 모든 검사를 다시 수행합니다.
   `ask` 정책에서는 다이제스트 지정이 필수입니다. 다이제스트에 바인딩된 항목(소스, 대상, 정책, 준비 상태, 정리 범위) 중 하나라도
   변경되었다면 명령은 `INTEGRATION_REQUEST_STALE` 오류로 실행을 거부합니다. `auto` 정책에서는 다이제스트가 선택 사항이지만,
   값을 지정한 경우에는 여전히 일치해야 합니다.

다이제스트는 자격 증명이 아니라 동시성 전제 조건(concurrency precondition)입니다. 즉, 요청이 사용자가 확인한 바로 그 요청임을
보장할 뿐, 사용자가 승인했음을 증명하지는 않습니다. `ask` 정책에서 다이제스트 없이, 또는 더 이상 일치하지 않는 다이제스트로
`integrate`를 실행하면 거부(`INTEGRATION_AUTHORITY_REQUIRED` 또는 `INTEGRATION_REQUEST_STALE`)는 사용자와의 상호작용으로
처리됩니다. 해결 방법은 현재 범위를 보여 주는 `prepare` 명령이며, 이에 맞는 `integrate` 명령은 사용자가 승인한 뒤에 쓰도록
세부 정보로만 제시됩니다.

호출자 `--claims`(예: 세션의 리뷰, 테스트, 린트 결과)는 각 명령에 명시적으로 전달합니다. 어느 명령도 다른 명령의 claims를
저장하거나 재사용하지 않으므로 두 명령 모두에 전달하세요.

종료 코드: `0`은 성공이며, 유일한 문제가 `INTEGRATION_CLEANUP_INCOMPLETE` 경고인 `partial` 결과(Git 통합은 끝났고 범위 지정
정리만 남은 경우)도 포함합니다. `1`은 일부 효과가 적용된 뒤 오류로 중단된 실행, `2`는 어떤 효과도 적용되기 전의 거부입니다.
`--strict`는 경고를 `1`로 올리지만 `2`를 낮추지는 않습니다.

## 경로 선택

- **로컬**(`--route local`): devkit이 베이스 체크아웃 외부에서 병합 커밋을 구성하고, 검증을 거친 뒤 베이스 브랜치를 fast-forward하며,
  지정된 범위의 정리 작업을 실행합니다. 원격 브랜치를 fetch, push하거나 삭제하지 않습니다. 이는 `devkit worktree finish`와 동일한
  병합 메커니즘을 사용하며([워크트리](worktree.md) 참고), `[worktree] merge = "ff-only"` 설정을 따릅니다.
- **풀 리퀘스트**(`--route pull-request`): devkit이 GitHub 어댑터를 통해 원격 쓰기 작업을 명시적으로 수행하며, 저장소 바인딩과
  HEAD 고정을 유지하고, 필수 검사 완료를 대기합니다. 반영이 확인되면 로컬 정리를 수행하기 전에 임대한 원격 브랜치를 삭제합니다.
  이 과정은 자동으로 실행되지 않으며, `[worktree] pull_request = "required"` 정책이 설정되어 있으면 로컬 경로 실행을 거부합니다.

어느 경로를 선택하든 호스트 도구 권한, 파일 시스템 권한, 신뢰 수준, 게시 정책은 변경되지 않습니다. 병합 커밋 구성과 경로 보호 장치는
`CAP-INT-mcp-services` 계약의 일부이며, `ADR-host-cli-lifecycle-authority`가
`ADR-local-and-pull-request-integration`을 대체합니다.

## 문제 해결

모든 실행 결과에는 완료된 단계, 실패한 작업, 고유 에러 코드, 확인된 Git 상태가 상세히 표시됩니다. 호출 간에는 아무런 상태도
유지되지 않습니다. 요청 ID, 승인 내역, 복구 저널 등이 보존되지 않으므로, 상태를 확인하고 다시 prepare를 실행하는 방식으로
복구해야 합니다.

| 코드 | 조치 방법 |
| --- | --- |
| `INTEGRATION_NOT_READY` | 보고된 완료 조건을 해결한 뒤 다시 prepare를 실행합니다. 증거가 `SESSION_CLAIMS_INVALID`이면 소스는 바꿀 필요가 없습니다. `--claims`를 고쳐 같은 명령을 다시 실행하세요. |
| `INTEGRATION_RULE_RUNTIME_MISMATCH` | 소스의 동기화된 규칙이 실행 중인 런타임(대상에서 빌드됨)에 없는 것을 임포트합니다. 소스는 바꿀 필요가 없습니다. 별도로 권한을 받은 뒤 워크트리 밖에서 소스 코드로 런타임을 빌드하고, 그 런타임으로 베이스 체크아웃에서 통합하세요. |
| `INTEGRATION_AUTHORITY_REQUIRED` | `ask` 정책에서 다이제스트가 없으면 제안된 `prepare`로 범위를 보여 주고, 승인을 받은 뒤 통합합니다. 그 밖에는 베이스 정책과 경로를 확인합니다. |
| `INTEGRATION_REQUEST_STALE` | 범위가 바뀐 경우 다시 보여 주고 결정합니다. 일부 효과가 적용된 경우 이미 처리된 내역을 확인하고, 남은 범위를 prepare한 뒤 다시 결정합니다. |
| `INTEGRATION_APPROACH_MISMATCH`, `INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED` | 프로젝트 준비 상태 제공자가 SDD 작업을 만났습니다(아래 참고). spec 제공자의 수명 주기를 사용하거나, 지목된 유닛의 수명 주기 검증을 실행하세요. |
| `INTEGRATION_TARGET_MOVED` | 현재 베이스 브랜치를 작업 브랜치에 병합하고 검사를 다시 실행한 뒤 결정을 다시 진행합니다. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | 남은 정리 작업을 완료합니다(아래 설명 참고). |
| `INTEGRATION_LANDED_UNCHECKED` | 통합 완료로 처리하기 전에, 제공자의 대상 브랜치 반영 검사를 실행합니다. |
| `INTEGRATION_CONFIG_INVALID`, `INTEGRATION_PROVIDER_FAILED` | 준비 상태 제공자를 설치 또는 복구하거나, 지원되는 경로를 사용합니다. |

대표적인 복구 절차는 다음과 같습니다.

- 병합이 반영되지 않은 경우: 소스와 대상을 확인한 뒤, 다시 시도하기 전에 새로운 결정을 받으세요.
- 병합은 반영되었으나 정리가 실패한 경우: `devkit worktree status`를 확인합니다. 워크트리가 남아 있다면 남은 정리 작업만 안전하게
  수행하는 `devkit worktree finish <branch> --merge --local-only`를 실행하세요. 완료 후속(post-finish) 작업이 실패했다면,
  보고된 대상에 대해 해당 작업 고유의 명령(예: `devkit spec proposal prune <slug>`)을 직접 실행합니다.
- 풀 리퀘스트 경로에서 원격 브랜치 삭제가 실패했거나 결과를 알 수 없는 경우: 로컬 워크트리와 브랜치가 그대로 유지됩니다. 문제를
  해결한 뒤 남은 범위를 prepare 및 integrate하세요. 이미 병합된 PR은 유효성만 검증되며, 중복으로 병합되지 않습니다.
- 결과를 알 수 없는 경우: 항상 Git이나 풀 리퀘스트 상태를 먼저 확인해야 합니다. 결과를 알 수 없는 원격 쓰기 작업을 무작정 다시
  실행해서는 안 됩니다.

## 대상에서 빌드한 런타임이 소스의 규칙을 판정

준비 상태 검사는 이를 호출한 런타임, 즉 대상에서 빌드된 런타임에 설치된 devkit으로 실행되지만, 평가하는 동기화된 규칙은
소스의 것입니다(`CAP-GOV-evaluation-lifecycle`). 브랜치가 추가한 규칙의 모듈이 대상 런타임에 없으면, 통합은 제공자를 실행하기
전에 `INTEGRATION_RULE_RUNTIME_MISMATCH`로 각 규칙 파일과 누락된 임포트를 알려 주고 아무것도 바꾸지 않습니다. 이 검사는 규칙
모듈을 파싱만 할 뿐 소스 코드를 실행하지 않으며, 통합이 스스로 소스에서 런타임을 빌드하는 일도 없습니다
(`UC-drive-development-to-integration`, 확장 7h).

## SDD 없는 통합

커밋된 개발 방식(development approach)이 인큐베이션인 프로젝트에서는 설치된 `project` 준비 상태 제공자가 SDD 유닛, 단계,
엔벨로프를 만들어 내지 않고 `--task-kind session` 통합을 처리합니다. `--claims`에는 통과한 `review`, `tests`, `lint` 결과가
있어야 합니다. 제공자는 예정된 병합 결과에 대해 누적 린터 규칙을 실행하지만, 리뷰·테스트·린트를 다시 실행하지는 않으며 이를
claims로 공개합니다. 커밋된 SDD 대상은 거부하고(`INTEGRATION_APPROACH_MISMATCH`), 유지 중인 워크플로 유닛의 기록을 건드리는
변경은 해당 유닛의 수명 주기 검증이 실행될 때까지 거부합니다(`INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED`). spec 제공자는 일반
인큐베이션 세션을 이 제공자에게 넘깁니다.

## 통합 기능 확장

패키지는 `devkit_agt.features.integration`을 통해 기능을 확장할 수 있습니다. `ReadinessProvider`는 작업 완료 여부를 판단하고,
`ScopedCleanup`은 연계된 정리 대상을 추가합니다(devkit-spec은 이를 활용해 범위 기록을 제거하고 제안 디렉터리를 정리합니다.
[협업](collaboration.md) 참고). 공개 API에는 `IntegrationService`, `IntegrationRequest`, `IntegrationResult`와 관련
타입화된 오류들이 포함됩니다.

이전 설계에 있었던 수명 주기 MCP 도구(`integration_prepare`, `integration_integrate` 등)는 등록되지 않습니다. MCP 런타임은
제안 검토를 위한 공유 아티팩트 용도로만 유지되며, 수락(acceptance) 과정에는 필요하지 않습니다([MCP](mcp.md) 참고).

## 출처

- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문):
  CLI 계약, 권한, 경로, 복구와 코드.
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-drive-development-to-integration.md).
- [ADR-host-cli-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md),
  [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261022-local-and-pull-request-integration.md).
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md) (영어 원문):
  어떤 규칙이 어디서 실행되는지.
- 관련 문서: [워크트리](worktree.md)(`CAP-WT-task-worktrees`).
