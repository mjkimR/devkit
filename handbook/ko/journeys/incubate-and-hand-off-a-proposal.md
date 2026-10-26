---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-proposal-incubation: null
  CAP-DLV-spec-bundles: null
  UC-incubate-and-hand-off-a-proposal: null
title: 제안 숙성 후 넘기기
translated_from: en/journeys/incubate-and-hand-off-a-proposal.md@c1122e522326aade
---

# 제안 숙성 후 넘기기

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

요구사항의 기술적 방향이 처음부터 확정되지 않은 작업들이 있습니다. 다양한 아키텍처 형태가 고려되는 신규 기능,
기술 검증(spike), 대규모 구조 개편 등이 대표적입니다. 이러한 작업에는 `proposal` 계획 깊이를 적용합니다. 에이전트는
아이디어를 체계적인 제안(proposal)으로 구체화하고, 객관적 증거를 수집하며, 미결정 사항을 사용자에게 질문합니다. 사용자는
제시된 증거를 검토하여 최선의 기술 방향을 승인(수락)합니다. 이후 제안 문서는 모든 맥락과 결정을 보존한 채 스펙 번들로
정식 이관(handoff)되며, 본격적인 개발(Development) 단계는 일관성 있는 Living Spec을 토대로 시작됩니다.

유스케이스는
[`UC-incubate-and-hand-off-a-proposal`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md) (영어 원문)입니다.
제안, PADR, Planning과 Development, 게이트(gate) 등의 개념은 [개념](../concepts.md)에서 설명합니다.

## 1. 제안 초안(Draft) 작성

Backlog 단계에서 에이전트는 `sdd-proposal` 워크플로에 연결된 제안 초안을 생성합니다.

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --summary "Replaces the regex rule engine with an AST parser."
```

생성된 초안과 제안된 Planning 작업 강도(effort)에 대한 사용자의 확인을 `plan-intent` 게이트 레코드로 기록합니다
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md) (영어 원문)).

## 2. 기획 및 설계 (Planning)

에이전트는 격리된 `plan-<slug>` 브랜치에서 Planning 단계를 개시하고 제안 상태를 검토 중(`in review`)으로 전환합니다. 지정된
Planning 작업 강도에 따라 `scout` 서브에이전트에게 기술적 사실 증거 조사를, `challenger` 서브에이전트에게 엄밀한 비판 검토를
요청하고 그 결과를 기록합니다. 이 과정에서 도출된 예비 아키텍처 결정을 PADR(Provisional Architecture Decision Record)로 작성합니다.

```bash
uv run devkit spec proposal padr fast-engine "Use AST parser"
```

## 3. 미결정 사항(Open Questions) 해결

에이전트는 검토 중 도출된 모든 질문을 취합하여 한 라운드에 사용자에게 전달합니다. 사용자의 답변을 제안 본문 및 PADR에 충실히
반영하고, 향후 Development 단계의 작업 강도 힌트를 구체화합니다. 사용자에게 피드백을 요청할 때마다 사전에 최신 피드백
정리(feedback-sweep) 범위를 충실히 기록합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

## 4. 제안 검토 및 승인 수락 (Accept)

Planning 커밋이 완료되면, 에이전트는 제안 본문, PADR, 엔벨로프 기록을 종합 검토하고 최종 보고를 제시합니다. 사용자는
다음 명령어로 브리핑 내용을 직접 조회할 수 있습니다.

```bash
uv run devkit spec proposal report fast-engine
```

사용자가 제시된 방향을 승인(수락)하면, 에이전트는 수락 기록과 제안의 수락 완료 상태를 단일 작업으로 원자적으로 기록합니다.

```bash
uv run devkit spec proposal accept fast-engine --by user --note "<your decision>"
```

`--mode accept_and_handoff --effort <level>` 옵션을 전달하면 수락과 동시에 후속 개발 단계까지 즉시 시작되며, `accept_only`
모드는 수락 기록까지만 진행하고 멈춥니다. 이후 에이전트는 Planning 브랜치를 기본 브랜치로 통합하며, 워크플로는 제안 유닛(Unit)이
성공적으로 완료되었음을 보고합니다.

## 5. 개발 스펙 번들로 핸드오프 (Handoff)

`proposal-handoff` 권한을 확보한 상태에서 기본 체크아웃 환경을 기준으로 실행합니다 (`ask` 정책에서는 Host가 제시한 통합 효과와
Development 작업 강도를 사용자가 승인한 후에 실행되며, `auto` 정책에서는 기 설정된 `dev_effort` 힌트를 사용하여 자동 실행됩니다).

```bash
uv run devkit spec proposal handoff fast-engine --effort medium
```

이 명령어는 전용 `dev-<slug>` 브랜치 및 작업 워크트리를 생성하거나 유효성을 검증하고, 프로젝트 설정 및 동기화를 수행한 후
해당 워크트리로 모든 컨텍스트를 핸드오프합니다. 핸드오프가 수행되면 `sdd-spec-<task_kind>` 워크플로에 연결된 새로운 스펙
번들이 생성되고
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)),
검토를 통과한 PADR은 공식 승인된 ADR로 자동 승격되며, 참고 자료와 미해결 피드백이 함께 이관됩니다. 또한 `plan-intent` 및
`plan-accept` 게이트 기록이 명시적으로 승계되며, 기존 제안 문서를 가리키던 모든 참조 경로가 새로운 스펙 및 ADR 경로로 자동 재작성된 후
원본 제안 문서는 안전하게 정리됩니다. 명령어 출력 라인은 이러한 전환 내역을 명확히 보여줍니다 (`[PROMOTED_ADR: ...]`,
`[MATERIALS: ...]`, `[CARRIED_GATE: ...]`, `[REWRITTEN: ...]`, 그리고 다음에 실행할 명령어인
`[NEXT_CMD: devkit workflow next --unit <dir>]`).

## 6. 재작성 참조 점검 및 개발 착수

`SPEC_PROPOSAL_REFS_REWRITTEN` 어드바이저리 알림은 에이전트에게 경로가 자동 재작성된 문장들을 다시 읽고 문맥의 자연스러움을
점검하도록 지시합니다. 에이전트는 깨진 상대 링크나 부자연스러운 표현을 즉시 수정한 뒤,
[개발부터 통합까지 진행하기](drive-development-to-integration.md) 가이드에 따라 스펙 워크플로의 후속 단계를 진행합니다.

## 다양한 분기 시나리오

- **별도 Planning이 불필요한 경우 (직접 수락):** 기술적 방향이 이미 명확히 정립된 초안이라면, 에이전트는 기본 체크아웃에서 직접
  수락 자격을 읽기 전용으로 사전 점검한 뒤 사용자의 명시적 승인에 따라 직접 수락(direct acceptance)을 기록합니다
  (`uv run devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"` 검증 후 `--check` 플래그를 제외하고 실제 기록 실행).
