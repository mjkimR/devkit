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
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

작업 목표(intent)가 합의되고 전용 활동 브랜치가 마련되었습니다. 이 여정은 에이전트가 기능 구현부터 코드 리뷰,
Living Spec 갱신, 검증을 거쳐 최종 변경 사항이 기본(base) 브랜치에 안전하게 병합되는 전 과정을 안내합니다.
사용자의 개입은 최소화되지만 결정적인 역할을 합니다. 기본 정책에서는 사용자가 대화창에서 직접 승인하기 전까지
어떠한 변경 사항도 기본 브랜치에 통합되지 않습니다.

유스케이스는
[`UC-drive-development-to-integration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-drive-development-to-integration.md) (영어 원문)입니다.
이 여정은 [개발 요청 라우팅하기](route-development-intent.md)나
[제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md) 단계 이후에 시작됩니다. 워크플로, 단계(stage),
게이트, 엔벨로프, 워크트리 등의 개념은 [개념](../concepts.md)에서 설명합니다.

## 출발점

스펙 유닛(Unit)이 작업 워크트리 또는 현재 체크아웃 트리의 `dev-<slug>` 활동 브랜치에 위치합니다.
아래 안내는 기본 설정을 기준으로 진행합니다 (`activity-effort`: `medium`, 실행 모드: `direct`, `dev-integration` 정책: `ask`, 통합 경로: 로컬).

## 1. 워크플로에 현재 위치 확인

```bash
uv run devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>
```

에이전트는 작업 강도(effort)와 산정 사유를 밝힌 뒤, `next` 명령어가 보고하는 현재 단계, 미충족 검사 항목, 다음에 실행할 스킬을
순서대로 따릅니다. 각 워크플로의 단계 진행 순서는 고정되어 있지 않고 개별 워크플로 정의에 명시되어 있습니다(`devkit workflow show <id>`로 확인).
자세한 내용은
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)를
참고하십시오.

## 2. 명세, 구현 및 검증

에이전트는 `spec.md`, `plan.md`, `tasks.md`를 순서대로 작성하고, 각 태스크에 지정된 `_Boundary:` 파일 범위 내에서 기능을 구현하며, 영향받는
테스트를 실행하고 각 단계 경계마다 커밋을 생성합니다.

## 3. 코드 리뷰

먼저 `code-reviewer` 서브에이전트가 요구사항 명세와 검사 결과를 바탕으로 Git diff를 엄밀히 검토합니다. 에이전트는 지적 사항을 리뷰 엔벨로프로
기록한 뒤 수정하고, 수정 사항을 검증한 다음 reverify 엔벨로프를 작성하여 해당 라운드를 마무리합니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).

리뷰 진행 범위와 심도는 작업 강도에 따라 결정됩니다.

| 작업 강도 | 코드 리뷰 | Living Spec 반영 검증 |
| --- | --- | --- |
| `low` | 작성 에이전트가 자체 리뷰 수행 (엔벨로프 기록) | 자체 점검 후 엔벨로프 기록 |
| `medium` | 독립된 `code-reviewer`를 통한 초기 리뷰 1회 | 독립된 `reconcile-reviewer` 검증, 또는 영향받는 모든 계약이 식별되고 컴포넌트 간 파급 영향이 없는 경우 기록을 동반한 자체 점검 |
| `high` | 지적 사항이 없거나 경미한 수정만 남을 때까지 새 리뷰어를 투입하여 지정된 횟수 한도 내에서 반복 검토 | 동일한 한도 내에서 반복 검증 |

## 4. Living Spec 갱신

에이전트는 변경 내용을 `docs/`의 Living Spec에 반영하고 `reconcile.md`를 작성합니다. Living Spec 반영 검증 결과는 `reconcile-check`
엔벨로프로 기록됩니다. 검증을 마치면 reconcile 상태를 해결(resolve) 처리하고 스펙을 완료(`completed`) 상태로 전환합니다.

## 5. 피드백 정리 및 최종 보고

에이전트는 개발 과정에서 사용한 도구 및 에셋에 대한 관찰 피드백을 기록한 뒤, 테스트·빌드·린트 검증 결과를 모두 포함한 최종 변경 보고서를 작성합니다.

## 6. 기본 브랜치 변경 사항 반영

에이전트는 작업 중 최신 변경 사항이 반영된 기본 브랜치를 작업 브랜치로 병합(merge)합니다. 충돌 해결 및 문서 동기화로 변경된 영역만 선별적으로
재검증하고, reconcile 대상 문서를 재확인한 뒤 누적 차분 검사(`devkit rules check --ci --base <ref>`)를 실행합니다.

## 7. 사용자 승인

에이전트는 `uv run devkit spec policy`로 현재 적용되는 프로젝트 정책을 확인하고
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)),
통합을 준비합니다.

```bash
uv run devkit integration prepare dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local
```

에이전트는 검증 완료 보고서와 함께 병합 및 워크트리 정리로 발생할 구체적인 변경 사항을 사용자에게 제시합니다. 사용자가 대화창에서 명시적으로 승인하면,
비로소 실제 통합 명령을 실행합니다.

```bash
uv run devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir>   --route local --expected-digest <request.digest>
```

다이제스트(digest)는 사용자가 확인하고 승인한 변경 범위를 확정(pin)하는 역할을 합니다. 이는 변경 범위가 중간에 바뀌지 않았는지 확인하는
동시성 검사 장치일 뿐, 그 자체로 승인을 증명하는 것은 아닙니다. CLI 명령어는 대화 세션의 승인 여부를 직접 인증할 수 없으므로,
에이전트는 사용자의 명시적인 승인 결정 없이는 이 명령을 임의로 실행하지 않습니다
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)).

## 8. 최종 통합 완료

devkit은 기본 체크아웃 바깥에서 안전하게 병합 커밋을 생성하고, 원격 통신(fetch나 push) 없이 로컬 기본 브랜치를 해당 커밋으로 fast-forward합니다.
이어서 작업 워크트리를 정리하고, 프로젝트 정책에 따라 로컬 브랜치를 삭제하며 지정된 정리 작업을 완료합니다
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
이제 기본 브랜치에는 `chore(merge): integrate dev-<slug> into <base>` 커밋이 기록됩니다. 에이전트는 이후
`devkit workflow next` 호출 시 `--given dev-integration` 옵션을 전달하고, 승인 권한 근거(authority)와 함께 최종 결과를 사용자에게 보고합니다.

## 다양한 작업 변형

- **세션 깊이(Session depth):** 경미한 작업의 경우 별도의 스펙, 엔벨로프, reconcile 문서를 생성하지 않습니다. 하지만 이 경우에도
  테스트 실행, 코드 리뷰, 단계별 커밋은 철저히 진행되며, 최종 응답이나 PR 본문에 변경 내역, 작업 강도, 리뷰 및 검증 결과를 명확히 보고합니다.
- **로컬 오케스트레이션 모드:** 사용자의 지시에 따라 `development-worker` 서브에이전트가 격리된 작업 워크트리에서 구현 턴을 수행합니다.
  호스트 에이전트는 반환된 변경 범위를 `uv run devkit spec worker inspect`로 철저히 검사하며, 반려된 변경 사항은 유닛 진행을 차단하는
  문제(problem) 레코드로 등록됩니다.
- **정책 기반 자동 승인(`auto`):** 공유 기본 설정에서 `dev-integration = "auto"`로 구성된 경우, 코드 리뷰, Living Spec 반영,
  필수 검사가 모두 충족되면 게이트가 정책에 따라 자동 승인되며 보고서에 `authority: policy`가 명시됩니다.
- **풀 리퀘스트 필수 정책:** `[worktree] pull_request = "required"` 설정 환경에서는 로컬 통합 경로가 `WORKTREE_PR_POLICY` 오류로
  거부됩니다. 에이전트는 `--route pull-request` 옵션을 사용하며, 원격 CI 검사와 필수 리뷰가 통과된 후 최종 병합됩니다.

선택 구성 요소인 MCP 런타임은 이 핵심 통합 경로에 필수적이지 않습니다. 워크플로 수명 주기 제어는 전적으로 CLI를 통해 이루어지며, 런타임은
공유 아티팩트(shared artifact) 조회에만 활용됩니다
([`CAP-MCP-runtime-registration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/mcp/CAP-MCP-runtime-registration.md) (영어 원문)).

