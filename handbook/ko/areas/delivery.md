---
sources:
  CAP-DLV-cli-and-output: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-drift-reconciliation: null
  CAP-DLV-human-interaction: null
  CAP-DLV-idea-incubation: null
  CAP-DLV-incubation-sdd-baseline: null
  CAP-DLV-performance-pass: null
  CAP-DLV-project-policy: null
  CAP-DLV-proposal-incubation: null
  CAP-DLV-release-handbook: null
  CAP-DLV-review-refactor: null
  CAP-DLV-spec-bundles: null
  CAP-DLV-weekly-report: null
  CAP-DLV-workflow-definitions: null
  CAP-DLV-workflow-envelopes: null
  CAP-DLV-workflow-orchestration: null
  CAP-INT-mcp-services: null
  UC-drive-development-to-integration: null
  UC-handle-delivery-problems-and-exceptions: null
  UC-incubate-and-hand-off-a-proposal: null
  UC-publish-a-weekly-report: null
  UC-reconcile-living-spec-drift: null
  UC-review-and-refactor-accumulated-slop: null
  UC-route-development-intent: null
title: 전달
translated_from: en/areas/delivery.md@24472c9124c56d7f
---

# 전달

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](../journeys/adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](../journeys/incubate-an-idea.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
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

전달(delivery)은 "이 기능을 원한다"는 요청에서 시작해 병합된 변경에 이르기까지 작업이 이동하는 과정입니다. devkit은 이를 위해 두 가지
개발 방식을 제공합니다. 하나는 스펙 주도 개발(SDD)로, 전달 절차 자체를 데이터로 관리합니다. 워크플로(workflow) 정의가 단계(stage),
검사 항목, 게이트(gate)를 선언하고, CLI가 작업 유닛의 현재 위치와 다음 단계를 사용자나 에이전트에게 알려 줍니다. 다른 하나는
인큐베이션(incubation)으로, 아직 제품의 모습을 찾아가는 단계를 위한 가벼운 반복 방식입니다. 이 페이지는 먼저 방식 선택을 다루고,
SDD를 실제로 접하는 순서대로 설명한 뒤, 인큐베이션과 인큐베이션에서 SDD로의 전환, 그리고 유지보수 플레이북을 다룹니다. 주요 용어의
정의는 [개념](../concepts.md)을 참고하십시오.

## 방식 선택하기

개발 방식(development approach)은 하나의 공유 프로젝트 설정으로, `.devkit/config.toml`의 `[development] approach = "sdd" | "incubation"`이며
지정하지 않으면 `sdd`입니다. `uv run devkit config show`는 이 값과 출처를 보고하고, `uv run devkit spec policy`는
`[DEVELOPMENT_APPROACH: approach=... source=...]` 줄로 출력을 시작합니다
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
`devkit-spec`을 설치하거나 `incubation` 번들을 선택해도 이 값은 바뀌지 않습니다. 에이전트는 작업을 라우팅하기 전에 이 설정을 읽으며,
스스로 방식을 전환하지 않습니다.

| | SDD | 인큐베이션 |
| --- | --- | --- |
| 적합한 경우 | 요구사항과 계약을 문서로 남길 가치가 있는 작업 | 제품의 모습이 아직 정해지지 않은 아이디어 |
| 진입점 | `/spec <intent>` | `/incubate` |
| 남는 것 | 스펙 번들이나 제안, 엔벨로프, 결정 기록, 조정된 Living Spec | `.devkit/incubation.md`(현재 사실만), 코드, 유지하기로 한 현재 문서 |
| 승인 | 게이트(`plan-intent`, `plan-accept`, `dev-integration`) | 목표나 제약이 바뀔 때의 사용자 지시, 평소와 같은 통합 승인 |

인큐베이션이 활성화된 동안에는 SDD 수명 주기 명령(`devkit spec new`, `devkit spec proposal new`, `accept`, `handoff`)이 아무것도
바꾸기 전에 `SPEC_LIFECYCLE_INACTIVE`로 거부됩니다. 범용 워크플로, 정책·범위·워커 점검, 문서 조회는 계속 사용할 수 있고, 이미 존재하는
SDD 기록도 기존 검사를 유지합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).
[오케스트레이션과 통합](#orchestration-and-integration)까지의 절은 SDD를, [인큐베이션](#incubation) 절은 다른 방식을 설명합니다.

## 전달 모델

SDD에서 모든 작업은 시작 전에 `task-kind`(`feature`, `bugfix` 또는 `overall-refactor`)와 `planning-depth`를 부여받습니다.

| 기획 깊이 | 적용 상황 | 산출물 |
| --- | --- | --- |
| `session` | 지속적인 설계 변경이나 공개 계약 수정이 필요 없는 소규모 변경 | 디스크 아티팩트 없음: 최종 결과는 대화 세션이나 PR 본문에 요약 보고 |
| `spec` | 공식적인 요구사항 명세, 기술 계획, Living Spec 반영이 필요한 변경 | `specs/` 디렉터리 아래의 스펙 번들 |
| `proposal` | 기술적 아키텍처나 방향 자체를 먼저 확정해야 하는 경우 | `docs/proposals/` 디렉터리 아래의 제안, 추후 스펙으로 인계 |

각 조합은 정확히 하나의 워크플로에 1:1로 대응합니다: `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`,
`sdd-spec-bugfix`, `sdd-proposal`, `sdd-overall-refactor`. 워크플로에는 임의의 조건부 분기 단계가 없습니다. 작업 규모가 예상보다 커지면
기존 워크플로에 단계를 동적으로 끼워 넣는 대신, 기획 깊이(depth)를 승격하여 새로운 작업 유닛을 생성합니다. 워크플로 카탈로그와 세부 설계 근거는
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)에
기술되어 있습니다. 작업 분류 절차는 여정 [개발 요청 라우팅하기](../journeys/route-development-intent.md)(`UC-route-development-intent`)에서
다룹니다.

