---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-workflow-envelopes: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-handle-delivery-problems-and-exceptions: null
title: 전달 문제와 예외 처리하기
translated_from: en/journeys/handle-delivery-problems-and-exceptions.md@8c658d5762921c08
---

# 전달 문제와 예외 처리하기

<!-- handbook:provenance -->
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

개발 과정에서는 다양한 장애물을 마주하게 됩니다. 그러나 그 대부분은 시스템 수준의 '문제(problem)'가 아닙니다.
두 가지 유효한 대안 중 하나의 설계 선택이거나, 나중에 처리해도 무방한 개선 사항에 불과합니다. devkit이 규정하는
문제(problem)란 사전에 합의된 목표, 구현 범위, 또는 아키텍처 계약을 변경하지 않고는 해결할 수 없는 장애물을 뜻합니다.
이 여정에서는 에이전트가 일반 장애물과 문제를 어떻게 식별하는지, 문제가 발생했을 때 어떻게 작업을 보류하여 결함이 있는
코드가 기본 브랜치에 통합되지 않도록 방지하는지, 그리고 작업을 어떻게 안전하게 복구하거나 정상 종료하는지 살펴봅니다.

유스케이스는
[`UC-handle-delivery-problems-and-exceptions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md) (영어 원문)입니다.
엔벨로프(envelope), 유닛(Unit), `exception` 단계 등의 개념은 [개념](../concepts.md)에서 설명합니다.

## 1. 문제(Problem) 여부 판단

작업 실행자(워커 또는 에이전트 자신)는 마주한 장애물을 기 합의된 명세와 대조하여 분류합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)):

| 장애물 유형 | 실행자의 조치 |
| --- | --- |
| 합의된 의도 범위 내의 설계 선택 | 권장되는 최선의 선택지를 채택하고 그 사유를 `plan.md`, 엔벨로프의 가정 사항(`assumptions`), 또는 최종 보고서에 명시합니다. 작업은 계속 진행됩니다. |
| 현재 작업을 차단하지 않는 개선 사항 | 피드백 레코드나 후속 초안 제안(draft proposal)으로 등록합니다. 작업은 중단 없이 계속 진행됩니다. |
| `session` 태스크의 차단 문제 | 대화창에서 사용자에게 즉시 보고하고, 별도 영구 기록을 남기지 않으며 기본 브랜치에 통합하지 않습니다. |
| 스펙 유닛(Unit)의 차단 문제 | 아래 절차에 따라 문제 레코드를 정식으로 기록하고 작업을 보류합니다. |

## 2. 문제 엔벨로프 기록

실행자는 발생 원인, 시도했던 해결 방안, 권장 복구 계획을 명시하여 해당 실행에 대한 `worker` 엔벨로프를 작성합니다.

```bash
uv run devkit workflow envelope worker --unit <dir> --stage <stage> --effort <effort>   --problem "<cause>" --tried "<attempt>" --recovery "<recommended recovery>"
```

미완료된 작업 상태와 작성한 엔벨로프를 함께 작업 브랜치에 커밋하고, 기본 브랜치로 통합하지 않은 채 해당 실행 턴을 안전하게 종료합니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

## 3. 유닛의 보류(Hold) 상태 전환

문제가 정식으로 해결(`resolution`)되기 전까지는 다음과 같은 보호 메커니즘이 작동합니다.

- 프로젝트 정책이나 `--given` 플래그 설정과 관계없이, 문제가 발생한 단계 이후의 모든 승인 게이트(gate)는 통과할 수 없습니다.
- 다른 워커나 프로세스로의 핸드오프가 거부됩니다.
- `devkit worktree finish --merge` 명령어가 `WORKTREE_BLOCKED` 에러를 발생시키며 브랜치 병합을 엄격히 거부합니다.

현재의 보류 상태는 다음 명령어로 상세히 확인할 수 있습니다.

```bash
uv run devkit workflow envelope check --unit <dir>
```

미해결 문제마다 `[BLOCKED: ...]` 라인이 출력되고, 미답변 질문마다 `[PENDING_QUESTION: ...]` 라인이 출력됩니다.

## 4. 원인 해결 및 해결(Resolution) 엔벨로프 작성

에이전트는 승인된 범위 내에서 최선의 복구 방안을 결정합니다. 근본 원인을 직접 수정하거나, 필요한 경우 변경 사항을 안전하게 되돌립니다.
수정을 완료하면 문제가 보고되었던 `worker` 엔벨로프를 지정한 `resolution` 엔벨로프를 작성하고 변경 사항과 함께 커밋합니다.

```bash
uv run devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml --summary "<what fixed it>"
```

`resolution` 엔벨로프는 실제로 원인을 해결한 주체가 수정 코드와 동일한 커밋에 직접 작성해야 합니다. 에이전트가 복구 작업을
새로운 워커 서브에이전트에게 위임한 경우, 해당 워커가 이 엔벨로프를 작성합니다.

## 5. 작업 재개 및 워크플로 진행

`devkit workflow envelope check` 실행 결과 더 이상 `[BLOCKED]` 라인이 출력되지 않으면, 워크플로는 유닛이 중단되었던 단계부터
정상 재개됩니다. 문제 발생 이전에 이미 통과했던 게이트 상태는 그대로 유효하게 유지됩니다.

## 복구가 불가능한 경우의 예외 처리

- **수정 시도가 원인을 해소하지 못한 경우:** `resolution` 엔벨로프를 임의로 작성하지 않으며, 문제는 미해결 상태로 유지되고 유닛의
  보류도 지속됩니다. 에이전트는 다른 복구 방안을 시도하거나 차단 요인을 사용자에게 보고합니다.
- **복구를 위해 목표나 범위의 재합의가 필요한 경우:** 시스템 목표, 구현 범위, 또는 계약 자체를 수정해야 하거나 기존 방향의
  실현이 불가능하다고 판단되면, 사용자가 후속 조치를 결정합니다. 새로운 초안 제안으로의 깊이 상향(depth escalation), 기존 제안의
  대체(supersede), 또는 작업 포기(abandon) 중 하나를 선택합니다. 이러한 종료 결정은 Backlog 작업으로 기본 브랜치에 커밋됩니다.
  이후 에이전트는 열려 있는 풀 리퀘스트와 원격 브랜치를 정리하고, 미병합 브랜치를 안전하게 폐기합니다.

  ```bash
  uv run devkit worktree finish dev-<slug> --discard
  ```

  명령어 실행 결과로 `merged=no discarded=yes`가 확인됩니다. 작업 트리에 커밋되지 않은 변경 사항이 남아 있는 경우 워크트리를
  임의로 삭제하지 않습니다 (`WORKTREE_DIRTY`)
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문),
  [`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)).
