---
sources:
  CAP-DIST-content-packages: null
  CAP-DIST-context-and-playbooks: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-drift-reconciliation: null
  CAP-DLV-performance-pass: null
  CAP-DLV-review-refactor: null
  UC-review-and-refactor-accumulated-slop: null
title: 누적된 군더더기 검토와 리팩터링
translated_from: en/journeys/review-and-refactor-accumulated-slop.md@1dbdabe5363b83e2
---

# 누적된 군더더기 검토와 리팩터링

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](incubate-an-idea.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
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

에이전트는 코드를 쉽게 추가하지만 스스로 삭제하는 경우는 드뭅니다. 여러 기능 개발이 반복되면서 중복 로직, 단일 호출자만 가진 헬퍼 함수, 불필요한 호환성 래퍼(shim), 여러 스킬에 걸쳐 중복된 지침, 서로 겹치는 CLI 옵션 등이 점차 쌓이게 됩니다. 각각의 요소는 정상 동작하더라도, 이들이 누적되면 이후의 모든 변경 비용이 증가합니다. `review-refactor` 플레이북은 이러한 유지보수 부채를 줄이기 위한 절차입니다. 에이전트가 지정된 코드, 지침, CLI 인터페이스 영역을 검토하고 각 발견 사항이 유발하는 유지보수 비용을 제시한 후, 사용자가 승인한 통합 및 축소 작업만을 기존 동작이 보존된다는 증거와 함께 적용합니다.

이 여정의 목표는 단순한 문제 목록 작성이 아니라 표면적을 실제로 줄이는 것입니다. 코드와 계약 간의 불일치는 별도의 작업입니다. 에이전트는 이를 [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)(`CAP-DLV-drift-reconciliation`)를 위한 보류 발견 사항으로 기록할 뿐, 해당 플레이북을 스스로 실행하지 않습니다. 느린 작업도 별도의 일입니다. [선택한 느린 작업 빠르게 하기](speed-up-selected-slow-operations.md)는 이 플레이북의 적용 및 증거 절차를 참고 텍스트로 재사용합니다. 플레이북과 워크플로의 개념은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-review-and-refactor-accumulated-slop`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md) (영어 원문),
계약 [`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-review-refactor.md) (영어 원문),
플레이북 [`review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md) (영어 원문).

## 시작하기 전에

- 선택형 `maintenance` 카탈로그 번들을 추가하고 동기화합니다. `uv run devkit add maintenance`(네 플레이북 전체), `maintenance:upkeep`(드리프트 조정 포함), `maintenance:refactoring`(본 플레이북 단독), `maintenance:performance`(`performance-pass` 포함) 중 하나를 선택할 수 있습니다([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)).
- 릴리스 전, 기능 개발이 한동안 누적된 후, 또는 저장소 일부가 지나치게 무거워졌을 때 실행하기에 적합합니다.
- 검토 대상 영역(`code`, `guidance`, `cli`)과 각 영역의 루트 디렉터리를 미리 정해 둡니다. 실행 시 에이전트가 이를 묻습니다.
- 작업과 무관한 변경 사항은 미리 커밋하거나 스태시(stash)해 둡니다. 에이전트는 이번 실행에 속하지 않는 변경을 발견하면 건드리지 않고 멈춥니다.

## 단계별 진행

1. **플레이북 호출.** `/devkit-playbook`을 실행하여 `review-refactor`를 선택하거나, `uv run devkit playbook get maintenance/review-refactor`로 가져오거나, `/spec`이 제안할 때 확인합니다. 플레이북은 필요할 때 로드되며, 설치되어 있다거나 대화 문구가 비슷하다는 이유만으로 실행되지 않습니다([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).
2. **작업 접수(Intake).** 에이전트가 실행 ID, 저장소, `HEAD`, 수정된(dirty) 경로, 이전 보고서, 보고서 저장 위치를 기록합니다. 사용자가 대상 영역과 루트를 지정하면, 실행은 영역별 배치로 나뉩니다.
3. **단일 배치 검토.** 에이전트가 루트를 조사하고 영역별 검토 질문을 던집니다. 코드는 중복 동작, 반복된 기술 헬퍼, 호출자가 하나뿐인 추상화, 추측성 호환성 코드, 미사용 코드를, 지침은 유도 가능하거나 중복되거나 상충하는 내용을, CLI는 겹치거나 불필요하거나 파편화된 명령과 부정확한 도움말을 봅니다. 탐지 도구의 출력은 후보일 뿐이며, 묻지 않고 아무것도 설치하지 않습니다. 호스트가 서브에이전트를 지원하면 검토를 나눌 수 있지만, 에이전트는 모든 주장을 인용된 위치에서 확인하고 그 명령을 다시 실행한 후에만 사용합니다.
4. **발견 사항 기록.** 각 발견 사항에는 위치, 검토 질문, 유지보수 비용(향후 변경이 반복하거나 읽거나 일관되게 맞춰야 하는 것), 제안 조치, 증거가 포함됩니다. 비용을 말할 수 없는 후보는 제외되고 집계되며, "에이전트가 작성함"이나 줄 수 자체는 발견 사항이 될 수 없습니다.
5. **일괄 결정 라운드.** 에이전트가 배치 전체를 한 번에 보여 주며, 제안된 각 변경의 경로, 수정 경로, 쓰기 범위(write scope)를 함께 제시합니다. 사용자는 각 항목에 대해 동작을 보존하는 통합·축소·제거, 계약 변경으로 처리, 보류(대상 위치와 재개 조건 포함), 유지(사유 포함) 중 하나를 고릅니다. 이 승인은 결과 작업 단위의 의도이며, 통합 승인과는 별개입니다.
6. **병렬 수정.** 합의된 동작 보존 변경은 독립 브랜치의 작업 단위 하나가 됩니다. 여러 모듈에 걸치면 유닛이나 워커 없이 직접(direct) 모드의 `sdd-overall-refactor`를 따르고, 한 기능이나 모듈 안이면 그 기능 워크플로를 자체 깊이로 따릅니다([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문), [전달 영역](../areas/delivery.md)). 호스트가 서브에이전트를 지원하면 쓰기 범위가 겹치지 않는 변경들을 동시에 수정하며, 각각은 브랜치의 현재 커밋에서 만들고 새 체크아웃처럼 준비(의존성 설치, 관리 자산 동기화)한 독립 체크아웃에서 진행됩니다. 서브에이전트는 자기 범위만 수정하고 결과를 커밋하지 않은 채 남깁니다.
7. **하나씩 커밋.** 에이전트가 각 결과를 차례로 브랜치에 옮겨 이전 체크포인트 기준으로 전후를 검증하고, 저장소의 커밋 검사를 거쳐 보존 증거와 함께 단독으로 커밋합니다. 최종 헤드는 깨끗한 작업 트리에서 전체 검증을 통과해야 합니다.
8. **검토 및 통합.** 새로운 리뷰어(또는 기록된 셀프 리뷰)가 작업 단위의 diff를 검토합니다. 리뷰어 브리프에는 변경별 보존 주장이 담기며, 동작이 달라지는 입력을 재현 방법과 함께 찾도록 요청합니다. 에이전트는 지적 사항을 고치고 모든 호환성 파괴 변경을 보고하며, 사용자가 승인하면 작업 단위는 저장소의 통합 경로로 통합됩니다.
9. **보고서 작성.** 에이전트가 실행 보고서를 완성합니다: 배치별 검토 범위, 발견 사항과 변경 내역의 분리 기록, 더 이상 받지 않는 입력과 구분된 별도 섹션의 승인된 동작 변경, 결정, 후속 작업, 통계(발견, 적용, 계약 작업 단위, 보류, 유지, 대기), 통합 상태. 작업 단위가 통합되기 전에 작성된 보고서는 통합되거나 멈출 때 갱신됩니다. 대기 중인 결정이 없으면 배치가 완료됩니다.

## 변경 사항이 충족해야 하는 조건

- **모든 축소의 근거:** 내용이 유도 가능하거나, 명시된 정본(canonical copy)과 중복이거나, 다른 검사로 강제되거나, 기록된 검사로 불필요함이 입증되어야 합니다. 줄 수나 토큰 수 차이는 보고만 할 뿐 사유가 되지 않습니다.
- **실제 호출처 두 곳 이상:** 공용 구현으로 통합하기 전에 필요합니다. 합쳐지는 구현들이 똑같이 동작하지 않으면, 발견 사항에 각 차이와 유지할 동작을 나열하고 사용자의 결정이 각 차이를 다뤄야 합니다.
- **도달 가능성(reachability):** 정적 참조와 동적 도달(진입점, 레지스트리, 설정, 문자열 디스패치)을 각 검색과 결과와 함께 기록합니다. 특성화 테스트는 통합되는 호출자에 테스트가 없을 때만 추가합니다.
- **나란히 비교:** 파서, 스캐너, 매처, 파일 목록, 직렬화 형식처럼 입력을 열거할 수 있는 것을 바꾸는 변경은 이전 코드와 새 코드를 같은 입력(저장소 자체 코퍼스와 경계 사례)으로 실행해 입력 수와 결과를 기록합니다. 이전 코드는 추출한 사본이나 별도 체크아웃에서 실행하며, 스태시는 모든 워크트리가 공유하므로 스태시로 복원하지 않습니다.
- **제거 후 정리:** 제거된 경로만 도달하던 분기, 매개변수, 타입, 오류, 헬퍼는 합의된 변경 안에서 함께 제거하거나, 남기거나 보류한 항목으로 기록합니다.
- **지침의 경우:** 제거된 텍스트의 각 제약이 어디에 남아 있는지 매핑을 제시합니다.
- **배치 위치:** 선언된 계층 구조에서 가장 낮은 공통 소유자에 둡니다. 새 크로스 패키지 모듈이나 기반 모듈을 만들지는 결정 라운드에서 사용자가 정합니다.

## 문제가 생겼을 때

- **검토 영역이나 루트가 지정되지 않은 경우:** 에이전트가 먼저 묻고, 기록될 때까지 아무것도 조사하지 않습니다.
- **호스트에 서브에이전트가 없는 경우:** 에이전트가 같은 검토를 직접 하고, 변경을 하나씩 차례로 적용하며, diff도 직접 검토해 셀프 리뷰로 기록합니다.
- **두 변경이 겹치거나 한 변경이 다른 변경에 기반하는 경우:** 차례로 실행하며, 두 번째 변경은 첫 번째가 커밋한 체크포인트에서 시작합니다.
- **서브에이전트의 주장이 맞지 않는 경우:** 예컨대 레지스트리가 아직 참조하는 함수를 "미사용"으로 보고한 경우입니다. 그 주장은 버려지거나 범위 공백으로 기록되며 결정 라운드에 오르지 않습니다.
- **변경이 계층, 규칙, 설정 검사에 실패하는 경우:** 서브에이전트는 실패를 보고하며, 서브에이전트도 에이전트도 예외, 무시 항목, 규칙 설정, 검사 우회를 추가하지 않습니다. 에이전트가 변경 위치를 다시 정하거나 결정 라운드로 되돌립니다.
- **비교나 리뷰어가 차이를 찾은 경우:** 에이전트가 고치거나, 사용자가 동작 변경으로 승인하면 보고서에 기록됩니다.
- **선택하지 않은 영역에서 발견 사항이 나온 경우:** 후속 작업과 함께 보류합니다. 그 영역을 추가하면 별도의 배치, 루트, 결정 라운드가 생기고 보고서에 기록됩니다.
- **아무도 답하지 않거나 외부 러너가 실행을 시작한 경우:** 결정 라운드에서 `stopped at decision round`로 멈추며, 아무것도 적용되지 않고 보고서만 바뀝니다.
- **명령, 옵션, 공개 인터페이스의 제거를 승인한 경우:** 이는 계약 변경입니다. 리팩터링 작업 단위 밖에서, 계약과 문서 갱신을 포함한 일반 개발 워크플로의 별도 작업 단위가 됩니다. 선언된 정책상 외부 소비자가 없는 호환 경로는 더 이상 받지 않는 입력을 명시한 채 이 배치에 남을 수 있습니다.
- **서브에이전트 수정이 할당 범위를 벗어나거나 합의와 다른 경우:** 에이전트가 다른 범위를 건드리지 않고 해당 hunk를 되돌린 뒤, 변경을 다시 하거나 결정 라운드로 되돌립니다.
- **접수 이후 `HEAD`나 관련 수정 경로가 바뀐 경우:** 증거를 다시 검증하며, 의도가 달라진 변경은 결정 라운드로 돌아갑니다.
- **설치 기록(receipt)이 소유한 파일(`.devkit/managed/`, 에이전트 프로젝션)이 관련된 경우:** 직접 수정하지 않고, 원본 번들, 업스트림 후속 작업 또는 `devkit override`로 처리합니다.
- **모의 연습(seeded exercise)인 경우:** 결정은 모의로 표시되고 픽스처만 바뀝니다.

## 최종 결과

적용된 모든 변경이 합의되고, 커밋 검사를 거쳐 증거와 함께 단독으로 커밋되며, 각자의 승인으로 검토·통합된 더 작은 표면을 얻습니다. 보고서는 발견 사항과 변경을 구분하고, 승인된 동작 변경을 나열하며, 검토 범위, 공백, 후속 작업, 통합 상태를 밝힙니다. 플레이북 호출만으로는 아무것도 바뀌지 않고, 계약 변경을 리팩터링으로 가장하지 않으며, 변경을 통과시키려고 거버넌스 검사를 완화하지 않고, 한 배치가 저장소 전체를 검토했다고 주장하지 않습니다.
