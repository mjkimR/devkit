---
sources:
  CAP-DIST-content-packages: null
  CAP-DIST-context-and-playbooks: null
  CAP-DLV-performance-pass: null
  UC-speed-up-selected-slow-operations: null
title: 선택한 느린 작업 빠르게 하기
translated_from: en/journeys/speed-up-selected-slow-operations.md@6f240ccd54bce0e2
---

# 선택한 느린 작업 빠르게 하기

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

명령이 느리게 느껴질 때 원인을 짐작하고 한 번만 시간을 재면, 다음 시도에서 사라지는 절감 효과를 보고하기 쉽습니다. `performance-pass` 플레이북은 이 작업을 측정 가능하게 만듭니다. 사용자가 작업을 고르면, 에이전트가 프로파일러 없이 교차(interleaved) 반복으로 측정하고, 프로파일러는 시간이 어디에 쓰이는지 찾는 데만 쓰며, 사용자가 동의한 속도 개선만 적용합니다. 각 개선은 전후 수치와 동작이 바뀌지 않았다는 증거와 함께 커밋됩니다.

출처: [`UC-speed-up-selected-slow-operations`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-speed-up-selected-slow-operations.md) (영어 원문),
계약 [`CAP-DLV-performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-performance-pass.md) (영어 원문),
플레이북 [`performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/performance-pass/SKILL.md) (영어 원문).
유지보수 비용은 별개의 일입니다: [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)이며, 이 플레이북은 그 적용 절차를 재사용합니다.

## 시작하기 전에

- 선택형 `maintenance` 카탈로그 번들을 `all`(`uv run devkit add maintenance`) 또는 `maintenance:performance`로 선택합니다. 둘 다 이 플레이북이 필요로 하는 `review-refactor`도 배포합니다
  ([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)).
- 중요한 작업을 정해 둡니다: 정확한 명령, 작업 디렉터리와 환경, 지표(실행 시간, 서브프로세스 수, 최대 메모리). 목표는 선택 사항입니다.
- 측정하는 동안 기계를 조용히 둡니다. 플레이북에는 타이밍 스크립트가 없으며, 에이전트는 `hyperfine` 같은 설치된 도구를 쓰거나 짧은 루프를 작성합니다.

## 단계별 진행