작업 단위와 별개로 지정하는 `activity-effort`(`low`, `medium`, `high`) 설정은 해당 활동의 리뷰 및 검증을 얼마나 엄격하게 수행할지를
결정합니다. 이 설정이 낮다고 해서 게이트나 필수 검사 항목이 생략되는 일은 결코 없습니다. `low` 수준에서는 작성자 본인이 자체 검토(self-review)를
수행하고, `medium`에서는 `code-reviewer`와 `reconcile-reviewer`가 1회 독립 검증을 수행하며, `high`에서는 두 리뷰어가 엄격하게 제한된
다회차 리뷰 라운드를 거칩니다.

## 워크플로 엔진 아키텍처

범용 오케스트레이션 엔진은 `devkit workflow` 명령어로 제공됩니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
**작업 유닛(work unit)**은 앵커 파일(`spec.md`, `proposal.md`)을 포함하는 디렉터리이며, 앵커 파일의 frontmatter에 바인딩된 워크플로
식별자가 기록됩니다. `devkit workflow next --unit <dir>` 명령어는 각 단계의 종료 조건(exit check)을 순서대로 평가하여 아직 완료되지 않은
첫 번째 단계를 안내하므로, 에이전트가 텍스트 가이드를 보고 다음 단계를 임의로 추론할 필요가 없습니다. 워크플로 정의 파일이 수정되면 현재 진행 중인
작업에도 즉시 반영됩니다.

