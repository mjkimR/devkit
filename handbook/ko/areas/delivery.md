---
sources:
  CAP-DLV-cli-and-output: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-drift-reconciliation: null
  CAP-DLV-human-interaction: null
  CAP-DLV-project-policy: null
  CAP-DLV-proposal-incubation: null
  CAP-DLV-release-handbook: null
  CAP-DLV-review-refactor: null
  CAP-DLV-spec-bundles: null
  CAP-DLV-weekly-report: null
  CAP-DLV-workflow-definitions: null
  CAP-DLV-workflow-envelopes: null
  CAP-DLV-workflow-orchestration: null
  UC-drive-development-to-integration: null
  UC-handle-delivery-problems-and-exceptions: null
  UC-incubate-and-hand-off-a-proposal: null
  UC-publish-a-weekly-report: null
  UC-reconcile-living-spec-drift: null
  UC-review-and-refactor-accumulated-slop: null
  UC-route-development-intent: null
title: 전달
translated_from: en/areas/delivery.md@8afc7203af77911d
---

# 전달

<!-- handbook:provenance -->
> 소스 커밋 `b44f759024a5` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
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

전달(delivery)은 하나의 작업이 "이걸 원한다"에서 Living Spec이 갱신된 병합된 변경까지 가는 과정입니다. devkit은
그 절차를 데이터로 유지합니다. 워크플로(workflow) 정의가 단계(stage), 검사, 게이트(gate)를 선언하고, CLI가 작업 단위가
어디에 있고 다음에 무엇을 할지 여러분(또는 에이전트)에게 알려 줍니다. 이 페이지는 이 모델을 여러분이 마주치는 순서대로
설명합니다. 용어는 [개념](../concepts.md)을 참고하세요.

## 전달 모델

모든 작업은 시작 전에 `task-kind`(`feature`, `bugfix` 또는 `overall-refactor`)와 `planning-depth`를 받습니다.

| 깊이 | 언제 | 남기는 것 |
| --- | --- | --- |
| `session` | 지속되는 설계나 계약 변경이 없는 작은 변경 | 디스크에는 아무것도 없음: 결과는 대화나 PR 본문으로 보고 |
| `spec` | 서면 요구사항, 계획, Living Spec 반영이 필요한 변경 | `specs/` 아래의 스펙 번들 |
| `proposal` | 방향 자체를 먼저 정해야 하는 경우 | `docs/proposals/` 아래의 제안서, 나중에 스펙으로 인계 |

각 조합은 정확히 하나의 워크플로에 대응합니다. `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`,
`sdd-spec-bugfix`, `sdd-proposal`, `sdd-overall-refactor`입니다. 조건부 단계는 없습니다. 작업이 더 커지면 단계를 켜는
대신 깊이를 올립니다(새 유닛(Unit)). 카탈로그와 그 근거는
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)에
있습니다. 분류 과정은 여정 [개발 요청 라우팅하기](../journeys/route-development-intent.md)(`UC-route-development-intent`)에서
다룹니다.

별도의 조절값인 `activity-effort`(`low`, `medium`, `high`)는 한 활동의 리뷰와 검증을 얼마나 철저히 할지 정합니다. 이
값은 게이트나 필수 검사를 결코 없애지 않습니다. `low`에서는 작성자가 셀프 리뷰를 하고, `medium`에서는 `code-reviewer`와
`reconcile-reviewer`가 한 번 확인하며, `high`에서는 둘 다 제한된 리뷰 라운드로 실행됩니다.

## 그 아래의 엔진

범용 엔진은 `devkit workflow`에 있습니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
**작업 단위(work unit)**는 앵커 파일(`spec.md`, `proposal.md`)이 있는 디렉터리이며, 앵커의 frontmatter에 바인딩된
워크플로가 기록됩니다. `devkit workflow next --unit <dir>`는 각 단계의 종료 검사를 순서대로 평가해 처음으로 충족되지
않은 단계를 보고하므로, 에이전트가 산문에서 이를 다시 유도할 필요가 없습니다. 정의가 바뀌면 진행 중인 작업에도 즉시
적용됩니다.

