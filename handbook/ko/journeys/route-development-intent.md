---
sources:
  ADR-spec-intake-playbook-discovery: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-project-policy: null
  CAP-DLV-spec-bundles: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-incubate-and-hand-off-a-proposal: null
  UC-route-development-intent: null
title: 개발 요청 라우팅하기
translated_from: en/journeys/route-development-intent.md@729f535f1b53a309
---

# 개발 요청 라우팅하기

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
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

거의 모든 작업은 여기서 시작합니다. 원하는 것을 에이전트에게 말하면(`/spec <intent>` 또는 어떤 개발 요청이든),
에이전트는 여러분과 의도를 합의한 상태로 그 요청을 정확히 하나의 전달 워크플로(workflow)에 올립니다. 정할 것이
없는 작은 작업은 가볍게 유지되고, 계약이 바뀌는 작업은 스펙 번들을 얻으며, 방향이 열려 있는 작업은 제안(proposal)이
됩니다. 여러분이 가진 모든 승인은 가정되지 않고 알맞은 시점에 요청됩니다.

워크플로, 단계(stage), 게이트(gate), 세 가지 분류 축은 [개념](../concepts.md)과
[전달 영역](../areas/delivery.md)에서 설명합니다.

출처: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-route-development-intent.md) (영어 원문).

## 시작하기 전에

`devkit-spec`이 설치되어 있고 그 `spec` 번들이 동기화되어 있습니다. 에이전트는 개발 작업을 하기 전에 에이전트
컨텍스트마다 한 번 스펙 헌장을 불러옵니다(`uv run devkit get-context spec`).

## 단계별 진행

일반적인 경로는 `direct` 모드의 `spec` 깊이 `feature`입니다.

1. **접수.** 에이전트는 요청을 가지고 `spec` 스킬에 들어가 한정된 플레이북 검색을 한 번 실행합니다
   (`devkit playbook search "<query>" --limit 3 --max-bytes 4096`). 요청한 작업을 이름으로 가리키는 플레이북이 없으면
   아무 말 없이 계속 진행합니다(`ADR-spec-intake-playbook-discovery`).
2. **정책.** 실제로 적용되는 프로젝트 정책을 읽습니다.

   ```sh
   uv run devkit spec policy
   ```

   출력에는 `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]` 같은 줄과 게이트마다 하나씩의
   `[GATE_POLICY: ...]`가 포함됩니다
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
3. **분류.** 요청을 `task-kind`(`feature` 또는 `bugfix`), 이어서 `planning-depth`(`session`, `spec`, `proposal` 중
   하나이며, 크기가 아니라 구현 전에 정해야 할 것으로 판단), 그다음 모드와 `activity-effort`로 분류하고 이를
   여러분에게 알립니다
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
4. **브랜치.** Git 정책이 허용하는 대로 현재 체크아웃(`devkit worktree start dev-<slug> --no-worktree`)이나 별도의
   작업 워크트리(task worktree)에서 `dev-<slug>`를 시작합니다.
5. **스펙 번들.** 번들을 만듭니다.

   ```sh
   uv run devkit spec new <slug>
   ```

   이 명령은 뼈대만 있는 `spec.md`, `plan.md`, `tasks.md`와 함께 `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`를 만들어
   `sdd-spec-feature`에 연결하고, `[NEXT_CMD: devkit workflow next --unit <dir>]`로 끝납니다
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
6. **의도.** 여러분의 명시적 지시를 바탕으로 `plan-intent`를 기록합니다.
7. **다음 단계.** `devkit workflow next --unit <dir>`를 실행하고, 그 단계와 충족되지 않은 검사, 지정된 스킬을
   따릅니다 ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## 다른 경로