워크플로 정의는 `stages[]`를 정의한 YAML frontmatter를 포함하는 Markdown 파일입니다. 스키마 규격, 검사 프리미티브(`file-exists`,
`frontmatter`, `envelope-check-pass` 등) 및 바인딩 규칙은
[`CAP-DLV-workflow-definitions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md) (영어 원문)에
명시되어 있습니다. `next` 실행 시 출력되는 CLI 명령어, 종료 코드 및 `[STAGE]`, `[WAITING]`, `[REQUEST]`, `[DELEGATE]` 센티널 규격은
[`CAP-DLV-cli-and-output`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-cli-and-output.md)을 참고하십시오.

## 제안: 기술적 방향 결정하기

제안(proposal)은 기술적 방향이나 아키텍처가 아직 확정되지 않은 아이디어를 구체화하고 숙성시키는 절차입니다
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md) (영어 원문)).
제안은 `docs/proposals/PROP-<slug>/` 번들로 구성되며, `proposal.md`, 선택적인 예비 결정(PADR), 참고 자료, 피드백, 그리고 의도한
Living Spec 변경 사항의 선택적 청사진인 `target-docs.md`를 포함합니다. 전체 수명 주기는 다음과 같습니다.

1. **Backlog**: `uv run devkit spec proposal new <slug>` 명령어로 `draft` 제안을 생성합니다. 드래프트를 수동으로 직접 편집,
   분할, 삭제하기 전에는 반드시 `uv run devkit spec proposal check <slug>`로 상태를 확인하십시오. `plan-<slug>` 브랜치에서 이미
   Planning이 진행 중인 경우에는 변경이 거부됩니다. 초안 단계에서는 `size: XL`(스펙이 둘 이상 필요하거나 다른 `task_kind`가 필요한
   작업)을 달 수 있지만, Planning 전에 분할(`new --decomposed-from`)하거나 마일스톤으로 승격해야 합니다. 그 전까지 `plan-intent`는
   요청되지 않으며, 이를 통과하려고 크기 값을 고치지 않습니다. 읽기 전용 `decomposer` 역할이 분할안을 제안해 사용자의 결정을 도울 수 있습니다.
2. **Planning**: `plan-<slug>` 브랜치에서 진행됩니다. 지정된 Planning 노력 수준(effort)에 맞추어 설계 질문 도출, 사실 증거 수집(`scout`),
   비판적 검증(`challenger`)을 수행하고 그 결과를 제안 본문과 PADR에 종합 반영합니다.
3. **수락** (`plan-accept`): `uv run devkit spec proposal accept <slug> --by user` 명령어가 `status: accepted`와 게이트 승인을
   단일 단계로 기록합니다. 요건을 충족하는 소규모 드래프트는 기본 체크아웃에서 `--direct --note "<reason>"` 플래그를 통해 Planning 단계를
   생략하고 직접 수락(direct acceptance)할 수 있습니다. 수락 자격 조건의 충족 여부는 `--check` 플래그로 사전에 한 번에 확인할 수 있습니다.
   기본 체크아웃에서 `uv run devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff --by user`를 실행하면, 사용자가
   그 효과를 승인한 뒤 수락, `plan-<slug>` 통합, 그리고 `--effort`를 주면 아래의 인계까지 한 번에 수행합니다.
4. **인계(handoff)**: `dev-<slug>` 브랜치에서 `uv run devkit spec proposal handoff <slug>`를 실행하면 정식 스펙 번들을 생성하고,
   제안 본문을 이전하며, PADR을 정식 ADR로 승격하고, 참고 자료와 미해결 피드백을 이전하며, 문서 링크를 재작성한 후 원본 제안 디렉터리를
   삭제합니다. 인계 중 파일 쓰기가 실패하면 모든 변경이 안전하게 롤백되고 원본 제안이 보존되므로 재실행이 가능합니다. 인자의 기본 형태는
   `proposal-handoff` 결정 이후 Host가 직접 실행하는 단순 단계이며 별도의 프로젝트 정책을 읽지 않습니다. 기본 체크아웃에서
   `uv run devkit spec proposal handoff <slug> --effort <level>`을 실행하면 프로젝트 정책을 자동으로 확인하여 `dev-<slug>` 환경을
   준비한 후 그곳에서 인계 작업을 완료합니다.

반려된 제안은 즉시 삭제되지 않고 상태만 변경되며, 이후 정기 위생(hygiene) 정리 작업 시 반려 ADR을 작성하고 정리됩니다. 진행 중인 활성 제안
목록은 `uv run devkit docs list proposal`로 조회하며, Planning 중인 초안은 `reviewing`으로 표시됩니다. 전체 여정은
[제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)(`UC-incubate-and-hand-off-a-proposal`)에 기술되어 있습니다.

## 스펙과 유닛

스펙 번들은 `spec` 기획 깊이의 작업과 모든 인계 완료된 제안의 기본 작업 유닛(Unit)입니다
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)).
디렉터리 경로는 `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` 형식이며, `spec.md`(앵커 파일), `plan.md`, `tasks.md`, `reconcile.md` 및
`envelopes/`, `decisions/` 기록을 포함합니다. 신규 번들은 다음과 같이 생성합니다.

```bash
uv run devkit worktree start dev-login-flow --no-worktree   # 스펙은 전용 dev- 브랜치에서 진행됨
uv run devkit spec new login-flow --summary "이메일과 비밀번호를 사용한 사용자 로그인 흐름을 정의합니다."
uv run devkit spec new crash-on-save --workflow sdd-spec-bugfix   # spec.md만 우선 생성되며 plan과 tasks는 이후 작성
```

각 파일은 `<!-- devkit:skeleton -->` 스켈레톤 마커로 시작하며, `spec-specify`, `spec-plan`, `spec-tasks` 스킬이 실제 명세 내용을 작성하고
마커를 제거할 때까지 해당 단계는 미완료 상태로 유지됩니다. 제안과 스펙은 동일한 slug를 공유할 수 없습니다.

## 워크플로 단계 구조

`devkit workflow show <id>` 명령어가 워크플로의 공식적인 단계 순서를 보여줍니다. 주요 워크플로의 개요는 다음과 같습니다.

- **Session** (`sdd-session-*`): intent, (reproduce), execute and verify, report, approval, commit, merge. 별도의 스펙 문서는 남기지 않습니다.
- **Spec feature**: `intent`, `specify`, `build-verify`, `review-refine`, `living-spec-draft`, `collect-feedback`,
  `final-change-report`, `integration-approval`, `integrate`, `merge`.
- **Spec bugfix**: `specify`와 `build-verify` 대신 `characterize`, `plan-tasks`, `reproduce`(결함을 증명하는 `red` 엔벨로프),
  `fix-verify`(수정 검증 및 기존 동작 보존을 증명하는 `green` 엔벨로프) 단계를 수행합니다.
- **Proposal**: `intent-proposal`, `spike`, `collect-feedback`, `direction-handoff`, `handoff`.

특히 주목해야 할 핵심 단계는 두 가지입니다. `living-spec-draft`는 구현자가 코드 변경 내역을 `docs/`의 Living Spec에 동기화하고
(`spec-sync` 스킬) `reconcile.md`의 목표 항목을 완결하는 단계이며, 최종 통합 승인 전에 반드시 완료되어야 합니다. `collect-feedback`은
작업 중 발견한 도구 및 하네스 개선 피드백을 수집하는 단계입니다.

사람이 보는 화면이 바뀌는 변경이라면 코드 작성 전에 `docs/ux/` 아래에 화면 초안을 만들고, 선택적인 읽기 전용 `ux-reviewer`가 연결된
유스케이스를 초안에 따라 진행해 보며 화면마다 점수를 매길 수 있습니다(최대 두 라운드, Planning 중이나 계획 수립 전에 `ux-review`
엔벨로프로 기록). 이는 위임일 뿐 단계나 게이트가 아니며, 이후 구현자가 각 발견 사항을 `resolved` 또는 `waived`로 표시합니다.
또한 모든 워크플로에는 재시도 횟수 초과, 도구 오류, 미해결된 의미론적 충돌에
대비한 대역 외(out-of-band) `exception` 단계가 마련되어 있습니다. 세부 대응 절차는
[전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)(`UC-handle-delivery-problems-and-exceptions`)를
참고하십시오. 이러한 단계들을 거치며 스펙을 진행하는 전체 흐름은
[개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)(`UC-drive-development-to-integration`) 여정을 따릅니다.

## 게이트와 승인

게이트(gate)는 사람(또는 명시적으로 선언된 정책)이 진행 여부를 결정하는 주요 마일스톤입니다. 총 4개의 게이트가 존재합니다.

| 게이트 | 결정 사항 | 응답 방법 |
| --- | --- | --- |
| `plan-intent` | 작업의 목표, 범위, 검증 방식, 종류 및 기획 깊이 승인 | `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user` |
| `plan-accept` | 제안의 아키텍처 및 기술 방향 승인 | `devkit spec proposal accept <slug> --by user` |
| `proposal-handoff` | 수락된 제안으로부터 정식 Development 단계 착수 승인 | Host가 변경 효과를 확인한 뒤 `devkit spec proposal handoff <slug> --effort <level>`(또는 `accept --mode accept_and_handoff`) 실행. 별도의 워크플로 단계에서 이를 재검사하지 않음 |
| `dev-integration` | 단일 통합 단위(풀 리퀘스트 단위)의 코드베이스 반영 승인 | 후속 `next` 실행 시 `--given dev-integration` 플래그 지정, 또는 PR ready 상태 충족 |

Development 단계 내부에는 의도적으로 사람의 승인을 요구하는 게이트를 두지 않습니다. 사전 합의된 범위 내에서의 기술적 세부 선택은
실행자(에이전트)의 자율에 맡겨지며, 이미 합의된 목표, 범위, 외부 계약을 변경해야 하는 예외 상황에서만 작업이 중단됩니다.

각 게이트는 `.devkit/config.toml`의 `[workflow.approvals]` 설정에 따라 `ask`(기본값, 명시적 사용자 확인) 또는 `auto`(자동 승인)로 동작합니다.
`auto` 모드는 정책에 따른 자동 승인으로 명확히 기록될 뿐 사용자 직접 동의로 위장되지 않으며, 필수 검사 항목을 건너뛰지도 않습니다.
불필요한 단계는 `[workflow.stages]` 설정에서 비활성화할 수 있습니다. 현재 유효한 최종 정책은 `uv run devkit spec policy` 명령어로
확인할 수 있습니다([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
동일한 명령어로 Git 워크트리 정책(`[tool.spec] worktree` `auto` 또는 `required`, `[worktree] pull_request`), 라우팅 에스컬레이션
(`depth_escalation`), 피드백 수집 정책 등도 종합 조회할 수 있습니다.

요청 종류(`approve`, `choose`), 결정 기록 형식 및 `devkit workflow return` 명령어를 통해 이전 승인을 무효화하는 메커니즘은
[`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-human-interaction.md) (영어 원문)에
자세히 설명되어 있습니다.