정의는 `stages[]` YAML frontmatter를 가진 Markdown 파일입니다. 그 스키마, 검사 프리미티브(`file-exists`,
`frontmatter`, `envelope-check-pass`, ...)와 바인딩 규칙은
[`CAP-DLV-workflow-definitions`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md) (영어 원문)에
있습니다. `next`에서 보게 되는 명령, 종료 코드, `[STAGE]`, `[WAITING]`, `[REQUEST]`, `[DELEGATE]` 센티널은
[`CAP-DLV-cli-and-output`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-cli-and-output.md)에 있습니다.

## 제안서: 방향 정하기

제안서(proposal)는 방향이 정해지지 않은 아이디어를 숙성시킵니다
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md) (영어 원문)).
제안서는 `docs/proposals/PROP-<slug>/` 번들로, `proposal.md`, 선택적인 예비 결정(PADR), 자료, 피드백, 의도한 Living
Spec 변경의 선택적 청사진인 `target-docs.md`로 이루어집니다. 수명 주기는 다음과 같습니다.

1. **Backlog**: `uv run devkit spec proposal new <slug>`가 `draft`를 만듭니다. draft를 손으로 수정, 분할 또는 삭제하기
   전에 `uv run devkit spec proposal check <slug>`를 실행하세요. `plan-<slug>`에서 Planning이 진행 중이면 거부합니다.
2. **Planning**은 `plan-<slug>` 브랜치에서 진행됩니다. Planning 노력 수준이 요구하는 만큼 질문, 증거(`scout`), 비판
   (`challenger`)을 거쳐 제안서와 그 PADR에 반영합니다.
3. **수락** (`plan-accept`): `uv run devkit spec proposal accept <slug> --by user`가 `status: accepted`와 게이트를 한
   번에 기록합니다. 작고 자격을 갖춘 draft는 기본 체크아웃에서 `--direct --note "<reason>"`로 Planning을 건너뛸 수
   있습니다. 먼저 `--check`로 실행하면 모든 자격 조건을 한 번에 볼 수 있습니다.
4. **인계(handoff)**: `dev-<slug>` 브랜치에서 `uv run devkit spec proposal handoff <slug>`를 실행하면 스펙 번들을 만들고,
   본문을 옮기고, PADR을 ADR로 승격하고, 자료와 열린 피드백을 옮기고, 링크를 다시 쓰고, 제안서를 제거합니다. 쓰기가
   실패하면 롤백하고 제안서를 남겨 두므로 다시 실행할 수 있습니다.

거절된 제안서는 상태만 바뀌고, 이후의 위생(hygiene) 점검이 거절 ADR을 기록하고 삭제합니다. 활성 제안서는
`uv run devkit spec list proposal`로 나열합니다. 전체 여정은
[제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)(`UC-incubate-and-hand-off-a-proposal`)입니다.

## 스펙과 유닛

스펙 번들은 `spec` 깊이 작업과 인계된 모든 제안서의 유닛입니다
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)).
`specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` 디렉터리에 `spec.md`(앵커), `plan.md`, `tasks.md`, `reconcile.md`와
`envelopes/`, `decisions/` 기록이 들어 있습니다. 직접 만들 때는 다음과 같이 합니다.

```bash
uv run devkit worktree start dev-login-flow --no-worktree   # specs live on their dev- branch
uv run devkit spec new login-flow --summary "Defines how users sign in with email and password."
uv run devkit spec new crash-on-save --workflow sdd-spec-bugfix   # spec.md only; plan and tasks come later
```

각 파일은 `<!-- devkit:skeleton -->` 마커로 시작하며, `spec-specify`, `spec-plan`, `spec-tasks` 스킬이 실제 내용을
쓰고 마커를 지울 때까지 해당 단계는 열려 있습니다. 제안서와 스펙은 같은 slug를 공유하지 않습니다.

## 워크플로 단계

`devkit workflow show <id>`가 권위 있는 순서입니다. 개요는 다음과 같습니다.

- **Session** (`sdd-session-*`): intent, (reproduce), execute and verify, report, approval, commit, merge. 기록은
  남기지 않습니다.
- **Spec feature**: `intent`, `specify`, `build-verify`, `review-refine`, `living-spec-draft`, `collect-feedback`,
  `final-change-report`, `integration-approval`, `integrate`, `merge`.
