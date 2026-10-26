---
sources:
  CAP-GATE-commit-gates: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
  CAP-WT-task-worktrees: null
  UC-drive-development-to-integration: null
  UC-handle-delivery-problems-and-exceptions: null
  UC-resolve-stale-activity-branches: null
  UC-route-development-intent: null
  UC-run-parallel-work-safely: null
title: 워크트리
translated_from: en/areas/worktree.md@091c1620f04acbe5
---

# 워크트리

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [어드바이저리](advisory.md)
- [에이전트 우선 CLI 도구 키트](cli.md)
- [협업](collaboration.md)
- [컴팩트 명령 출력](compact.md)
- [전달](delivery.md)
- [배포](distribution.md)
- [문서](documents.md)
- [커밋 게이트](gate.md)
- [생성 파일](generated.md)
- [거버넌스 규칙](governance.md)
- [하네스](harness.md)
- [호스트](host.md)
- [통합](integration.md)
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

`devkit worktree`는 작업의 각 활동에 자체 브랜치를, 작업에 필요하면 자체 Git 워크트리를 주고, 작업의 마무리를 하나의
결정적인 명령으로 만듭니다(`CAP-WT-task-worktrees`). 모든 단계는 강제하지 않고 거부하며, 같은 명령을 다시 실행하면
멈춘 곳에서 이어집니다. 어떤 작업이 워크트리를 받을지는 이 모듈이 아니라 방법론 계층(devkit-spec과 그 Git 정책)이
정합니다. 활동, 유닛, 통합은 [개념](../concepts.md)을 참고하세요.

## 이름과 위치

- **활동 브랜치**(activity branch): Planning은 `plan-<slug>`, Development는 `dev-<slug>`입니다. slug는 소문자, 숫자,
  `-`, `_`로 이루어지며 전체 이름은 64자 이하입니다. 명령은 항상 브랜치 이름 전체를 받습니다.
- **작업 워크트리**(task worktree): `<parent of base>/<base name>-wt-<branch>`입니다. 예를 들어 `devkit` 옆의
  `devkit-wt-dev-login`입니다. 경로가 고정되어 있으므로 모든 세션과 에이전트가 같은 경로를 계산합니다.
- **베이스 체크아웃**: 메인 작업 트리입니다. `start`와 `finish`는 여기서 실행하고, `status`는 어디서든 실행됩니다.
- **마커**: `start`는 공유 Git 설정에 `branch.<branch>.devkitWorktree`를 기록하며, 이것으로 작업 브랜치와 같은 이름의
  무관한 브랜치를 구별합니다.

## 작업 시작하기

```sh
devkit worktree start dev-login
```

devkit은 로컬이나 도달 가능한 원격에 이미 있는 브랜치를 거부하고(`WORKTREE_BRANCH_EXISTS`), 연결된 워크트리 안에서의
중첩을 거부한 뒤(`WORKTREE_NESTED`), 베이스 HEAD에서 워크트리를 만듭니다. 새 체크아웃에는 베이스의 무시된 파일이
없으므로 `start`는 다음도 수행합니다.

1. `.devkit/config.local.toml`이 있으면 스냅샷으로 복사합니다(이후 어느 쪽의 편집도 전파되지 않습니다).
2. 워크트리에서 `[worktree] setup`(예: `uv sync`)을 실행합니다.
3. `devkit sync --locked`를 실행해 규칙, 게이트, `get-context`, 플레이북에 필요한 관리 번들 사본을 복원하고, 이어서
   선택형 MCP 항목을 위해 `devkit sync --registrations-only`를 실행합니다(`CAP-MCP-runtime-registration`).

setup이나 sync가 실패하면 수정 방법을 담은 경고(`WORKTREE_SETUP_FAILED`, `WORKTREE_SYNC_FAILED`)가 되며 워크트리는
남습니다. 명령은 `[NEXT_CMD: cd <path>]`로 끝납니다. 커밋 게이트(commit gate)는 워크트리 자체의 `.venv`를 먼저 써서
실행됩니다(`CAP-GATE-commit-gates`).

두 가지 변형이 있습니다.

- `devkit worktree start dev-login --no-worktree`는 현재 체크아웃에 브랜치를 만들고, 커밋하지 않은 변경을 그대로
  가져갑니다. setup은 실행되지 않습니다. 그 디렉터리를 쓰는 모든 세션이 브랜치 전환을 보게 되므로, 동시에 실행되는
  세션 사이의 격리는 없습니다.
- `devkit worktree start dev-login --existing-branch [<remote>/]dev-login --unit <dir>`는 다른 체크아웃, 다른 컴퓨터,
  클라우드 실행 등 다른 곳에서 시작한 브랜치를 이어 갑니다. 아무것도 리셋하지 않습니다. devkit은 fetch하지 않으므로
  먼저 fetch하세요. 뒤처지거나 갈라진 로컬 사본은 `WORKTREE_BRANCH_OUT_OF_SYNC`이며, 설치된 연결 검사가 유닛이 그
  브랜치에 속하는지 확인합니다(`WORKTREE_ATTACH_REFUSED`).