## 엔벨로프와 작업 기록

엔벨로프(envelope)는 워크플로의 특정 단계나 역할이 산출한 결과를 표준화된 형식으로 기록하는 YAML 파일(`<unit>/envelopes/<kind>-NN.yaml`)입니다.
`P1`/`P2`/`P3` 심각도별 리뷰 발견 사항, 리뷰 라운드를 완결하는 `reverify`, `red`/`green` 버그 수정 입증 데이터, `feedback` 수집 기록,
`final-report`의 테스트/빌드/린트 실행 결과, `reconcile-check`, 그리고 매 실행 시마다 생성되는 `worker` 기록 등이 포함됩니다.
엔벨로프 파일은 기존 파일을 덮어쓰지 않고 일련번호를 증가시키며 저장되므로 번호가 가장 큰 파일이 최신 상태를 나타냅니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

엔벨로프는 작업 단위를 **보류(hold)** 상태로 전환시키기도 합니다. 후속 `resolution` 엔벨로프가 등록되지 않은 `worker` 엔벨로프의
`problem` 항목은 유닛 진행을 차단하며, `answer` 엔벨로프가 없는 질문 역시 작업을 대기 상태로 묶어둡니다. 보류 상태에서는 어떤 게이트도
통과할 수 없고 인계도 진행되지 않으며, `devkit worktree finish --merge` 실행 시 `WORKTREE_BLOCKED` 오류와 함께 작업이 거부됩니다.
`uv run devkit workflow envelope check --unit <dir>` 명령어로 현재의 보류 상태를 확인할 수 있습니다. `resolution` 엔벨로프는 문제를
실제로 해결한 주체만 작성해야 합니다.

