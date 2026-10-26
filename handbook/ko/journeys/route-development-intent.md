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

대부분의 개발 작업은 이 여정에서 출발합니다. 사용자가 원하는 요구 사항을 에이전트에 전달하면(`/spec <intent>` 또는 일반적인 개발 요청), 에이전트는 작업 의도를 먼저 상호 합의한 후 해당 요청을 정확히 하나의 전달 워크플로에 배정합니다. 사전에 결정할 사항이 없는 단순한 작업은 가볍게 세션으로 진행되고, 규격 계약이 변경되는 작업은 정식 스펙 번들을 생성하며, 탐색과 검토가 더 필요한 작업은 제안(proposal)으로 전환됩니다. 사용자가 승인해야 할 모든 사항은 임의로 예단하지 않고 적절한 시점에 명시적으로 확인을 구합니다.

워크플로, 단계, 게이트 및 세 가지 분류 축에 대한 자세한 내용은 [개념](../concepts.md)과 [전달 영역](../areas/delivery.md)을 참고하십시오.

출처: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-route-development-intent.md) (영어 원문).

## 시작하기 전에

`devkit-spec` 패키지가 설치되어 있고 `spec` 번들이 동기화되어 있어야 합니다. 에이전트는 개발 작업을 시작하기에 앞서 각 에이전트 컨텍스트마다 한 번씩 스펙 헌장을 로드합니다(`uv run devkit get-context spec`).

## 단계별 진행

가장 일반적인 경로는 `direct` 모드의 `spec` 깊이 `feature` 개발입니다.

1. **요청 접수.** 에이전트가 사용자의 요청을 받아 `spec` 스킬을 실행하고 제한된 범위의 플레이북 검색을 1회 수행합니다(`devkit playbook search "<query>" --limit 3 --max-bytes 4096`). 요청된 작업과 일치하는 플레이북이 없으면 별도의 알림 없이 조용히 다음 단계로 넘어갑니다(`ADR-spec-intake-playbook-discovery`).
2. **정책 확인.** 적용 중인 프로젝트 정책을 확인합니다.

   ```sh
   uv run devkit spec policy
   ```

   출력 결과에는 `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]` 및 게이트별 `[GATE_POLICY: ...]` 센티널이 포함됩니다
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)).
3. **작업 분류.** 요청을 작업 종류(`task-kind`: `feature` 또는 `bugfix`), 계획 깊이(`planning-depth`: `session`, `spec`, `proposal` 중 하나이며, 작업 크기가 아니라 구현 전 사전 결정 필요 여부 기준), 작업 모드 및 활동 노력 수준(`activity-effort`) 순으로 분류한 뒤 그 결과를 사용자에게 보고합니다
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
4. **브랜치 생성.** Git 정책에 따라 현재 체크아웃 디렉터리(`devkit worktree start dev-<slug> --no-worktree`) 또는 별도의 독립 작업 워크트리에서 `dev-<slug>` 브랜치를 시작합니다.
5. **스펙 번들 생성.** 새로운 스펙 번들을 초기화합니다.

   ```sh
   uv run devkit spec new <slug>
   ```

   이 명령은 뼈대 구조를 갖춘 `spec.md`, `plan.md`, `tasks.md` 파일을 포함하는 `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` 디렉터리를 생성하여 `sdd-spec-feature` 워크플로에 연결하며, `[NEXT_CMD: devkit workflow next --unit <dir>]` 센티널로 종료됩니다
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
6. **의도 기록.** 사용자의 명시적 지시를 바탕으로 `plan-intent`를 기록합니다.
7. **다음 단계 진행.** `devkit workflow next --unit <dir>`를 실행하여 안내되는 단계와 미충족 검사 항목, 담당 스킬 지침을 따릅니다
   ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## 다른 경로

