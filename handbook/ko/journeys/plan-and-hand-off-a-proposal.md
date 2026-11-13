---
sources:
  CAP-DLV-delivery-workflows: null
  CAP-DLV-proposal-planning: null
  CAP-DLV-spec-bundles: null
  UC-plan-and-hand-off-a-proposal: null
title: 제안 계획 후 넘기기
translated_from: en/journeys/plan-and-hand-off-a-proposal.md@e5a8a173a83d6d26
---

# 제안 계획 후 넘기기

<!-- handbook:provenance -->
> 소스 커밋 `a6e769c5721d` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](assess-test-management.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [아이디어 발굴하고 구체화하기](discover-and-refine-an-idea.md)
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
- [격리된 명령 실행하기](execute-an-isolated-command.md)
- [설계 문제 탐색하기](explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [결정 대체 관계 읽기](read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](snapshot-bundle-sources.md)
- [선택한 느린 작업 빠르게 하기](speed-up-selected-slow-operations.md)
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
[`UC-plan-and-hand-off-a-proposal`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md) (영어 원문)입니다.
제안, PADR, Planning과 Development, 게이트(gate) 등의 개념은 [개념](../concepts.md)에서 설명합니다.

제안은 스펙 주도 개발(SDD)에 속하는 절차입니다. 저장소의 개발 방식(development approach)이 적응형 개발(adaptive development)이면
제안의 생성, 수락, 핸드오프는 아무것도 바꾸기 전에 `SPEC_LIFECYCLE_INACTIVE`로 거부되며, 기존 제안을 읽는 것은 그대로
가능합니다. 적응형 개발 작업은 [아이디어 발전시키기](advance-an-idea.md)를 따릅니다.

## 1. 제안 초안(Draft) 작성

Backlog 단계에서 에이전트는 `sdd-proposal` 워크플로에 연결된 제안 초안을 생성합니다.

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --summary "Replaces the regex rule engine with an AST parser."
```

접수 시 명시적으로 요청된 초안 범위와 제안하는 Planning 작업 강도(effort)를 알립니다
([`CAP-DLV-proposal-planning`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-proposal-planning.md) (영어 원문)).
`--milestone`에는 계획·진행 중인 마일스톤뿐 아니라 완료되거나 중단된 마일스톤도 지정할 수 있습니다. 완료·중단된
마일스톤이면 소속을 다시 검토하라는 `SPEC_PROPOSAL_MILESTONE_INACTIVE` 알림만 추가됩니다.

초안의 `size`는 Planning을 시작할 수 있는지를 결정합니다. `S`, `M`, `L`(또는 크기 미지정)은 Planning 대상입니다.
`XL`은 작업이 둘 이상의 스펙을 만들거나 성격이 다른 산출물(예: 버그 수정과 신규 기능)을 함께 묶는다는 뜻입니다. `XL`
초안은 Backlog에서는 유효하지만, `devkit workflow next`가 `intent-proposal`의 크기 검사를 미충족(`detail="size=XL"`)으로
보여 줍니다. 에이전트는 이를 "먼저 분할하라"는 뜻으로 읽고, 검사를 통과하려고 크기를
고치지 않습니다. 사용자의 결정에 따라 초안을 분할하거나(`devkit spec proposal new <child> --decomposed-from
PROP-<parent>`, 부모의 마일스톤 유지) 하위 초안을 담는 마일스톤으로 승격하며, 필요하면 읽기 전용 `decomposer` 역할에
분할안을 요청합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

## 2. 기획 및 설계 (Planning)

에이전트는 `plan-<slug>` 브랜치에서 Planning 단계를 개시하고 제안 상태를 검토 중으로 전환합니다. 지정된 Planning 작업
강도에 따라 `scout` 서브에이전트에게 증거 조사를, `challenger` 서브에이전트에게 비판 검토를 요청하고 그 결과를 기록합니다.
이 과정에서 도출된 예비 결정을 PADR로 작성합니다.

```bash
uv run devkit spec proposal padr fast-engine "Use AST parser"
```

제안이 사람이 보는 화면을 바꾸는 경우 `target-docs.md`에 화면 초안이 담기며, 에이전트는 코드 작성 전에 읽기 전용
`ux-reviewer`에게 연결된 유스케이스를 화면에 따라 점검하도록 맡길 수 있습니다. 그 지적 사항에는 심각도가 없으며, 남은
항목은 수락 시점에 사용자가 결정합니다.

## 3. 미결정 사항(Open Questions) 해결

에이전트는 모든 질문을 취합하여 한 라운드에 사용자에게 전달합니다. 답변을 제안 본문과 PADR에 반영하고 Development 작업
강도 힌트를 구체화합니다. 사용자에게 돌아갈 때마다 그 전에 최신 피드백 정리(feedback sweep) 범위를 기록합니다.

## 4. 제안 검토 및 수락

최종 Planning 커밋 후 Host가 제안·PADR·엔벨로프를 검토하고 브리핑을 제시합니다.
`uv run devkit spec proposal report <slug>`로 공유 산출물 게시 없이 읽을 수 있습니다.
사용자의 방향 결정 후 유지되는 베이스 체크아웃에서 실행합니다.

```bash
uv run devkit spec proposal accept-plan <slug> --by user --mode accept_only
```

수락을 기록하고 Planning을 통합합니다. 이동한 베이스와 충돌이 없으면 `plan-<slug>`에 먼저 병합할 필요가 없습니다.
제안 범위 변경이나 Git 충돌은 재검토·수리 후 진행합니다.
`accept_and_handoff --effort <level>`는 handoff 권한도 필요하지만 Planning 병합 후 최종 검증 대기·handoff 미시작으로 반환합니다.
Host가 반영된 런타임을 동기화·검사하고 승인된 범위와 강도를 유지해 새 프로세스에서 handoff를 실행합니다.

## 5. 개발 스펙 번들로 핸드오프 (Handoff)

`proposal-handoff` 권한을 가진 상태에서 유지된 기본 체크아웃에서 실행합니다(`ask`에서는 Host가 제시한 효과와
Development 작업 강도를 사용자가 승인한 후에만, `auto`에서는 `dev_effort` 힌트로 실행됩니다).

```bash
uv run devkit spec proposal handoff fast-engine --effort medium
```

이 명령은 `dev-<slug>` 브랜치와 워크트리를 생성하거나 검증하고, 설정과 동기화를 실행한 뒤 그곳으로 핸드오프합니다.
핸드오프는 `sdd-spec-<task_kind>`에 연결된 스펙 번들을 만들고
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)),
PADR을 수락된 ADR로 승격하며, 참고 자료와 미해결 피드백을 옮기고, `plan-accept` 기록을 이름 그대로
승계하고, 제안을 가리키던 참조를 다시 쓴 뒤 제안을 제거합니다. 출력 라인이 옮겨진 내용을 알려 줍니다:
`[PROMOTED_ADR: ...]`, `[MATERIALS: ...]`, `[CARRIED_GATE: ...]`, `[REWRITTEN: ...]`, 그리고
`[NEXT_CMD: uv run devkit workflow next --unit <dir>]`.

## 6. 재작성 참조 점검 및 개발 착수

`SPEC_PROPOSAL_REFS_REWRITTEN` 알림은 에이전트에게 다시 쓰인 문장을 재확인하도록 지시합니다. 에이전트는 해결되지 않은
링크를 같은 변경에서 고치고, [개발부터 통합까지 진행하기](drive-development-to-integration.md)처럼 스펙 워크플로의 다음
단계를 따릅니다.

## 다양한 분기 시나리오

- **Planning이 필요 없는 경우.** 방향이 이미 정해진 초안이면 에이전트가 기본 체크아웃에서 자격을 읽기 전용으로 점검한 뒤,
  사용자의 명시적 결정에 따라 직접 수락(direct acceptance)을 기록합니다:
  `uv run devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"` 후 `--check`를 뺀 같은 명령.
  점검은 모든 자격 제한 조건을 보고하며 의도 기록을 요구하지 않습니다.
  `XL` 초안은 직접 수락 대상이 될 수 없습니다.
- **실제로는 작은 작업인 경우.** 착수 시점에 PADR이 없는 대기 초안을 `session` 작업으로 정할 수 있습니다. 에이전트는
  미해결 피드백을 보존하는 기본 브랜치 커밋 하나로 초안을 삭제하고 세션으로 작업합니다.
- **분할이 필요한 경우.** Planning이 제안을 분할 표시가 붙은 초안으로 돌려보냅니다. Planning 브랜치가 사라지고 기본
  브랜치에서 `devkit spec proposal check <slug>`가 통과하면, Backlog가 1단계와 같은 방식으로 하위 초안을 만듭니다.
- **반려하는 경우.** 에이전트는 커밋 메시지에 사유를 담아 `status: rejected`로 설정하고 정책에 따라 Planning 브랜치를
  병합합니다. 이후 `devkit rules check --phase hygiene`이 `SPEC_PROPOSAL_REJECTED_PENDING`을 경고하며, 그 수정이 반려
  ADR을 작성하고 미해결 피드백을 보존한 채 제안을 삭제합니다.
- **정책이 수락하는 경우.** 소유 기본 브랜치와 작업 브랜치가 모두 `plan-accept = "auto"`이면 에이전트가
  `accept --by policy`를 실행하며, 보고서는 사용자의 동의가 아니라 정책을 근거로 밝힙니다. 그 밖의 정책에서
  `--by policy`는 `SPEC_PROPOSAL_POLICY_NOT_AUTO`로 거부됩니다.

## 문제 해결

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `SPEC_LIFECYCLE_INACTIVE` | 개발 방식이 적응형 개발이어서 제안 생성, 수락, 핸드오프를 쓸 수 없습니다. | `uv run devkit config show`를 확인하십시오. SDD로 전환할지는 사용자의 명시적 선택입니다([적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)). |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | 직접 수락 조건을 충족하지 못했습니다(예: `size: XL`). 각 조건과 해결 명령이 나열됩니다. | 조건을 해결하거나 Planning을 진행하십시오. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | 워크플로가 `plan-accept`를 열지 않았습니다(예: 피드백 정리 누락). 상태는 복원됩니다. | 나열된 검사를 충족한 뒤 다시 수락하십시오. |
| `SPEC_PROPOSAL_APPROVAL_NOT_READY` | 합성 수락에서 Planning이 끝나지 않았습니다: 미충족 검사, 열린 질문, 보류, 또는 `plan-<slug>` 없음. | 그곳에서 Planning을 마친 뒤 다시 실행하십시오. |
| `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED` | 커밋 게이트가 수락 커밋을 거부했고, 두 수락 기록은 철회되었습니다. | `plan-<slug>`에서 `uv run devkit rules check`를 실행하고 고쳐 커밋한 뒤 다시 실행하십시오. |
| `SPEC_PROPOSAL_IN_PLANNING` | Backlog 변경이 `plan-<slug>`가 있는 초안을 건드렸습니다. | 초안은 Planning 브랜치에 맡기십시오. |
| `SPEC_PROPOSAL_NOT_APPROVED` | 수락되지 않은 제안을 핸드오프하려 했습니다. | 결정을 요청하십시오. 승인은 추정되지 않습니다. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | 제안이 `accepted`라고 하지만 `plan-accept` 기록이 없습니다. | 기본 브랜치에서 직접 수락으로 보완하거나 Planning 병합을 되돌릴지 결정하십시오. |
| `SPEC_HANDOFF_NOT_READY` | 합성 핸드오프에서 제안이 수락되지 않았거나, 분할이 필요하거나, Planning이 완료되지 않았습니다. | 지목된 조건을 해결하고 유지된 기본 체크아웃에서 다시 실행하십시오. |
| `SPEC_HANDOFF_BASE_DIRTY` | 유지된 기본 체크아웃에 커밋되지 않은 변경이 있습니다(목록 표시). | 그 변경의 처리를 정한 뒤 다시 실행하십시오. |
| `SPEC_HANDOFF_WORKTREE_CONFLICT` | 이 수락된 기준을 위해 devkit이 만들지 않은 `dev-<slug>` 워크트리가 있거나, 변경 또는 다른 커밋을 담고 있습니다. 재사용하거나 제거하지 않습니다. | 그 워크트리를 직접 확인하고 정리하십시오. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | 핸드오프가 `dev-<slug>` 밖에서 실행되었거나, 합성 명령이 유지된 기본 체크아웃 밖에서 실행되었습니다. | `[TARGET]`과 `[FIX]`가 가리키는 곳에서 실행하십시오. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | 쓰기가 실패해 롤백을 시도하지만 일부 복구가 실패할 수 있습니다. | 보고된 롤백 결과와 남은 경로를 확인한 뒤 수리·재시도하십시오. |
| `SPEC_HANDOFF_STALE` | 점검 후 효과 적용 전에 기본 브랜치, 수락된 계획, 정책이 바뀌었습니다(종료 코드 `2`). 또는 새 워크트리가 검토한 기본 커밋을 더 이상 담고 있지 않아 `status=needs_recovery`로 보존되었습니다(종료 코드 `1`). | 현재 상태를 검토하고 다시 승인하십시오. 보존된 워크트리를 점검하십시오. |

사전 조건 거부는 아무것도 쓰지 않습니다. 효과가 발생한 뒤의 실패는 워크트리나 쓰기를 남길 수 있으므로 보고된 상태를 먼저 확인합니다. 버그 수정 제안은 `spec.md`만 담은 `sdd-spec-bugfix` 번들로
핸드오프됩니다. 관련 영역: [전달](../areas/delivery.md).

## Handoff 커밋과 복구

복합 handoff는 검토한 베이스의 깨끗한 직접 자식으로 트랜잭션을 한 번 커밋하고 `commit`을 보고합니다.
커밋 게이트가 거부하면 `SPEC_HANDOFF_COMMIT_REFUSED`, `status=needs_recovery`와 함께
`dev-<slug>`에 쓰기를 staged 상태로 남깁니다. 원인을 고치고 그곳에서 커밋하며 수정된 워크트리에 handoff를 재실행하지 않습니다.
커밋 후 미커밋 파일이나 이력 변경도 현재 위치에서 확인·복구합니다.

로컬 오케스트레이션에서는 git-operator가 관찰한 `head`, `dirty_paths`를 `checks.worker_input`으로 반환합니다.
Host는 Git과 대조하고 해당 깨끗한 HEAD 또는 자신이 추가한 링크 수정 자식 커밋에서 워커를 시작합니다.
재작성한 참조를 다시 읽고 별도 후속 커밋으로 고쳐 handoff 트랜잭션 SHA를 유지합니다.

## 이 릴리스의 작업 방식

UX 리뷰 지적은 초안에서 고친 항목까지 `build-verify`에서 닫습니다. 이 기록은 추가 독립 리뷰 회차가 아닙니다. 최종 조정 검사는 전체 반영을 확인하고 앞선 검사를 식별하며 각 지적을 해결 또는 사유가 있는 면제로 표시합니다. 필수 계약 불일치는 면제할 수 없습니다.
