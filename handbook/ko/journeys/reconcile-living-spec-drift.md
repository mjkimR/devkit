---
sources:
  CAP-DIST-context-and-playbooks: null
  CAP-DLV-drift-reconciliation: null
  UC-reconcile-living-spec-drift: null
title: Living Spec 드리프트 조정하기
translated_from: en/journeys/reconcile-living-spec-drift.md@ed93d8aee2229cd3
---

# Living Spec 드리프트 조정하기

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

구조 검사로는 모든 참조가 정상적으로 연결되고 모든 진입점이 존재하는지만 확인할 수 있습니다. 문서화된 capability 규격이 실제 코드의 동작과 여전히 일치하는지는 이러한 정적 검사만으로 파악하기 어렵습니다. 코드와 문서 사이의 의미적 드리프트(semantic drift)가 의심될 때 `drift-reconciliation` 플레이북을 실행합니다. 에이전트가 지정된 범위의 계약을 구현 코드 및 사용자 가이드와 대조 검토하여, 확인된 각 불일치를 명확한 증거와 함께 제시하고 사용자가 승인한 변경 사항만 적용합니다.

구조적 일관성 검사는 별도 여정인 [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)에서 다룹니다. 기능 단위 전달 과정 중 발생하는 규격 동기화는 `spec-sync`가 담당하지만, 이 플레이북은 여러 기능 개발 사이에 점진적으로 누적된 괴리를 포착합니다. Living Spec과 플레이북의 기본 개념은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-reconcile-living-spec-drift`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-reconcile-living-spec-drift.md) (영어 원문),
계약 [`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md).

## 시작하기 전에

- 선택형 `maintenance` 카탈로그 번들을 추가(`uv run devkit add maintenance`, 또는 이 플레이북과 review-refactor만 쓰려면 `maintenance:upkeep`)하고 동기화했습니다.
- 검토 대상의 대략적인 범위를 파악해 둡니다. 특정 계약 ID 목록이나 검토할 영역, 그리고 에이전트가 탐색할 수 있는 구현 코드 및 가이드의 루트 경로를 지정해야 합니다.

## 단계별 진행

1. **플레이북 호출.** `/devkit-playbook`을 실행하여 `drift-reconciliation`을 선택하거나, "Living Spec을 코드와 맞춰 줘"와 같은 요청 시 `spec` 스킬이 제안하는 한 줄 확인에 동의합니다. 플레이북은 일반적인 대화 문구만으로는 자동 실행되지 않으며, 사용자의 명시적인 확인을 거쳐야만 호출됩니다([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md), [배포 영역](../areas/distribution.md)).
2. **작업 접수.** 에이전트가 저장소 상태, `HEAD` 커밋 및 수정된(dirty) 경로, 선택한 계약 또는 영역, 탐색이 허용된 루트 경로, 기존 보고서 이력, 보고서 저장 위치를 기록합니다. 이후 지정된 범위(배치) 내의 검토 후보 목록을 도출합니다.
3. **대조 비교.** 각 계약에 문서화된 명령, 옵션, 인터페이스, 용어, 동작, 경로를 해당 리비전의 코드, 테스트, 가이드와 비교 대조합니다. 확인된 불일치 사항은 각각 하나의 발견 사항(finding)으로 정리되며, 양측의 인용 구문, 기대 동작과 관찰된 동작, 확인 증거, `deterministic` 또는 `semantic-assessment` 분류, 제안 처리 방안이 함께 기록됩니다.
4. **일괄 결정 라운드.** 에이전트가 도출된 모든 발견 사항을 한 번에 정리하여 보여 줍니다. 각 항목에 대해 문서/가이드 갱신, 코드 수정, 보류(defer), 면제(waive) 중 처리 방식을 선택합니다. 결정 사항과 그 사유는 발견 사항별로 기록됩니다.
5. **수정 반영.** 에이전트는 사용자가 결정한 항목에 한해서만 표준 개발 워크플로를 따르고 지정된 쓰기 범위 안에서 수정을 적용합니다([개발 요청 라우팅하기](route-development-intent.md) 참고).
6. **검증.** 코드 수정의 경우 회귀 방지 테스트 증거가 필요하며, 문서 수정은 지적된 설명 내용, 교차 참조, 관련 검사를 통해 다시 검증합니다.
7. **보고서 작성.** `HEAD`와 변경된 파일 경로를 재확인한 후 배치 보고서를 완성합니다. 검토 범위, 발견 사항, 결정 사항, 수정 내역, 통계(감지됨, 해결됨, 보류됨, 면제됨, 대기 중), 검증 결과, 후속 작업이 포함됩니다. 대기 중인 결정이 모두 해소되면 해당 배치의 드리프트 조정이 완료됩니다.

