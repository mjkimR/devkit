---
sources:
  CAP-COLL-work-scope-registry: null
  CAP-DLV-project-policy: null
  CAP-TRACE-code-entrypoints: null
  CAP-WT-task-worktrees: null
  UC-run-parallel-work-safely: null
title: 병렬 작업 안전하게 실행하기
translated_from: en/journeys/run-parallel-work-safely.md@b0a22cdb968a4ff9
---

# 병렬 작업 안전하게 실행하기

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
- [개발 요청 라우팅하기](route-development-intent.md)
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

출처: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/collaboration/UC-run-parallel-work-safely.md) (영어 원문),
계약 [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md).

## 시작하기 전에

- `devkit-spec`이 설치된 Git 저장소여야 합니다.
- 각 작업은 자신의 스펙 번들에 작업 범위를 선언해 둡니다. 구체적으로는 `target-docs.md` 또는 `reconcile.md`의 대상 문서, `tasks.md`의 `_Boundary` 항목, 그리고 대상 문서에 정의된 `entrypoints`입니다. 진입점(`entrypoints`) 정보를 통해 문서를 실제 코드 경로로 변환할 수 있습니다([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)). `specs/` 하위의 `_Boundary` 항목은 비교 대상에서 제외되지만, 다른 스펙 번들의 피드백 파일을 가리키는 특정 경로(`specs/**/feedback/<name>.md`)는 예외적으로 코드 경로로 수집됩니다. 따라서 동일한 피드백 파일을 처리하는 두 작업은 해당 파일에서 겹치는 것으로 감지됩니다.
- 작업 범위 레지스트리는 Git 공통 디렉터리(`.git/`)에 저장되므로, 저장소 내의 모든 작업 워크트리가 추가 설정 없이 동일한 레지스트리를 공유합니다.

## 단계별 진행

1. **Git 정책 확인.** 어떤 작업 활동이 독립된 작업 워크트리를 할당받는지 Git 정책을 확인합니다.

   ```sh
   uv run devkit spec policy     # look at [GIT_POLICY: worktree=...]
   ```

   자세한 내용은 [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)를 참고하십시오.
2. **계획된 범위 비교.** 실제 작업을 시작하기 전에 계획된 작업 범위를 비교합니다. 이 단계에서는 선언된 명세만 읽으며 어떠한 변경도 기록하지 않습니다.

   ```sh
   uv run devkit spec scope compare --proposal <a> --proposal <b>
   uv run devkit spec scope compare --spec <dir-a> --spec <dir-b>
   ```

   비교 대상 쌍마다 `[EVIDENCE: <path> ... kind=doc|code ...]` 증거가 포함된 `[PAIR: ... docs=N ...]` 센티널이 출력되고, 마지막에 `[SUMMARY: sets=2 pairs=1 overlapping=1]`이 표시됩니다.
3. **작업 착수.** 병렬로 진행하기로 결정한 각 작업을 고유한 활동 브랜치와 독립된 작업 워크트리에서 시작합니다
   (`uv run devkit worktree start dev-<slug>`,
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
4. **작업 등록.** 각 작업 워크트리 디렉터리에서 해당 작업을 등록합니다.

   ```sh
   uv run devkit spec scope register --spec <dir>
   ```

   레지스트리는 선언된 범위와 Git 추적 기반의 관찰 범위를 함께 저장하고, 해당 워크트리의 소유자 토큰을 1회 출력합니다.
5. **계획 변경 시 갱신.** 작업 진행 중 `tasks.md`나 `reconcile.md`를 수정할 때마다 범위를 갱신합니다.

   ```sh
   uv run devkit spec scope update --spec <dir>
   ```

   갱신 결과로 `[SCOPE_ACK: status=applied ... overlaps=N ...]` 센티널과 함께 겹치는 작업 기록이 반환됩니다. 범위 중첩이 감지되더라도 쓰기 작업이 차단되거나 거부되지 않으며, 이는 병렬 작업 일정 조율을 위한 참고 정보로 제공됩니다.
6. **통합 순서 결정.** `uv run devkit spec scope query`를 실행하여 등록된 전체 작업 목록과 현재 워크트리가 다른 작업들과 중첩되는 내역을 확인합니다. 범위가 겹치는 작업들은 순차적으로 차례차례 통합하십시오.
7. **작업 완료.** `devkit worktree finish`를 실행하여 브랜치를 통합하고 워크트리를 제거합니다. 완료 후속 정리 단계에서 해당 워크트리의 범위 등록 정보가 자동으로 삭제되며, 다른 작업의 기록은 온전히 유지됩니다.

## "unresolved" 항목의 의미

실제 코드 경로로 변환할 수 없는 입력 항목은 사유와 함께 미해결(unresolved) 상태로 집계됩니다(예: `entrypoints` 정보가 누락된 capability 대상의 경우 `reason=no-entrypoints`, 계획 단계에만 존재하는 문서, 면제된 대상, 실제 존재하지 않는 파일 등). unresolved 상태가 결코 "충돌이나 중첩이 없음"을 의미하지는 않습니다. 대상 capability 규격에 `entrypoints`를 충실히 기재해 둘수록 범위 대조 결과가 훨씬 정밀해집니다.

## 문제가 생겼을 때

- **`SPEC_SCOPE_TOKEN_EXISTS`:** 해당 워크트리에 이미 등록된 작업이 있습니다. 최초 등록 기록과 토큰이 그대로 유지되므로 `update` 명령으로 계속 진행하십시오.
- **`SPEC_SCOPE_TOKEN_MISSING`:** 해당 워크트리에 등록된 작업이 없습니다. 아무것도 저장되지 않으며, 해당 작업은 레지스트리에 참여하지 않은 채로 진행됩니다.
- **`SPEC_SCOPE_STALE_REVISION` 및 `[SCOPE_ACK: status=stale ...]`: **정보를 읽은 시점과 기록을 쓰려는 시점 사이에 레지스트리가 변경되었습니다. 변경 사항이 반영되지 않았으므로 `update`를 다시 실행하십시오.
- **`SPEC_SCOPE_TIMEOUT` 및 `status=timeout`: **파일 잠금 획득이나 Git 실행에 너무 오랜 시간이 걸렸습니다. 동일한 요청 ID로 다시 시도하십시오(`devkit spec scope update --spec <dir> --request-id <id>`). 이미 정상 반영된 갱신 요청이라면 중복 쓰기 없이 저장된 기록을 바탕으로 즉시 응답합니다.
- **워크트리가 삭제된 후에도 레지스트리 기록이 남아 있는 경우:** 워크트리 정리 단계가 실패했거나 `finish` 절차 없이 워크트리가 강제 삭제된 경우입니다. 기본 체크아웃에서 `uv run devkit spec scope sweep --apply`를 실행하십시오. 리비전 변동이 없는 유효하지 않은 기록은 안전하게 정리되며(`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`), 리비전이 변경된 기록은 보존된 채 `SPEC_SCOPE_STALE_REVISION`으로 보고됩니다.

## 최종 결과

실행 중인 모든 작업의 등록 정보는 항상 최신 범위를 반영하며, 각 작업 쌍이 공유하는 문서와 코드 경로뿐 아니라 불확실한 미지의 범위까지 명확히 파악할 수 있습니다. 어떤 작업도 불필요하게 대기열에 묶여 차단되지 않으며, 완료된 작업은 잔여 기록을 남기지 않습니다. 범위 중첩 증거는 선언된 명세와 Git의 관찰 결과를 종합한 분석일 뿐, 실제 Git 병합 충돌이나 완벽한 독립성을 단정하는 것은 아닙니다.
