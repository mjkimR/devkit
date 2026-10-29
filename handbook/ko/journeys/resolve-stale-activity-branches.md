---
sources:
  CAP-GOV-evaluation-lifecycle: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-resolve-stale-activity-branches: null
title: 오래된 활동 브랜치 정리하기
translated_from: en/journeys/resolve-stale-activity-branches.md@42d1931fc65cad67
---

# 오래된 활동 브랜치 정리하기

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](incubate-an-idea.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
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

모든 Planning 작업은 `plan-<slug>` 브랜치에서, 모든 Development 작업은 `dev-<slug>` 브랜치에서 격리되어 실행됩니다. 이 브랜치들은 자동으로 만료되지 않으므로, 아무런 진척이 없어도 여전히 '진행 중' 상태로 남게 됩니다. 이 여정에서는 프로젝트에서 허용한 유휴 기간을 초과한 브랜치를 에이전트가 식별하고, 각 브랜치에 대해 재개, 폐기, 유지 여부를 사용자가 판단하여 정리하는 절차를 다룹니다. devkit은 사용자의 지시 없이 브랜치를 임의로 삭제하지 않습니다.

활동 브랜치와 작업 워크트리에 대한 배경 설명은 [개념](../concepts.md) 및 [워크트리 영역](../areas/worktree.md)을 참고하십시오.

출처: [`UC-resolve-stale-activity-branches`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-resolve-stale-activity-branches.md) (영어 원문),
계약 [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md)
("Stale Branches" 절).

## 시작하기 전에

- `devkit-agt`가 설치되어 있으며 기본(베이스) 체크아웃 디렉터리에서 작업합니다.
- 다른 환경에서 생성된 원격 브랜치는 미리 로컬로 가져옵니다(`git fetch`). devkit은 자동으로 브랜치를 패치하지 않습니다.
- 최종 활동 시점 판단에 풀 리퀘스트(PR) 갱신 이력도 반영되므로, GitHub CLI에 로그인되어 있어야 합니다(`gh auth status`).
- 비활성 판정 기준 시간은 `.devkit/config.toml`의 `[worktree] stale_after` 설정값(예: `"<N>d"` 또는 `"<N>w"`)을 따르며, 기본값은 `"14d"`(14일)입니다.

## 단계별 진행

1. **보고서 실행.** 단독으로 상태를 점검하거나 워크스페이스 전체 위생(hygiene) 검사의 일환으로 실행합니다.

   ```sh
   uv run devkit worktree status --stale
   uv run devkit rules check -p hygiene     # same warnings, via the worktree-stale extension
   ```

   `feedback-hygiene` 플레이북을 통해서도 실행할 수 있습니다. 위생 확장 검사는 `hygiene` 페이즈에 속합니다
   ([`CAP-GOV-evaluation-lifecycle`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md) (영어 원문),
   [거버넌스 영역](../areas/governance.md)).
2. **결과 확인.** 로컬 브랜치 또는 원격 추적 브랜치 중 마지막 활동(마지막 커밋 시점과 PR의 최종 갱신 시점 중 더 최근 시각)이 `stale_after` 기준을 넘긴 `plan-*` 또는 `dev-*` 브랜치 목록이 유휴 기간이 긴 순서대로 한 줄씩 출력됩니다.

   ```text
   [STALE_BRANCH: dev-<slug> unit=... last_activity=... pr=open refs=local,origin]
   [SUMMARY: checked=yes branches=... stale=1 stale_after=14d]
   ```

   각 항목은 `WORKTREE_STALE_BRANCH` 경고로도 표시되며, 그 `[REPORT]`는 브랜치를 재개할지 폐기할지 사용자에게 묻습니다. 브랜치의 유닛이
   기록되어 있으면 `[FIX]`가 정확한 재개 명령을 알려 주고, `[DETAIL]`에는 폐기 명령이 안내됩니다. 보고서 출력 단계에서는 어떠한 변경도 일어나지 않습니다.
3. **처리 방식 결정.** 에이전트는 식별된 오래된 브랜치마다 재개와 폐기라는 두 가지 선택지를 제시하며, 사용자의 요청 없이 임의로 진행하지 않습니다.
4. **폐기(Discard) 진행 시:** 에이전트는 우선 해당 브랜치에 열려 있는 PR을 닫고 원격 사본을 삭제한 뒤(원격 정리는 devkit 외부 호출자가 담당), 기본 체크아웃에서 다음 명령을 실행합니다.

   ```sh
   uv run devkit worktree finish dev-<slug> --discard
   ```

   이 명령은 연결된 작업 워크트리를 제거하고 병합되지 않은 로컬 브랜치를 정리한 뒤, `merged=no discarded=yes` 속성을 담은 `[WORKTREE_FINISHED: ...]` 센티널을 출력합니다.
5. **재개(Resume) 진행 시:** 에이전트가 경고의 `[FIX]`에 명시된 명령을 실행합니다. 예시:

   ```sh
   uv run devkit worktree start plan-<slug> --existing-branch plan-<slug> --unit docs/proposals/PROP-<slug>
   ```

   해당 브랜치에 대해 기존 작업 내용이 초기화되거나 손실되지 않은 온전한 워크트리가 연결되며, `devkit workflow next --unit <dir>`이 가리키는 다음 단계부터 작업을 이어나갈 수 있습니다.
6. **유지(Keep) 결정 시:** 별도의 조치를 취하지 않고 그대로 둡니다. 다음 위생 검사 실행 시 동일한 경고가 다시 보고됩니다.

## 문제가 생겼을 때

- **커밋 게이트나 CI 실행 중에 경고가 나타나지 않는 경우:** 이는 의도된 동작입니다. 커밋 게이트, CI, 대상을 직접 지정한 규칙 실행은 `linter` 페이즈만 사용하므로 브랜치 유휴 상태를 검사하지 않습니다. 워크스페이스 전체에 대해 위생 검사를 실행하십시오.
- **`WORKTREE_CONFIG_INVALID` 오류가 발생하는 경우:** `stale_after` 설정값이 `<N>d` 또는 `<N>w` 형식이 아닙니다(예: `"2 weeks"`). 보고서 생성이 거부되며, 위생 검사 실행 시 전체 프로세스를 실패시키지는 않고 해당 확장이 `HYGIENE_EXTENSION_FAILED`로 표시됩니다. 설정값을 올바른 형식으로 수정하십시오.
- **`WORKTREE_STALE_SKIPPED` 알림 및 `checked=no`가 나타나는 경우:** `gh` CLI가 설치되어 있지 않거나 인증이 만료되어 브랜치 상태를 검사하지 못했습니다. 로그인 후 다시 실행하십시오. 이는 치명적인 실패가 아닙니다.
- **`pr=unknown`이 나타나는 경우:** `gh pr list` 실행에 실패하여 PR 상태를 제외하고 최종 커밋 시점만을 기준으로 브랜치를 판정했습니다.
  GitHub 원격 저장소가 있는 저장소에서는 `WORKTREE_STALE_PR_UNKNOWN` 알림도 표시되며, GitHub 원격이 없어 조회가 매번 실패하는
  저장소에서는 로그에만 남깁니다.
- **기본 브랜치에 머지된 승인 제안이 걸려 있는 브랜치인 경우:** 이 브랜치를 폐기하는 것은 작업 종료(close) 절차에 해당합니다. 대체(supersede)할지 폐기(abandon)할지 사용자가 결정하면, 에이전트가 종료 작업(폐기의 경우 기각 ADR 작성 및 승인 제안 삭제)을 Backlog 작업으로서 기본 브랜치에 먼저 커밋한 후 브랜치를 폐기합니다
  ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)).
