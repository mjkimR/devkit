---
sources:
  CAP-DLV-uiux-improvement: null
  UC-improve-an-interface-and-user-flow: null
title: 인터페이스와 사용 흐름 개선하기
translated_from: en/journeys/improve-an-interface-and-user-flow.md@190b59ca81643bba
---

# 인터페이스와 사용 흐름 개선하기

<!-- handbook:provenance -->
> 소스 커밋 `f115e96c8059` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-11에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

선택형 `app-uiux-improve` 번들을 선택한 뒤 `/app-uiux-improve <목표>`를 명시적으로 호출하고
인터페이스, 사용자 과업과 제약을 제공합니다. 개선 요청은 소비 프로젝트의 기존 절차에 따라 요청된 구현까지 진행할 수 있습니다.
리뷰 전용 요청은 제품을 편집하지 않고 발견 사항을 반환합니다.

1. 대표 과업 경로, 관련 산출물과 영향받는 인터페이스 상태를 확인합니다.
2. 작은 요청은 직접 처리하고, 필요하면 designer, unconventional-designer, reference-researcher, critic 관점을 고릅니다.
   지원되는 경우 새 독립 컨텍스트로 최초 검토를 하고 지원되지 않는 부분은 밝힙니다.
3. 일관된 흐름과 시각적 방향, 중요한 상충 관계와 빠진 제품 결정을 종합합니다.
4. 프로젝트의 전달·권한·승인 절차로 요청된 변경을 적용합니다.
   현재 권한을 벗어난 범위 결정은 사용자 답변을 기다립니다.
5. 바뀐 인터페이스와 대표 상호작용을 확인하고 범위 안의 결함을 고친 뒤 영향 검사를 반복합니다.
6. 실제 변경, 수행한 검증과 중요한 한계를 보고합니다.

실행 화면을 볼 수 없으면 스크린샷·소스·텍스트 확인도 유용하지만 실제 상호작용 검증으로 보고하지 않습니다.
도구나 승인이 없으면 유용한 부분 작업과 구체적인 차단 사유를 남깁니다.
선택적 역할은 보존 파일·index·HEAD를 편집하지 않고 제안과 근거를 반환합니다.
고정 팀·점수·토론 반복·지속 메모리·다른 진입점의 자동 호출은 요구하지 않습니다.

## 출처

- [UC-improve-an-interface-and-user-flow](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md) (영어 원문)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md) (영어 원문)

## 객체 정리와 선택적 Impeccable 작업

진입점은 `app-uiux-improve` 번들의 `/app-uiux-improve`입니다. 구조·흐름 변경은 프로젝트의 OOUX 객체를 먼저 읽습니다. 사용자가 선택한 Impeccable 세션에는 제한된 작업 설명을 전달하고 조정자는 제품 편집을 멈춥니다. 세션이 열거한 제품 파일 변경만 수락하며 관련 없는 변경은 보고하고 자동으로 되돌리거나 삭제하지 않습니다. 소비자 소유 문맥 파일은 보존합니다. 오래된 OOUX 문서는 소비자 워크플로에서 갱신하도록 이름을 보고합니다.
