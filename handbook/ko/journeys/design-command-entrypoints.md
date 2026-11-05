---
sources:
  CAP-HARN-command-design: null
  UC-design-command-entrypoints: null
title: 필요한 명령 진입점 설계하기
translated_from: en/journeys/design-command-entrypoints.md@d50722202f721222
---

# 필요한 명령 진입점 설계하기

<!-- handbook:provenance -->
> 소스 커밋 `dabb86f9e659` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-05에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
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

선택형 `command-design` 번들은 justfile recipe, CLI 명령, MCP 도구의 생성·설정·확장을 안내합니다.
`uv run devkit add command-design`으로 선택하고 관련 작업 때
`uv run devkit get-context command-design`으로 지침을 찾습니다.
번들 자체가 명령을 생성하거나 등록하지는 않습니다.

1. 동작(operation), 호출자(caller)와 기존 실행 경로를 확인합니다.
2. 기존 경로가 요구를 충족하면 재사용합니다. 유용한 조합, 필수 실행 컨텍스트나 다른 호출자 계약이 있을 때만
   wrapper 또는 alias를 추가합니다.
3. 기존 recipe 이름을 보존하고 커밋 검사를 빠르고 명시적으로 유지하며 훅 검사를 중복하지 않습니다.
   MCP 동작은 전체 CLI를 복제하지 않고 호출자 요구에 따라 고릅니다.
4. 프로젝트 관례에 따라 필요한 추가를 구현하고 문서에 적힌 디렉터리에서 필수 도구로 검증합니다.
   추가한 진입점마다 구체적인 목적이 있어야 합니다.

기존 공개 명령 삭제는 별도 호환성 결정입니다. 현재 작업에서 쓰지 않는다고 삭제하지 않고,
가상의 미래 작업을 위해 자리표시자 명령을 추가하지 않습니다.
Python CLI 구현은 [에이전트 우선 CLI 도구](../areas/cli.md)를 참고하십시오.

## 출처

- [UC-design-command-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/harness/UC-design-command-entrypoints.md) (영어 원문)
- [CAP-HARN-command-design](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-command-design.md) (영어 원문)
