---
sources:
  CAP-DLV-idea-discovery: null
  UC-discover-and-refine-an-idea: null
title: 아이디어 발굴하고 구체화하기
translated_from: en/journeys/discover-and-refine-an-idea.md@6fccf2ac6994f26f
---

# 아이디어 발굴하고 구체화하기

<!-- handbook:provenance -->
> 소스 커밋 `a6e769c5721d` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](assess-test-management.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
- [격리된 명령 실행하기](execute-an-isolated-command.md)
- [설계 문제 탐색하기](explore-a-design-problem.md)
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

`uv run devkit add deep-research`로 번들을 선택한 뒤 덜 구체화된 아이디어에 `/discovery <idea>`를 호출합니다. 아이디어 발굴(Idea discovery)은 출처 기반 조사와 별도 진입점이며 구현·커밋·게시 권한을 부여하지 않습니다.

1. 제공된 문맥에서 원하는 변화, 사용 장면, 제약과 결과를 파악합니다. 첫 제안을 바꾸는 사용자 고유의 선택만 질문합니다.
2. 탐색 질문, 투입 범위와 종료 조건을 밝힙니다. 편익, 비용, 근거와 가정을 갖춘 구체적 사용 예를 만들며 선택적 독립 역할이 서로 다른 전제를 살펴봅니다.
3. 사실 부족은 제한된 조사로, 경험 부족은 예시나 실험 제안으로, 실패한 전제는 재정의·보류·기각으로 연결합니다. 실행에는 별도 권한이 필요합니다.
4. 제안, 추천, 실제 사용자 결정, 불확실성, 근거의 한계와 다음 결정을 반환합니다. 결과는 구체화됨, 검증 필요, 보류 또는 기각입니다.

보존 요청이 없으면 결과는 대화에 남습니다. 보존 자료의 완전·부분 커버리지와 발굴 결과를 구분하고 커밋하지 않습니다. 독립 검증의 누락을 알리며 거부된 자원은 다른 경로로 접근하지 않습니다.

- [CAP-DLV-idea-discovery](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-idea-discovery.md) (영어 원문)

- [UC-discover-and-refine-an-idea](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-discover-and-refine-an-idea.md) (영어 원문)