<a id="orchestration-and-integration"></a>

## 오케스트레이션과 통합

`direct` 모드에서는 메인 대화 세션(Host)이 모든 워크플로 단계를 직접 수행합니다. 반면 활동 단위로 구동되는 `local-orchestrated` 모드에서는
Host가 각 턴의 세부 실행을 해당 활동 전용 워크트리에서 구동되는 일회성 워커(worker)에게 위임합니다. `planning-worker`는 `plan-<slug>`
브랜치에서 드래프트 제안을 `plan-accept` 단계까지 완성시키고, `development-worker`는 `dev-<slug>` 브랜치에서 스펙 유닛을 최종 변경
보고서 작성 시점까지 실행하며 각 단계의 경계마다 커밋을 남깁니다. 워커는 커밋 권한을 가진 유일한 역할이지만, 푸시, 머지, 리베이스,
커밋 수정(amend)은 수행하지 않습니다. 읽기 전용 역할(`code-reviewer`, `reconcile-reviewer`, `challenger`, `scout`,
`ux-reviewer`)은 검토 결과를 반환하고, 호출자가 이를 엔벨로프 파일로 기록합니다. Backlog에서는 `triage`가 열린 피드백을 묶고
`decomposer`가 초안의 분할안을 제안하며, 둘 다 사용자가 결정할 메시지를 반환합니다.