1. **호출.** `/devkit-playbook`을 실행해 `performance-pass`를 고르거나, `uv run devkit playbook get maintenance/performance-pass`로 가져오거나, `/spec`이 제안할 때 확인합니다. 필요할 때 로드되며, 설치되어 있다는 이유로 실행되지 않습니다
   ([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).
2. **작업 접수(Intake).** 에이전트가 실행 ID, 저장소, `HEAD`, 수정 경로, 이전 보고서, 보고서 위치, 환경(기계, 운영체제, 런타임 버전, 현재 부하)을 기록합니다. 사용자가 각 대상을 지정합니다. 실행은 `survey` 모드(찾아서 순위만 매기고 적용하지 않음) 또는 `targeted` 모드(측정하고 승인된 것을 적용)입니다.
3. **기준선.** 각 대상을 정확한 인자로 실제 프로세스로 측정합니다: 워밍업 실행 한 번은 버리고, 최소 다섯 번의 교차 반복, 종료 코드와 출력 다이제스트 확인, 중앙값·최솟값·범위 보고, warm/cold 상태 표시, 측정 전후 부하 기록.
4. **비용 귀속.** 프로파일러는 비용 위치를 찾을 뿐 절감을 보고하지 않습니다. 각 핫스폿의 비중은 프로파일러 없이 확인하고, 서브프로세스는 따로 세고 측정하며, 복합 대상은 구성 요소를 측정해 합이 전체와 맞는지 확인합니다.
5. **후보.** 각 후보는 위치, 비용의 원리, 측정된 비중, 제안 변경, 예상 절감, 위험, 분류, 계획된 비교 입력, 경로, 수정 경로를 기록합니다. 예상 절감이 노이즈 하한보다 작으면 제외하고 집계합니다. 반복 작업 제거(여러 번 대신 한 번의 스캔, 한 실행 안의 메모, 더 적은 프로세스)가 단일 호출 미세 조정보다 우선입니다. 그다음 에이전트는 `review-refactor`를 정확한 ID로 가져와 그 적용·증거 섹션을 참고 텍스트로 읽으며, 그 플레이북을 시작하지는 않습니다.
6. **일괄 결정 라운드.** 모든 후보를 경로와 수정 경로와 함께 보고 고릅니다: 동작을 보존한 채 적용, 계약 변경으로 처리, 보류(대상과 재개 조건 포함), 유지(사유 포함). `survey` 실행에서 하나라도 승인하면 `targeted`가 됩니다. 이 승인은 작업 단위의 의도이며, 통합 승인이 아닙니다.
7. **적용.** 합의된 변경은 모듈 수와 상관없이 저장소의 기능 워크플로를 자체 깊이로 따르는 작업 단위 하나가 됩니다(overall-refactor 경로는 쓰지 않음). `review-refactor`의 브랜치, 수정, 커밋, 리뷰, 보고 섹션을 따릅니다. 각 변경은 이전 체크포인트에서 이전 코드와 새 코드를 측정해 커밋 본문에 수치를 남기며, 저장소 코퍼스와 오류 사례(읽을 수 없는 항목, 심볼릭 링크 루프, 철자가 다른 경로, 사라진 작업 디렉터리)에 대한 차등 비교를 함께 기록합니다. 이전 코드는 추출한 사본이나 별도 워크트리에서 실행하며, 작업 체크아웃을 스태시하거나 전환하지 않습니다. 수정 작업이나 검증이 실행 중일 때는 시간을 재지 않습니다.
8. **리뷰와 최종 측정.** 각 변경의 분류, 동일 동작 주장, 교체된 API의 오류 경로, 캐시나 메모 키를 브리프로 받은 새로운 리뷰어가 이를 깨는 입력을 찾습니다. 그런 다음 모든 대상을 한 세션에서 접수 시점 리비전과 교차 측정합니다.
9. **보고서.** 실행 보고서에 접수 정보, 모드, 기준선, 검토 범위, 후보와 변경, 결정, 후속 작업, 최종 측정, 결과(`stopped at decision round`, `applied`, `partially applied`)와 통합 상태를 기록하며, 작업 단위가 통합되거나 멈추면 갱신합니다.

## 동작 보존의 기준

stdout, stderr, 종료 코드, 쓰인 파일과 그 바이트, 저장 형식, 오류 동작, 관찰 가능한 부수 효과의 순서가 받아들이는 모든 입력에 대해 같을 때만 동작을 보존하는 변경입니다. 비공개 캐시 형식은 버전이나 지문이 이전 항목을 무효화하고 캐시를 끈 상태, cold, warm에서 출력이 같으면 해당되며, 한 실행 안의 메모는 키가 답을 바꾸는 모든 입력을 포함하고 실패를 메모하지 않으면 해당됩니다. 출력 변경, 실행 간에 유지되는 새 상태, 동시성, 기본값·정확도·오류 처리 변경, 옵션 제거는 계약 변경이며, 각각 일반 개발 워크플로의 별도 작업 단위가 됩니다.

## 문제가 생겼을 때

- **대상의 명령, 지표, 디렉터리가 빠진 경우:** 시간을 재기 전에 에이전트가 묻습니다.
- **기계가 바빴거나 실행 자체의 검증이 돌고 있었던 경우:** 측정을 버리고 나중에 다시 합니다.
- **이상치 하나가 결과를 좌우하는 경우:** 결론 전에 변형마다 다섯 번을 더 반복하며, 노이즈 하한보다 작은 중앙값 차이는 측정 가능한 변화 없음으로 보고합니다.
- **인용한 `review-refactor` 제목이 없는 경우:** 예컨대 오버라이드가 이름을 바꾼 경우입니다. 실행은 그 섹션을 밝힌 보고서와 함께 멈추고 아무것도 적용하지 않습니다.
- **아무도 답하지 않거나, 무인 실행이거나, `survey`가 아무것도 승인하지 않은 경우:** 결정 라운드에서 아무것도 적용하지 않고 멈춥니다.
- **호스트에 서브에이전트가 없는 경우:** 변경을 하나씩 차례로 적용하고, diff 리뷰는 기록된 셀프 리뷰로 합니다.
- **비교나 리뷰어가 차이를 찾은 경우:** 변경을 고치거나 계약 변경으로 결정 라운드에 되돌립니다. 이 작업 단위 안에 승인된 차이로 남기지 않습니다.
- **변경에 측정 가능한 이득이 없는 경우:** 서브프로세스 감소나 최대 메모리 감소처럼 다른 측정된 이유로 승인하지 않았다면 결정 라운드로 돌아갑니다.
- **접수 이후 `HEAD`나 관련 수정 경로가 바뀐 경우:** 먼저 기준선을 다시 측정하고 증거를 재검증합니다.

## 최종 결과

적용된 모든 변경은 합의되었고, 동작을 보존하며, 측정된 전후 수치와 차등 증거와 함께 단독으로 커밋되고, 각자의 승인으로 검토·통합됩니다. 보고된 모든 절감은 한 세션 안의 프로파일러 없는 교차 실행에서 나오며, 접수 시점 리비전과의 최종 비교로 끝납니다. 호출이나 측정만으로는 아무것도 바뀌지 않으며, `review-refactor` 자체의 접수와 결정 라운드는 시작되지 않습니다.
