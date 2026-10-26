---
sources:
  CAP-GOV-evaluation-lifecycle: null
  CAP-HARN-agent-guidance: null
  CAP-WT-task-worktrees: null
  UC-resolve-stale-activity-branches: null
title: 오래된 활동 브랜치 정리하기
translated_from: en/journeys/resolve-stale-activity-branches.md@3114192e67747fb5
---

# 오래된 활동 브랜치 정리하기

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

모든 Planning 작업은 `plan-<slug>` 브랜치에서, 모든 Development 작업은 `dev-<slug>` 브랜치에서 진행됩니다. 이
브랜치들은 만료되지 않습니다. 아무도 움직이지 않는 브랜치는 그저 "진행 중"으로 남습니다. 이 여정은 에이전트가
프로젝트가 허용하는 기간보다 오래 멈춰 있는 브랜치를 찾아, 각각을 재개, 폐기, 유지 중 하나로 여러분이 결정하게
하는 과정을 보여 줍니다. devkit은 스스로 아무것도 삭제하지 않습니다.

활동 브랜치(activity branch)와 작업 워크트리(task worktree)는 [개념](../concepts.md)과
[워크트리 영역](../areas/worktree.md)을 참고하십시오.

출처: [`UC-resolve-stale-activity-branches`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-resolve-stale-activity-branches.md) (영어 원문),
계약 [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)
("Stale Branches" 절).

## 시작하기 전에

- `devkit-agt`가 설치되어 있고, 베이스 체크아웃에서 작업합니다.
- 다른 곳에서 만든 브랜치를 가져와(`git fetch`) 둡니다. devkit은 아무것도 가져오지 않습니다.
- 마지막 활동에는 풀 리퀘스트 갱신도 포함되므로 GitHub CLI에 로그인되어 있어야 합니다(`gh auth status`).
- 기준값은 `.devkit/config.toml`의 `[worktree] stale_after`이며, `"<N>d"` 또는 `"<N>w"` 형식이고 기본값은
  `"14d"`입니다.

## 단계별 진행

1. **보고서를 실행합니다.** 단독으로 실행하거나 작업 공간 전체의 위생(hygiene) 검사의 일부로 실행합니다.

   ```sh
   uv run devkit worktree status --stale
   uv run devkit rules check -p hygiene     # same warnings, via the worktree-stale extension
   ```

   `feedback-hygiene` 플레이북도 이를 실행합니다. 위생 확장은 `hygiene` 페이즈에 속합니다
   ([`CAP-GOV-evaluation-lifecycle`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md) (영어 원문),
   [거버넌스 영역](../areas/governance.md)).
2. **결과를 읽습니다.** 로컬이든 원격 추적이든, 마지막 활동(마지막 커밋과 풀 리퀘스트 마지막 갱신 중 나중 것)이
   `stale_after`보다 오래된 `plan-*` 또는 `dev-*` 브랜치마다 한 줄이 출력되며, 가장 오래 멈춘 것부터 나옵니다.

   ```text
   [STALE_BRANCH: dev-<slug> unit=... last_activity=... pr=open refs=local,origin]
   [SUMMARY: checked=yes branches=... stale=1 stale_after=14d]
   ```

   각 항목은 `WORKTREE_STALE_BRANCH` 경고로도 나오며, 그 `[FIX]`에 재개 명령과 폐기 명령이 적혀 있습니다. 보고서는
   아무것도 바꾸지 않습니다.
3. **결정합니다.** 에이전트는 오래된 브랜치마다 두 경로를 모두 알려 주고, 요청받지 않은 쪽은 택하지 않습니다.
4. **폐기하려면:** 에이전트는 먼저 브랜치의 열린 풀 리퀘스트를 닫고 원격 사본을 삭제한 뒤(devkit은 이를 호출자에게
   맡깁니다), 베이스 체크아웃에서 다음을 실행합니다.

   ```sh
   uv run devkit worktree finish dev-<slug> --discard
   ```

   이 명령은 워크트리를 제거하고 머지되지 않은 브랜치를 삭제한 뒤 `merged=no discarded=yes`가 담긴
   `[WORKTREE_FINISHED: ...]`를 출력합니다.
