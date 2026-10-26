---
sources:
  CAP-DIST-content-packages: null
  CAP-DIST-context-and-playbooks: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-drift-reconciliation: null
  CAP-DLV-review-refactor: null
  UC-review-and-refactor-accumulated-slop: null
title: 누적된 군더더기 검토와 리팩터링
translated_from: en/journeys/review-and-refactor-accumulated-slop.md@f08853a79e0b002b
---

# 누적된 군더더기 검토와 리팩터링

<!-- handbook:provenance -->
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
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

에이전트는 코드를 쉽게 더하지만 좀처럼 지우지 않습니다. 기능이 쌓일수록 중복된 로직, 호출자가 하나뿐인 헬퍼,
아무도 쓰지 않는 호환성 심(shim), 여러 스킬에 반복된 지침, 서로 겹치는 CLI 옵션이 남습니다. 하나하나는 동작하지만,
모이면 이후의 모든 변경 비용을 키웁니다. `review-refactor` 플레이북(playbook)은 이 비용을 갚는 방법입니다. 에이전트가
여러분이 고른 코드, 지침 또는 CLI 표면(surface)을 검토하고, 각 발견 사항(finding)을 그것이 일으키는 유지보수 비용과
함께 보여 준 뒤, 여러분이 동의한 통합(consolidation)과 축소(reduction)만 동작이 유지된다는 증거와 함께 적용합니다.

목표는 문제 목록이 아니라 더 작은 표면입니다. 코드와 그 계약(contract) 사이의 불일치는 다른 일입니다. 에이전트는
이를 [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)(`CAP-DLV-drift-reconciliation`)을 위한 보류된 발견
사항으로 기록할 뿐, 그 플레이북을 직접 시작하지 않습니다. 플레이북과 워크플로(workflow)는 [개념](../concepts.md)을
참고하세요.

출처: [`UC-review-and-refactor-accumulated-slop`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md) (영어 원문),
계약 [`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-review-refactor.md),
플레이북 [`review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md).

## 시작하기 전에

- 옵트인 `maintenance` 카탈로그 번들이 선택되고 동기화되어 있어야 합니다. `uv run devkit add maintenance`(세 플레이북
  모두), `maintenance:upkeep`(드리프트 조정 포함) 또는 `maintenance:refactoring`(이 플레이북만) 중 하나를 씁니다
  ([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)).
- 릴리스 직전, 기능이 한동안 늘어난 뒤, 또는 저장소의 어느 부분이 필요 이상으로 무겁게 느껴질 때가 좋은 시점입니다.
- 검토할 표면(`code`, `guidance`, `cli`)과 각 표면의 루트(root)를 정해 두세요. 에이전트가 물어봅니다.
- 관련 없는 작업은 먼저 커밋하거나 stash 하세요. 에이전트는 실행에 속하지 않은 변경을 건드리는 대신 멈춥니다.

## 단계별 진행

1. **플레이북 호출.** `/devkit-playbook`을 실행해 `review-refactor`를 고르거나,
   `uv run devkit playbook get maintenance/review-refactor`로 가져오거나, `/spec`이 제안할 때 확인합니다. 플레이북은
   필요할 때 로드되며, 설치되어 있다거나 요청 문구가 비슷하다는 이유만으로 실행되지 않습니다
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).
2. **접수(intake).** 에이전트가 실행 ID, 저장소, `HEAD`, 더티 경로, 이전 보고서, 보고서를 둘 위치를 기록합니다.
   여러분이 표면과 루트를 지정하면, 실행은 표면마다 하나의 배치(batch)로 나뉩니다.
3. **배치 하나 검토.** 에이전트는 루트의 목록을 만들고 표면별 검토 질문을 던집니다. 코드에서는 중복된 동작, 반복된
   기술 헬퍼, 호출자가 하나뿐인 추상화, 추측성 호환성, 쓰이지 않는 코드를, 지침에서는 유도 가능하거나 중복되거나
   충돌하는 내용을, CLI에서는 겹치거나 불필요하거나 쪼개진 명령과 부정확한 도움말을 봅니다. 탐지 도구의 출력은 후보일
   뿐이며, 묻지 않고는 아무것도 설치하지 않습니다. 호스트가 서브에이전트를 지원하면 검토를 나눠 맡길 수 있지만,
   에이전트는 모든 주장을 인용된 위치에서 확인하고 그 명령을 다시 실행한 뒤에만 사용합니다.
4. **발견 사항 기록.** 각 발견 사항에는 위치, 답하는 질문, 유지보수 비용(이후 변경이 반복하거나 읽거나 일관되게
   유지해야 하는 것), 제안 처분(disposition), 증거가 붙습니다. 비용을 말할 수 없는 후보는 버리고 개수만 셉니다.
   "에이전트가 썼다"거나 줄 수는 그 자체로 발견 사항이 되지 않습니다.
5. **한 번의 결정 라운드.** 에이전트는 배치 전체를 한꺼번에 보여 주고, 제안된 변경마다 경로(route), 수정 경로, 쓰기
   범위(write scope)를 함께 제시합니다. 발견 사항마다 여러분은 동작을 유지한 통합·축소·제거, 계약 변경으로 처리, 보류
   (목적지와 재개 조건 포함), 유지(이유 포함) 중 하나를 고릅니다. 여러분의 승인은 그 결과 작업 항목의 의도이며, 통합
   승인이 아닙니다.
