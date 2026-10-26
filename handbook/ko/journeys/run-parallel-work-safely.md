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
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

여러분(또는 오케스트레이션하는 에이전트)이 둘 이상의 제안(proposal)이나 스펙 번들을 동시에 진행하면, 같은 문서나
코드를 건드려 통합 시점에 충돌할 위험이 있습니다. devkit은 아무것도 잠그지 않습니다. 대신 `devkit spec scope`가
작업 전과 작업 중에 각 작업이 공유하는 Living Spec 문서와 코드 경로, 그리고 범위 중 아직 알 수 없는 부분이 얼마나
되는지를 보여 주므로, 무엇을 병렬로 실행하고 어떤 순서로 반영할지 여러분이 결정할 수 있습니다.

작업 워크트리(task worktree)와 활동 브랜치(activity branch)는 [개념](../concepts.md)에서, 레지스트리 자체는
[협업 영역](../areas/collaboration.md)에서 설명합니다.

출처: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/collaboration/UC-run-parallel-work-safely.md) (영어 원문),
계약 [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md).

## 시작하기 전에

- 저장소가 Git 저장소이고 `devkit-spec`이 설치되어 있습니다.
- 각 작업은 자기 번들에 범위를 선언합니다. `target-docs.md` 또는 `reconcile.md`의 대상, `tasks.md`의 `_Boundary`
  항목, 그리고 대상 문서의 `entrypoints`입니다. 진입점(entrypoint)은 문서를 코드 경로로 바꿔 줍니다
  ([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)).
  `specs/` 아래의 `_Boundary` 항목은 제외되지만, 다른 스펙 번들의 피드백 파일을 정확히 가리키는 경로
  (`specs/**/feedback/<name>.md`)는 예외입니다. 이 경로는 코드로 수집되므로, 같은 피드백 파일을 해결하는 두 작업은
  그 파일에서 겹칩니다.
- 레지스트리는 Git 공통 디렉터리에 있으므로, 저장소의 모든 워크트리가 별도 설정 없이 이를 공유합니다.

## 단계별 진행

1. **Git 정책을 읽어** 어떤 활동이 자기 워크트리를 갖는지 확인합니다.

   ```sh
   uv run devkit spec policy     # look at [GIT_POLICY: worktree=...]
   ```

   [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)를
   참고하십시오.
2. **아무것도 시작하기 전에 계획된 범위를 비교합니다.** 이 명령은 선언만 읽고 아무것도 쓰지 않습니다.

   ```sh
   uv run devkit spec scope compare --proposal <a> --proposal <b>
   uv run devkit spec scope compare --spec <dir-a> --spec <dir-b>
   ```

   각 쌍마다 `[EVIDENCE: <path> ... kind=doc|code ...]` 줄이 딸린 `[PAIR: ... docs=N ...]` 줄이 나오고, 이어서
   `[SUMMARY: sets=2 pairs=1 overlapping=1]`이 나옵니다.
3. **병렬로 실행하기로 정한 작업을 시작합니다.** 각 작업은 자기 활동 브랜치에서 자기 작업 워크트리를 갖습니다
   (`uv run devkit worktree start dev-<slug>`,
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
4. **각 작업을 자기 워크트리에서 등록합니다.**

   ```sh
   uv run devkit spec scope register --spec <dir>
   ```

   레지스트리는 선언된 범위와 Git에서 관찰한 범위를 저장하고, 워크트리의 소유자 토큰을 한 번 출력합니다.
5. **계획이 바뀌면 갱신합니다.** 작업이 `tasks.md`나 `reconcile.md`를 쓸 때마다 다음을 실행합니다.

   ```sh
   uv run devkit spec scope update --spec <dir>
   ```

   결과는 `[SCOPE_ACK: status=applied ... overlaps=N ...]`와 겹치는 기록들입니다. 겹침은 쓰기를 허용하거나 거부하지
   않으며, 일정 조정을 위한 정보입니다.
6. **통합 순서를 정합니다.** `uv run devkit spec scope query`는 기록 목록과 이 워크트리가 다른 워크트리와 겹치는
   부분을 보여 줍니다. 겹치는 작업은 하나씩 차례로 통합하십시오.
7. **마무리합니다.** `devkit worktree finish`가 브랜치를 통합하고 워크트리를 제거하며, 마무리 후 정리 작업이 그
   워크트리의 범위 기록을 지웁니다. 다른 기록은 남습니다.

## "unresolved" 읽는 법

경로로 바꿀 수 없는 입력은 이유와 함께 unresolved로 집계됩니다(예: `entrypoints`가 없는 capability 대상에 대한
`reason=no-entrypoints`, 계획만 된 문서, 면제된 대상, 없는 파일). unresolved는 결코 "겹침 없음"을 뜻하지 않습니다.
대상 capability에 `entrypoints`를 추가하면 비교가 더 정확해집니다.

## 문제가 생겼을 때

- **`SPEC_SCOPE_TOKEN_EXISTS`.** 이 워크트리가 이미 작업을 등록했습니다. 첫 기록과 토큰은 유지되니 `update`로
  계속하십시오.
- **`SPEC_SCOPE_TOKEN_MISSING`.** 이 워크트리는 아무것도 등록하지 않았습니다. 아무것도 쓰이지 않으며, 그 작업은
  레지스트리에 참여하지 않을 뿐입니다.
- **`[SCOPE_ACK: status=stale ...]`와 함께 `SPEC_SCOPE_STALE_REVISION`.** 읽은 시점과 쓴 시점 사이에 기록이
  바뀌었습니다. 아무것도 쓰이지 않았으니 `update`를 다시 실행하십시오.
- **`status=timeout`과 함께 `SPEC_SCOPE_TIMEOUT`.** 잠금이나 Git이 너무 오래 걸렸습니다. 같은 요청 ID로
  재시도하십시오(`devkit spec scope update --spec <dir> --request-id <id>`). 이미 적용된 갱신은 두 번 쓰지 않고
  저장된 기록으로 응답합니다.
- **기록이 워크트리보다 오래 남습니다**(정리가 실패했거나, finish 없이 워크트리를 제거한 경우). 베이스
  체크아웃에서 `uv run devkit spec scope sweep --apply`를 실행하십시오. 리비전이 바뀌지 않은 오래된 기록은
  제거되고(`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`), 리비전이 바뀐 기록은 유지된 채
  `SPEC_SCOPE_STALE_REVISION`으로 보고됩니다.

## 결과

실행 중인 각 작업의 기록은 최신 범위를 반영하고, 모든 쌍이 공유하는 문서와 코드, 그리고 알 수 없는 부분의 크기를
알게 되며, 어떤 작업도 차단되지 않았고, 끝난 작업은 기록을 남기지 않습니다. 겹침 증거는 선언과 Git 관찰을 결합한
것일 뿐, 머지 충돌도 독립성도 증명하지 않습니다.
