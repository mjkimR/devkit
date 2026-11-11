---
sources:
  ADR-delivery-approval-and-lifecycle-authority: null
  ADR-local-and-pull-request-integration: null
  ADR-post-merge-verification: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-project-policy: null
  CAP-GOV-evaluation-lifecycle: null
  CAP-INT-mcp-services: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
title: 통합
translated_from: en/areas/integration.md@41b9ee7b7b6a10c2
---

# 통합

<!-- handbook:provenance -->
> 소스 커밋 `f115e96c8059` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-11에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](../journeys/adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](../journeys/advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](../journeys/assess-test-management.md)
- [필요한 명령 진입점 설계하기](../journeys/design-command-entrypoints.md)
- [개발에서 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [격리된 명령 실행하기](../journeys/execute-an-isolated-command.md)
- [설계 문제 탐색하기](../journeys/explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](../journeys/find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](../journeys/import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](../journeys/improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](../journeys/plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [결정 대체 관계 읽기](../journeys/read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](../journeys/record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](../journeys/snapshot-bundle-sources.md)
- [선택한 느린 작업 빠르게 하기](../journeys/speed-up-selected-slow-operations.md)
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

통합(integration)은 커밋된 작업 브랜치를 베이스 브랜치에 반영하고 정해진 범위를 정리합니다.
Host는 승인 전에 소스 내용을 검사하고 반영 후 최종 내용을 다시 검증합니다.
CLI는 Git 효과와 정책을 확인합니다. `status=completed`는 그 효과의 완료이며,
`verification=pending`은 최종 프로젝트 검증이 남았다는 뜻입니다.

## 정확한 효과 준비하기

정리할 워크트리 밖의 런타임을 사용해 유지되는 베이스 체크아웃에서 실행합니다.

```bash
uv run devkit integration prepare dev-login --route local
uv run devkit integration integrate dev-login --route local --expected-digest <digest>
```

`prepare`는 소스·대상 SHA, 워크트리 식별 정보, 정책, 병합 방식과 정리 범위를 묶습니다.
반영하거나 삭제하지는 않습니다. `dev-integration=ask`에서는 Host가 이 효과를 제시하고 대화에서 사용자의 결정을 받은 뒤
`integrate`를 실행합니다. digest는 범위 변경을 감지하며 승인을 인증하지 않습니다.
공유 베이스의 `auto` 정책에서는 로컬 통합이 위임되며 `authority: policy`로 보고합니다.
소스에서만 바뀐 정책으로 자신의 병합을 승인할 수는 없습니다.

SDD와 적응형 개발(adaptive development)은 같은 명시적 브랜치 명령을 씁니다.
task-kind, task-id, unit, claims 인자와 준비 상태 제공자 선택은 없습니다.
`[integration]` 테이블은 키를 허용하지 않습니다. 폐기된 `provider` 키를 제거합니다. Host가 소스 런타임으로 워크플로 보류와 필수 검사를 먼저 확인합니다.

## 경로 선택하기

- **로컬:** 대상 체크아웃 밖에서 예상 병합을 만들고 대상을 그 결과로 fast-forward합니다.
  `no-ff`에서는 이동한 대상과 충돌이 없으면 소스에 베이스를 먼저 병합하지 않아도 됩니다.
  `ff-only`에서는 소스가 대상을 포함해야 합니다. fetch, push, 원격 브랜치 삭제는 수행하지 않습니다.
- **풀 리퀘스트:** 인증된 `gh`로 승인된 소스 SHA를 고정하고 필수 검사·리뷰와 반영을 확인한 뒤,
  lease를 이용한 원격 삭제와 로컬 정리를 수행합니다. 자동 실행하지 않습니다. PR 필수 정책은 로컬 경로를 거부하며,
  병합 큐나 보호 우회가 필요한 작업은 지원하지 않습니다.

PR 검사가 대기 중이면 `INTEGRATION_CHECKS_PENDING`과 함께 PR을 병합하지 않고 유지합니다.
병합에는 새 준비와 권한이 필요합니다. 호스트 권한과 게시 권한은 통합 정책과 별개입니다.

## 반영 후 검증하기

첫 병합 전에 대상 SHA를 저장합니다. 반영이 확인되면 다음을 수행합니다.

1. 대상의 선언된 의존성을 동기화합니다.
2. 새 프로세스에서 자산을 동기화하고 추적되는 생성 파일을 검사합니다.
3. 오래된 생성물을 재생성·커밋하고, 저장한 대상 SHA를 기준으로 필수 lint·타입·규칙·영향 테스트를 실행합니다.
4. 실제 검사한 최종 HEAD, 명령과 결과를 보고합니다.

로컬 오케스트레이션 배치는 선택한 병합과 수리를 마친 결합 HEAD를 한 번 검증할 수 있습니다.
그 HEAD가 통과하기 전까지 각 작업은 검증 대기입니다. 실패한 대상은 현재 위치에서 수리하고 다시 검사합니다.
병합을 재실행하거나 자동 롤백하지 않습니다.

`INTEGRATION_GENERATED_SEEDED`는 알려진 생성 파일 충돌을 선언된 seed 쪽 내용으로 유지했다는 뜻입니다.
결과의 `generated.seeded`, `generated.regenerate`가 대상을 나열합니다. 통합은 재생성을 실행하지 않았으므로
Host가 동기화 후 최종 검사 전에 처리합니다. 알 수 없는 충돌은 일반적인 충돌 해결이 필요합니다.

## 남은 효과만 복구하기

| 결과 | 다음 행동 |
| --- | --- |
| `INTEGRATION_AUTHORITY_REQUIRED`, `INTEGRATION_REQUEST_STALE` | 현재 범위를 다시 준비·제시하고 `ask`에서는 결정을 받습니다. |
| `INTEGRATION_TARGET_MOVED` | 현재 대상으로 다시 준비합니다. 로컬은 병합을 구성하고, PR 경로는 소스에 대상이 포함되어야 합니다. |
| `INTEGRATION_RUNTIME_IN_WORKTREE`, `WORKTREE_RUN_FROM_BASE` | 유지되는 베이스와 정리 범위 밖의 런타임을 씁니다. |
| `INTEGRATION_CLEANUP_INCOMPLETE` | Git·워크트리를 확인하고 보고된 남은 정리만 수행합니다. |

병합이 확인된 표시된 워크트리는 `uv run devkit worktree finish <branch>`로 남은 정리를 수행합니다.
확장 기능만 남았다면 `uv run devkit spec proposal prune <slug>`처럼 소유 명령을 정확한 대상에 실행합니다.
원격 결과가 불명확하면 쓰기를 반복하기 전에 확인합니다. 부분 정리의 종료 코드가 0이어도 남은 작업은 존재합니다.
`landed_sha`는 확인된 반영을 식별합니다.

로컬 오케스트레이션에서는 재사용하는 `git-operator`가 현재 승인된 정확한 수명 주기 작업을 실행할 수 있습니다.
Host가 결정, 소스 준비, 의미적 충돌 판단과 결과 수용을 맡습니다. 정상 통합에는 이미 정리가 포함됩니다.
[워크트리](worktree.md)와 [개발에서 통합까지 진행하기](../journeys/drive-development-to-integration.md)를 참고하십시오.

## 출처

- [ADR-delivery-approval-and-lifecycle-authority](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md) (영어 원문)
- [ADR-local-and-pull-request-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-local-and-pull-request-integration.md) (영어 원문)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md) (영어 원문)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)
- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md) (영어 원문)
- [ADR-post-merge-verification](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261104-post-merge-verification.md) (영어 원문)
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)
