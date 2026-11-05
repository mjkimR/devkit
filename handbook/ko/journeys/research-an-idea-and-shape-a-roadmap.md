---
sources:
  CAP-DLV-deep-research: null
  CAP-HARN-agent-guidance: null
  UC-research-an-idea-and-shape-a-roadmap: null
title: 아이디어 조사와 로드맵 구체화하기
translated_from: en/journeys/research-an-idea-and-shape-a-roadmap.md@b2d21efa1a726d4a
---

# 아이디어 조사와 로드맵 구체화하기

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
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
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

선택형 `deep-research` 번들을 선택한 뒤 `/deep-research <질문 또는 결정>`을 명시적으로 호출합니다.
진입점은 개발 방식(development approach)을 확인하거나 변경하지 않고 두 방식에서 모두 동작합니다.
결과는 출처 있는 조사이며 구현이나 전달 약속이 아닙니다.

## 질문에서 보존할 근거까지

1. 요청한 산출물, 용도, 제약과 유용한 조사 한도를 제공합니다.
2. 조정자가 주어진 사실을 복구하고 결정을 구체화하며 필요한 독립 질문을 고릅니다.
   작은 질문은 직접 처리할 수 있습니다. 선택적 역할은 출처 조사, 방향 탐색, 근거 비평이나 종합 초안을 맡습니다.
3. 조정자는 실제 반환을 확인하고 중요한 누락·모순에 대해 출처를 다시 엽니다.
   대안의 전제를 구분하고 관찰·추론·가정·미확인 사항을 나눕니다.
4. 유용한 종합과 안정적인 근거를 `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` 아래 하나의 자료(material)로 보존합니다.
   인덱스는 `id: MAT-<slug>`와 `Status: complete` 또는 `partial`을 가집니다.
5. 결과는 자료, 근거의 한계와 다음 결정을 알려 줍니다. 이후 제안·스펙·결정·적응형 개발 현재 컨텍스트가 ID를 인용하기 전에
   프로젝트 Git 정책에 따라 커밋합니다.

임시 작업은 `.devkit/transient/deep-research/` 아래에 두며 보존한 링크는 임시 디렉터리에 의존하지 않습니다.
보존 자료는 조정자만 씁니다. 조사 진입점은 stage·커밋·게시하지 않고 SDD 유닛·엔벨로프를 만들거나
`.devkit/adaptive-dev.md`를 편집하지 않습니다.

## 재개와 한계

자료 ID나 위치가 충돌하면 다른 slug를 고릅니다. 같은 조사의 명시된 `partial` 자료는 갱신할 수 있습니다.
완료 자료는 유지하고 후속 조사는 새 자료에서 이를 인용합니다. 이전 실행은 사용자가 입력으로 지목할 때만 읽습니다.

일반적인 공개 출처 조회 실패는 한정된 재시도나 접근 가능한 다른 1차 출처로 복구하고 실제 확인한 대체 출처를 기록합니다.
접근 거부가 있으면 해당 자원 접근을 멈춥니다. 부족한 근거는 미검증으로 남깁니다.
우승 대안을 꾸미거나 거절된 비교를 요구하지 않아도 부분 결과는 유용할 수 있습니다.
결과를 활용한 구현은 이후 프로젝트의 일반 개발 절차로 시작합니다.

## 출처

- [UC-research-an-idea-and-shape-a-roadmap](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md) (영어 원문)
- [CAP-DLV-deep-research](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-deep-research.md) (영어 원문)
- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)