5. **재개하려면:** 에이전트가 경고에 적힌 명령을 실행합니다. 예를 들면 다음과 같습니다.

   ```sh
   uv run devkit worktree start plan-<slug> --existing-branch plan-<slug> --unit docs/proposals/PROP-<slug>
   ```

   브랜치는 아무것도 초기화되거나 다시 쓰이지 않은 채 워크트리를 얻고, 작업은 `devkit workflow next --unit <dir>`이
   알려 주는 단계(stage)부터 이어집니다.
6. **유지하려면:** 아무것도 하지 않습니다. 다음 보고서가 그 브랜치에 대해 다시 경고합니다.

## 문제가 생겼을 때

- **커밋이나 CI 실행에서 경고가 나오지 않습니다.** 정상입니다. 커밋 게이트(commit gate), CI, 대상을 명시한 실행은
  `linter` 페이즈를 사용하며 브랜치를 판정하지 않습니다. 작업 공간 전체에 대해 위생 검사를 실행하십시오.
- **`WORKTREE_CONFIG_INVALID`.** `stale_after`가 `<N>d`나 `<N>w` 형식이 아닙니다(예: `"2 weeks"`). 보고서는 실행을
  거부하며, 위생 실행에서는 실행 전체를 실패시키지 않고 확장이 `HYGIENE_EXTENSION_FAILED`로 표시됩니다. 값을
  고치십시오.
- **`WORKTREE_STALE_SKIPPED` 알림, `checked=no`.** `gh`가 없거나 로그아웃되어 아무것도 판정하지 못했습니다.
  로그인한 뒤 다시 실행하십시오. 실패가 아닙니다.
- **`WORKTREE_STALE_PR_UNKNOWN`, `pr=unknown`.** `gh pr list`가 실패해서 브랜치를 마지막 커밋만으로 판정했습니다.
- **브랜치에 베이스에 아직 남아 있는 승인된 제안(proposal)이 걸려 있습니다.** 이 브랜치를 폐기하는 것은 종료(close)에
  해당합니다. 대체(supersede)할지 포기(abandon)할지 여러분이 결정하면, 에이전트가 종료 내용(포기라면 거절 ADR과
  승인된 제안의 삭제)을 Backlog 작업으로 베이스에 커밋하고, 그다음에야 브랜치를 폐기합니다
  ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)).
- **브랜치가 원격에만 있습니다.** `[FIX]`에는 `git -C <base> push origin --delete dev-<slug>`만 있고 로컬 폐기는
  없습니다. 원격 사본이 사라지면 남는 것이 없습니다.
- **`WORKTREE_DIRTY`.** 워크트리에 커밋되지 않았거나 추적되지 않는 변경이 있습니다. devkit은 강제로 제거하지
  않습니다. 변경을 어떻게 할지 여러분이 정한 뒤 다시 실행하십시오.
- **`WORKTREE_BASE_ON_BRANCH`.** 브랜치가 `--no-worktree`로 시작되었고 베이스 체크아웃이 아직 그 브랜치에 있습니다.
  `[FIX]`가 베이스를 원래 시작한 브랜치로 되돌립니다. 다시 실행하십시오.
- **`WORKTREE_LOCKED`.** 워크트리가 잠겨 있습니다. `[FIX]`는 `git worktree unlock <path>`이며, 여러분이 동의한
  뒤에만 실행됩니다.

## 결과

결정한 브랜치는 각각 유닛(Unit)이 그대로인 채 워크트리에서 재개되거나, 풀 리퀘스트, 원격 사본, 워크트리와 함께
사라집니다. 유지하기로 한 브랜치는 그대로 남습니다. 거부된 폐기는 아무것도 삭제하지 않습니다.
