---
sources:
  CAP-DLV-weekly-report: null
  UC-inspect-weekly-repository-progress: null
  UC-publish-a-weekly-report: null
title: 주간 저장소 진행 상황 점검하기
translated_from: en/journeys/inspect-weekly-repository-progress.md@fd4a0a7c98ad16bb
---

# 주간 저장소 진행 상황 점검하기

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
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

한 주가 끝나면 실제로 무엇이 전달되었는지, 무엇이 아직 검증되지 않았는지, 저장소 건강 상태에 어떤 빈틈이 있는지,
다음에 무엇을 할지 알고 싶어집니다. `weekly-report` 플레이북은 저장소에 이미 있는 증거로 에이전트가 그 보고서를
쓰게 합니다. 이 플레이북은 읽기만 합니다. 아무것도 fetch하지 않고, 브랜치를 바꾸지 않으며, 유지 보수나 검사를
실행하지 않고, 후속 작업을 만들지 않습니다. 완성된 보고서의 게시는 별도의 권한을 갖는 별도 단계입니다.

유스케이스는
[`UC-inspect-weekly-repository-progress`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-inspect-weekly-repository-progress.md) (영어 원문)이며,
[`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md)를
바탕으로 합니다. 플레이북은 [개념](../concepts.md)에서 설명합니다.

## 시작하기 전에

이 플레이북은 devkit-catalog의 선택형 `maintenance` 번들에 들어 있으며, 배포되려면 프로젝트가 그 번들을 선택해야
합니다. 생성에는 외부 대상이 필요하지 않습니다.

## 1. 플레이북 호출

`devkit-playbook`을 통해 에이전트에게 주간 보고서를 요청하거나, `spec` 스킬이 내놓는 제안을 확인하십시오.
에이전트는 다음 명령으로 플레이북을 가져옵니다.

```bash
uv run devkit playbook get maintenance/weekly-report
```

범위를 알려 주십시오. 시간대나 정확한 기간, 보고서를 쓸 위치, 비교할 이전 보고서도 함께 줄 수 있습니다.

## 2. 점검 대상 고정

에이전트는 로컬 Git만으로 저장소 식별 정보, 점검 리비전과 통합 리비전, 생성 시각, 체크아웃의 변경 여부를
기록합니다. 기본 기간은 여러분의 시간대 기준으로 직전의 완결된 월요일부터 월요일까지의 한 주이며, 시작은 포함하고
끝은 제외하고, 각 끝점의 UTC 오프셋을 함께 둡니다.

## 3. 증거 수집

에이전트는 포착한 리비전에서 커밋된 내용을 읽습니다. 완료된 스펙도 포함하고, 의도한 모든 네임스페이스와 각 목록의
모든 페이지를 읽습니다. 사실에 관한 주장은 모두 증거를 인용합니다. 커밋과 경로, 문서 ID, 엔벨로프(envelope), 또는
검사 아티팩트입니다.

## 4. 전달된 것과 검증되지 않은 것 구분

작업은 완료, 검증, 도달 가능성의 증거가 있을 때만 전달된 것으로 셉니다. 완료된 스펙에는 상태, 체크된 태스크, 검증과
reconcile 증거, 그리고 통합 리비전에서 도달 가능한 커밋이 필요합니다. 제안, 체크박스, 커밋만으로는 아무것도
증명되지 않으며, 그런 작업은 검증되지 않은 것으로 보고됩니다.

## 5. 건강 상태, 비교, 조치

에이전트는 건강 상태 출처의 목록을 만들고, 여러분이 지정한 이전 보고서와 결과를 비교하며, 다음 조치를 영향도와
긴급도에 따라 순위를 매깁니다. 기존의 열린 후속 작업은 링크하되 새로 만들지는 않습니다.

## 6. 쓰기 직전 재확인

쓰기 직전에 에이전트는 점검 리비전, 통합 ref, 관련된 미커밋 내용을 다시 확인합니다. 바뀐 것은 다시 수집하거나
검증되지 않은 것으로 표시하며, 조용히 섞지 않습니다.

## 7. 보고서 수령

에이전트는 보고서를 새 로컬 파일에 쓰고, 다시 읽어 식별 정보와 증거 링크를 검증하며, SHA-256을 기록합니다. 함께
남기는 기록에는 생성 결과와 `pending` 상태의 게시 결과가 담깁니다. 여러분은 아티팩트, 두 결과, 한계, 다음 단계를
받습니다.

## 문제가 생겼을 때

| 상황 | 일어나는 일 |
| --- | --- |
| 시간대를 알 수 없음 | 에이전트가 기간을 정하거나 무언가를 쓰기 전에 묻습니다. |
| 기간이 뒤집혔거나, 모호하거나, 정해지지 않았거나, 저장소 식별 정보가 없음 | 생성이 실패하고 보고서는 쓰이지 않습니다. |
| 소유 유닛의 자료 위치도, 저장소 자료 위치도 없음 | 에이전트가 어디에 쓸지 묻습니다. 기본 브랜치에 추적되는 보고서를 조용히 만들지 않습니다. |
| 출처가 없거나, 오래되었거나, 실패했거나, 비교할 수 없음 | 이유와 함께 한계로 표시됩니다. 선택 출처의 실패는 생성을 멈추지 않으며, 빠진 것을 문제없음으로 세지 않습니다. |
| 작업에 통합 시각이나 검증 증거가 없음 | 도달 가능한 변경은 그 주의 전달이 아니라 스냅샷 증거로 보고됩니다. |
| 이전 보고서가 없거나 범위가 다름 | 보고서에 비교하지 않았다고 표시합니다. 사라진 결과를 해결된 것으로 읽지 않습니다. |
| 같은 저장소, 범위, 기간의 보고서가 이미 있음 | 자체 ID를 가진 새 실행이 대체하는 실행을 명시하며, 이전 파일은 바뀌지 않습니다. |
| 다시 읽기나 식별 정보 검사가 실패함 | 생성이 실패하고 아무것도 게시되지 않습니다. 증거 링크를 사용할 수 없는 경우만이라면 대신 검증되지 않은 것으로 표시됩니다. |

## 다음 단계

검증된 보고서를 여러분이 고른 대상에 게시하는 것은
[`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-publish-a-weekly-report.md) (영어 원문)이며,
[주간 보고서 게시하기](publish-a-weekly-report.md)에서 다룹니다. 영역: [Delivery](../areas/delivery.md),
[Governance](../areas/governance.md).
