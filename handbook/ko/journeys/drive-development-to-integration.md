---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-project-policy: null
  CAP-DLV-workflow-envelopes: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
title: 개발에서 통합까지 진행하기
translated_from: en/journeys/drive-development-to-integration.md@f213520ed0b5f1b5
---

# 개발에서 통합까지 진행하기

<!-- handbook:provenance -->
> 소스 커밋 `dabb86f9e659` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-05에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [설계 문제 탐색하기](explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [인터페이스와 사용 흐름 개선하기](improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [선택한 느린 작업 빠르게 하기](speed-up-selected-slow-operations.md)
- [어드바이저리](../areas/advisory.md)
- [에이전트 우선 CLI 도구 키트](../areas/cli.md)
- [협업](../areas/collaboration.md)
- [컴팩트 명령 출력](../areas/compact.md)
- [전달](../areas/delivery.md)
- [배포](../areas/distribution.md)
- [문서](../areas/documents.md)
- [커밋 게이트](../areas/gate.md)
- [생성 파일](../areas/generated.md)
- [거버넌스 규칙](../areas/governance.md)
- [하네스](../areas/harness.md)
- [호스트](../areas/host.md)
- [통합](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [검색](../areas/search.md)
- [추적성](../areas/traceability.md)
- [뷰어](../areas/viewer.md)
- [워크트리](../areas/worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

의도가 합의되면 Development는 브랜치의 워크플로에 따라 구현, 리뷰, Living Spec 반영과 최종 보고를 진행합니다.
Host가 Git 통합 권한을 확인하고 반영된 대상을 검증합니다.
유닛·게이트·엔벨로프는 [개념](../concepts.md)을 참고하십시오.

## 1. 소스 워크플로 따르기

```bash
uv run devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>
```

에이전트가 강도와 이유를 밝히고 보고된 단계·검사·스킬을 따릅니다.
코드 전에 스펙·계획·작업 범위를 작성하고 범위 안에서 구현하며 영향 검사를 실행하고 단계마다 커밋합니다.
bugfix는 특성화, 재현(Red), 수정(Green) 근거를 남깁니다.
화면 초안은 코드보다 먼저 작성하며 선택적으로 UX 리뷰를 받고, 조정에서 `docs/ux/`에 유지합니다.

## 2. 리뷰, 조정과 보고

medium은 최초 독립 code-reviewer 검토가 필요합니다. 구현자가 발견 사항을 고치고 수정 결과를 검증합니다.
범위가 늘거나 정확성이 불확실하면 재검토할 수 있습니다. high는 제한된 반복, low는 자체 리뷰를 사용합니다.
구현자는 Living Spec을 갱신하고 `reconcile.md`를 해결하며 모든 강도에서 reconcile-check 근거를 기록합니다.
high는 독립 조정 리뷰가 필요합니다. medium은 영향 계약과 diff의 일치가 명확하고 구성 요소 간 해석이 없을 때만 자체 검증할 수 있습니다.

활성화된 피드백 단계를 수행하고 최종 변경 보고서를 작성합니다.
질문·문제·미해결 조정·미완료 검사는 명시적으로 남습니다.
Host가 소스 자체의 런타임으로 커밋된 내용을 확인하며 통합이 이 콘텐츠 검사를 대신 수행하지 않습니다.

## 3. 준비와 승인

최종 영향 테스트 선택을 위해 병합 전 대상 SHA를 저장합니다. 유지되는 베이스 체크아웃에서 실행합니다.

```bash
uv run devkit integration prepare dev-<slug> --route local
```

요청은 소스·대상 SHA, 정책, Git 식별 정보와 정확한 정리 효과를 고정합니다.
`dev-integration=ask`에서는 Host가 검증 보고와 효과를 제시하고 대화에서 결정을 받습니다.
공유 베이스의 `auto`에서는 검증된 로컬 통합이 정책으로 위임됩니다.

```bash
uv run devkit integration integrate dev-<slug> --route local --expected-digest <digest>
```

digest가 바뀌면 새 준비와 권한 확인이 필요합니다. 로컬 `no-ff` 통합은 충돌 없는 이동한 대상을 직접 병합합니다.
`ff-only`와 PR 경로는 소스가 대상을 포함해야 합니다.
콘텐츠 충돌은 소스 준비와 영향 검사로 돌아갑니다.

## 4. 반영, 동기화와 검증

로컬 통합은 대상 체크아웃 밖에서 결과를 구성하고 베이스를 fast-forward하며 fetch·push 없이 정해진 워크트리·브랜치를 정리합니다.
`landed_sha`가 반영을 확인합니다. `status=completed`는 Git 효과를 뜻하고
`verification=pending`은 Host의 전달 검증이 남았음을 나타냅니다.

반영된 의존성을 동기화한 뒤 새 프로세스에서 자산 동기화, 생성물 검사와 필수 lint·타입·규칙·영향 테스트를 실행합니다.
오래된 생성물은 최종 검사 전에 재생성·커밋합니다.
영향 테스트는 저장한 병합 전 대상을 기준으로 선택하고 최종 검사 HEAD와 실제 결과를 보고합니다.
로컬 오케스트레이션 배치는 선택한 병합·수리 후 결합 대상을 한 번 검증할 수 있습니다.
실패하면 전달은 대기 상태이며 대상을 수리하고 재검사합니다. 병합 재실행이나 자동 롤백은 하지 않습니다.

## 변형

- **Session:** 유닛·엔벨로프·조정 기록 없이 대화나 PR 본문에 변경·강도·리뷰·검사를 보고합니다.
  통합은 claims나 작업 식별 인자 없이 명시적 소스 브랜치만 받습니다.
- **Local-orchestrated:** Host가 워커의 커밋된 턴과 누적 규칙을 검사하고, 정확히 승인된 수명 주기 작업에 git-operator를 재사용할 수 있습니다.
  결정·의미적 충돌 처리·결과 수용은 Host에 남습니다.
- **PR 필수:** `--route pull-request`를 사용하며 플랫폼 필수 검사·리뷰와 소스 고정을 유지합니다.
  검사 대기 중인 미병합 PR은 새 준비와 권한 확인 후 병합합니다.
- **생성물 충돌 seed:** `INTEGRATION_GENERATED_SEEDED`가 seed·재생성 대상을 알려 줍니다.
  Host가 동기화 후 재생성하며 통합 자체는 생성기를 실행하지 않습니다.

## 부분 효과 복구

불명확한 작업을 반복하기 전에 Git·워크트리·PR 상태를 확인합니다.
확인된 병합 뒤 정리만 남으면 이미 병합된 상태를 확인하는 finish나 정확한 확장 명령을 사용합니다.
정상 통합에는 이미 정리가 포함됩니다.
`INTEGRATION_TARGET_MOVED`는 새 준비가 필요하고 `INTEGRATION_REQUEST_STALE`은 제시한 범위가 바뀌었다는 뜻입니다.
미응답 질문·미해결 문제는 [문제와 예외 처리](handle-delivery-problems-and-exceptions.md)를 따릅니다.
경로와 복구의 자세한 설명은 [통합](../areas/integration.md)에 있습니다.

## 출처

- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)
- [CAP-DLV-workflow-envelopes](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)
- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/mcp/CAP-MCP-runtime-registration.md) (영어 원문)
- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md) (영어 원문)
