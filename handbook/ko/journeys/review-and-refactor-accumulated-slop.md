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
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

에이전트는 코드를 쉽게 추가하지만 스스로 삭제하는 경우는 드뭅니다. 여러 기능 개발이 반복되면서 중복 로직, 단일 호출자만 가진 헬퍼 함수, 불필요한 호환성 래퍼(shim), 여러 스킬에 걸쳐 중복된 지침, 서로 겹치는 CLI 옵션 등이 점차 쌓이게 됩니다. 각각의 요소는 정상 동작하더라도, 이들이 누적되면 이후의 모든 변경 비용이 증가합니다. `review-refactor` 플레이북은 이러한 유지보수 부채를 줄이기 위한 절차입니다. 에이전트가 지정된 코드, 지침, CLI 인터페이스 영역을 검토하고 각 발견 사항이 유발하는 유지보수 비용을 투명하게 제시한 후, 사용자가 승인한 통합 및 축소 작업만을 기존 동작이 보존된다는 증거와 함께 적용합니다.

이 여정의 목표는 단순한 문제 목록 작성이 아니라 시스템의 표면적을 실제로 줄이는 것입니다. 코드와 명세 계약 간의 불일치는 별도의 작업 영역입니다. 에이전트는 이를 [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)(`CAP-DLV-drift-reconciliation`)의 후속 처리를 위한 보류 발견 사항으로만 기록하며, 해당 플레이북을 임의로 실행하지 않습니다. 플레이북과 워크플로의 전반적인 개념은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-review-and-refactor-accumulated-slop`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md) (영어 원문),
계약 [`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-review-refactor.md),
플레이북 [`review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md).

## 시작하기 전에

- 선택형 `maintenance` 카탈로그 번들을 추가하고 동기화합니다. `uv run devkit add maintenance`(세 플레이북 전체 포함), `maintenance:upkeep`(드리프트 조정 포함), `maintenance:refactoring`(본 플레이북 단독) 중 하나를 선택할 수 있습니다([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)).
- 새로운 릴리스 전, 장기간 기능 개발이 누적된 후, 또는 저장소 일부가 과도하게 무겁고 복잡해졌을 때 실행하기에 적합합니다.
- 검토 대상 영역(`code`, `guidance`, `cli`)과 각 영역의 루트(root) 디렉터리를 미리 정해 둡니다. 실행 시 에이전트가 이를 확인합니다.
- 작업과 무관한 변경 사항은 미리 커밋하거나 스태시(stash)해 둡니다. 에이전트는 이번 실행 대상이 아닌 변경 사항을 발견하면 임의로 건드리지 않고 작업을 즉시 중단합니다.

## 단계별 진행

1. **플레이북 호출.** `/devkit-playbook`을 실행하여 `review-refactor`를 선택하거나, `uv run devkit playbook get maintenance/review-refactor`로 가져오거나, `/spec`이 제안할 때 확인합니다. 플레이북은 필요 시 온디맨드로 로드되며, 단순히 설치되어 있다거나 대화 문구가 유사하다는 이유만으로 자동 실행되지 않습니다([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).
2. **작업 접수(Intake).** 에이전트가 실행 ID, 저장소 상태, `HEAD`, 수정된(dirty) 경로, 이전 보고서 이력, 보고서 저장 위치를 기록합니다. 사용자가 대상 영역과 루트 디렉터리를 지정하면, 실행 작업은 영역별 배치로 나뉩니다.
3. **단일 배치 검토.** 에이전트가 루트 디렉터리의 자산을 조사하고 영역별 검토 기준을 점검합니다. 코드 영역에서는 중복 동작, 반복된 기술 헬퍼, 단일 호출자만 가진 추상화, 불필요한 호환성 코드, 미사용 코드를 점검합니다. 지침 영역에서는 다른 규칙에서 유도 가능한 내용, 중복되거나 상충하는 지침을 확인합니다. CLI 영역에서는 기능이 겹치거나 불필요하게 파편화된 명령, 부정확한 도움말을 확인합니다. 자동 탐지 도구의 출력은 어디까지나 후보일 뿐이며, 에이전트는 사전 동의 없이 임의로 패키지를 설치하지 않습니다. 호스트 환경이 서브에이전트를 지원하는 경우 검토 작업을 병렬 분할할 수 있지만, 에이전트는 인용된 소스 코드 위치에서 모든 주장을 검증하고 관련 명령을 직접 재실행한 후에만 결과를 채택합니다.
4. **발견 사항 기록.** 각 발견 사항에는 위치, 검토 질문, 유지보수 비용(향후 변경 작업 시 반복해서 작성하거나 읽고 일관성을 맞춰야 하는 부담), 제안 조치 방안, 근거 증거가 포함됩니다. 명확한 유지보수 비용을 설명할 수 없는 후보는 집계에서 제외되며, "에이전트가 작성한 코드임"이나 단순 코드 라인 수 자체는 발견 사항의 근거가 될 수 없습니다.
5. **일괄 결정 라운드.** 에이전트가 해당 배치의 모든 발견 사항을 한 번에 정리하여 보여 주며, 제안된 각 변경 사항에 대해 워크플로 경로, 수정 파일 경로, 쓰기 범위(write scope)를 함께 제시합니다. 사용자는 각 항목에 대해 기존 동작을 보존하는 통합·축소·제거, 규격 계약 변경으로 전환, 보류(대상 위치 및 재개 조건 포함), 유지(사유 포함) 중 하나를 선택합니다. 사용자의 승인은 생성될 작업 단위의 의도를 확정하는 것이며, 최종 통합 승인과는 구별됩니다.
6. **수정 적용.** 합의된 동작 보존 변경 사항들은 독립 브랜치에 하나의 작업 단위로 묶여 진행됩니다. 여러 모듈에 걸친 변경은 유닛이나 워커 없이 직접(direct) 모드의 `sdd-overall-refactor` 워크플로를 따르며, 단일 기능이나 모듈 내부의 변경은 해당 기능 워크플로의 자체 깊이를 따릅니다([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문), [전달 영역](../areas/delivery.md)). 각 변경 사항은 이전 체크포인트를 기준으로 전후 동작을 검증하고, 도달 가능성(reachability) 증거와 함께 단독으로 커밋되며, 최종 헤드는 깨끗한 작업 트리에서 전체 검증을 통과해야 합니다.
7. **검토 및 통합.** 새로운 리뷰어(또는 기록된 셀프 리뷰)가 작업 단위의 diff를 검토하고, 에이전트는 지적 사항을 조치한 뒤 모든 하위 호환성 파괴(breaking change) 여부를 보고합니다. 사용자가 승인하면 해당 작업 단위는 저장소의 표준 통합 경로를 통해 통합됩니다.
8. **보고서 작성.** 에이전트가 실행 보고서를 완성합니다. 배치별 검토 범위, 발견 사항과 실제 변경 내역의 분리 기록, 결정 사항, 후속 작업, 통계(발견됨, 적용됨, 계약 작업 단위, 보류됨, 유지됨, 대기 중)가 포함됩니다. 대기 중인 결정 사항이 모두 정리되면 배치가 완료됩니다.

## 변경 사항이 충족해야 하는 조건

- **모든 축소의 명확한 근거:** 내용이 다른 곳에서 도출 가능하거나, 명시된 정본(canonical copy)과의 중복이거나, 다른 검사 규칙에 의해 강제되거나, 기록된 검사를 통해 불필요함이 입증되어야 합니다. 줄 수나 토큰 수의 차이는 보고 대상일 뿐 변경 사유가 될 수 없습니다.
- **최소 2곳 이상의 실제 호출처:** 공용 모듈로 로직을 통합하기 전에는 반드시 둘 이상의 실제 호출처가 존재해야 합니다.
- **도달 가능성(Reachability):** 정적 참조와 동적 도달 경로(진입점, 레지스트리, 설정, 문자열 디스패치)를 추적하고, 각 검색 내역과 결과를 함께 기록합니다. 특성화 테스트(characterization test)는 통합 대상 호출자 중 테스트가 누락된 경우에만 보강합니다.
- **지침(Guidance) 문서의 경우:** 제거된 텍스트에 포함되어 있던 각 제약 조건이 남아 있는 다른 문서의 어느 위치로 이전되었는지 매핑한 내역을 제시해야 합니다.
- **배치 위치:** 선언된 계층 구조상 가장 낮은 공통 소유자 모듈에 배치해야 합니다. 새로운 크로스 패키지 모듈이나 기반 모듈을 신설할지는 결정 라운드에서 사용자가 직접 판단합니다.

## 문제가 생겼을 때

- **검토 영역이나 루트 디렉터리가 지정되지 않은 경우:** 에이전트가 먼저 확인을 요청하며, 범위가 기록될 때까지 조사를 시작하지 않습니다.
- **호스트 환경에 서브에이전트가 없는 경우:** 에이전트가 검토 및 이후의 diff 리뷰를 직접 수행하며, diff 리뷰는 셀프 리뷰로 기록됩니다.
- **서브에이전트의 주장이 맞지 않는 경우:** 예컨대 레지스트리에서 여전히 참조 중인 함수를 '미사용'으로 잘못 보고한 경우입니다. 해당 주장은 기각되거나 범위 공백으로 기록되며 결정 라운드에 상정되지 않습니다.
- **발견 사항이 선택하지 않은 영역에 속한 경우:** 후속 작업으로 분류하여 보류합니다. 해당 영역을 나중에 추가하면 별도의 배치, 루트, 결정 라운드가 구성되어 보고서에 기록됩니다.
- **사용자 응답이 없거나 외부 러너가 실행을 시작한 경우:** 실행은 결정 라운드에서 `stopped at decision round` 상태로 중단되며, 아무것도 적용되지 않고 보고서만 갱신됩니다.
- **명령, 옵션 또는 공개 인터페이스의 제거를 승인한 경우:** 이는 명세 계약 변경에 해당합니다. 리팩터링 작업 단위와 분리하여, 계약 명세 및 문서 갱신을 포함하는 표준 개발 워크플로의 별도 작업 단위로 처리됩니다. 단, 공표된 호환성 정책상 외부 소비자가 없다고 명시된 호환 경로의 경우, 더 이상 지원하지 않는 입력을 명시한 채 현재 배치 내에서 정리할 수 있습니다.
- **서브에이전트의 수정이 지정된 범위를 벗어나거나 합의된 변경과 다른 경우:** 에이전트는 다른 범위를 건드리지 않고 해당 코드 덩어리(hunk)를 되돌린 후, 수정을 다시 수행하거나 결정 라운드로 되돌립니다.
- **접수 이후 `HEAD`나 관련 파일 경로가 변경된 경우:** 증거를 다시 검증하며, 변경 의도에 영향을 주는 항목은 결정 라운드로 되돌려 재확인합니다.
- **설치 기록(receipt)이 소유한 관리 파일(`.devkit/managed/`, 에이전트 프로젝션)이 관련된 경우:** 이러한 파일은 직접 수정할 수 없으며, 원본 번들 수정, 업스트림 후속 작업 또는 `devkit override`를 통해 변경해야 합니다.
- **모의 연습(seeded exercise)인 경우:** 결정 사항은 모의(`simulated`)로 표시되며 테스트 픽스처만 변경됩니다.

## 최종 결과

적용된 모든 변경 사항이 사전에 합의되고, 증거와 함께 단독으로 커밋되며, 독립된 검토 및 승인을 거쳐 통합된 간결한 아키텍처를 확보하게 됩니다. 보고서는 발견 사항과 실제 변경 내역을 명확히 구분하여 검토 범위, 공백, 후속 작업을 투명하게 제공합니다. 플레이북을 호출하는 것만으로는 아무것도 임의로 바뀌지 않고, 계약 변경을 일반 리팩터링으로 가장하지 않으며, 단일 배치의 결과를 저장소 전체를 검토한 것처럼 과장하지 않습니다.