| 분류 | 진행 방식 |
| --- | --- |
| `session` 깊이 | 대화로 의도를 합의하고, 에이전트가 직접 `sdd-session-<task-kind>`를 따릅니다. 유닛(Unit), 엔벨로프(envelope), 게이트 기록, reconcile 문서는 만들지 않습니다. |
| `proposal` 깊이 | `devkit spec proposal new <slug>`가 초안 `docs/proposals/PROP-<slug>/proposal.md`를 만들고, [제안 숙성과 인계](incubate-and-hand-off-a-proposal.md)로 이어집니다. |
| 지금 시작하지 않거나 너무 큼 | Backlog에 하나 이상의 초안 제안으로 보관하며, 마일스톤에 넣을 수도 있고, `decomposed_from` 또는 `supersedes`로 출처를 보존합니다. |
| `overall-refactor` | 동작 추가 없이 여러 영역을 재구성합니다. 유닛, 제안, 번들 없이 `direct` 모드의 `sdd-overall-refactor`를 따릅니다. |
| 계약에 대한 결함 | `devkit spec new <slug> --workflow sdd-spec-bugfix`: `spec.md`만 만들며, 재현이 기록될 때까지 `reproduce` 단계가 열려 있습니다. |
| "다음에 뭘 하지?"만 묻는 경우 | `spec-next`가 대기 중인 적격 초안을 추천하고(선행 조건, 마일스톤, 우선순위, 크기 기준), 승인은 여러분에게 남습니다. |

## 의도 승인하기

`plan-intent` 정책이 `ask`(기본값)일 때 목표, 범위, 검증, 종류, 깊이 중 아직 정해지지 않은 것이 있으면
`devkit workflow next`가 `[WAITING: human gate:plan-intent]`를 출력합니다. 에이전트는 여러분에게 묻고, 여러분이
답한 뒤에만 답을 기록합니다.

```sh
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action decline --by user --note "<reason>"
```

`auto`에서는 게이트가 정책에 따라 통과하며, 에이전트는 이를 여러분의 동의가 아니라 정책으로 보고합니다. 거절하면
작업이 끝납니다.

## 문제가 생겼을 때

- **플레이북이 일치합니다.** 에이전트는 분류와 함께 그 플레이북을 한 줄로 알리고 기다립니다. 확인하면 실행되고,
  거절하면 이 대화에서 다시 제안되지 않습니다. 이어지는 작업과 후속 작업에서는 검색하지 않습니다.
- **`devkit spec policy`가 `SPEC_CONFIG_INVALID`를 냅니다.** `[tool.spec]`에 알 수 없는 키가 있거나, 게이트 정책이
  `ask`나 `auto`가 아닙니다(예: `plan-intent = "off"`). 여러분이 `.devkit/config.toml`을 고칠 때까지 에이전트는
  정책에 의존하는 작업을 멈춥니다.
- **`SPEC_WRONG_BRANCH`.** 체크아웃이 `dev-<slug>`에 있지 않아 아무것도 쓰지 않았습니다. 그 브랜치를 시작하거나
  이어서 작업한 뒤 `devkit spec new`를 다시 실행하십시오.
- **`SPEC_EXISTS`.** 다른 문서, 제안 또는 번들이 이미 그 slug를 쓰고 있습니다(`[TARGET]`에 나열됨). 다른 slug를
  고르십시오.
- **워크트리가 필요합니다.** `worktree=required`이거나, `auto`인데 체크아웃에 관련 없는 변경이나 다른 작업이 있으면
  에이전트는 `dev-<slug>`를 별도의 워크트리에서 시작합니다
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
- **세션 작업에 계약 변경이 필요한 것으로 드러납니다.** 에이전트는 깊이를 `spec`으로 올리고(`depth_escalation=auto`면
  스스로, `ask`면 여러분의 확인 후), 같은 위치의 `dev-<slug>`에 스펙 유닛을 추가하며, 지금까지 한 작업은 그대로
  유지합니다. 깊이가 저절로 낮아지는 일은 없습니다.

## 결과

작업마다 하나의 워크플로가 있으며, 그 유닛이, 세션이라면 대화가 이를 가리킵니다. 기록된 모든 승인은 여러분의 지시,
명시적 답변 또는 `auto` 정책에서 나오며, 거부된 `devkit spec new`는 작업 공간을 바꾸지 않습니다.
