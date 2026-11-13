---
sources:
  CAP-COLL-work-scope-registry: null
  CAP-DLV-project-policy: null
  CAP-TRACE-code-entrypoints: null
  CAP-WT-task-worktrees: null
  UC-run-parallel-work-safely: null
title: 병렬 작업 안전하게 실행하기
translated_from: en/journeys/run-parallel-work-safely.md@43ab7928cceec9e6
---

# 병렬 작업 안전하게 실행하기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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
- [제안 계획 후 넘기기](plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [결정 대체 관계 읽기](read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
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

사용자(또는 오케스트레이션을 담당하는 에이전트)가 둘 이상의 제안이나 스펙 번들을 동시에 진행할 때, 동일한 문서나 코드를 동시에 수정하여 통합 시점에 충돌이 발생할 위험이 있습니다. devkit은 리소스를 강제로 잠그지(lock) 않습니다. 대신 `devkit spec scope` 명령을 통해 작업 착수 전과 진행 중에 여러 작업이 공유하는 Living Spec 문서와 코드 경로, 그리고 아직 확정되지 않은 미지의 범위가 얼마나 되는지 가시화해 줍니다. 이를 통해 어떤 작업을 병렬로 진행하고 어떤 순서로 통합할지 사용자가 직접 판단할 수 있습니다.

작업 워크트리와 활동 브랜치에 관한 개념은 [개념](../concepts.md)을, 작업 범위 레지스트리 자체에 관한 내용은 [협업 영역](../areas/collaboration.md)을 참고하십시오.

출처: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/collaboration/UC-run-parallel-work-safely.md) (영어 원문),
계약 [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md) (영어 원문).

## 시작하기 전에

- `devkit-spec`이 설치된 Git 저장소여야 합니다.
- 각 작업은 자신의 스펙 번들에 작업 범위를 선언해 둡니다. 구체적으로는 `target-docs.md` 또는 `reconcile.md`의 대상 문서, `tasks.md`의 `_Boundary` 항목, 그리고 대상 문서에 정의된 `entrypoints`입니다. 진입점(`entrypoints`) 정보를 통해 문서를 실제 코드 경로로 변환할 수 있습니다([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)). `specs/` 하위의 `_Boundary` 항목은 비교 대상에서 제외되지만, 다른 스펙 번들의 피드백 파일을 가리키는 특정 경로(`specs/**/feedback/<name>.md`)는 예외적으로 코드 경로로 수집됩니다. 따라서 동일한 피드백 파일을 처리하는 두 작업은 해당 파일에서 겹치는 것으로 감지됩니다.
- 작업 범위 레지스트리는 Git 공통 디렉터리(`.git/`)에 저장되므로, 저장소 내의 모든 작업 워크트리가 추가 설정 없이 동일한 레지스트리를 공유합니다.

## 단계별 진행

1. **Git 정책 확인.** 어떤 작업 활동이 독립된 작업 워크트리를 할당받는지 Git 정책을 확인합니다.

   ```sh
   uv run devkit spec policy     # [GIT_POLICY: worktree=...] 확인
   ```

   자세한 내용은 [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)를 참고하십시오.
2. **기존 활동 소스 확인.** `uv run devkit spec scope collect`로 `plan-*` 또는 `dev-*` 소스가 있는 작업의 선언과 관찰된 변경을 비교합니다. 소스 없는 대기 초안은 제외하며 중첩과 함께 미해결 입력도 읽습니다.
3. **작업 착수.** 병렬로 진행하기로 결정한 각 작업을 고유한 활동 브랜치와 독립된 작업 워크트리에서 시작합니다
   (`uv run devkit worktree start dev-<slug>`,
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
   `devkit spec new`나 `devkit spec proposal handoff`가 연결된 워크트리(linked worktree)에서 유닛을 만들면, 초기 범위 스냅샷이
   레지스트리에 자동으로 기록됩니다. 이 등록은 최선 노력(best effort) 방식이어서, 실패하더라도 생성 자체는 성공하며 누구도 이를
   복구할 필요가 없습니다.
4. **작업 진행.** 워커는 평소의 전달 워크플로에 따라 선언과 변경 사항을 작성합니다. 워커에게는 범위를 등록하거나 갱신하거나
   확인 응답(ACK)할 의무가 없으며, `devkit workflow next`도 범위를 수집하지 않습니다.
5. **필요할 때 관찰.** 증거가 필요하면 오케스트레이션 에이전트가 어느 체크아웃에서든 명시적으로 요청합니다.

   ```sh
   uv run devkit spec scope collect
   uv run devkit spec scope collect --fetch origin
   ```

   한 번의 수집은 생성 스냅샷·활동 ref·접근 가능한 워크트리의 선언과 변경을 함께 읽으며, 실제 관찰한 현재 쓰기와 Planning 제안이 선언한 미래 범위(`horizon`: `current` vs `future`)를 구분합니다. 활동 소스가 없는 초안은 제외합니다. `--fetch`는 설정된 원격 저장소를 먼저 갱신하며, 이 옵션이 없으면 원격 브랜치는 마지막 fetch 시점의 상태입니다. 출력에는 각 `[SCOPE_CANDIDATE: ...]`와 `[SCOPE_OBSERVATION: ...]`, `[PAIR: ...]`(`current`/`future` 개수 포함)와 `[EVIDENCE: ...]` 줄, 그리고 `current_overlapping`을 보고하는 `[SUMMARY: ... coverage=complete|partial ...]`가 표시됩니다. 수집은 기록이나 토큰을 전혀 바꾸지 않습니다.
6. **작업 및 통합 순서 결정.** 범위 중첩, 중첩 시점(`horizon`: `current` vs `future`), 각 관찰의 출처, 누락된 커버리지를 바탕으로 무엇을 계속 병렬로 진행할지 판단합니다. 현재 겹치는 작업은 순차적으로 실행합니다(`current_overlapping`). 미래 범위만 겹치는 작업은 Planning을 병렬로 유지하되 핸드오프와 통합 순서를 차례대로 정할 수 있습니다.
7. **작업 완료.** 통합 과정에서 워크트리가 제거되고, 완료 후속 정리 단계에서 해당 워크트리의 범위 기록이 삭제됩니다. 다른 작업의
   기록은 그대로 유지됩니다.

## "unresolved"와 "partial"의 의미

실제 코드 경로로 변환할 수 없는 입력 항목은 사유와 함께 미해결(unresolved) 상태로 집계됩니다(예: `entrypoints` 정보가 누락된 capability 대상의 경우 `reason=no-entrypoints`, 계획 단계에만 존재하는 문서, 면제된 대상, 실제 존재하지 않는 파일 등). unresolved 상태가 결코 "충돌이나 중첩이 없음"을 의미하지는 않습니다. 대상 capability 규격에 `entrypoints`를 충실히 기재해 둘수록 범위 대조 결과가 훨씬 정밀해집니다.

`coverage=partial`과 `SPEC_SCOPE_COLLECTION_PARTIAL` 경고는 일부 소스, 기준(base), 식별 정보 또는 비교를 예산(budget) 안에서
관찰하지 못했다는 뜻입니다. 수집된 증거는 그대로 사용할 수 있으며, 경고에는 누락된 소스마다 그 사유가 나옵니다. 알 수 없는 입력이나
접근할 수 없는 소스로는 독립성을 판단할 수 없으며, 계산되지 않은 쌍은 결코 중첩 0으로 계산되지 않습니다.

## 문제가 생겼을 때

- **`SPEC_SCOPE_COLLECTION_PARTIAL`:** 누락된 부분이 있지만 사용할 수 있는 증거입니다. 종료 코드는 `0`(`--strict`에서는 `1`)입니다.
  누락된 부분을 감안해 판단하거나, 접근 문제를 해결한 뒤 다시 수집하십시오.
- **`SPEC_SCOPE_COLLECTION_FAILED`:** 선택한 인벤토리 소스를 하나도 읽지 못했습니다. `[TARGET]`에 나온 소스의 접근 문제를 해결한 뒤
  다시 수집하십시오.
- **`ARGUMENT_INVALID`:** 예산 값이나 원격 이름이
  잘못되었습니다. 인자를 바로잡으십시오.
- **다른 머신의 작업이 보이지 않는 경우:** 어떤 관찰도 다른 PC의 푸시되지 않았거나 커밋되지 않은 변경을 읽지 못합니다. 여러 PC에서
  자주 작업한다면 선언과 변경 사항을 푸시하고, 가능하면 풀 리퀘스트를 사용하여 수집으로 볼 수 있게 하십시오.
- **워크트리가 삭제된 후에도 레지스트리 기록이 남아 있는 경우:** 워크트리 정리 단계가 실패했거나 `finish` 절차 없이 워크트리가 강제 삭제된 경우입니다. 리비전 변동이 없는 유효하지 않은 기록은 정리되고(`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`) 리비전이 변경된 기록은 보존된 채 `SPEC_SCOPE_STALE_REVISION`으로 보고되므로, 기본 체크아웃에서 `uv run devkit spec scope sweep --apply`를 실행하십시오.

## 최종 결과

각 작업 쌍이 공유하는 문서와 코드 경로, 각 관찰의 출처, 그리고 누락된 커버리지가 얼마나 되는지 명확히 파악할 수 있습니다. 어떤 작업도 차단되거나 추가 기록 부담을 지지 않으며, 완료된 작업은 잔여 기록을 남기지 않습니다. 범위 중첩 증거는 선언된 명세와 Git의 관찰 결과를 종합한 분석일 뿐, 실제 Git 병합 충돌이나 완벽한 독립성을 단정하는 것은 아닙니다.
