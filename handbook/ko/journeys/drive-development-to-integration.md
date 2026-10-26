---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-project-policy: null
  CAP-DLV-workflow-envelopes: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
title: 개발부터 통합까지 진행하기
translated_from: en/journeys/drive-development-to-integration.md@b0bc4c52f4bf70f3
---

# 개발부터 통합까지 진행하기

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
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

의도가 합의되었고 작업용 브랜치도 있습니다. 이 여정은 에이전트가 구현에서 시작해 리뷰, Living Spec 갱신, 검증을
거쳐 변경이 기본 브랜치에 들어가는 순간까지를 따라갑니다. 사용자인 여러분의 몫은 작지만 결정적입니다. 기본
정책에서는 여러분이 대화에서 승인하기 전까지 아무것도 통합되지 않습니다.

유스케이스는
[`UC-drive-development-to-integration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-drive-development-to-integration.md) (영어 원문)입니다.
이 여정은 [개발 의도 라우팅하기](route-development-intent.md)나
[제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md) 다음에 시작합니다. 워크플로(workflow), 단계(stage),
게이트(gate), 엔벨로프(envelope), 워크트리는 [개념](../concepts.md)에서 설명합니다.

## 출발점

스펙 유닛(Unit)이 작업 워크트리(task worktree)나 현재 체크아웃에서 자신의 `dev-<slug>` 활동 브랜치에 있습니다.
아래 안내는 기본값을 사용합니다. `activity-effort`는 `medium`, 모드는 `direct`, `dev-integration` 정책은 `ask`,
경로는 로컬입니다.

## 1. 워크플로에 현재 위치 묻기

```bash
uv run devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>
```

에이전트는 노력 수준과 그 이유를 밝힌 뒤, `next`가 보고하는 현재 단계, 충족되지 않은 검사, 실행할 스킬을
따릅니다. 각 워크플로의 단계 순서는 그 정의에만 있습니다(`devkit workflow show <id>`).
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)를
참고하십시오.

## 2. 명세, 구현, 검증

에이전트는 `spec.md`, `plan.md`, `tasks.md`를 작성하고, 각 태스크를 그 `_Boundary:` 범위 안에서 구현하며, 영향받는
테스트를 실행하고, 단계 경계마다 커밋합니다.

## 3. 리뷰

먼저 `code-reviewer`가 요구 사항과 검사 결과에 비추어 diff를 검토합니다. 에이전트는 결과를 리뷰 엔벨로프로
기록하고, 수정하고, 수정 사항을 검증한 다음 reverify 엔벨로프로 라운드를 닫습니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

리뷰를 얼마나 수행할지는 노력 수준에 달려 있습니다.

| 노력 수준 | 코드 리뷰 | reconcile 검증 |
| --- | --- | --- |
| `low` | 작성자가 직접 리뷰하되, 엔벨로프로 기록 | 자체 점검, 기록 |
| `medium` | 최초 `code-reviewer` 1회 | 독립된 `reconcile-reviewer`, 또는 영향받는 계약이 모두 식별되고 컴포넌트 간 영향이 남지 않았다면 기록된 자체 점검 |
| `high` | 한 라운드에서 아무것도 찾지 못하거나 사소한 수정만 남을 때까지, 횟수 제한 안에서 새 리뷰어로 라운드 반복 | 같은 제한 반복 |

## 4. Living Spec 갱신

에이전트는 변경 내용을 `docs/`에 반영하고 `reconcile.md`를 작성합니다. reconcile 검증은 `reconcile-check`
엔벨로프로 기록됩니다. 그런 다음 reconcile을 해결(resolve)하고 스펙을 완료로 표시합니다.

## 5. 피드백 정리와 보고

에이전트는 도구와 에셋에 대한 관찰을 기록한 다음, 테스트, 빌드, 린트 결과를 담은 최종 변경 보고서를 작성합니다.

## 6. 기본 브랜치 반영

에이전트는 앞으로 나아간 기본 브랜치를 작업 브랜치에 병합하고, 충돌 해결과 문서 반영으로 바뀐 부분만 다시
검증하며, reconcile 대상을 재확인하고 누적 검사(`devkit rules check --ci --base <ref>`)를 실행합니다.

## 7. 승인

에이전트는 `uv run devkit spec policy`로 유효한 정책을 읽고
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)),
통합을 준비합니다.

```bash
uv run devkit integration prepare dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local
```

검증된 보고서와 정확한 병합 및 정리 효과를 여러분에게 보여 줍니다. 여러분은 대화에서 승인합니다. 그때에야 다음을
실행합니다.

```bash
uv run devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> \
  --route local --expected-digest <request.digest>
```

다이제스트(digest)는 여러분이 본 범위를 고정합니다. 이는 동시성 검사일 뿐 승인의 증명이 아닙니다. 명령은 여러분의
대화를 인증할 수 없으므로, 에이전트는 여러분의 결정 없이 이 명령을 실행하지 않습니다
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)).

## 8. 통합 완료

devkit은 기본 체크아웃 바깥에서 병합 커밋을 만들고, fetch나 push 없이 기본 브랜치를 그 커밋으로 fast-forward하며,
작업 워크트리를 제거하고, 정책에 따라 로컬 브랜치를 삭제하고, 범위가 정해진 정리를 실행합니다
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
이제 기본 브랜치에는 `chore(merge): integrate dev-<slug> into <base>`가 있습니다. 에이전트는 이후
`devkit workflow next` 호출에 `--given dev-integration`을 넘기고, 결과를 그 권한 근거와 함께 보고합니다.

## 변형

- **세션 깊이.** 작은 태스크에는 스펙, 엔벨로프, reconcile 문서가 없습니다. 그래도 에이전트는 테스트와 리뷰를 하고,
  커밋하며, 최종 응답이나 PR 본문에 변경, 노력 수준, 리뷰, 검증을 보고합니다.
- **로컬 오케스트레이션 모드.** 여러분이 지시하면 `development-worker`가 자체 워크트리에서 그 턴을 실행합니다.
  에이전트는 반환된 범위를 `uv run devkit spec worker inspect`로 살펴보며, 거부한 범위는 유닛을 막는 문제(problem)가
  됩니다.
- **정책 `auto`.** 공유 기본 설정이 `dev-integration = "auto"`이면, 리뷰, reconcile, 검사가 충족될 때 게이트가
  정책에 따라 통과하며 보고서에는 `authority: policy`가 표시됩니다.
- **필수 풀 리퀘스트.** `[worktree] pull_request = "required"`에서는 로컬 경로가 `WORKTREE_PR_POLICY`로 거부됩니다.
  에이전트는 `--route pull-request`를 사용하며, 필수 검사와 리뷰가 통과하면 병합됩니다.

선택 사항인 MCP 런타임은 이 경로에 포함되지 않습니다. 수명 주기 작업은 CLI로 실행되고, 런타임은 공유
아티팩트(shared artifact)만 제공합니다
([`CAP-MCP-runtime-registration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/mcp/CAP-MCP-runtime-registration.md) (영어 원문)).