워커가 작업을 마치고 복귀하면 Host는 `uv run devkit spec worker inspect`를 실행합니다. 이 명령어는 커밋 기록으로부터 작업 유닛,
베이스, 헤드, 파일 범위를 분석하여 커밋 계통, 범위 외 수정 파일, 작업 트리 청결도, 보류 상태, 누적 규칙 검증 결과 및 다음 실행 단계를
보고합니다. 누적 규칙은 `--rules-base`로 지정할 수 있는 규칙 기준 커밋과 비교합니다. 이 단계에서 임의로 코드를 수정하거나 허용 범위를
확장하지 않으며, 실패한 검사는 Host가 판단할 오류로 보고됩니다. 역할별 인터페이스 계약과 호스트 환경별 지원 현황(Claude Code 네이티브,
Codex 에뮬레이션)은 `CAP-DLV-delivery-workflows` 4.6절에 정리되어 있습니다. 역할에는 추론 노력 프리셋이 없습니다. 기본적으로 세션의
모델을 이어받으며, `scout`만 compact 모델 수준을 기본으로 사용하고, 프로젝트는 `[subagents]`에서 역할별 수준을 지정할 수 있습니다.

`integrate` 단계에서는 개발 작업을 베이스 브랜치와 병합하고, 충돌이 발생하면 승인된 의도 범위 내에서 해결하며, 병합으로 인해 새로 변경된
내용만 선별하여 재검증합니다. `spec` 준비 상태 검증기는 격리된 스냅샷 환경에서 커밋된 헤드를 점검합니다: 단계 완료 여부, 보류 항목 부재,
`spec.md` 완성도, `reconcile.md` 목표 완결, 누적 CI 규칙 통과 등을 종합 확인합니다. `pull_request = "required"` 정책 하에서는
모든 작업이 풀 리퀘스트를 거쳐야 하며, 그렇지 않은 환경에서는 `devkit worktree finish --merge`를 통한 로컬 직접 병합이 허용됩니다.

<a id="incubation"></a>

## 인큐베이션

인큐베이션은 옵트인 `incubation` 카탈로그 번들로 제공됩니다. `devkit-docs`와 `devkit-catalog`를 설치한 뒤
`uv run devkit add incubation`을 실행하면 되며, `devkit-spec`은 필요 없습니다. 번들을 선택하면 `/incubate`, 세 가지 선택적 지원 역할,
템플릿이 배포되지만 개발 방식은 바뀌지 않습니다. `/incubate`는 먼저 실제 적용 중인 방식을 확인하고, `incubation`이 아니면 제품 작업을
하지 않고 멈춘 뒤 필요한 설정 변경을 보여 줍니다
([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md) (영어 원문)).

각 세션은 정해진 순서가 아니라 다음으로 유용한 제품 작업을 진행합니다.

- **명확히 하기**: 이미 받은 답은 재사용하고, 빠진 제품 결정만 묻습니다. 완전한 백로그나 아키텍처를 먼저 요구하지 않습니다.
- **조사 또는 실험**: 명시한 쓰기 범위와 중단 조건 안에서 진행하며, 관찰, 가정, 한계를 구분합니다.
- **구현**: 대표 흐름을 구현하고, 이를 실행하고 확인하는 방법을 함께 남깁니다.
- **검증**: 실제로 실행해 확인합니다. 건너뛰었거나 실행할 수 없었던 검사는 통과가 아니라 미검증으로 보고합니다.