- **경미한 일반 작업으로 판정된 경우:** 대기 중인 초안에 복잡한 아키텍처 결정(PADR)이 포함되어 있지 않다면, 착수 시점에 해당 작업을
  `session` 깊이로 재분류할 수 있습니다. 에이전트는 미해결 피드백을 보존하는 단일 기본 브랜치 커밋으로 초안을 깔끔히 정리하고, 가벼운
  세션 작업으로 개발을 이어갑니다.
- **여러 과제로 분할이 필요한 경우:** Planning 단계에서 규모가 너무 크다고 판단되면, 제안을 분할 대상 초안으로 표시하여 되돌립니다.
  Planning 브랜치가 정리되고 기본 브랜치에서 `devkit spec proposal check <slug>` 검증이 통과하면, Backlog 단계에서 분할된 하위
  초안들을 생성합니다.
- **제안이 반려(거절)된 경우:** 에이전트는 커밋 메시지에 사용자의 반려 사유를 명시하고 `status: rejected`로 상태를 지정한 뒤
  프로젝트 정책에 따라 Planning 브랜치를 병합합니다. 이후 `devkit rules check --phase hygiene` 실행 시
  `SPEC_PROPOSAL_REJECTED_PENDING` 경고가 감지되며, 자동 수정 기능을 통해 공식 거절 ADR을 남기고 미해결 피드백을 보존하면서
  제안 문서를 최종 정리합니다.
- **정책 기반 자동 수락:** 기본 브랜치와 작업 브랜치 양쪽 모두 `plan-accept = "auto"`로 설정된 경우, 에이전트는 `accept --by policy`를
  실행하며 최종 보고서에는 사용자의 개별 승인이 아닌 프로젝트 정책을 공식 권한 근거로 명시합니다.

## 문제 해결

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | 직접 수락에 필요한 전제 조건을 만족하지 못했습니다. 미충족 조건이 목록으로 출력됩니다. | 조건을 해결하거나 정식 Planning 단계를 진행하십시오. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | 워크플로 상에서 `plan-accept` 게이트가 아직 개방되지 않았습니다(예: 피드백 정리 미수행). 상태가 이전으로 복원됩니다. | 안내된 검사 항목을 모두 충족한 뒤 다시 수락하십시오. |
| `SPEC_PROPOSAL_IN_PLANNING` | Backlog 단계의 작업이 이미 `plan-<slug>` 브랜치가 생성된 초안을 수정하려고 했습니다. | 해당 초안은 전용 Planning 브랜치에서 수정하십시오. |
| `SPEC_PROPOSAL_NOT_APPROVED` | 아직 승인(수락)되지 않은 제안을 핸드오프하려고 시도했습니다. | 사용자의 승인 결정을 요청하십시오. 승인 여부는 시스템이 임의로 추측하지 않습니다. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | 제안 상태는 `accepted`로 표시되어 있으나 공식 `plan-accept` 게이트 레코드가 누락되었습니다. | 기본 브랜치에서 직접 수락 절차로 레코드를 보완하거나, Planning 브랜치 병합을 되돌릴지 결정하십시오. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | 핸드오프 명령어가 지정된 `dev-<slug>` 워크트리 외부에서 실행되었습니다. | `dev-<slug>` 작업 워크트리를 생성하거나 해당 환경에서 명령을 실행하십시오. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | 핸드오프 파일 작성 중 오류가 발생했습니다. 모든 변경이 안전하게 롤백되었으며 원본 제안은 보존됩니다. | 실패 원인을 해결한 뒤 핸드오프를 다시 시도하십시오. |
| `SPEC_HANDOFF_STALE` | 사전 점검 완료 후 실제 작업이 적용되기 전에 기본 브랜치, 수락된 계획, 또는 정책 설정이 변경되었습니다(종료 코드 `2`). 또는 새로 생성된 워크트리가 검토했던 기본 커밋을 더 이상 포함하지 않아 `status=needs_recovery` 상태로 안전하게 보존되었습니다(종료 코드 `1`). | 현재 저장소 상태를 재검토한 후 다시 승인하십시오. 보존된 워크트리가 있다면 상태를 점검하십시오. |

승인 거부나 핸드오프 실패 시에는 파일 시스템에 어떠한 잔여 변경도 남기지 않습니다. 버그 수정 제안의 경우 `spec.md` 단일 문서만 포함하는
`sdd-spec-bugfix` 워크플로 번들로 핸드오프됩니다. 관련 영역: [전달](../areas/delivery.md).
