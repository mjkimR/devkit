---
sources:
  ADR-spec-intake-playbook-discovery: null
  CAP-DIST-sync-and-transactions: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-project-policy: null
  CAP-DLV-spec-bundles: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-incubate-an-idea: null
  UC-incubate-and-hand-off-a-proposal: null
  UC-route-development-intent: null
title: 개발 요청 라우팅하기
translated_from: en/journeys/route-development-intent.md@547043a6c8929149
---

# 개발 요청 라우팅하기

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

스펙 주도 개발(SDD)을 쓰는 저장소에서는 대부분의 작업이 이 여정에서 출발합니다. 사용자가 원하는 바를 에이전트에 전달하면(`/spec <intent>` 또는 일반적인 개발 요청), 에이전트는 의도를 합의한 후 요청을 정확히 하나의 전달 워크플로에 배정합니다. 사전에 정할 것이 없는 작은 작업은 가볍게 진행되고, 계약이 바뀌는 작업은 스펙 번들을 만들며, 방향이 열려 있는 작업은 제안(proposal)이 됩니다. 사용자가 승인해야 할 사항은 추정하지 않고 적절한 시점에 묻습니다.

워크플로, 단계, 게이트 및 세 가지 분류 축은 [개념](../concepts.md)과 [전달 영역](../areas/delivery.md)에서 설명합니다.

출처: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-route-development-intent.md) (영어 원문).

## 시작하기 전에

`devkit-spec`이 설치되어 있고 `spec` 번들이 동기화되어 있어야 합니다. 이 라우팅이 적용되는지는 저장소의 공유 개발 방식(development approach)이 결정합니다. `.devkit/config.toml`의 `[development] approach`는 `sdd`(미설정 시 기본값) 또는 `incubation`이며, 번들 선택은 이를 바꾸지 않습니다. 에이전트는 `uv run devkit config show`로 이를 확인하고, 개발 작업 전에 에이전트 컨텍스트마다 한 번 스펙 헌장을 로드합니다(`uv run devkit get-context spec`).

## 단계별 진행

가장 일반적인 경로는 `direct` 모드의 `spec` 깊이 `feature`입니다.

1. **요청 접수.** 에이전트가 적용 중인 개발 방식이 SDD인지 확인하고, 요청을 가지고 `spec` 스킬에 들어갑니다. 제한된 플레이북 검색을 한 번 실행하며(`devkit playbook search "<query>" --limit 3 --max-bytes 4096`), 요청한 작업을 가리키는 플레이북이 없으면 별도 질문 없이 계속합니다(`ADR-spec-intake-playbook-discovery`).
2. **정책 확인.** 적용 중인 프로젝트 정책을 읽습니다.

   ```sh
   uv run devkit spec policy
   ```

   출력은 `[DEVELOPMENT_APPROACH: approach=sdd source=default]`로 시작하며, `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]`, 게이트별 `[GATE_POLICY: ...]` 같은 줄을 포함합니다
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
3. **작업 분류.** 요청을 `task-kind`(`feature` 또는 `bugfix`), `planning-depth`(`session`, `spec`, `proposal`: 크기가 아니라 구현 전에 정해야 할 것 기준), 모드와 `activity-effort` 순으로 분류하고 사용자에게 알립니다
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)).
4. **브랜치 생성.** Git 정책이 허용하는 대로 현재 체크아웃(`devkit worktree start dev-<slug> --no-worktree`) 또는 별도 작업 워크트리에서 `dev-<slug>`를 시작합니다.
5. **스펙 번들 생성.** 번들을 만듭니다.

   ```sh
   uv run devkit spec new <slug>
   ```

   이 명령은 뼈대 `spec.md`, `plan.md`, `tasks.md`를 담은 `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`를 만들어 `sdd-spec-feature`에 연결하고, `[NEXT_CMD: uv run devkit workflow next --unit <dir>]`로 끝납니다
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)).
6. **의도 기록.** 사용자의 명시적 지시로 `plan-intent`를 기록합니다.
7. **다음 단계 진행.** `devkit workflow next --unit <dir>`를 실행하고 안내되는 단계, 미충족 검사, 지정된 스킬을 따릅니다
   ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

## 다른 경로

