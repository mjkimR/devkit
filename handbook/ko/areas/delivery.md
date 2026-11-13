---
sources:
  CAP-DLV-adaptive-assignments: null
  CAP-DLV-adaptive-development: null
  CAP-DLV-cli-and-output: null
  CAP-DLV-deep-research: null
  CAP-DLV-delivery-roles: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-design-exploration: null
  CAP-DLV-drift-reconciliation: null
  CAP-DLV-human-interaction: null
  CAP-DLV-maintenance-history: null
  CAP-DLV-performance-pass: null
  CAP-DLV-project-policy: null
  CAP-DLV-proposal-lifecycle: null
  CAP-DLV-proposal-planning: null
  CAP-DLV-release-handbook: null
  CAP-DLV-review-refactor: null
  CAP-DLV-sdd-baseline-adoption: null
  CAP-DLV-spec-bundles: null
  CAP-DLV-test-management: null
  CAP-DLV-uiux-improvement: null
  CAP-DLV-weekly-report: null
  CAP-DLV-workflow-definitions: null
  CAP-DLV-workflow-envelopes: null
  CAP-DLV-workflow-orchestration: null
  CAP-INT-mcp-services: null
  UC-drive-development-to-integration: null
  UC-handle-delivery-problems-and-exceptions: null
  UC-plan-and-hand-off-a-proposal: null
  UC-publish-a-weekly-report: null
  UC-reconcile-living-spec-drift: null
  UC-review-and-refactor-accumulated-slop: null
  UC-route-development-intent: null
title: 전달
translated_from: en/areas/delivery.md@5c059b36142e000d
---