- **원격 저장소에만 존재하는 브랜치인 경우:** `[FIX]` 지시문에 로컬 폐기 명령 없이 `git -C <base> push origin --delete dev-<slug>` 명령만 제시됩니다. 원격 브랜치가 삭제되면 모든 정리가 완료됩니다.
- **`WORKTREE_DIRTY` 오류가 발생하는 경우:** 해당 작업 워크트리에 커밋되지 않았거나 추적되지 않는 변경 사항이 남아 있습니다. devkit은 어떤 변경도 하기 전에 이를 확인하며, 워크트리를 강제로 삭제하지 않습니다. 변경 사항을 어떻게 처리할지 결정한 뒤 다시 실행하십시오.
- **`WORKTREE_BASE_ON_BRANCH` 오류가 발생하는 경우:** 해당 브랜치가 `--no-worktree` 옵션으로 시작되었으며, 기본 체크아웃이 여전히 그 브랜치에 머물러 있습니다. 안내되는 `[FIX]` 지시문에 따라 기본 체크아웃을 원래 시작 브랜치로 전환한 후 다시 실행하십시오.
- **`WORKTREE_LOCKED` 오류가 발생하는 경우:** 워크트리가 잠겨 있는 상태입니다. 안내되는 `[FIX]`는 `git worktree unlock <path>`이며, 사용자가 명시적으로 동의한 경우에만 실행합니다.

## 최종 결과

정리하기로 결정한 브랜치는 관련 작업 단위(유닛)를 안전하게 유지한 채 작업 워크트리에서 재개되거나, 연결된 PR, 원격 브랜치, 워크트리와 함께 완전히 정리됩니다. 유지를 선택한 브랜치는 변경 없이 그대로 남습니다. 정리가 거부된 경우에는 어떠한 파일이나 브랜치도 삭제되지 않습니다.