선택적 역할인 `product-clarifier`, `incubation-researcher`, `usage-reviewer`는 따로 떼어 낼 만한 질문이 있을 때만 위임되며, 근거를
반환할 뿐 현재 컨텍스트를 수정하거나 커밋하지 않습니다. 목표와 제약이 유지되는 동안 에이전트는 유닛, 승인, 엔벨로프 없이 코드, 테스트,
문서를 자유롭게 고칠 수 있지만, 목표나 제약이 바뀌면 먼저 사용자의 지시를 구합니다.

**인큐베이션 현재 컨텍스트**(incubation current context)인 `.devkit/incubation.md`는 세션 사이에 유지되는 유일한 기록입니다. 프로젝트가
소유하는 Markdown 파일로 현재 사실만 담습니다. 목표, 사용자, 제약, 사용자가 내린 선택과 에이전트의 가정의 구분, 실행·확인 명령과 그
실제 결과, 남은 질문, 다음으로 유용한 작업이 여기에 들어갑니다. 더 이상 의미 없는 실험은 기록으로 쌓지 않고 지우며, `devkit sync`는 이
파일을 덮어쓰지 않습니다. 이후 세션은 오래된 항목을 그대로 믿지 않고 바뀐 부분을 다시 확인합니다. 해당 여정은
[아이디어 인큐베이션하기](../journeys/incubate-an-idea.md)(`UC-incubate-an-idea`)입니다.

통합은 SDD의 `session` 작업과 같이 사용자의 승인 아래 `devkit integration prepare`와 `integrate`로 진행합니다. 프로젝트 준비 상태
제공자(project readiness provider)는 에이전트가 보고한 리뷰, 테스트, 린트 결과를 결합하고, 결과물에 저장소 규칙을 실행하며, 보존된 SDD
유닛을 건드리는 변경은 그 유닛의 검증이 실행될 때까지 거부합니다
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)).

### 인큐베이션에서 SDD 도입하기

프로젝트의 규모, 경과 시간, 실험 횟수 중 어느 것도 프로젝트를 자동으로 SDD로 옮기지 않습니다. 사용자가 요청하면 에이전트는 `spec`
번들에 포함된 `spec/sdd-baseline` 플레이북(`uv run devkit playbook get spec/sdd-baseline`)을 실행합니다
([`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md) (영어 원문)).

1. 준비하는 동안에는 `devkit-spec`을 설치하고 번들을 선택한 뒤에도 방식이 계속 `incubation`으로 유지되므로, 기준선이 완성되지 않은
   상태에서도 인큐베이션으로 개발을 이어 갈 수 있습니다.
2. 제품에서 유지할 범위는 사용자가 정합니다. 유지할 각 동작, 구조, 선택, 검증 방법을 구현, 현재 문서, 실제 근거와 연결하고
   `verified`, `gap`, `excluded`(이유 포함, 제외 항목은 커버리지로 세지 않음) 중 하나로 표시합니다.
3. 빠진 현재 상태 문서는 지금 모습 그대로, 알려진 이유와 함께 작성하며 지어낸 과거 이력은 넣지 않습니다.
4. `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/` 아래의 보고서에 소스, 범위, 근거, 공백, 정확한 활성화 효과를 기록합니다.
5. 공백이 하나도 남지 않았을 때만 에이전트가 그 효과(`[development]` 변경과 필요한 통합 제공자 변경)를 사용자의 명시적 결정을 위해
   제시합니다. 소스가 바뀌었다면 먼저 다시 검증합니다.
6. 활성화 후에는 `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy`, `uv run devkit sync --check`로
   확인하며, 이후 새 작업은 일반적인 SDD 경로를 따릅니다. 기준선 작업은 과거를 재구성한 스펙 번들이나 엔벨로프를 만들지 않으며, 일부만
   성공한 경우에는 그대로 보고하고 롤백했다고 주장하지 않습니다.

해당 여정은 [인큐베이션에서 SDD 도입하기](../journeys/adopt-sdd-from-incubation.md)(`UC-adopt-sdd-from-incubation`)입니다.

## 유지보수 플레이북

`devkit-catalog`의 `maintenance` 카탈로그 번들에 포함된 4종의 선택형 플레이북(playbook)은 사용자가 명시적으로 호출할 때만 실행됩니다
(`devkit-playbook`, 고유 ID 직접 지정, 또는 `/spec` 프롬프트의 제안 승인을 통해 호출). 이 플레이북들은 워크플로 단계나 자동 스케줄러를
추가하지 않습니다.

- **드리프트 조정(Drift reconciliation)**: Living Spec, 코드베이스, 안내 문서의 특정 범위를 점검하여 누적된 정합성 드리프트를 식별하고,
  각 불일치 항목을 근거 자료와 함께 기록한 후 사용자가 명시적으로 승인한 수정 조치만 선별 반영합니다
  ([`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md) (영어 원문);
  여정 [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md), `UC-reconcile-living-spec-drift`).