## 문제 해결

| 보이는 상황 | 해야 할 일 |
| --- | --- |
| 제안된 변경 사항에 동의하지 않는 경우 | 기본 브랜치에 아무것도 병합되지 않습니다. 에이전트는 `devkit workflow return --unit <dir> --to review-refine --note "..."` 명령을 실행하여 검토·수정 단계로 워크플로를 되돌립니다. |
| `INTEGRATION_AUTHORITY_REQUIRED` 또는 `INTEGRATION_REQUEST_STALE` | 다이제스트가 누락되었거나 승인 이후 변경 범위가 바뀌었습니다. 준비 명령을 다시 실행하고 현재 범위를 승인하십시오. |
| `INTEGRATION_TARGET_MOVED` | 통합 대상 커밋을 생성한 뒤 기본 브랜치에 새로운 변경이 발생한 경우입니다. 기존 코드는 변경되지 않습니다. 기본 브랜치의 최신 변경을 작업 브랜치로 병합한 후 다시 통합을 준비하십시오. |
| `WORKTREE_BLOCKED` | 유닛에 미해결 문제(problem)나 미답변 질문이 남아 있는 상태입니다. [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)를 참고하십시오. |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | 정리 대상인 작업 워크트리 내부에서 CLI 명령어가 실행된 경우입니다. 워크트리 외부의 런타임 환경에서 다시 준비 명령을 실행하고 승인하십시오. |
| `INTEGRATION_RECEIPT_READER_CHANGED` | 작업 브랜치가 자체 설치 기록(receipt)을 해석하는 리더 로직 자체를 변경한 경우입니다. 아무것도 병합되지 않으므로, 불일치 원인을 먼저 해소한 후 재시도하십시오. |
| 병합 후 정리 단계가 미완료 상태로 남은 경우 | `devkit worktree status` 및 Git 상태를 확인하십시오. 브랜치가 남아 있다면 `devkit worktree finish <branch> --merge --local-only`를 다시 실행하거나, `devkit spec proposal prune <slug>` 등 해당 정리 명령을 직접 실행합니다. 병합 작업 자체가 중복 실행되지는 않습니다. |
| 작업 결과를 즉시 확정하기 어려운 경우 | Git, 워크트리, 풀 리퀘스트 상태를 먼저 점검한 뒤, 아직 완료되지 않은 것으로 명확히 확인된 정리 작업만 선별하여 실행하십시오. |
| 재시도 한도를 초과했거나 도구 실행이 실패한 경우 | 에이전트는 원인 분석과 명확한 증거를 첨부하여 `exception` 단계로 진입하며, 한도를 우회하기 위해 임의로 신규 태스크를 생성하지 않습니다. |

전체 통합 오류 코드 목록은 `CAP-INT-mcp-services`를 참고하십시오. 관련 영역: [전달](../areas/delivery.md),
[통합](../areas/integration.md), [워크트리](../areas/worktree.md).
