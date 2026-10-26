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
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

어떤 요청은 방향이 아직 열린 채로 들어옵니다. 여러 형태가 가능한 새 기능, 스파이크, 아키텍처 변경 같은 경우입니다.
이런 요청은 `proposal` 깊이를 택합니다. 에이전트는 아이디어를 제안(proposal)으로 다듬고, 증거를 모으고, 열린 질문을
여러분에게 묻습니다. 여러분은 그 증거를 바탕으로 방향을 수락합니다. 그러면 제안은 모든 것을 이어받는 스펙 번들로
넘겨지고(handoff), Development는 일관된 Living Spec에서 출발합니다.

유스케이스는
[`UC-incubate-and-hand-off-a-proposal`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md) (영어 원문)입니다.
제안, PADR, Planning과 Development, 게이트(gate)는 [개념](../concepts.md)에서 설명합니다.

## 1. 초안 만들기

Backlog에서 에이전트는 `sdd-proposal` 워크플로(workflow)에 묶인 초안을 만듭니다.

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --summary "Replaces the regex rule engine with an AST parser."
```

초안과 제안된 Planning 노력 수준에 대한 여러분의 확인을 `plan-intent`로 기록합니다
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md) (영어 원문)).

## 2. Planning

에이전트는 `plan-<slug>` 브랜치에서 Planning을 시작하고 제안을 리뷰 상태로 둡니다. Planning 노력 수준이 요구하는
만큼 `scout`에게 증거를, `challenger`에게 비판을 요청하고, 그 반환을 기록하며, 예비 결정을 PADR로 씁니다.

```bash
uv run devkit spec proposal padr fast-engine "Use AST parser"
```

## 3. 열린 질문에 답하기

에이전트는 열린 질문을 모두 한 라운드로 여러분에게 묻고, 답을 제안과 PADR에 반영하며, Development 노력 수준
힌트를 다듬습니다. 여러분에게 돌아올 때마다 그 전에 새로운 피드백 점검 범위를 기록합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

## 4. 검토와 수락

마지막 Planning 커밋 후 에이전트는 제안, PADR, 엔벨로프(envelope)를 검토하고 결과를 제시합니다. 같은 브리핑을
여러분도 읽을 수 있습니다.

```bash
uv run devkit spec proposal report fast-engine
```

여러분이 방향을 수락하면, 에이전트는 수락과 수락 상태를 한 단계로 기록합니다.

```bash
uv run devkit spec proposal accept fast-engine --by user --note "<your decision>"
```

`--mode accept_and_handoff --effort <level>`을 붙이면 같은 호출이 Development도 시작하고, `accept_only`는 수락 후
멈춥니다. 그다음 에이전트는 Planning 브랜치를 통합하고, 워크플로는 제안 유닛(Unit)이 완료되었다고 보고합니다.

## 5. 넘기기

`proposal-handoff` 권한을 갖고 유지된 기본 체크아웃에서 실행합니다(`ask`에서는 Host가 제시한 효과와 Development 노력 수준을
여러분이 승인한 뒤에만, `auto`에서는 `dev_effort` 힌트로 실행합니다).

```bash
uv run devkit spec proposal handoff fast-engine --effort medium
```

이 명령은 `dev-<slug>`와 그 워크트리를 만들거나 검증하고, 설정과 동기화를 실행한 뒤 그곳에서 핸드오프합니다.
핸드오프는 `sdd-spec-<task_kind>`에 묶인 스펙 번들을 만들고
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)),
PADR을 수락된 ADR로 승격하며, 자료와 열린 피드백을 옮기고, `plan-intent`와 `plan-accept` 기록을 이름으로 이어받고,
제안 안을 가리키던 참조를 고쳐 쓴 뒤 제안을 제거합니다. 출력 줄은 무엇이 옮겨졌는지 알려 줍니다.
`[PROMOTED_ADR: ...]`, `[MATERIALS: ...]`, `[CARRIED_GATE: ...]`, `[REWRITTEN: ...]`, 그리고
`[NEXT_CMD: devkit workflow next --unit <dir>]` 순입니다.

## 6. 다시 읽고 계속하기

`SPEC_PROPOSAL_REFS_REWRITTEN` 알림은 에이전트에게 고쳐 쓴 문장을 다시 읽으라고 요청합니다. 에이전트는 해석되지
않는 링크를 같은 변경에서 고치고, [개발부터 통합까지 진행하기](drive-development-to-integration.md)처럼 스펙
워크플로의 다음 단계를 따릅니다.

## 지름길과 다른 결말

- **Planning이 필요 없음.** 방향이 정해진 초안이라면, 에이전트는 기본 체크아웃에서 읽기 전용으로 자격을 확인한 뒤,
  여러분의 명시적 결정에 따라 직접 수락(direct acceptance)을 기록합니다.
  `uv run devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"`을 실행한 다음, `--check`
  없이 같은 명령을 실행합니다.