- **주간 보고서(Weekly report)**: 완료된 전달 작업 내역, 저장소 건전성 지표, 우선순위 조치 사항을 취합하여 불변의 리비전 연동 보고서를
  작성합니다. 보고서의 외부에 게시는 별도의 명시적 승인 절차를 거칩니다
  ([`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-weekly-report.md);
  여정 [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md), `UC-publish-a-weekly-report`).
- **검토와 리팩터링(Review and refactor)**: 사용자가 지정한 코드베이스, 지침 문서, CLI 인터페이스 범위를 점검하여 불필요하게 누적된
  군더더기(slop)를 식별하고, 사용자가 동의한 통합 및 단순화 조치만 동작 보존 리팩터링으로 안전하게 적용합니다(direct 모드의 `sdd-overall-refactor`).
  쓰기 범위가 겹치지 않는 변경은 격리된 체크아웃에서 병렬로 진행하고 각각 단독 커밋으로 남깁니다. 파서처럼 입력을 열거할 수 있는 함수를
  교체할 때는 같은 입력으로 이전 코드와 새 코드를 비교하며, 통과를 위해 저장소 검사를 완화하는 변경은 허용되지 않습니다. 공개 계약의 제거가 승인된 항목은 별도의 독립된 작업 유닛으로 분리하여 처리합니다
  ([`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-review-refactor.md);
  여정 [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md), `UC-review-and-refactor-accumulated-slop`).
- **성능 점검(Performance pass)**: `maintenance:performance`(`review-refactor`도 함께 배포)로 선택하며, 사용자가 고른 작업을 정확한 명령과
  지표(실행 시간, 하위 프로세스 수, 최대 메모리)로 측정합니다. 측정은 프로파일러 없이 한 세션 안에서 변형을 번갈아 실행하며, 워밍업,
  최소 다섯 번의 반복, 그리고 그보다 작은 차이는 변화 없음으로 보는 노이즈 하한을 둡니다. 프로파일링은 비용의 출처를 찾는 데만 씁니다.
  후보는 한 번의 결정 라운드에서 정합니다. 출력, 종료 코드, 기록된 파일, 오류 동작이 모두 같을 때만 동작 보존으로 보고, 그 밖의 변경(실행
  간 새 캐시, 병렬화, 기본값 변경 등)은 별도의 계약 변경 작업 항목이 됩니다. 합의된 변경은 저장소의 기능 워크플로를 따르는 하나의 작업
  항목이 되어 `review-refactor`의 적용·근거 절차대로 진행되며, 변경마다 이전과 이후를 측정하고 마지막에 시작 리비전과 비교 측정합니다.
  `survey` 실행은 아무것도 적용하지 않고 결정 라운드에서 멈춥니다
  ([`CAP-DLV-performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-performance-pass.md) (영어 원문);
  여정 [선택한 느린 작업 빠르게 하기](../journeys/speed-up-selected-slow-operations.md), `UC-speed-up-selected-slow-operations`).

현재 읽고 계신 핸드북 역시 전달 산출물의 일종입니다. 릴리스 준비 과정에서 필요 시 저장소 전용 `devkit-dev/handbook` 플레이북과
`just handbook` 명령어를 통해 Living Spec으로부터 최신 내용을 추출하여 생성된 파생 스냅샷입니다
([`CAP-DLV-release-handbook`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-release-handbook.md) (영어 원문)).
핸드북과 `docs/`의 내용이 충돌할 경우 항상 `docs/`의 Living Spec이 우선합니다.
