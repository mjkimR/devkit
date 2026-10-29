---
sources:
  CAP-DLV-weekly-report: null
  UC-inspect-weekly-repository-progress: null
  UC-publish-a-weekly-report: null
title: 주간 저장소 진행 상황 점검하기
translated_from: en/journeys/inspect-weekly-repository-progress.md@8e63b9a5de337b57
---

# 주간 저장소 진행 상황 점검하기

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

한 주를 마무리하는 시점에는 지난 한 주 동안 실제로 무엇이 배포·전달되었는지, 무엇이 아직 검증되지 않은 상태인지,
저장소의 건전성(health)에 어떤 취약점이 있으며 다음 주에 어떤 작업을 우선해야 하는지 명확히 파악할 필요가 있습니다.
`weekly-report` 플레이북은 에이전트가 저장소 내부의 객관적 증거 데이터만을 바탕으로 이러한 주간 보고서를 체계적으로
작성하도록 안내합니다. 이 플레이북은 순수 읽기 전용으로 동작합니다. 원격 저장소에서 fetch하지 않고, 브랜치를 변경하지 않으며,
유지보수 작업이나 테스트를 직접 실행하지 않고, 후속 작업을 임의로 생성하지 않습니다. 완성된 보고서를 외부에 공식 게시하는
작업은 별도의 권한과 승인이 필요한 독립된 단계로 분리되어 있습니다.