| 분류 | 진행 방식 |
| --- | --- |
| `session` 깊이 | 대화를 통해 의도를 합의한 후 에이전트가 직접 `sdd-session-<task-kind>`를 진행합니다. 유닛, 엔벨로프, 게이트 기록, 동기화(reconcile) 문서는 작성하지 않습니다. |
| `proposal` 깊이 | `devkit spec proposal new <slug>`로 `docs/proposals/PROP-<slug>/proposal.md` 초안을 작성하며, [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md) 여정으로 이어집니다. |
| 지금 시작하지 않거나 규모가 너무 큰 경우 | 백로그(Backlog)에 하나 이상의 제안서 초안으로 보관하며, 필요 시 마일스톤에 할당합니다. `decomposed_from`이나 `supersedes` 속성으로 원본 출처를 보존합니다. |
| `overall-refactor` | 새로운 기능을 추가하지 않고 여러 영역의 구조를 개편하는 경우로, 유닛, 제안, 번들 생성 없이 `direct` 모드의 `sdd-overall-refactor` 워크플로를 따릅니다. |
| 기존 계약에 대한 결함 수정 | `devkit spec new <slug> --workflow sdd-spec-bugfix`로 시작합니다. `spec.md`만 생성되며, 버그 재현 단계(`reproduce`)가 기록될 때까지 다음 단계가 열리지 않습니다. |
| 단순 현황 문의("다음에 뭘 하지?") | `spec-next`가 대기열에서 적격 초안(선행 조건, 마일스톤, 우선순위, 규모 기준)을 추천하며, 최종 착수 승인은 사용자가 직접 결정합니다. |

## 작업 의도 승인

기본 정책인 `plan-intent = "ask"` 환경에서는 목표, 범위, 검증 기준, 작업 종류, 계획 깊이 중 미결정 항목이 남아 있는 경우 `devkit workflow next`가 `[WAITING: human gate:plan-intent]`를 출력합니다. 에이전트는 사용자에게 확인을 요청하며, 사용자의 응답을 받은 후에만 결정을 기록합니다:

```sh
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action decline --by user --note "<reason>"
```

정책이 `auto`로 설정된 경우 게이트는 규정에 따라 자동 통과하며, 에이전트는 이를 사용자의 직접 승인이 아니라 시스템 정책에 의한 통과로 보고합니다. 사용자가 거절(`decline`)을 선택하면 작업은 즉시 종료됩니다.

## 문제가 생겼을 때

- **플레이북이 일치하는 경우:** 에이전트가 작업 분류와 함께 일치하는 플레이북을 한 줄로 안내하고 확인을 대기합니다. 사용자가 승인하면 해당 플레이북이 실행되며, 거절하면 이번 대화 세션에서는 동일한 플레이북이 다시 제안되지 않습니다. 작업 지속 및 후속 단계에서는 플레이북 검색을 재수행하지 않습니다.
- **`devkit spec policy` 실행 시 `SPEC_CONFIG_INVALID` 오류가 발생하는 경우:** `[tool.spec]`에 알 수 없는 키가 존재하거나 게이트 정책이 `ask` 또는 `auto`가 아닌 경우입니다(예: `plan-intent = "off"`). 사용자가 `.devkit/config.toml`을 수정할 때까지 에이전트는 정책에 의존하는 작업을 일시 중단합니다.
- **`SPEC_WRONG_BRANCH` 오류가 발생하는 경우:** 작업 체크아웃이 `dev-<slug>` 브랜치에 위치하지 않아 파일이 생성되지 않은 상태입니다. 해당 브랜치로 전환하거나 새로 시작한 후 `devkit spec new`를 다시 실행하십시오.
- **`SPEC_EXISTS` 오류가 발생하는 경우:** 다른 문서, 제안서 또는 스펙 번들에서 이미 동일한 식별자(slug)를 사용 중입니다(`[TARGET]`에 목록 안내). 다른 slug를 선택하십시오.
- **작업 워크트리가 요구되는 경우:** 정책이 `worktree=required`로 설정되어 있거나, `auto` 설정 상태에서 체크아웃에 관련 없는 변경 사항 또는 다른 작업이 진행 중인 경우, 에이전트는 독립된 작업 워크트리에서 `dev-<slug>` 브랜치를 생성합니다
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
- **세션 작업 진행 중 계약 변경이 필요한 것으로 밝혀진 경우:** 에이전트는 계획 깊이를 `spec`으로 상향 조정합니다(`depth_escalation=auto` 설정 시 자체 승격, `ask` 설정 시 사용자 확인 후 승격). 동일한 위치의 `dev-<slug>` 브랜치에 스펙 유닛을 추가하며 지금까지 진행한 작업 내용은 안전하게 유지됩니다. 계획 깊이가 자동으로 하향 조정되는 경우는 없습니다.

## 최종 결과

각 작업마다 고유한 작업 단위(유닛) 또는 세션 대화에 의해 식별되는 정확히 하나의 전달 워크플로가 배정됩니다. 시스템에 기록되는 모든 승인은 사용자의 명시적 지시, 확인 응답 또는 사전 정의된 `auto` 정책에 기반하며, 거부된 `devkit spec new` 명령은 워크스페이스에 어떠한 임의의 변경도 남기지 않습니다.
