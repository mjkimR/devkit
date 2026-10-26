---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-workflow-envelopes: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-handle-delivery-problems-and-exceptions: null
title: 전달 문제와 예외 처리하기
translated_from: en/journeys/handle-delivery-problems-and-exceptions.md@7298a26e6886207a
---

# 전달 문제와 예외 처리하기

<!-- handbook:provenance -->
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
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

작업은 장애물을 만납니다. 대부분은 문제가 아닙니다. 유효한 두 선택지 사이의 선택이거나, 미뤄도 되는 개선입니다.
devkit에서 말하는 문제(problem)는 합의된 목표, 범위, 계약을 바꾸지 않고는 해결할 수 없는 장애물입니다. 이 여정은
에이전트가 둘을 어떻게 구별하는지, 문제가 어떻게 작업을 붙잡아 망가진 것이 통합되지 않게 하는지, 그리고 작업이
어떻게 회복하거나 깔끔하게 종료되는지 보여 줍니다.

유스케이스는
[`UC-handle-delivery-problems-and-exceptions`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md) (영어 원문)입니다.
엔벨로프(envelope), 유닛(Unit), `exception` 단계는 [개념](../concepts.md)에서 설명합니다.

## 1. 문제인가?

실행자(워커 또는 에이전트 자신)는 장애물을 합의 내용과 대조합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

| 장애물이 | 실행자는 |
| --- | --- |
| 합의된 의도 안의 선택 | 권장 선택지를 택하고, 이유를 `plan.md`, 엔벨로프의 가정, 또는 최종 보고서에 기록합니다. 작업은 계속됩니다. |
| 작업을 막지 않는 개선 | 피드백이나 후속 초안 제안으로 기록합니다. 작업은 계속됩니다. |
| `session` 태스크의 문제 | 대화에서 보고하고, 기록을 남기지 않으며, 통합하지 않습니다. |
| 유닛의 문제 | 아래와 같이 기록합니다. |

## 2. 문제 기록

실행자는 원인, 시도한 내용, 권장 회복 방법을 담아 그 실행의 `worker` 엔벨로프를 씁니다.

```bash
uv run devkit workflow envelope worker --unit <dir> --stage <stage> --effort <effort> \
  --problem "<cause>" --tried "<attempt>" --recovery "<recommended recovery>"
```

마무리하지 못한 작업을 엔벨로프와 함께 커밋하고, 통합하지 않은 채 실행을 끝냅니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

## 3. 유닛이 보류됨

문제가 해결(resolution)되지 않은 동안에는 다음과 같습니다.

- 정책이나 `--given`이 무엇이든, 문제가 생긴 단계 이후의 게이트(gate)는 통과하지 않습니다.
- 핸드오프가 거부됩니다.
- `devkit worktree finish --merge`가 `WORKTREE_BLOCKED`로 브랜치를 거부합니다.

보류 상태는 다음과 같이 확인할 수 있습니다.

```bash
uv run devkit workflow envelope check --unit <dir>
```

열린 문제마다 `[BLOCKED: ...]` 줄을, 답하지 않은 질문마다 `[PENDING_QUESTION: ...]` 줄을 출력합니다.

## 4. 원인 수정과 해결

에이전트는 승인된 범위 안에서 회복 방법을 정합니다. 근본 원인을 직접 고치거나 되돌립니다. 그리고 문제의 `worker`
엔벨로프를 지정한 `resolution` 엔벨로프와 함께 수정 사항을 커밋합니다.

```bash
uv run devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml --summary "<what fixed it>"
```

resolution은 실제로 원인을 고친 쪽이 수정과 같은 커밋에 씁니다. 에이전트가 회복을 새 워커에게 넘기면 그 워커가
씁니다.

## 5. 계속 진행

`devkit workflow envelope check`가 `[BLOCKED]` 줄을 보고하지 않으면, 워크플로는 유닛이 멈췄던 단계에서 이어집니다.
문제 이전에 통과한 게이트는 통과 상태를 유지합니다.

## 회복이 통하지 않을 때

- **수정이 원인을 해결하지 못함.** resolution을 쓰지 않으므로 문제는 열린 채로, 유닛은 보류된 채로 남습니다.
  에이전트는 다른 해결책을 시도하거나 차단 요인을 보고합니다.
- **회복에 다른 합의가 필요함.** 목표, 범위, 계약을 바꿔야 하거나 방향이 실현 불가능하면, 종료 방식은 여러분이
  정합니다. 새 초안으로의 깊이 상향(depth escalation), 대체(supersede), 포기(abandon) 중 하나입니다. 종료 결정은
  Backlog 작업으로 기본 브랜치에 커밋됩니다. 에이전트는 풀 리퀘스트와 원격 브랜치를 닫고, 병합되지 않은 브랜치를
  버립니다.

  ```bash
  uv run devkit worktree finish dev-<slug> --discard
  ```

  결과에는 `merged=no discarded=yes`가 표시됩니다. 커밋되지 않은 변경이 있는 워크트리는 제거하지 않습니다
  (`WORKTREE_DIRTY`)
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문),
  [`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
- **기록 자체를 쓸 수 없음.** 호스트가 엔벨로프나 비상 커밋을 거부하면, 워커는 원인, 시도한 명령, 실제 마지막 커밋,
  변경된 경로, 누락된 기록을 담아 `failed`를 반환하며, 결과를 지어내지 않습니다. 에이전트는 그 반환을 보류로 취급하고
  회복을 직접 실행합니다.

## exception 단계

에이전트 혼자 처리할 수 없는 실패도 있습니다. 재시도 한도 초과, 도구나 실행 실패, 해결되지 않은 의미 충돌 등입니다.
이때 워크플로는 원인과 증거를 갖고 `exception`에 들어갑니다. 이 단계는 여러분이 원인을 처리할 때까지
(`exception-handled`) 현재 단계로 남아 있다가, 그것을 일으킨 단계로 돌아갑니다. 한도를 우회하려고 새 태스크를
여는 일은 없습니다.

## 만날 수 있는 코드

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `WORKTREE_BLOCKED` | 병합이 거부되었습니다. 열린 문제나 질문마다 상세 정보가 하나씩 나옵니다. | 해결하거나 답한 다음 다시 실행하십시오. |
| `ENVELOPE_REFERENCE_INVALID` | resolution이 문제를 담지 않은 `worker` 엔벨로프를 지정했습니다. | 문제를 담은 엔벨로프를 지정하십시오. |
| `HANDOFF_HELD` | 보류된 유닛은 핸드오프할 수 없습니다. | 먼저 보류를 해결하십시오. |
| `WORKTREE_DIRTY` | 워크트리에 커밋되지 않았거나 추적되지 않는 변경이 있습니다. | 커밋하거나 밖으로 옮긴 다음 다시 버리십시오. |

어떤 일이 생기든, 해결되지 않은 문제는 기본 브랜치를 깨끗하게 지킵니다. 실패한 범위, 열린 결과, 시도한 해결책은
Git에 남고, 여러분의 결정 없이는 아무것도 삭제되지 않습니다. 영역: [Delivery](../areas/delivery.md),
[Worktree](../areas/worktree.md).