워크플로가 이 가운데 무엇을 고르는지는 [개발 의도 라우팅](../journeys/route-development-intent.md)
(`UC-route-development-intent`) 여정의 일부입니다. 별도 워크트리에서 실행되는 병렬 작업은 공유 레지스트리로 범위를
비교할 수 있습니다. [병렬 작업을 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`)와 [협업](collaboration.md)을 참고하세요.

## 작업 마무리하기

Host가 진행하는 워크플로에서 통합은 `devkit integration`을 거칩니다([통합](integration.md), `CAP-INT-mcp-services`
참고). 이 명령은 여러분의 결정 뒤에, 또는 `auto` 정책에서 같은 병합·정리 기구를 사용합니다. 그 바탕이 되는 명령은
다음과 같습니다.

```sh
devkit worktree finish dev-login --merge [--local-only]
```

베이스 체크아웃에서 실행되며, 다음 순서로 진행합니다.

1. **통합합니다.** 베이스는 브랜치 위에 있고 깨끗해야 하며, 작업 브랜치는 이미 베이스 HEAD를 포함해야 합니다
   (`WORKTREE_MERGE_NOT_FF`: 베이스를 브랜치에 병합하세요. 기록이 커밋 SHA를 인용하므로 rebase는 절대 하지 않습니다).
   설치된 완료 보호 장치가 실행되며, devkit-agt는 유닛에 해결되지 않은 문제나 답하지 않은 질문이 있는 브랜치를
   거부합니다(`WORKTREE_BLOCKED`). 그 다음 베이스는 어떤 체크아웃에도 속하지 않는 곳에서 만든 병합 커밋으로(또는
   `merge = "ff-only"`에서는 fast-forward로) 브랜치를 반영하고, `--local-only`가 아니면 업스트림으로 push합니다.
2. 워크트리를 **제거합니다.** 커밋되지 않았거나 추적되지 않는 변경이 있으면 멈춥니다(`WORKTREE_DIRTY`). 강제로 제거하는
   일은 없습니다.
3. `git branch -d`로 브랜치를 **삭제합니다**(`delete_branch = false`가 아니라면).
4. devkit-spec의 범위 기록과 넘겨진 제안 정리 같은 완료 후 확장을 실행합니다.

`--merge` 없이 `finish`를 실행하면 이미 병합된 브랜치만 정리합니다. squash나 rebase로 병합된 풀 리퀘스트는 Git의 의미로는
브랜치를 병합되지 않은 상태로 남기므로, 그런 브랜치는 여러분의 승인이 있을 때만 제거하세요.

통합하지 않고 작업을 버리려면(포기, 대체, 깊이 상향) `devkit worktree finish dev-login --discard`를 사용합니다. 깨끗한
워크트리를 제거하고 `git branch -D`로 브랜치를 삭제합니다. 원격 브랜치와 풀 리퀘스트는 여러분이 직접 닫아야 합니다.

병합 단계 이후의 거부는 이미 수행한 것을 출력합니다. 원인을 고치고 같은 명령을 다시 실행하세요. 막히거나 중단된 전달의
복구는 [전달 문제와 예외 처리](../journeys/handle-delivery-problems-and-exceptions.md)
(`UC-handle-delivery-problems-and-exceptions`)에서, 반영까지의 전체 흐름은
[개발을 통합까지 진행하기](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`)에서 다룹니다.

## 열려 있는 것 확인하기

`devkit worktree status`는 모든 워크트리(브랜치, HEAD, 병합 여부, dirty 여부, prune 가능 여부)와 워크트리가 없는
병합되지 않은 모든 로컬 브랜치를 나열합니다. 아무것도 바꾸지 않습니다. `merged=yes dirty=no`인 연결된 워크트리는
`devkit worktree finish <branch>`로 정리합니다. 병합되지 않았거나, dirty하거나, prune 가능한 것은 여러분이 결정했을
때만 제거됩니다.

### 오래된 브랜치

활동 브랜치는 저절로 만료되지 않습니다. `devkit worktree status --stale`은 마지막 커밋과 마지막 풀 리퀘스트 갱신을
기준으로 `[worktree] stale_after`(기본값 14일)보다 오래 유휴 상태인 로컬 및 원격 추적 `plan-*`, `dev-*` 브랜치를
보고합니다. 인증된 `gh`가 필요하며, 없으면 `WORKTREE_STALE_SKIPPED` 알림을 받습니다. 오래된 브랜치마다
`WORKTREE_STALE_BRANCH` 경고가 되며, 그 수정 안내에는 재개 명령과 폐기 명령이 담깁니다. 같은 보고는
`devkit rules check --phase hygiene`에도 나타납니다. 자동으로 정리되는 것은 없습니다.
[오래된 활동 브랜치 정리](../journeys/resolve-stale-activity-branches.md)(`UC-resolve-stale-activity-branches`)
여정이 그 결정 과정을 안내합니다.

## 설정

```toml
[worktree]
pull_request = "auto"   # "required" refuses `finish --merge` and the local integration route
delete_branch = true    # finish deletes the merged branch
merge = "no-ff"         # or "ff-only"
setup = "uv sync"       # run in each new worktree (default: none)
stale_after = "14d"     # "<N>d" or "<N>w"
```

잘못된 값은 `WORKTREE_CONFIG_INVALID`입니다.

## 확장 지점

패키지는 진입점을 통해 수명 주기에 연결됩니다. `devkit.attach_check`(연결 전에 브랜치와 유닛 확인),
`devkit.finish_guard`(통합 거부), `devkit.post_finish`(성공적인 완료 후 정리)입니다. 잘못 동작하는 확장은 검사와 보호
장치에서는 닫힌 상태로 실패하고, 완료 후에는 경고만 합니다.

## 출처

- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문):
  경로, start 변형, finish 단계, status, 설정과 오래된 브랜치.
- [Worktree quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/worktree.md):
  명령과 오류 코드.
- 관련 문서: [통합](integration.md), [협업](collaboration.md).