6. **적용.** 합의된 동작 보존 변경은 자체 브랜치의 작업 항목 하나가 됩니다. 여러 모듈에 걸치면 유닛(Unit)이나 워커
   없이 직접(direct) 모드로 `sdd-overall-refactor`를 따르고, 한 기능이나 모듈 안이면 그 기능 워크플로를 자체 깊이로
   따릅니다
   ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문),
   [delivery 영역](../areas/delivery.md)). 각 변경은 이전 체크포인트 위에서 전후로 검증되고, 도달 가능성(reachability)
   증거와 함께 단독으로 커밋되며, 최종 헤드는 깨끗한 트리에서 전체 검증을 통과합니다.
7. **리뷰와 통합.** 새로운 리뷰어(또는 기록된 셀프 리뷰)가 작업 항목의 diff를 확인하고, 에이전트는 지적 사항을 고친
   뒤 모든 호환성 깨짐(breaking change)을 보고하며, 작업 항목은 여러분이 승인하면 저장소의 통합 경로로 통합됩니다.
8. **보고.** 에이전트는 실행 보고서를 완성합니다. 배치별 범위, 별도 기록으로 나눈 발견 사항과 변경, 결정, 후속 작업,
   개수(발견, 적용, 계약 작업 항목, 보류, 유지, 대기)가 담깁니다. 대기 중인 결정이 없으면 배치가 완료됩니다.

## 변경이 보여야 하는 것

- **모든 축소의 근거**: 내용이 유도 가능하거나, 정본(canonical copy)이 명시된 중복이거나, 다른 곳의 검사가 강제하거나,
  기록된 검사로 불필요함이 드러났어야 합니다. 줄 수나 토큰 수의 차이는 보고만 할 뿐 이유가 되지 않습니다.
- 공유 구현으로 통합하기 전에 **실제 호출자 둘**이 있어야 합니다.
- **도달 가능성**: 정적 참조와 동적 도달(엔트리 포인트, 레지스트리, 설정, 문자열 디스패치)을 확인하고, 각 검색을
  결과와 함께 기록합니다. 특성화 테스트(characterization test)는 통합되는 호출자 중 테스트가 없는 것이 있을 때만
  추가합니다.
- **지침의 경우**, 제거된 텍스트의 각 제약과 그것이 여전히 남아 있는 위치를 대응시킨 표가 필요합니다.
- **배치 위치**는 선언된 계층 구조에서 가장 낮은 공통 소유자입니다. 새 패키지 간 모듈이나 기반 모듈은 결정 라운드에서
  여러분이 정합니다.

## 문제가 생겼을 때

- **표면이나 루트를 주지 않았습니다.** 에이전트가 먼저 묻고, 기록될 때까지 아무것도 살펴보지 않습니다.
- **호스트에 서브에이전트가 없습니다.** 에이전트가 검토와 이후의 diff 리뷰를 직접 수행하며, 후자는 셀프 리뷰로
  기록됩니다.
- **서브에이전트의 주장이 맞지 않습니다.** 예를 들어 레지스트리가 여전히 참조하는 "쓰이지 않는" 함수입니다. 그 주장은
  버려지거나 범위 공백(coverage gap)으로 기록되며 결정 라운드에 오르지 않습니다.
- **발견 사항이 선택하지 않은 표면에 떨어집니다.** 후속 작업과 함께 보류됩니다. 그 표면을 추가하면 자체 배치, 루트,
  결정 라운드가 생기고 보고서에 기록됩니다.
- **아무도 답하지 않거나**, 외부 실행기가 실행을 시작했습니다. 실행은 결정 라운드에서 결과 `stopped at decision round`로
  멈추고, 아무것도 적용되지 않으며 보고서만 바뀝니다.
- **명령, 옵션 또는 공개 인터페이스 제거를 승인했습니다.** 이는 계약 변경입니다. 리팩터링 작업 항목 밖에서, 계약과
  문서 갱신을 포함한 일반 개발 워크플로의 별도 작업 항목이 됩니다. 선언된 호환성 정책이 외부 소비자가 없다고 밝힌
  호환성 경로는 더 이상 받지 않는 입력을 명시한 채 배치에 남을 수 있습니다.
- **서브에이전트의 수정이 할당된 범위를 벗어나거나 합의된 변경과 다릅니다.** 에이전트는 다른 범위를 건드리지 않고 그
  헝크(hunk)를 되돌린 뒤, 변경을 다시 하거나 결정 라운드로 되돌립니다.
- **접수 이후 `HEAD`나 관련 더티 경로가 바뀌었습니다.** 증거를 다시 검증하고, 의도가 바뀌는 변경은 결정 라운드로
  돌아갑니다.
- **설치 기록(receipt)이 소유한 파일이 관련됩니다** (`.devkit/managed/`, 에이전트 프로젝션(projection)). 이 파일들은
  수정하지 않으며, 변경은 원본 번들, 업스트림 후속 작업 또는 `devkit override`로 갑니다.
- **시드된 연습(seeded exercise)입니다.** 결정은 시뮬레이션으로 표시되고 픽스처만 바뀝니다.

## 결과

적용된 모든 변경이 합의되고, 증거와 함께 단독으로 커밋되고, 리뷰를 거쳐 자체 승인으로 통합된 더 작은 표면을
얻습니다. 보고서는 발견 사항과 변경을 구분하고 범위, 공백, 후속 작업을 밝힙니다. 플레이북을 호출하는 것만으로는
아무것도 바뀌지 않고, 계약 변경을 리팩터링으로 포장하지 않으며, 배치 하나로 저장소 전체를 검토했다고 주장하지
않습니다.