유스케이스는
[`UC-inspect-weekly-repository-progress`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-inspect-weekly-repository-progress.md) (영어 원문)이며,
[`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-weekly-report.md) (영어 원문)를
바탕으로 합니다. 플레이북의 기본 개념은 [개념](../concepts.md)에서 설명합니다.

## 시작하기 전에

이 플레이북은 `devkit-catalog`의 옵트인(opt-in) `maintenance` 번들에 포함되어 제공되며, 사용하려면 프로젝트 설정에서 해당 번들을
활성화해야 합니다. 보고서 생성 단계 자체는 외부 목적지를 필요로 하지 않습니다.

## 1. 플레이북 실행 호출

`devkit-playbook` 스킬을 통해 에이전트에게 주간 보고서 작성을 요청하거나, `spec` 스킬이 제안하는 옵션을 승인하십시오.
에이전트는 다음 명령어로 플레이북 명세를 가져옵니다.

```bash
uv run devkit playbook get maintenance/weekly-report
```

점검할 범위를 지정하십시오. 필요에 따라 기준 시간대(timezone), 정확한 점검 기간, 보고서를 저장할 파일 경로, 비교 대상으로 삼을
이전 보고서 경로를 함께 전달할 수 있습니다.

## 2. 점검 대상 메타데이터 확정

에이전트는 순수 로컬 Git 정보만을 바탕으로 저장소 식별자, 점검 대상 커밋 리비전과 통합 기준 리비전, 생성 타임스탬프, 그리고 현재
체크아웃 트리에 미커밋 변경 사항(`dirty`)이 있는지 여부를 메타데이터로 정확히 기록합니다. 기본 점검 기간은 사용자 시간대 기준으로
직전 완결된 1주일(월요일 시작부터 다음 주 월요일까지, 시작 시점 포함·종료 시점 제외)이며, 각 시점의 UTC 오프셋을 함께 기록합니다.

## 3. 객관적 증거 수집

에이전트는 캡처된 기준 리비전의 커밋된 콘텐츠를 조회합니다. 완료된 스펙 번들을 포함하여 지정된 모든 네임스페이스와 목록의 각 페이지를
빠짐없이 검토합니다. 보고서에 기술되는 모든 사실 관계와 성과 주장은 객관적 증거를 반드시 인용합니다 (구체적인 커밋 해시와 파일 경로,
표준 문서 ID, 워크플로 엔벨로프, 또는 검증 결과 아티팩트 등).

## 4. 전달 완료 성과와 미검증 항목 분리

어떠한 작업 항목도 완료(completion), 검증(verification), 도달 가능성(reachability)이라는 3대 증거가 모두 입증될 때에만 '전달 완료'로
집계됩니다. 예를 들어 완료된 스펙으로 인정받으려면 완료 상태 선언, 체크 완료된 태스크 목록, 검증 및 Living Spec 반영(reconcile)
증빙 엔벨로프, 그리고 기준 통합 리비전에서 도달 가능한 Git 커밋 이력이 모두 확인되어야 합니다. 제안 문서의 존재나 단순 체크박스 표시,
또는 미검증 커밋만으로는 완료를 증명할 수 없으며, 이러한 작업은 엄격히 '미검증(unverified)' 항목으로 분류되어 보고됩니다.

## 5. 건전성 점검, 이전 보고서 비교 및 후속 조치

에이전트는 저장소 건전성(health)을 나타내는 소스 목록을 취합하고, 사용자가 지정한 이전 주간 보고서와 지표 변화를 대조 분석하며,
권장되는 후속 조치들을 영향도와 시급성에 따라 우선순위화합니다. 이때 이미 열려 있는 기존 후속 작업 링크를 참조할 뿐, 보고서 작성
과정에서 임의로 신규 작업을 생성하지는 않습니다.

## 6. 파일 작성 직전 재확인

보고서 파일을 디스크에 작성하기 직전, 에이전트는 점검 대상 리비전, 통합 ref, 작업 트리의 관련 미커밋 변경 사항을 다시 한번 점검합니다.
그 사이 변경된 내용이 감지되면 데이터를 재수집하거나 미검증 항목으로 명시하며, 확인되지 않은 변경 사항을 기 검증된 성과와 묵인하고
혼합하지 않습니다.

## 7. 보고서 수령

에이전트는 완성된 보고서를 새로운 로컬 파일로 저장한 뒤, 이를 다시 읽어 들여 문서 식별자와 증거 링크의 유효성을 검증하고 파일의 SHA-256
해시를 기록합니다. 동반 생성되는 결과 레코드에는 보고서 생성 결과와 함께 게시 상태가 `pending`으로 기록됩니다. 사용자는 최종 보고서
아티팩트 파일과 함께 생성 결과, 한계 사항(limitations), 그리고 권장되는 다음 단계 조치를 요약 브리핑으로 전달받습니다.

## 문제 해결

| 상황 | 일어나는 일 |
| --- | --- |
| 기준 시간대를 확인할 수 없는 경우 | 에이전트가 기간을 확정하거나 파일을 작성하기 전에 사용자에게 시간대를 먼저 질문합니다. |
| 지정된 기간의 시작·종료가 역전되었거나, 모호하거나, 산정할 수 없거나, 저장소 식별 정보가 누락된 경우 | 생성이 실패하며 보고서 파일은 생성되지 않습니다. |
| 담당 유닛의 자료(materials) 디렉터리나 저장소 공용 자료 위치가 지정되지 않은 경우 | 에이전트가 저장 위치를 사용자에게 먼저 질문합니다. 기본 브랜치에 추적 대상 보고서 파일을 임의로 생성하지 않습니다. |
| 검증 소스가 누락되었거나, 오래되었거나, 수집에 실패했거나, 비교가 불가능한 경우 | 해당 사유와 함께 보고서의 한계 사항(limitations) 섹션에 명시됩니다. 선택적 소스의 수집 실패가 전체 보고서 생성을 중단시키지는 않으며, 누락된 항목을 정상(clean)으로 간주하지 않습니다. |
| 작업에 공식 통합 타임스탬프나 검증 증빙이 누락된 경우 | 도달 가능한 커밋 변경 사항이더라도 해당 주의 '전달 완료' 성과가 아닌 단순 '스냅샷 증거'로만 분류되어 보고됩니다. |
| 비교할 이전 보고서가 없거나 점검 범위가 서로 다른 경우 | 보고서에 비교 대조를 수행하지 않았음을 명시합니다. 이전 보고서에 있던 지적 사항이 단순히 이번 결과에서 누락되었다고 해서 해결된 것으로 해석하지 않습니다. |
| 동일한 저장소, 점검 범위, 기간에 대한 보고서가 이미 존재하는 경우 | 고유 ID를 가진 새로운 실행이 이전 실행을 대체(supersede)함을 명시하며, 기존 보고서 파일은 덮어쓰지 않고 온전히 보존됩니다. |
| 작성 후 재확인(readback)이나 식별자 검증이 실패한 경우 | 보고서 생성이 실패 처리되며 아무것도 게시되지 않습니다. 단, 증거 링크 중 일부에 일시적으로 접근할 수 없는 경우라면 생성을 중단하는 대신 해당 항목을 '미검증'으로 분류하여 보고합니다. |

## 다음 단계

검증된 보고서를 사용자가 선택한 외부 대상에 공식 게시하는 절차는
[`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-publish-a-weekly-report.md) (영어 원문)이며,
[주간 보고서 게시하기](publish-a-weekly-report.md)에서 다룹니다. 관련 영역: [전달](../areas/delivery.md) 및
[거버넌스 규칙](../areas/governance.md).
