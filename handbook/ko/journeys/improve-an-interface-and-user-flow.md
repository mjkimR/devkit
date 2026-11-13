---
sources:
  CAP-DLV-uiux-improvement: null
  UC-improve-an-interface-and-user-flow: null
title: 인터페이스와 사용 흐름 개선하기
translated_from: en/journeys/improve-an-interface-and-user-flow.md@276f54504ad0e145
---

# 인터페이스와 사용 흐름 개선하기

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
- [아이디어 발굴하고 구체화하기](discover-and-refine-an-idea.md)
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

인터페이스, 대표 작업과 제약을 제시하고 `/app-uiux-improve <goal>`을 명시적으로 호출합니다. 리뷰 전용 요청은 편집 없이 지적을 반환합니다. 구현 전 안내된 워크플로 외 절차 또는 소비자 워크플로를 선택합니다. 소비자 워크플로의 필수 단계와 리뷰는 유지되며 양쪽 경로 모두 제품 제약, 호스트 권한과 관련 검사를 따릅니다. 경로 선택만으로 별도 Git 권한이 생기지는 않습니다.

1. 편집 전 실제 대상과 실행 가능한 로컬 브랜치를 확인합니다. 구조·흐름 변경은 관련 OOUX 문서를 읽습니다. 시각 감지기의 부정 결과만으로 UI가 없다고 판단하지 않습니다.
2. 유용한 디자인 관점을 선택하고 방향을 종합합니다. 작업 초점은 순서를 정하며 명시적 제약이나 연기만 비목표가 됩니다.
3. 승인된 목표를 구현하고 같은 대표 작업·데이터와 재실행 가능한 캡처 방식으로 브랜치를 검증합니다. 모의(mock) 검증과 누락된 실제 환경 검증을 구분합니다. 색상 변경은 주요 쌍과 상태의 유효 색상 대비율을 계산해 보고합니다.
4. 수락한 변경, 검사, 한계, 오래된 문서의 해당 구절과 별도 후속 작업, 권한이 필요한 남은 Git 작업을 보고합니다.

## 선택적 Impeccable 세션

사용자가 선택한 세션에 제한된 설명을 전달하고 조정자는 제품 편집을 멈춥니다. 질문 없는 개선은 네이티브 스킬 로드가 되는 새 하위 에이전트에서 실행할 수 있습니다. 대화 중계는 실제 네이티브 로드와 같은 하위 에이전트의 연속 실행이 확인되어야 하며 `shape`와 `critique`는 중첩 역할도 필요합니다. 첫 단계는 쓰기 없이 읽고 전체 질문 묶음을 준비합니다. 출처가 있는 추천 답변까지 모든 답변을 사용자가 확인한 뒤 같은 하위 에이전트가 씁니다. 기능 부족, 연속 실행 손실 또는 필수 자율성 검사 불가는 관련 작업을 멈추고 사용자 세션이나 승인된 인라인 경로로 이어가며 검사를 실행했다고 주장하지 않습니다.

열거된 편집 중 승인 목표 안의 변경만 수락합니다. 다른 변경은 임의로 되돌리거나 삭제하지 않고 보고합니다. 로컬 전용 문맥은 절대 경로로 읽으며 복사·커밋·제거 권한을 추정하지 않습니다. `PRODUCT.md`와 `DESIGN.md` 편집은 명시적 파일·행위 권한이 필요합니다. 지원되는 상위 도구 도움말에 감사 저장 작업이 없으면 보고서로 지적을 반환하고 저장 불가를 알립니다.

## 문맥 링크

요청된 설정에서 `sh <installed-skill>/scripts/link-impeccable-context.sh`로 루트 문맥을 현재 워크트리의 `docs/materials/impeccable`에 연결합니다. 로컬 Git 제외 항목 `/PRODUCT.md`, `/DESIGN.md`, `/.impeccable`을 추가하기 전에 해당 줄을 보여 줍니다. `--check`는 쓰기 없이 차이를 확인합니다. 추적 중인 루트, 기존 항목과 교체된 항목을 보존하며 내용이 다르면 사용자 지시에 따라 병합합니다.

## 출처

- [UC-improve-an-interface-and-user-flow](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md) (영어 원문)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md) (영어 원문)