# 전달

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](../journeys/adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](../journeys/advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](../journeys/assess-test-management.md)
- [필요한 명령 진입점 설계하기](../journeys/design-command-entrypoints.md)
- [아이디어 발굴하고 구체화하기](../journeys/discover-and-refine-an-idea.md)
- [개발에서 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [격리된 명령 실행하기](../journeys/execute-an-isolated-command.md)
- [설계 문제 탐색하기](../journeys/explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](../journeys/find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](../journeys/import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](../journeys/improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](../journeys/plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [결정 대체 관계 읽기](../journeys/read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](../journeys/record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](../journeys/snapshot-bundle-sources.md)
- [선택한 느린 작업 빠르게 하기](../journeys/speed-up-selected-slow-operations.md)
- [어드바이저리](advisory.md)
- [에이전트 우선 CLI 도구 키트](cli.md)
- [협업](collaboration.md)
- [컴팩트 명령 출력](compact.md)
- [배포](distribution.md)
- [문서](documents.md)
- [커밋 게이트](gate.md)
- [생성 파일](generated.md)
- [거버넌스 규칙](governance.md)
- [하네스](harness.md)
- [호스트](host.md)
- [통합](integration.md)
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

전달 절차를 고르기 전에 개발 방식(development approach)을 확인합니다.
프로젝트는 `.devkit/config.toml`의 `[development] approach = "sdd"`(기본값) 또는 `"adaptive-dev"`를 공유합니다.
`uv run devkit config show`가 적용 값과 출처를 보여 줍니다. 패키지 설치나 번들 선택으로 이 값은 바뀌지 않습니다.
용어는 [개념](../concepts.md)에서 설명합니다.

## SDD: 작업 분류하기

SDD는 작업을 `task-kind`(feature, bugfix, overall-refactor), `planning-depth`(session, spec, proposal),
작업 노력 수준(`activity-effort`: low, medium, high)으로 분류합니다. 깊이는 구현 전에 무엇을 정해야 하는지를 나타냅니다.

- **Session:** 방향이나 계약에 미해결 질문이 없습니다. 유닛(Unit), 엔벨로프, 조정 문서를 만들지 않습니다.
- **Spec:** 방향은 분명하고 코드 전에 계약을 작성합니다.
- **Proposal:** 방향 자체를 Planning에서 정하고 승인한 뒤 Development로 넘어갑니다.

bugfix는 합의된 계약을 어기는 결함을 재현하고 Red와 Green 근거를 남깁니다.
overall-refactor는 새 동작 없는 프로젝트 전반의 구조 변경이며 유닛을 만들지 않습니다. 국소 리팩터링은 feature 경로입니다.
medium은 최초 독립 코드 리뷰를, high는 횟수가 제한된 리뷰 반복을 요구합니다. low는 자체 리뷰가 가능합니다.
작업 노력 수준이 낮다고 해서 필수 검사나 승인을 생략하지는 않습니다.

`/spec`은 새 요청을 받을 때 작업과 범위가 맞는 플레이북을 한 번 검색합니다.
일치하는 후보는 편집 전에 제안하고 사용자가 확인해야 실행합니다. 같은 작업의 후속 응답과 명시된 진입점은 검색을 생략합니다.
주제만 같다는 이유로 플레이북을 선택하지 않습니다.

## 제안 계획하기

Backlog는 `sdd-proposal`에 연결된 `docs/proposals/PROP-<slug>/proposal.md`를 만들고 합의된 의도를 기록합니다.
`size: XL`은 여러 전달물·스펙이나 서로 다른 작업 종류를 포함하므로 Planning 전에 분해합니다.
초안 수정 전에 `uv run devkit spec proposal check <slug>`를 실행합니다. `plan-<slug>`가 있으면 해당 Planning이 소유합니다.

Planning은 `plan-<slug>`에서 제안서, 예비 결정(PADR), 근거와 `target-docs.md` 청사진을 다룹니다.
에이전트가 질문을 한 차례로 모으고 최종 커밋된 제안과 검토 브리핑을 제시합니다.
`uv run devkit spec proposal report <slug>`로 공유 산출물 게시 없이 브리핑을 읽을 수 있습니다.

유지되는 베이스 체크아웃에서 복합 수락(composed acceptance)을 실행하면 검토한 Planning 결과를 통합합니다.

```bash
uv run devkit spec proposal accept-plan <slug> --by user --mode accept_only
```

일반 `devkit spec proposal accept`에는 `--mode`와 `--effort` 플래그가 없습니다.

`accept_and_handoff`에는 handoff 권한과 `--effort`도 필요합니다. Planning 반영 후 검증 대기·handoff 미시작 상태로 반환합니다.
Host가 반영된 런타임을 동기화하고 검사한 뒤, 동일하게 승인된 범위와 작업 노력 수준으로 새 프로세스에서 handoff를 실행합니다.
이동한 베이스와 충돌이 없으면 Planning에 먼저 병합할 필요가 없습니다. 제안 범위가 바뀌었다면 재검토합니다.

```bash
uv run devkit spec proposal handoff <slug> --effort medium
```

복합 handoff는 `dev-<slug>`를 준비하고 검토한 베이스의 깨끗한 자식 커밋으로 트랜잭션을 한 번 커밋합니다.
제안을 스펙으로 바꾸고 PADR을 승격하며 자료·피드백을 보존하고 승인 기록과 참조를 옮깁니다.
커밋이 거부되면 그 워크트리에 쓰기를 staged 상태로 남깁니다. 원인을 고쳐 커밋하며 handoff를 재실행하지 않습니다.
방향이 정해진 적격 초안은 명시적 결정 후 베이스에서 직접 수락할 수 있습니다.
[제안 계획 후 넘기기](../journeys/plan-and-hand-off-a-proposal.md)를 참고하십시오.

## 스펙 개발하기

`uv run devkit spec new <slug>`는 `dev-<slug>`에서 `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` 번들을 만듭니다.
`spec.md`, `plan.md`, `tasks.md`를 제품 코드 전에 작성합니다. 결함에는 `--workflow sdd-spec-bugfix`를 씁니다.
`uv run devkit workflow next --unit <dir>`가 권위 있는 단계와 미충족 검사를 알려 주고,
`uv run devkit workflow show <id>`가 전체 정의를 보여 줍니다.

feature 경로는 명세, 구현·검증, 리뷰, Living Spec 반영, 피드백과 최종 보고를 거쳐 통합합니다.
bugfix 경로는 특성화와 Red·Green 근거를 추가합니다.
화면은 코드 전에 제안이나 스펙에 초안을 작성하고 선택적으로 `ux-reviewer`의 검토를 받습니다.
초안에서 이미 고친 항목을 포함한 UX 리뷰 지적은 `build-verify`에서 닫습니다. 이는 별도의 독립 리뷰 회차가 아니라 종결 기록입니다.
유지할 화면과 사용 사례 참조는 조정 단계에서 `docs/ux/`로 반영합니다.

`reconcile.md`는 변경을 `docs/`의 지속되는 계약과 연결합니다. 모든 작업 노력 수준에서 조정 검증을 기록합니다.
medium에서 독립 조정 리뷰를 자체 검사로 대신하려면 영향 계약과 diff의 일치가 분명하고 구성 요소 간 해석이 남지 않아야 합니다.
high는 독립 검증이 필요합니다. 최종 조정 검사는 전체 반영을 확인하고 앞선 검사를 식별하며, 각 지적을 해결됨 또는 사유가 있는
면제로 표시합니다. 필수 계약 불일치는 면제할 수 없습니다.

테스트 스위트 구성을 평가할 때는 [선택한 테스트 스위트 평가하기](../journeys/assess-test-management.md)에 따라
선택한 스위트를 점검하고, 확정된 변경만 기본 워크플로로 보냅니다.

## 결정과 기록

| 경계 | 결정 |
| --- | --- |
| `plan-accept` | 제안의 방향. |
| `proposal-handoff` | Development 시작과 설치·워크트리 효과. |
| `dev-integration` | 검증된 변경 반영과 한정된 정리. |

각 경계는 `ask` 또는 `auto`입니다. 위임은 사용자 동의가 아닌 정책으로 보고합니다.
`uv run devkit spec policy`가 승인, 단계 스위치와 Git·피드백 정책을 보여 줍니다.
합의 안의 구현 선택은 실행자가 정합니다. 목표·범위·제약 변경에는 사용자 결정이 필요합니다.

유닛 엔벨로프(envelope)는 기존 기록을 덮어쓰지 않고 리뷰, 재검증, 피드백, 최종 보고, 질문과 문제를 기록합니다.
미응답 질문이나 미해결 문제는 워크플로를 보류합니다. 실제로 문제를 해결한 행위자가 resolution을 기록합니다.
완전히 작성된 엔벨로프 하나만 미커밋이면
`uv run devkit workflow envelope commit --unit <dir> --file envelopes/<name>.yaml`로 일반 훅을 유지하며 커밋할 수 있습니다.
소스 변경과 다중 기록은 일반 결합 커밋을 씁니다.
세션 작업은 대화나 PR 본문에 보고하고 이런 기록을 만들지 않습니다.

## 오케스트레이션과 통합

direct에서는 Host가 작업합니다. local-orchestrated는 각 워크트리의 일회성 Planning·Development 워커를 사용합니다.
조정자는 분리할 수 있는 조사·구현·검증을 위임하고 통합과 최종 검증을 맡습니다. 하위 작업의 범위와 커밋 권한은 부모 작업 안으로
제한하며 고정된 중첩 깊이 제한은 없습니다. 동시 작성자는 별도 워크트리를 사용하거나 순서대로 작업합니다.
읽기 전용 지원 역할은 근거를 반환하고 워커는 자신의 작업 브랜치에만 커밋합니다.
재사용하는 `git-operator`는 현재 승인된 정확한 수명 주기 작업을 실행합니다.
일정, 의미적 선택과 결과 수용은 Host가 맡습니다. scout의 기본 모델 수준은 compact,
git-operator는 lean이며 지원되는 호스트에서 medium 추론 수준을 씁니다. 이 자원 수준은 전달 작업 노력 수준이나 권한을 바꾸지 않습니다.

범위 관찰은 현재 쓰기와 미래 Planning 범위를 구분합니다. 현재 겹침은 실행 중 작업을 직렬화하고,
미래 범위만 겹치면 Planning을 직렬화하지 않고 handoff·통합 순서를 정합니다. 부분 관찰로 독립성을 증명할 수는 없습니다.
`uv run devkit spec worker inspect`가 반환된 턴과 누적 규칙을 의도한 베이스와 대조합니다.

Host가 소스 런타임으로 내용을 검사한 뒤 명시적 브랜치 통합을 준비·실행합니다.
보호된 통합은 고정된 소스나 대상에서 도달 가능한 커밋 이력에 제안 경로가 있을 때만 제안 정리를 포함합니다.
승인된 정리 대상은 병합과 재시도 사이에 유지되며, 커밋되지 않은 디렉터리만으로는 정리 대상이 되지 않습니다.
반영 후 의존성과 자산을 동기화하고 오래된 추적 생성물을 재생성한 뒤 새 프로세스에서 최종 검사합니다.
확인된 Git 병합도 검사가 통과하기 전까지 `verification=pending`입니다.
[통합](integration.md)과 [개발에서 통합까지 진행하기](../journeys/drive-development-to-integration.md)를 참고하십시오.

<a id="adaptive-development"></a>

## 적응형 개발

`devkit-adaptive`(devkit-docs 필요)를 설치하고 `uv run devkit add adaptive-dev`를 선택합니다.
`/adaptive-dev`는 변경별 SDD 기록 없이 유용한 질문, 한정된 실험, 대표 흐름 구현과 실제 사용 검사를 진행합니다.
제품 작업 전에 공유 방식이 `adaptive-dev`인지 확인합니다. 선택적 역할은 product-clarifier, product-researcher, usage-reviewer입니다.
조정자가 `.devkit/adaptive-dev.md`에 목표, 선택과 가정, 검사, 미확인 사항과 다음 행동을 유지합니다.
제품은 이 방식을 계속 사용할 수 있습니다.

적응형 개발에서 작업을 위임할 때는 `devkit adaptive assignment new`로 위임 전에 목표·리터럴 쓰기 경로·커밋 권한·선언된 검사·기준
문서를 기록하며, `return`·`verify`·`close`는 공통 Git 원장에 증거를 남깁니다. 검증은 저장소 사실과 보고된 결과를 확인할 뿐
에이전트를 시작하거나 테스트를 실행하지 않으며, `list`는 관찰 사실을 보고하고 에이전트 생존 여부를 판단하지 않습니다.
외부 스킬이나 역할 계약을 프로젝트 소유 오버레이로 변환할 때는
[선택한 외부 에이전트 자산 가져오기](../journeys/import-third-party-agent-assets.md)를 참고하십시오.

이전 incubation 방식·번들·진입점은 허용되지 않으며 이전 컨텍스트 파일을 대신 읽지도 않습니다.
사용자가 요청하면 `spec/sdd-baseline`이 유지할 제품을 코드·현재 문서·실제 근거에 연결합니다.
준비 중에는 `adaptive-dev`를 유지하고, 준비 완료와 정확한 효과에 대한 사용자 결정 후 SDD를 활성화합니다.
과거 유닛이나 통합 제공자 편집은 필요 없습니다. [아이디어 발전시키기](../journeys/advance-an-idea.md)와
[적응형 개발에서 SDD 도입하기](../journeys/adopt-sdd-from-adaptive-development.md)를 참고하십시오.

## 선택형 카탈로그 진입점

- `deep-research`는 사용자가 호출하는 개발 방식 중립 조사를 하나의 `MAT-<slug>` 자료로 보존합니다.
  구현·커밋·게시 권한을 주지 않습니다.
- `design-explore`는 구조·모델·워크플로의 해결 기제를 탐색하고 저장 위치 요청이 없으면 대화로 방향을 제시합니다.
  구현 권한을 주지 않습니다.
- `app-uiux-improve`는 인터페이스·사용 흐름을 개선하며 요청한 구현을 작업에 대해 승인된 경로로 진행합니다.
  리뷰 전용 요청에는 편집 없이 발견 사항을 반환합니다.

고정된 역할 구성이나 점수 없이 필요한 스킬 내부 관점을 선택합니다.
선택만으로 작업을 시작하거나 개발 방식을 바꾸지 않습니다. 각각 사용자의 명시적 호출로만 실행합니다.

## 유지보수와 릴리스 준비

선택형 maintenance 번들은 드리프트 조정, 주간 보고, review-refactor와 성능 점검을 제공합니다.
호출·확인 후 실행하고 수정·게시·통합은 각각의 권한을 따릅니다.
주간 보고는 불변 보고서 바이트와 별도 로컬 게시 기록을 유지합니다.
review-refactor와 성능 작업은 이전·이후 동작을 비교하고 계약 변경을 별도 작업으로 다룹니다.

유지보수 이력(maintenance history)은 별도 선택하는 동반 작업입니다.
명령 설치나 플레이북 실행만으로 이력을 시작하거나 반복 제안하지 않습니다.
요청한 수집은 근거를 동결하고, 승인된 게시는 전용 이력 브랜치를 쓰며, 이후 통합 변경은 추가 기록으로 남깁니다.
[유지보수 실행 기록하기](../journeys/record-a-maintenance-run.md)와
[최신 유지보수 실행 찾기](../journeys/find-the-latest-maintenance-run.md)를 참고하십시오.

릴리스 핸드북은 Living Spec에서 파생되며 요청 시 `devkit-dev/handbook`으로 갱신합니다.
조정 대상이 아니며 내용이 다르면 `docs/`가 우선합니다.

## 출처

- [CAP-DLV-cli-and-output](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-cli-and-output.md) (영어 원문)
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)
- [CAP-DLV-drift-reconciliation](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md) (영어 원문)
- [CAP-DLV-human-interaction](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-human-interaction.md) (영어 원문)
- [CAP-DLV-adaptive-development](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md) (영어 원문)
- [CAP-DLV-sdd-baseline-adoption](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md) (영어 원문)
- [CAP-DLV-performance-pass](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-performance-pass.md) (영어 원문)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)
- [CAP-DLV-proposal-planning](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-proposal-planning.md) (영어 원문)
- [CAP-DLV-release-handbook](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-release-handbook.md) (영어 원문)
- [CAP-DLV-review-refactor](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-review-refactor.md) (영어 원문)
- [CAP-DLV-spec-bundles](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)
- [CAP-DLV-weekly-report](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-weekly-report.md) (영어 원문)
- [CAP-DLV-workflow-definitions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md) (영어 원문)
- [CAP-DLV-workflow-envelopes](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)
- [CAP-DLV-workflow-orchestration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md) (영어 원문)
- [UC-handle-delivery-problems-and-exceptions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md) (영어 원문)
- [UC-plan-and-hand-off-a-proposal](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md) (영어 원문)
- [UC-publish-a-weekly-report](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-publish-a-weekly-report.md) (영어 원문)
- [UC-reconcile-living-spec-drift](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-reconcile-living-spec-drift.md) (영어 원문)
- [UC-review-and-refactor-accumulated-slop](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md) (영어 원문)
- [UC-route-development-intent](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-route-development-intent.md) (영어 원문)
- [CAP-DLV-deep-research](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-deep-research.md) (영어 원문)
- [CAP-DLV-design-exploration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-design-exploration.md) (영어 원문)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md) (영어 원문)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md) (영어 원문)