보고서는 해당 유닛의 `materials/` 디렉터리나 저장소의 기존 자료 저장 위치에 일반 Markdown 파일로 저장됩니다.

## 문제가 생겼을 때

- **검토 범위가 지정되지 않은 경우:** 에이전트는 대규모 탐색을 시작하기 전에 대상 계약, 영역, 허용 루트 경로를 먼저 확인합니다.
- **검토 대상 영역이 너무 큰 경우:** 대상을 명시적인 배치로 분할하고, 이번에 검토한 후보와 제외된 후보를 명확히 기록합니다. 작업 완료 판정은 해당 배치에만 적용됩니다.
- **도구, 문서, 진입점 또는 검사가 누락된 경우:** 이는 명확한 사유를 기재하는 범위 공백(coverage gap)으로 분류되며, 단순 불일치 발견 사항도 아니고 '일관됨'으로 간주되지도 않습니다. 에이전트는 사전 승인 없이 임의로 도구를 설치하지 않습니다. 구체적 증거가 없는 막연한 의심은 조사 공백(investigation gap)으로 처리합니다.
- **불일치가 발견되지 않은 경우:** 차이가 없더라도 무엇을 검토했고 어떤 공백이 있었는지를 보고서에 명시합니다. 발견 사항이 0건이라는 결론을 내리려면 충분한 검토 범위 증거가 제시되어야 합니다.
- **발견 사항을 보류하거나 면제하는 경우:** 보류(defer) 시에는 후속 처리를 위임할 대상(에이전트가 사전에 탐색한 미해결 피드백 파일, 제안서, 또는 사용자가 승인한 경로)과 재개 조건을 지정해야 합니다. 면제(waive) 시에는 의도적인 공백 사유와 타당한 근거를 기록합니다.
- **미응답 발견 사항이 남은 경우:** 해당 항목은 대기(pending) 상태로 남아 수정이 적용되지 않으며, 해당 배치가 완전히 조정되었다고 선언할 수 없습니다.
- **이전 보고서가 동일 배치를 다룬 적이 있는 경우:** 새로운 발견 사항을 이전 보고서의 키와 연결하고, 이전에 기록된 보류 및 면제 사항을 재점검합니다.
- **`HEAD` 또는 관련 변경 경로가 이동한 경우:** 에이전트가 대조 증거를 다시 검증하며, 기존 수정의 의도가 영향을 받는다면 사용자에게 재차 확인합니다.
- **수정 작업이 본래 범위를 벗어나거나 단순 구조 정리에 해당하는 경우:** 별도의 작업 유닛으로 분리하여 추적합니다.
- **모의 연습(seeded exercise)인 경우:** 결정 사항은 모의(`simulated`)로 표시되며 실제 소스 코드는 변경되지 않습니다.

## 최종 결과

언제든 감사(audit) 가능한 보고서를 확보할 수 있습니다. 모든 발견 사항에는 명확한 증거와 사용자의 결정이 기록되고, 적용된 수정 내역에는 검증 결과가 뒷받침되며, 확인된 공백 역시 투명하게 명시됩니다. 보고서 자체만으로는 어떠한 변경도 임의로 승인하지 않으며, 단순 테스트 통과를 의미론적 일관성으로 포장하지 않고, 단일 배치의 결과를 저장소 전체가 일치한다는 근거로 제시하지도 않습니다.
