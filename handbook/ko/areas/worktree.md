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
translated_from: en/areas/worktree.md@cf91e8fda0493a85
---

# 워크트리

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](../journeys/adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](../journeys/incubate-an-idea.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [선택한 느린 작업 빠르게 하기](../journeys/speed-up-selected-slow-operations.md)
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

`devkit worktree`는 작업의 각 활동에 독립된 브랜치를 할당하고, 작업 성격에 따라 전용 Git 워크트리를 구성하여,
작업 마무리 절차를 단 하나의 결정적인(deterministic) 명령으로 처리합니다(`CAP-WT-task-worktrees`). 모든 단계는
무리하게 강제 실행하지 않고 안전하게 실패(refuse)하도록 설계되어 있으며, 동일한 명령을 다시 실행하면 중단된 지점부터
이어서 진행됩니다. 어떤 작업에 워크트리를 생성할지는 이 모듈이 아니라 상위 방법론 계층(devkit-spec 및 해당 Git 정책)에서
결정합니다. 활동(activity), 유닛(unit), 통합(integration)의 기본 개념은 [개념](../concepts.md)을 참고하세요.

## 명칭 및 경로 규칙

- **활동 브랜치(Activity branch)**: Planning 활동은 `plan-<slug>`, Development 활동은 `dev-<slug>` 형식을 사용합니다.
  slug는 영문 소문자, 숫자, `-`, `_`로 구성되며 전체 브랜치 이름은 최대 64자까지 가능합니다. 모든 관련 명령에는 항상 브랜치
  이름 전체를 전달해야 합니다.
- **작업 워크트리(Task worktree)**: 경로 형식은 `<베이스의 부모 디렉터리>/<베이스 디렉터리명>-wt-<브랜치명>`입니다. 예를 들어
  `devkit` 디렉터리 옆의 `devkit-wt-dev-login` 형태로 생성됩니다. 경로 규칙이 정형화되어 있으므로 모든 세션과 에이전트가
  동일한 경로를 일관되게 계산할 수 있습니다.
- **베이스 체크아웃(Base checkout)**: 메인 작업 트리입니다. `start` 및 `finish` 명령은 여기서 실행하며, `status` 명령은
  어느 디렉터리에서나 실행할 수 있습니다.
- **마커(Marker)**: `start` 명령은 공유 Git 설정에 `branch.<branch>.devkitWorktree` 항목을 기록하여, devkit이 관리하는
  작업 브랜치와 동일한 이름을 가진 일반 브랜치를 명확히 구분합니다.

## 작업 시작

```sh
devkit worktree start dev-login
```

devkit은 로컬이나 연결 가능한 원격 저장소에 이미 존재하는 브랜치에 대한 생성을 거부하고(`WORKTREE_BRANCH_EXISTS`: 이어서
작업할지 묻고, 브랜치의 유닛이 기록되어 있으면 정확한 `--existing-branch` 명령을 제시합니다), 기존 연결 워크트리 내부에서의
중첩 생성을 거부한 뒤(`WORKTREE_NESTED`: 해결 방법은 `-w`로 베이스 체크아웃을 지정한 같은 명령입니다), 베이스 브랜치의 HEAD를
기준으로 새 워크트리를 생성합니다.
새로 생성된 체크아웃에는 베이스의 gitignore 대상 파일들이 누락되어 있으므로, `start` 명령은 다음 설정 작업도 함께 수행합니다.

1. 베이스 체크아웃에 `.devkit/config.local.toml` 파일이 있으면 이를 스냅샷으로 복사합니다(이후 양쪽에서 수정하더라도 상호 전파되지 않습니다).
2. 새로 생성된 워크트리 내에서 `[worktree] setup` 설정(예: `uv sync`)을 실행합니다.
3. `devkit sync --locked`를 실행하여 규칙 검사, 커밋 게이트, `get-context`, 플레이북 실행에 필요한 관리 번들 사본들을
   복원하고, 이어서 선택형 MCP 등록을 위한 `devkit sync --registrations-only`를 실행합니다(`CAP-MCP-runtime-registration`).

setup이나 sync 과정에서 오류가 발생하더라도 워크트리는 그대로 유지되며, 해결 방법이 포함된 경고(`WORKTREE_SETUP_FAILED`,
`WORKTREE_SYNC_FAILED`)가 출력됩니다. 명령 실행이 끝나면 `[NEXT_CMD: cd <path>]` 안내가 출력됩니다. 커밋 게이트(commit gate)는
작업 워크트리 자체의 `.venv` 환경을 최우선으로 사용하여 실행됩니다(`CAP-GATE-commit-gates`).

두 가지 변형 실행 방식이 지원됩니다.

- `devkit worktree start dev-login --no-worktree`: 새 워크트리를 만들지 않고 현재 체크아웃에 바로 브랜치를 생성하며, 커밋되지
  않은 로컬 변경 사항을 그대로 유지합니다. 별도의 setup 명령은 실행되지 않습니다. 해당 디렉터리를 사용하는 모든 세션이 브랜치
  전환의 영향을 받으므로, 동시 세션 간의 작업 격리는 제공되지 않습니다.
- `devkit worktree start dev-login --existing-branch [<remote>/]dev-login --unit <dir>`(유닛은 저장소 기준 상대 경로): 다른 체크아웃, 다른 컴퓨터, 또는
  클라우드 환경 등 외부에서 이미 시작된 브랜치를 이어서 작업할 때 사용합니다. 기존 상태를 임의로 초기화(reset)하지 않습니다.
  devkit이 원격 브랜치를 자동으로 fetch하지는 않으므로 먼저 fetch를 완료해야 합니다. 로컬 복사본이 원격보다 뒤처져 있거나 서로
  갈라진 경우 `WORKTREE_BRANCH_OUT_OF_SYNC` 오류가 발생하며, 설치된 연결 검사기(attach check)를 통해 해당 유닛이 브랜치에
  정상적으로 속해 있는지 확인합니다(`WORKTREE_ATTACH_REFUSED`).

워크플로에서 이러한 시작 방식들을 선택하는 기준은 [개발 요청 라우팅하기](../journeys/route-development-intent.md)
(`UC-route-development-intent`) 여정에 기술되어 있습니다. 분리된 워크트리에서 실행되는 병렬 작업들은 오케스트레이션하는
Host가 비교하고 관찰할 수 있습니다. 자세한 내용은 [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`) 및 [협업](collaboration.md)을 참고하세요.

## 작업 완료 및 정리

Host가 주도하는 워크플로에서 통합은 `devkit integration`을 통해 수행됩니다([통합](integration.md), `CAP-INT-mcp-services`
참고). 이 명령은 사용자의 명시적 승인 후 또는 `auto` 정책 하에서 동일한 병합 및 정리 메커니즘을 사용합니다. 이를 뒷받침하는
핵심 하위 명령은 다음과 같습니다.

```sh
devkit worktree finish dev-login --merge [--local-only]
```

이 명령은 베이스 체크아웃에서 실행됩니다. 커밋되지 않은 변경 사항이나 추적되지 않는 파일이 있는 워크트리는 아무것도 바뀌기
전에 거부되며(`WORKTREE_DIRTY`), 강제로 삭제되는 일은 없습니다. 그렇지 않으면 다음 순서로 엄격하게 진행됩니다.

1. **통합(Integration).** 베이스는 특정 브랜치에 위치해야 하며 작업 트리가 깨끗해야 합니다. 또한 작업 브랜치는 이미 베이스의
   최신 HEAD를 포함하고 있어야 합니다(`WORKTREE_MERGE_NOT_FF`: 베이스 브랜치를 작업 브랜치로 병합해야 하며, 각종 기록에서
   커밋 SHA를 직접 인용하므로 rebase는 절대 사용하지 마십시오). 등록된 완료 가드(finish guard)들이 실행되며, devkit-agt는
   유닛 내에 해결되지 않은 문제나 답변되지 않은 질문이 남아 있는 브랜치의 통합을 거부합니다(`WORKTREE_BLOCKED`). 이후 베이스는
   별도의 체크아웃을 거치지 않고 직접 구성된 병합 커밋을 통해(또는 `merge = "ff-only"` 설정인 경우 fast-forward로) 브랜치
   변경 사항을 반영하며, `--local-only` 플래그가 지정되지 않은 한 업스트림 원격 저장소로 push합니다.
2. **워크트리 제거.** 검사 이후 변경 사항이 생겼다면 여기서도 `WORKTREE_DIRTY`로 중단됩니다.
3. **브랜치 삭제.** `git branch -d` 명령으로 로컬 브랜치를 안전하게 삭제합니다(`delete_branch = false`로 설정된 경우 제외).
4. **완료 후 확장 실행.** devkit-spec의 작업 범위 기록 정리나 전달 완료된 제안서 디렉터리 정리 등 완료 후속(post-finish)
   확장 작업을 실행합니다.

`--merge` 플래그 없이 `finish`를 실행하면 이미 병합이 완료된 브랜치에 대해서만 정리 작업을 수행합니다. squash나 rebase 방식으로
병합된 풀 리퀘스트의 경우 Git 관점에서는 브랜치가 병합되지 않은 상태로 인식되므로, 이러한 브랜치는 사용자의 명시적 승인이 있을 때만
삭제하세요.

작업을 통합하지 않고 폐기하려는 경우(작업 포기, 대체, 태스크 분할 상향 등) `devkit worktree finish dev-login --discard`
명령을 사용합니다. 깨끗한 상태의 워크트리를 제거하고 `git branch -D`로 브랜치를 강제 삭제합니다. 단, 원격 브랜치와 풀 리퀘스트는
직접 닫아야 합니다.

병합 단계 이후에 작업이 거부된 경우, 이미 완료된 단계들이 성공 줄 `[WORKTREE_FINISHED: ...]`가 아닌
`[WORKTREE_FINISH_PARTIAL: ...]` 줄로 출력됩니다. 오류 원인을 해결한 뒤 동일한 명령을 다시 실행하세요.
진행이 차단되거나 중단된 작업의 복구 절차는 [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
(`UC-handle-delivery-problems-and-exceptions`)를, 최종 반영까지의 전체 흐름은
[개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`)를 참고하세요.

## 활성 작업 현황 확인

`devkit worktree status` 명령은 모든 워크트리(브랜치명, HEAD 커밋, 병합 여부, 변경 사항 유무, prune 가능 여부)와
워크트리가 연결되지 않은 채 남아 있는 병합되지 않은 로컬 브랜치 목록을 표시합니다. 이 명령은 저장소 상태를 변경하지 않습니다.
`merged=yes dirty=no` 상태인 연결 워크트리는 `devkit worktree finish <branch>` 명령으로 안전하게 정리할 수 있으며,
병합되지 않았거나 변경 사항이 남아 있거나 prune 가능한 대상은 사용자가 직접 검토하고 결정할 때만 제거됩니다.

### 오래된 브랜치 점검

활동 브랜치는 일정 시간이 지난다고 해서 자동으로 만료되지 않습니다. `devkit worktree status --stale` 명령은 마지막 커밋
시점과 마지막 풀 리퀘스트 갱신 시점을 기준으로 `[worktree] stale_after`(기본값: 14일) 이상 유휴 상태로 방치된 로컬 및
원격 추적 `plan-*`, `dev-*` 브랜치를 탐지하여 보고합니다. 이 기능을 실행하려면 인증된 `gh` CLI가 필요하며, 인증되지 않은 경우
`WORKTREE_STALE_SKIPPED` 알림이 출력됩니다. 오래된 브랜치마다 재개할지 폐기할지 묻는 `WORKTREE_STALE_BRANCH` 경고가
발생합니다. 브랜치의 유닛이 기록되어 있으면 정확한 재개 명령이 해결 방법으로, 폐기 명령은 세부 정보로 안내됩니다. 동일한 점검 결과는 `devkit rules check --phase hygiene` 실행 시에도 보고됩니다.
브랜치가 자동으로 삭제되는 일은 결코 없으며,
[오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)(`UC-resolve-stale-activity-branches`)
여정을 통해 정리 여부를 체계적으로 결정할 수 있습니다.

## 설정 옵션

```toml
[worktree]
pull_request = "auto"   # "required"로 설정하면 `finish --merge` 및 로컬 통합 경로를 거부함
delete_branch = true    # finish 완료 시 병합된 브랜치 삭제
merge = "no-ff"         # 또는 "ff-only"
setup = "uv sync"       # 새 워크트리마다 실행할 초기화 명령 (기본값: 없음)
stale_after = "14d"     # "<N>d" 또는 "<N>w"
```

올바르지 않은 설정값을 지정하면 `WORKTREE_CONFIG_INVALID` 오류가 발생합니다.

## 확장 지점

패키지들은 다음 세 가지 진입점(entry point)을 통해 워크트리 수명 주기에 훅을 연결할 수 있습니다.
`devkit.attach_check`(연결 전 브랜치와 유닛 확인), `devkit.finish_guard`(통합 조건 검사 및 거부), `devkit.post_finish`(성공적인
완료 후 정리)입니다. 확장 로직이 비정상 동작하는 경우, 검사 및 가드 단계에서는 안전을 위해 작업을 즉시 차단(fail closed)하며,
완료 후 단계에서는 경고만 출력합니다.

## 출처

- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문):
  경로, start 변형, finish 단계, status, 설정과 오래된 브랜치.
- [Worktree quick reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/worktree.md):
  명령과 오류 코드.
- 관련 문서: [통합](integration.md), [협업](collaboration.md).
