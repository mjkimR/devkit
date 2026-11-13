---
sources:
  CAP-DLV-design-exploration: null
  UC-explore-a-design-problem: null
title: 설계 문제 탐색하기
translated_from: en/journeys/explore-a-design-problem.md@b698e4ac98960c94
---

# 설계 문제 탐색하기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](assess-test-management.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [아이디어 발굴하고 구체화하기](discover-and-refine-an-idea.md)
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
- [격리된 명령 실행하기](execute-an-isolated-command.md)
- [최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [결정 대체 관계 읽기](read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](snapshot-bundle-sources.md)
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

선택형 `design-explore` 번들을 선택한 뒤 구조, 데이터 모델, 모듈 경계 또는 처리·개발 워크플로 문제로
`/design-explore <문제>`를 명시적으로 호출합니다.
결과는 장점·상충 관계·불확실성이 정리된 유용한 해결 방식 선택지입니다.

1. 목표, 기존 설계, 필수 제약과 열려 있는 선호를 제공합니다.
2. 조정자가 서로 다른 전제와 근거 질문을 고릅니다. 작은 문제는 직접 처리하고, 필요할 때만
   solution-explorer, reference-researcher, design-critic 관점을 사용합니다.
3. 새 하위 컨텍스트를 지원하면 최초 독립 탐색에 다른 관점의 결론을 전달하지 않습니다.
   지원되지 않으면 컨텍스트 공유와 빠진 범위를 밝힙니다.
4. 종합 결과는 유용한 차이와 비관습적 기제를 유지합니다. 비평은 근거와 실패 조건을 담고,
   지적 사항이 없어도 유효하며 보통 한 차례의 유용한 개선이면 충분합니다.
5. 대화에서 방향과 이유 있는 권고를 받습니다. 저장 위치를 명시적으로 요청한 경우에만 조정자가
   그 위치의 기존 형식으로 결과를 보존합니다.

고정된 역할 구성·대안 수·점수·프로토타입·효익 증명 실험은 요구하지 않습니다.
역할은 제품 소스, 보존 파일, 설정, `index`와 HEAD를 변경하지 않습니다.
호출은 구현·설정 변경·커밋·승인·게시를 허가하지 않습니다.
저장 위치가 거부되면 쓰기를 보류하고 유용한 대화 결과를 유지합니다.

## 중요한 반론 확인하기

조정자는 실제 후보와 반론을 탐색자에게 돌려보내 한 번의 응답을 받을 수 있습니다. 반론별 근거를 판단하고 불일치와 불확실성을 보존하며 합의나 역할 이름을 증거로 삼지 않습니다. 작성자 응답이 없으면 명시합니다. 추가 검토에는 결정을 바꿀 구체적 질문과 유한한 범위가 필요하며 자동 반박이나 구현으로 이어지지 않습니다.

## 출처

- [UC-explore-a-design-problem](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-explore-a-design-problem.md) (영어 원문)
- [CAP-DLV-design-exploration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-design-exploration.md) (영어 원문)