| 분류 | 진행 방식 |
| --- | --- |
| 개발 방식이 `incubation` | SDD 라우팅을 하지 않습니다. 에이전트는 프로젝트의 인큐베이션 지침과 독립적인 문서·프로젝트 검사를 따르며, 유닛을 만들지 않고 깊이도 정하지 않습니다. [아이디어 인큐베이션하기](incubate-an-idea.md)를 참고하십시오. 이미 SDD에 연결된 유닛은 자신의 검사를 유지합니다. |
| `session` 깊이 | 대화로 의도를 합의하고 에이전트가 직접 `sdd-session-<task-kind>`를 따르며, 유닛, 엔벨로프, 게이트 기록, reconcile 문서를 쓰지 않습니다. |
| `proposal` 깊이 | `devkit spec proposal new <slug>`로 `docs/proposals/PROP-<slug>/proposal.md` 초안을 만들고, [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)로 이어집니다. |
| 지금 시작하지 않거나 규모가 너무 큰 경우 | Backlog에 하나 이상의 제안 초안으로 보관하고, 필요하면 마일스톤에 넣으며, `decomposed_from` 또는 `supersedes`로 출처를 보존합니다. 둘 이상의 스펙이나 다른 `task-kind`가 필요한 작업은 `size: XL`이며 `plan-intent` 전에 분할합니다. |
| `overall-refactor` | 동작을 추가하지 않고 여러 영역을 재구성하는 경우로, 유닛, 제안, 번들 없이 `direct` 모드의 `sdd-overall-refactor`를 따릅니다. |
| 계약에 대한 결함 | `devkit spec new <slug> --workflow sdd-spec-bugfix`: `spec.md`만 생성되며, 재현이 기록될 때까지 `reproduce` 단계가 열려 있습니다. |
| "다음에 뭘 하지?"만 묻는 경우 | `spec-next`가 적격 대기 초안을 추천합니다(선행 조건, 마일스톤, 우선순위, 크기 기준). `needs_decompose`와 `XL` 초안은 `decomposer` 역할을 통한 Backlog 분할 작업으로 보고되며, 승인은 사용자에게 남습니다. |

## 작업 의도 승인

`plan-intent` 정책이 `ask`(기본값)이고 목표, 범위, 검증, 종류, 깊이 중 미정인 것이 있으면 `devkit workflow next`가 `[WAITING: human gate:plan-intent]`를 출력합니다. 에이전트는 사용자에게 묻고, 답을 받은 후에만 기록합니다.

```sh
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action decline --by user --note "<reason>"
```

`auto`에서는 게이트가 정책으로 통과하며, 에이전트는 이를 사용자의 동의가 아니라 정책으로 보고합니다. 거절하면 작업이 종료됩니다.

## 문제가 생겼을 때

- **플레이북이 일치하는 경우:** 에이전트가 분류와 함께 한 줄로 안내하고 기다립니다. 확인하면 실행하고, 거절하면 이번 대화에서 다시 제안하지 않습니다. 이어지는 작업과 후속 요청에서는 검색하지 않습니다.
- **`devkit spec new` 또는 `devkit spec proposal new`가 `SPEC_LIFECYCLE_INACTIVE`를 반환하는 경우:** 개발 방식이 인큐베이션이어서 SDD 유닛을 만들 수 없으며, 아무것도 쓰이지 않습니다. SDD로 전환하는 것은 사용자의 명시적 결정이며 [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)에서 설명합니다.
- **`DEVELOPMENT_CONFIG_INVALID`:** `[development]` 테이블에 알 수 없는 키나 값이 있습니다. `.devkit/config.toml`을 고칠 때까지 정책에 의존하는 명령이 거부됩니다.
- **`devkit spec policy`가 `SPEC_CONFIG_INVALID`를 반환하는 경우:** `[tool.spec]` 키를 알 수 없거나 게이트 정책이 `ask`나 `auto`가 아닙니다(예: `plan-intent = "off"`). `.devkit/config.toml`을 고칠 때까지 에이전트는 정책에 의존하는 작업을 멈춥니다.
- **`SPEC_WRONG_BRANCH`:** 체크아웃이 `dev-<slug>`에 있지 않아 아무것도 쓰이지 않았습니다. 그 브랜치를 시작하거나 이어서 `devkit spec new`를 다시 실행하십시오.
- **`SPEC_EXISTS`:** 다른 문서, 제안, 번들이 이미 그 slug를 쓰고 있습니다(`[TARGET]`에 표시). 다른 slug를 고르십시오.
- **워크트리가 필요한 경우:** `worktree=required`이거나, `auto`에서 체크아웃에 무관한 변경이나 다른 작업이 있으면 에이전트가 별도 워크트리에서 `dev-<slug>`를 시작합니다
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
- **세션 작업에 계약 변경이 필요해진 경우:** 에이전트가 깊이를 `spec`으로 올리고(`depth_escalation=auto`면 스스로, `ask`면 사용자 확인 후), 같은 위치의 `dev-<slug>`에 스펙 유닛을 추가하며 지금까지의 작업을 유지합니다. 깊이가 저절로 낮아지는 일은 없습니다.

## 최종 결과

작업마다 하나의 워크플로가 있고, 유닛 또는 세션의 경우 대화로 식별됩니다. 기록되는 모든 승인은 사용자의 지시, 명시적 답변, `auto` 정책 중 하나에서 오며, 거부된 `devkit spec new`는 워크스페이스를 바꾸지 않습니다.