## 문제가 생겼을 때

| 보이는 상황 | 해야 할 일 |
| --- | --- |
| 변경에 반대함 | 아무것도 통합되지 않습니다. 에이전트는 `devkit workflow return --unit <dir> --to review-refine --note "..."`로 되돌아갑니다. |
| `INTEGRATION_AUTHORITY_REQUIRED` 또는 `INTEGRATION_REQUEST_STALE` | 다이제스트가 없거나 범위가 바뀌었습니다. 다시 준비하고 현재 범위를 승인하십시오. |
| `INTEGRATION_TARGET_MOVED` | 결과를 만든 뒤 기본 브랜치가 움직였고, 바뀐 것은 없습니다. 기본 브랜치를 작업 브랜치에 병합하고 새 통합을 요청하십시오. |
| `WORKTREE_BLOCKED` | 유닛에 해결되지 않은 문제나 답하지 않은 질문이 있습니다. [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)를 참고하십시오. |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | CLI가 제거하려는 워크트리 안에서 실행되고 있습니다. 그 바깥의 런타임을 사용한 다음 다시 준비하고 승인하십시오. |
| `INTEGRATION_RECEIPT_READER_CHANGED` | 브랜치가 자기 설치 기록(receipt)이 의존하는 설치 기록 리더를 바꿉니다. 바뀐 것은 없으며, 재시도 전에 불일치를 해결하십시오. |
| 병합 후 정리 단계가 미완료로 남음 | `devkit worktree status`와 Git을 살펴보십시오. 표시된 브랜치가 남아 있는 동안 `devkit worktree finish <branch> --merge --local-only`를 다시 실행하거나, `devkit spec proposal prune <slug>` 같은 담당 명령을 실행합니다. 병합은 반복되지 않습니다. |
| 결과를 알 수 없음 | 먼저 Git, 워크트리, 풀 리퀘스트 상태를 살펴보고, 검증할 수 있는 남은 효과만 실행하십시오. |
| 재시도 한도를 넘었거나 도구가 실패함 | 에이전트는 원인과 증거를 갖고 `exception` 단계로 들어가며, 한도를 우회하려고 새 태스크를 만들지 않습니다. |

통합 코드의 전체 목록은 `CAP-INT-mcp-services`에 있습니다. 영역: [Delivery](../areas/delivery.md),
[Integration](../areas/integration.md), [Worktree](../areas/worktree.md).
