---
sources:
  CAP-DIST-context-and-playbooks: null
  CAP-DLV-drift-reconciliation: null
  UC-reconcile-living-spec-drift: null
title: Living Spec 드리프트 조정하기
translated_from: en/journeys/reconcile-living-spec-drift.md@9f9b8733af4fcb1c
---

# Living Spec 드리프트 조정하기

<!-- handbook:provenance -->
> 소스 커밋 `b44f759024a5` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
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

구조 검사는 모든 참조가 해석되고 모든 진입점(entrypoint)이 존재한다는 것까지만 알려 줍니다. capability가 여전히
코드가 하는 일을 설명하는지는 알려 주지 못합니다. 이런 의미상의 드리프트(drift)가 의심될 때 `drift-reconciliation`
플레이북(playbook)을 실행합니다. 에이전트는 한정된 묶음(batch)의 계약을 구현과 소비자 안내에 비추어 검토하고, 각
불일치를 증거와 함께 보여 준 뒤, 여러분이 결정한 것만 바꿉니다.

구조적 일관성은 별도의 여정인 [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)에서 다룹니다.
전달 과정에서 기능별로 이루어지는 반영(reconcile)은 `spec-sync`가 담당하며, 이 플레이북은 기능과 기능 사이에
쌓이는 차이를 잡아냅니다. Living Spec과 플레이북은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-reconcile-living-spec-drift`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-reconcile-living-spec-drift.md) (영어 원문),
계약 [`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md).

## 시작하기 전에

- 선택형 `maintenance` 카탈로그 번들이 선택되어(`uv run devkit add maintenance`, 또는 이 플레이북과
  review-refactor를 함께 쓰려면 `maintenance:upkeep`) 동기화되어 있습니다.
- 무엇을 검토받고 싶은지 대략 정해 둡니다. 몇 개의 계약 ID나 하나의 영역, 그리고 에이전트가 읽어도 되는 구현과
  안내의 루트 경로입니다.

## 단계별 진행

1. **플레이북을 호출합니다.** `/devkit-playbook`을 실행해 `drift-reconciliation`을 고르거나, "Living Spec을 코드와
   맞춰 줘" 같은 요청에 `spec` 스킬이 한 줄로 제안할 때 확인합니다. 플레이북은 평범한 문구만으로는 실행되지 않으며,
   여러분의 확인이 명시적 호출이 됩니다
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문),
   [배포 영역](../areas/distribution.md)).
2. **접수.** 에이전트는 저장소, `HEAD`와 변경된(dirty) 경로, 선택한 계약 또는 영역, 허용된 루트, 이전 보고서, 보고서를
   둘 위치를 기록합니다. 그런 다음 한정된 묶음 하나의 후보를 나열합니다.
3. **비교.** 계약마다 문서에 적힌 명령, 옵션, 인터페이스, 용어, 동작, 경로를 기록된 리비전의 코드, 테스트, 안내와
   비교합니다. 확인된 불일치는 각각 하나의 발견 사항(finding)이 되며, 양쪽의 인용, 기대 동작과 관찰된 동작, 증거,
   `deterministic` 또는 `semantic-assessment` 분류, 제안 처리 방안을 담습니다.
4. **한 번의 결정 라운드.** 에이전트는 모든 발견 사항을 한꺼번에 보여 줍니다. 각 항목마다 문서나 안내 갱신, 코드
   수정, 보류(defer), 면제(waive) 중 하나를 고릅니다. 결정과 그 이유는 발견 사항별로 기록됩니다.
5. **수정.** 에이전트는 여러분이 결정한 것만, 일반 개발 워크플로(workflow)를 통해 그 쓰기 범위 안에서 적용합니다
   ([개발 요청 라우팅하기](route-development-intent.md) 참고).
6. **검증.** 코드 수정에는 회귀 증거가 필요하고, 문서 수정은 문제가 된 주장, 참조, 해당 검사에 비추어 다시
   확인합니다.
7. **보고.** `HEAD`와 변경된 경로를 다시 확인한 뒤, 에이전트는 묶음 보고서를 완성합니다. 범위, 발견 사항, 결정, 수정,
   건수(감지, 해결, 보류, 면제, 대기), 검증, 후속 작업이 담깁니다. 대기 중인 결정이 없으면 그 묶음은 조정된
   것입니다.

보고서는 해당 유닛(Unit)의 `materials/` 아래, 또는 저장소의 기존 자료 위치에 일반 Markdown으로 저장됩니다.

## 문제가 생겼을 때

- **범위가 주어지지 않았습니다.** 에이전트는 넓게 살펴보기 전에 계약, 영역, 허용 루트를 묻습니다.
- **영역이 너무 큽니다.** 명시적인 묶음으로 나누고, 어떤 후보를 검토했고 어떤 후보를 제외했는지 기록합니다. 완료는
  그 묶음에만 해당합니다.
- **도구, 문서, 진입점 또는 검사가 없습니다.** 이는 이유가 붙은 범위 공백(coverage gap)이며, 발견 사항도 아니고
  "일관됨"도 아닙니다. 에이전트는 묻지 않고 아무것도 설치하지 않습니다. 증거 없는 의심은 조사 공백입니다.
- **차이가 없습니다.** 보고서는 여전히 무엇을 검토했고 어떤 공백이 있는지 밝힙니다. 발견 사항이 0건이라는 결론에도
  범위에 대한 증거가 필요합니다.
- **보류하거나 면제합니다.** 보류에는 목적지(에이전트가 먼저 찾은 열린 피드백 파일이나 제안, 또는 여러분이 승인한
  것)와 재개 조건이 붙고, 면제에는 의도된 공백과 그 근거가 기록됩니다.
- **답하지 않은 발견 사항이 있습니다.** 대기 상태로 남고 수정되지 않으며, 그 묶음은 완전히 조정되었다고 주장되지
  않습니다.
- **이전 보고서가 그 묶음을 다룹니다.** 발견 사항이 이전 보고서의 키에 연결되고, 이전의 보류와 면제를 다시
  확인합니다.
- **`HEAD`나 관련된 변경 경로가 바뀌었습니다.** 에이전트는 증거를 다시 검증하고, 수정의 의도가 바뀌면 다시
  묻습니다.
- **수정이 범위 밖이거나 구조 정리입니다.** 별도의 작업으로 추적됩니다.
- **준비된 연습(seeded exercise)입니다.** 결정은 모의(simulated)로 표시되고 실제 소스는 바뀌지 않습니다.

## 결과

감사할 수 있는 보고서를 얻습니다. 모든 발견 사항에 증거와 여러분의 결정이 있고, 적용된 수정에는 검증이 붙어 있으며,
공백은 명시되어 있습니다. 보고서는 그 자체로 아무것도 승인하지 않고, 검사 통과가 의미상의 일관성으로 제시되지
않으며, 하나의 묶음이 저장소 전체로 제시되지도 않습니다.