- **Spec bugfix**: `specify`와 `build-verify`를 `characterize`, `plan-tasks`, `reproduce`(결함을 증명하는 `red`
  엔벨로프), `fix-verify`(수정과 기존 동작 보존을 증명하는 `green` 엔벨로프)로 대체합니다.
- **Proposal**: `intent-proposal`, `spike`, `collect-feedback`, `direction-handoff`, `handoff`.

두 단계는 주의할 만합니다. `living-spec-draft`는 구현자가 변경을 `docs/`에 반영하고(`spec-sync` 스킬) `reconcile.md`를
해결하는 단계로, 통합이 승인되기 전에 끝나야 합니다. `collect-feedback`은 저장소 자체 도구에 대한 관찰을 피드백 파일로
모읍니다. 모든 워크플로에는 재시도 한도, 도구 실패, 해결되지 않은 의미 충돌을 위한 대역 외 `exception` 단계도 있습니다.
[전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
(`UC-handle-delivery-problems-and-exceptions`)를 참고하세요. 이 단계들을 거쳐 스펙을 진행하는 과정은 여정
[개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`)입니다.

## 게이트와 승인

게이트는 사람(또는 명시적 정책)이 결정하는 지점입니다. 네 가지가 있습니다.

| 게이트 | 결정하는 것 | 답하는 방법 |
| --- | --- | --- |
| `plan-intent` | 작업의 목표, 범위, 검증, 종류와 깊이 | `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user` |
| `plan-accept` | 제안서의 방향 | `devkit spec proposal accept <slug> --by user` |
| `proposal-handoff` | 수락된 제안서에서 Development 시작 | Host가 효과를 제시한 뒤 `devkit spec proposal handoff <slug> --effort <level>`(또는 `accept --mode accept_and_handoff`) 실행. 어떤 워크플로 단계도 이를 검사하지 않음 |
| `dev-integration` | 통합 단위 하나(풀 리퀘스트 하나)의 반영 | 이후 `next` 실행에서 `--given dev-integration`, 또는 PR ready 상태 |

Development 안에는 의도적으로 게이트가 없습니다. 합의된 의도 안의 선택은 실행자의 몫이며, 합의된 목표, 범위 또는 계약을
바꿀 문제만 작업을 멈춥니다.

각 게이트는 `[workflow.approvals]`에서 `ask`(기본값) 또는 `auto`입니다. `auto`는 정책으로 보고될 뿐 사용자 동의로
보고되지 않으며, 검사를 건너뛰지도 않습니다. 단계는 `[workflow.stages]`에서 끌 수 있습니다. 유효한 정책은 에이전트가
그러하듯 `uv run devkit spec policy`로 읽습니다
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
같은 명령이 Git 정책(`[tool.spec] worktree` `auto` 또는 `required`, `[worktree] pull_request`), 라우팅
(`depth_escalation`), 피드백 수집 설정도 보고합니다.

요청 종류(`approve`, `choose`), 결정 기록, 그리고 `devkit workflow return`이 이후 승인을 무효화하는 방식은
[`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-human-interaction.md) (영어 원문)에
있습니다.

## 엔벨로프와 기록

엔벨로프(envelope)는 단계나 역할이 반환한 내용을 기록하는 YAML 파일 `<unit>/envelopes/<kind>-NN.yaml`입니다. `P1`/`P2`/`P3`
심각도의 리뷰 지적, 리뷰 라운드를 닫는 `reverify`, `red`/`green` 버그 수정 증거, `feedback` 수집, `final-report`의
테스트/빌드/린트 결과, `reconcile-check`, 실행마다의 `worker` 기록이 있습니다. 파일은 덮어쓰지 않으며 번호가 가장 높은
것이 현재 값입니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

엔벨로프는 유닛을 **보류(hold)**시키기도 합니다. 어떤 `resolution`도 가리키지 않는 `worker` 엔벨로프의 `problem`은
유닛을 막고, `answer` 엔벨로프가 없는 질문은 유닛을 대기시킵니다. 보류 중에는 어떤 게이트도 통과하지 않고, 인계도
일어나지 않으며, `devkit worktree finish --merge`는 `WORKTREE_BLOCKED`로 거부합니다.
`uv run devkit workflow envelope check --unit <dir>`가 보류를 보여 줍니다. `resolution`은 실제로 문제를 고친 쪽만
씁니다.

## 오케스트레이션과 통합

`direct` 모드에서는 메인 에이전트 세션(Host)이 모든 단계를 직접 실행합니다. 활동마다 호출되는 `local-orchestrated`
모드에서는 Host가 한 턴을 그 활동의 워크트리에 있는 일회성 워커에게 넘깁니다. `planning-worker`는 `plan-<slug>`의 draft
제안서를 `plan-accept`까지 이끌고, `development-worker`는 `dev-<slug>`에서 스펙 유닛을 최종 변경 보고서까지 실행하며
단계 경계마다 커밋합니다. 워커만 커밋하는 역할이며, 푸시, 병합, 리베이스, amend는 하지 않습니다. 읽기 전용 역할
(`code-reviewer`, `reconcile-reviewer`, `challenger`, `scout`)은 지적 사항을 반환하고, 호출자가 이를 엔벨로프로
기록합니다.

워커가 돌아오면 Host는 `uv run devkit spec worker inspect`를 실행합니다. 이 명령은 커밋된 기록에서 유닛, 베이스, 헤드,
범위를 유도해 조상 관계, 범위 밖 경로, 깨끗한 상태 여부, 보류, 누적 규칙, 다음 단계를 보고하며, 무언가를 고치거나
범위를 넓히지는 않습니다. 역할 계약, 추론 노력 프리셋(preset), 호스트별 지원(Claude Code 네이티브, Codex 에뮬레이션)은
`CAP-DLV-delivery-workflows`의 4.6절에 있습니다.

`integrate`에서는 작업을 베이스와 병합하고, 충돌을 승인된 의도 안에서 해결하며, 그로 인해 바뀐 것만 다시 검증합니다.
`spec` 준비 상태 제공자는 커밋된 헤드를 격리된 스냅샷에서 확인합니다. 단계 완료, 보류 없음, `spec.md` 완료,
`reconcile.md` 해결, 누적 CI 규칙 통과를 봅니다. `pull_request = "required"`이면 모든 작업이 풀 리퀘스트를 거치고,
그렇지 않으면 `devkit worktree finish --merge`를 통한 로컬 병합이 허용됩니다.

## 유지보수 플레이북

`maintenance` 카탈로그 번들의 옵트인 플레이북(playbook) 세 개는 여러분이 호출할 때만 실행됩니다(`devkit-playbook`,
정확한 ID, 또는 `/spec`의 제안 확인). 어느 것도 단계나 스케줄러를 추가하지 않습니다.

- **드리프트 조정**은 Living Spec, 코드, 지침의 제한된 배치를 검토해 누적된 드리프트를 찾고, 각 불일치를 증거와 함께
  기록하며, 여러분이 결정한 수정만 적용합니다
  ([`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md) (영어 원문);
  여정 [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md), `UC-reconcile-living-spec-drift`).
- **주간 보고서**는 전달된 작업, 저장소 상태, 우선순위가 매겨진 조치를 담은 변경 불가능하고 리비전에 묶인 보고서를
  만듭니다. 게시는 별도로 명시적 승인을 받는 단계입니다
  ([`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md);
  여정 [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md), `UC-publish-a-weekly-report`).
- **검토와 리팩터링**은 여러분이 고른 코드, 지침 또는 CLI 표면을 표면마다 배치 하나와 결정 라운드 하나로 검토하고,
  여러분이 동의한 통합과 축소만 증거를 갖춘 동작 보존 리팩터링(직접 모드의 `sdd-overall-refactor`)으로 적용합니다.
  승인된 계약 제거는 별도의 작업 항목이 됩니다
  ([`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-review-refactor.md);
  여정 [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md),
  `UC-review-and-refactor-accumulated-slop`).

지금 읽고 있는 핸드북 자체도 전달 산출물입니다. 릴리스 준비 중에 요청이 있을 때 저장소 전용 `devkit-dev/handbook`
플레이북과 `just handbook` 명령으로 갱신되는, Living Spec에서 유도된 스냅샷입니다
([`CAP-DLV-release-handbook`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-release-handbook.md) (영어 원문)).
핸드북과 `docs/`가 다르면 `docs/`가 맞습니다.