- **사실은 작은 태스크임.** 대기 중인 초안에 PADR이 없다면, 착수 시점에 그것을 `session` 작업으로 정할 수 있습니다.
  에이전트는 열린 피드백을 보존하는 기본 브랜치 커밋 하나로 초안을 삭제하고, 세션으로 작업을 진행합니다.
- **분할해야 함.** Planning은 제안을 분해 표시가 된 초안으로 되돌립니다. Planning 브랜치가 사라지고 기본 브랜치에서
  `devkit spec proposal check <slug>`가 통과하면, Backlog가 하위 초안을 만듭니다.
- **거절함.** 에이전트는 커밋 메시지에 여러분의 이유를 담아 `status: rejected`로 설정하고, 정책에 따라 Planning
  브랜치를 병합합니다. 이후 `devkit rules check --phase hygiene`이 `SPEC_PROPOSAL_REJECTED_PENDING`을 경고하며,
  그 수정은 거절 ADR을 쓰고 열린 피드백을 보존한 채 제안을 삭제합니다.
- **정책이 수락함.** 소유 기본 브랜치와 작업 브랜치가 모두 `plan-accept = "auto"`로 설정하면 에이전트는
  `accept --by policy`를 실행하고, 보고서는 여러분의 동의가 아니라 정책을 근거로 명시합니다.

## 문제가 생겼을 때

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | 직접 수락이 어떤 조건을 충족하지 못했습니다. 조건마다 나열됩니다. | 조건을 고치거나 Planning을 거치십시오. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | 워크플로가 `plan-accept`를 열지 않습니다(예: 피드백 점검 누락). 상태는 복원됩니다. | 나열된 검사를 충족한 다음 다시 수락하십시오. |
| `SPEC_PROPOSAL_IN_PLANNING` | Backlog 변경이 `plan-<slug>`가 존재하는 초안을 건드렸습니다. | 초안은 그 Planning 브랜치에 맡기십시오. |
| `SPEC_PROPOSAL_NOT_APPROVED` | 수락되지 않은 제안을 핸드오프하려 했습니다. | 결정을 요청하십시오. 승인은 결코 추론되지 않습니다. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | 제안이 기록된 `plan-accept` 없이 `accepted`라고 표시합니다. | 기본 브랜치에서 직접 수락으로 바로잡거나, Planning 병합을 되돌릴지 결정하십시오. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | 핸드오프가 `dev-<slug>` 바깥에서 실행되었습니다. | `dev-<slug>`를 시작하거나 이어 가십시오. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | 쓰기가 실패했습니다. 모두 롤백되었고 제안은 유지됩니다. | 원인을 고치고 다시 실행하십시오. |
| `SPEC_HANDOFF_STALE` | 검사 이후 어떤 효과도 생기기 전에 기본 브랜치, 수락된 계획, 정책이 바뀌었습니다(종료 코드 `2`). 또는 새 워크트리가 리뷰한 기본 커밋을 더 이상 담고 있지 않아 `status=needs_recovery`로 보존되었습니다(종료 코드 `1`). | 현재 상태를 검토하고 다시 승인하십시오. 보존된 워크트리를 점검하십시오. |

거부된 수락이나 핸드오프는 아무것도 쓰지 않습니다. 버그 수정 제안은 `spec.md`만 담고 `sdd-spec-bugfix`에 묶인
번들로 넘겨집니다. 영역: [Delivery](../areas/delivery.md).