- **엔벨로프 기록 자체를 작성할 수 없는 환경적 장애:** 호스트 환경 권한 등으로 인해 엔벨로프 작성이나 비상 커밋이 거부되는 경우,
  워커는 원인, 시도한 명령어 내역, 실제 마지막 커밋, 변경된 경로, 누락된 기록 항목을 정직하게 담아 `failed` 상태로 반환하며
  결과를 꾸며내지 않습니다. 메인 에이전트는 이 반환을 보류 상태로 취급하고 자체적으로 복구 절차를 직접 수행합니다.

## 예외(Exception) 단계 진입

에이전트가 자율적으로 해결할 수 없는 장애가 발생할 수 있습니다. 예를 들어 자동 재시도 한도 초과, 외부 도구 실행 장애, 자동 해결이
불가능한 의미적 충돌 등이 이에 해당합니다. 이때 워크플로는 구체적 원인과 증거 데이터를 첨부하여 `exception` 단계로 공식 진입합니다.
이 단계는 사용자가 원인을 검토하고 개입 조치를 취할 때까지(`exception-handled`) 유지되며, 조치가 완료되면 예외를 유발했던 본래
단계로 안전하게 복귀합니다. 에이전트가 재시도 한도를 회피하기 위해 임의로 신규 태스크를 생성하는 일은 허용되지 않습니다.

## 문제 발생 시 마주치는 오류 코드

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `WORKTREE_BLOCKED` | 브랜치 병합이 거부되었습니다. 미해결 문제나 미답변 질문마다 구체적인 상세 정보가 출력됩니다. | 문제를 해결하거나 질문에 답변한 후 병합을 다시 시도하십시오. |
| `ENVELOPE_REFERENCE_INVALID` | `resolution` 엔벨로프가 문제가 등록되지 않은 일반 `worker` 엔벨로프를 참조하고 있습니다. | 실제 문제가 기록되어 있는 올바른 엔벨로프 파일을 지정하십시오. 거부 메시지에 문제를 담은 `worker` 엔벨로프가 모두 나열됩니다. |
| `HANDOFF_HELD` | 현재 보류 상태인 유닛은 다른 에이전트나 단계로 핸드오프할 수 없습니다. | 먼저 보류 원인을 해결하십시오. |
| `WORKTREE_DIRTY` | 작업 워크트리에 커밋되지 않았거나 추적되지 않는(untracked) 변경 파일이 남아 있습니다. | 변경 사항을 커밋하거나 외부로 백업한 후 다시 discard 명령을 실행하십시오. |

어떠한 예외 상황에서도, 미해결된 문제는 기본 브랜치로 절대 병합되지 않으므로 기본 브랜치의 무결성이 완벽히 보호됩니다. 실패한 코드 범위,
미해결 지적 사항, 시도했던 복구 내역은 작업 브랜치 Git 이력에 온전히 보존되며, 사용자의 명시적 결정 없이는 아무것도 삭제되지 않습니다.
관련 영역: [전달](../areas/delivery.md), [워크트리](../areas/worktree.md).
