---
sources:
  ADR-package-split-and-namespaces: null
  CAP-DIST-agent-projections: null
  CAP-DIST-content-packages: null
  CAP-DIST-context-and-playbooks: null
  CAP-DIST-in-repo-bundles: null
  CAP-DIST-manifest-spec: null
  CAP-DIST-sync-and-transactions: null
  CAP-DIST-workspace-ownership: null
  UC-reconcile-living-spec-drift: null
  UC-route-development-intent: null
title: 배포
translated_from: en/areas/distribution.md@2ed640299d6b563e
---

# 배포

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
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

배포(distribution)는 에이전트 자산(스킬, 서브에이전트, 지침, 플레이북, 규칙, 워크플로, 게이트, 훅, 문서)이 Python
패키지에서 저장소로, 그리고 각 코딩 에이전트의 고유 디렉터리로 옮겨지는 과정입니다. `uv`로 패키지를 설치하고
`.devkit/config.toml`에서 번들을 고른 뒤 `uv run devkit sync`를 실행합니다. 이 명령은 관리 사본, 네이티브 프로젝션,
커밋되는 설치 기록을 하나의 트랜잭션으로 씁니다. 번들, sync, 설치 기록이라는 용어는 [개념](../concepts.md)에서
설명합니다.

모델을 한 문단으로 정리하면 이렇습니다. **번들**(bundle)은 `bundle.toml` 매니페스트가 있는 디렉터리이며,
`devkit.bundles` 엔트리 포인트로 번들을 등록하는 wheel에 담겨 배포됩니다. wheel을 설치하면 번들은 *사용 가능*
상태가 되고, `config.toml`이 번들을 지정하거나 번들이 `auto_select`를 선언하면 *선택*됩니다. `devkit sync`는 선택된
프리셋(preset)을 배치하고, 에이전트마다 스킬과 서브에이전트를 프로젝션하며, 자신이 소유한 모든 파일을
`.devkit/installation.json`에 기록합니다.

## devkit 설치와 번들 선택

dev 의존성에는 devkit 요구사항을 정확히 하나만 선언합니다. 배포 기능만 원하면 `devkit-dist`, 하네스(규칙,
워크플로, 커밋 게이트, 워크트리, 통합)까지 원하면 `devkit-agt`입니다. `devkit-agt`는 같은 버전의 `devkit-dist`에
의존하므로 둘을 함께 선언하지 않습니다(`ADR-package-split-and-namespaces`). 도구는 항상 프로젝트 환경에서
`uv run devkit ...`으로 실행합니다. 전역으로 설치한 도구는 프로젝트의 콘텐츠 패키지를 보지 못합니다. 이미 코드가 있는
저장소에 devkit을 도입하는 과정은 여정 [기존 저장소에 도입하기](../journeys/adopt-in-an-existing-repository.md)에서
다룹니다.

```bash
uv run devkit sync               # deploys auto-selected bundles (devkit, advisory, harness)
uv run devkit add starter        # selects a bundle that is not auto-selected, then syncs
uv run devkit add advisory:python  # joins another preset of a bundle
uv run devkit remove starter     # deselects; unchanged deployed files are removed
```

선택할 때 알아 두면 좋은 점은 다음과 같습니다.

- `devkit add`는 *확정된* 프리셋 이름을 기록하므로, 업스트림에서 `default_preset`이 바뀌어도 명시적으로 고른 선택은
  바뀌지 않습니다. 항목이 없는 자동 선택 번들은 현재 기본값을 따릅니다.
- 원하지 않는 자동 선택 번들은 `devkit remove <bundle>`로 제외하며, 이 명령은 `<bundle> = false`를 씁니다.
- 매 sync는 설치되었지만 선택되지 않은 번들을 `unselected` 아래에 나열하고, 새 번들이 생기면 클론마다 한 번
  `BUNDLE_UNSELECTED` 알림이 뜹니다.
- 업그레이드는 `uv lock --upgrade-package <package>` 후 `uv run devkit sync`로 합니다. 제거는 항상 명시적입니다.
  패키지가 사라진 배치 번들이 있으면 커밋된 파일을 지우는 대신 sync가 실패합니다(`SELECTION_INVALID`).

내장 번들(`devkit`, `advisory`, `git-commits`, `harness`, `authoring`)과 `devkit-catalog`의 옵트인 번들
`response-style`, `maintenance`는
[CAP-DIST-content-packages](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)에
콘텐츠 패키지를 다른 콘텐츠 패키지 위에 쌓을 때의 의존성 규칙과 함께 정리되어 있습니다.

## sync가 쓰는 것과 커밋할 것

| 경로 | 소유자 | 커밋 여부 |
| --- | --- | --- |
| `.devkit/config.toml` | 사용자 | 예 |
| `.devkit/installation.json` (설치 기록) | devkit | 예 |
| `.devkit/overrides/` | 사용자 | 예 |
| 루트 `AGENTS.md` | 사용자(`DEVKIT:START/END` 블록 제외) | 예 |
| 시드 파일(한 번만 쓰이는 파일, 예: docs 골격) | 첫 기록 이후 사용자 | 예 |
| `.devkit/managed/`, `.devkit/transient/` | devkit | 아니요(무시됨) |
| `.agents/`, `.claude/`, `.codex/` 프로젝션 | devkit | 저장소가 결정 |

devkit은 설치 기록(receipt)에 기록된 파일만 건드립니다. 기록되지 않은 기존 파일에 쓰기가 계획되면, 그 파일이 이미
동일한 경우가 아니라면 한 바이트도 쓰기 전에 sync가 멈춥니다(`SYNC_CONFLICT`). devkit이 여전히 배치하려는 파일을
사용자가 수정했을 때도 `SYNC_CONFLICT`이며, 더는 배치하지 않는 파일은 고아 파일로 디스크에 남습니다(`ORPHAN_LEFT`).
`CLAUDE.md`는 절대 쓰지 않으므로 직접 `AGENTS.md`를 가리키게 하십시오. 자세한 내용은
[CAP-DIST-workspace-ownership](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md) (영어 원문)에
있습니다.

## 클론, 워크트리, CI를 같은 상태로 유지하기

설치 기록, 지침 블록, 시드 파일은 Git으로 공유되고, 관리 사본은 클론마다 다시 만들어집니다.

- 새 클론, 새 작업 워크트리(task worktree), CI는 `uv sync` 다음에 `uv run devkit sync --locked`를 실행합니다. 이
  명령은 무시된 사본을 커밋된 설치 기록대로 복원하기만 합니다. 설치 기록 자체가 바뀌어야 한다면 아무것도 쓰지 않고
  `RECEIPT_STALE`로 `1`을 반환하고 종료합니다. 누군가 번들 소스, 락 파일 또는 선택을 바꾸고 설치 기록을 커밋하지
  않았다는 뜻입니다. 일반 `uv run devkit sync`를 실행해 결과를 커밋하십시오. 에이전트가 재시도로 이 오류를 넘기지
  않습니다.
- `uv run devkit sync --check`는 "대기 중인 변경이 있는가?"를 묻는 읽기 전용 검사이고, `--dry-run`은 계획된 동작을
  보여 줍니다.
- `uv run devkit status`는 설치 상태, 오류, 드리프트를 보고합니다.

## sync가 멈췄을 때

쓰기를 하는 모든 명령은 프로젝트 락을 잡고, 쓰기를 저널에 남기며, 파일을 원자적으로 교체합니다. 그래서 실패하더라도
작업 공간이 반쯤 쓰인 상태로 남지 않습니다.

| 코드 | 일어난 일 | 할 일 |
| --- | --- | --- |
| `LOCK_HELD` | 다른 쓰기 작업이 프로젝트 락을 잡고 있음 | 기다렸다가 다시 실행 |
| `TRANSACTION_PENDING` | 이전 sync가 중단됨 | `uv run devkit recover` |
| `RECOVERY_BLOCKED` | 중단된 sync 이후 파일이 바뀜 | `[FIX]`를 따르고, 남길 내용을 결정 |
| `SYNC_CONFLICT` | 소유되지 않았거나 사용자가 수정한 파일이 걸림 | 파일을 옮기거나 수정 내용을 오버라이드로 전환 |
| `WORKSPACE_UNSAFE` | devkit이 쓰는 위치에 심볼릭 링크나 파일이 있음 | 치움 |
| `HARNESS_ENGINE_MISSING` | `devkit-agt` 없이 규칙, 게이트, 워크플로 자산이 배치됨 | 실행하려면 `devkit-agt` 추가 |

트랜잭션 전체 단계, 알림 목록, sync 후 확장은
[CAP-DIST-sync-and-transactions](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)에
있습니다.

## 포크하지 않고 업스트림 자산 바꾸기

`.devkit/managed/`는 절대 수정하지 않습니다. 자산 하나를 바꾸려면 직접 소유하는 완전한 파일 묶음인 프로젝트
오버라이드(project override)를 만듭니다.

```bash
uv run devkit override create starter:development   # copies the files to .devkit/overrides/starter/
uv run devkit override list                         # tracked overrides and their drift
uv run devkit override diff starter:development     # what upstream changed, what you changed
uv run devkit override accept starter:development   # record the new upstream as your baseline
uv run devkit override remove starter:development   # go back to upstream
```

업스트림이 오버라이드된 자산을 바꾸면 sync가 `OVERRIDE_DRIFT`를 보고합니다. 기본값 `override_drift = "warn"`에서는
계속 진행하며, 오버라이드가 거버넌스 콘텐츠를 가리는 곳에서는 `"block"`으로 설정합니다. 배포된 규칙의 설정을 바꾸려면
오버라이드 대신 `config.toml`의 `[rules]`를 사용합니다.

## 컨텍스트 로드와 플레이북 찾기

시작 파일은 작게 유지하고 지침은 단계적으로 로드합니다
([CAP-DIST-context-and-playbooks](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).

- 루트 `AGENTS.md` 블록에는 방향 안내만 들어 있습니다. 설치된 번들, 컨텍스트 규칙, 진입 스킬, 짧은 지침 포인터입니다.
- `uv run devkit get-context <bundle>`은 번들의 헌장(constitution)과 지침 헤더를 반환합니다. 배치된 모든 스킬에는
  에이전트 컨텍스트마다 번들당 한 번 이 명령을 실행하라는 전제 조건이 붙어 있습니다.
- 플레이북은 `get-context`가 나열하지 않는 가끔 쓰는 절차입니다. 생성된 `devkit-playbook` 스킬을 명시적으로 호출하면
  `uv run devkit playbook search "<query>"`를 실행하고 선택한 본문을 읽습니다.
  `uv run devkit playbook get <bundle>/<playbook>`은 자산 ID나 선언된 별칭(alias)으로 플레이북 하나를 정확히
  반환합니다.

평범한 작업 문구로는 플레이북이 시작되지 않습니다. `spec` 같은 진입 스킬이 접수 단계에서 후보 하나를 제안할 수 있고,
사용자의 확인이 곧 명시적 호출이 됩니다.
[개발 의도 라우팅](../journeys/route-development-intent.md)(`UC-route-development-intent`)과
[Living Spec 드리프트 조정](../journeys/reconcile-living-spec-drift.md)(`UC-reconcile-living-spec-drift`)을
참고하십시오. 검색 순위는 [검색](search.md)에서 설명합니다.

## 스킬과 서브에이전트를 받을 에이전트 고르기

기본적으로 지원되는 모든 에이전트(`codex`, `claude-code`, `antigravity`)가 대상입니다. `config.toml`의 `agents`로
목록을 좁히고, `uv run devkit sync --agent <name>`으로 지정하며, `--no-agents`로 프로젝션(projection)을 끕니다.
스킬은 `.claude/skills/` 또는 공유 디렉터리 `.agents/skills/`에, 서브에이전트는 `.claude/agents/`,
`.codex/agents/` 또는 `.agents/agents/`에 놓입니다. `invocation = "user"`로 선언된 스킬에는 각 에이전트의 네이티브
"명시적 호출 전용" 설정이 적용됩니다. 서브에이전트는 에이전트별 네이티브 파일로 배포되거나, 에이전트마다 렌더링되는
호스트 중립 역할 계약 하나로 배포됩니다. 매트릭스와 역할 계약 형식은
[CAP-DIST-agent-projections](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-agent-projections.md) (영어 원문)에
있습니다.

## 한 체크아웃만의 개인 설정

`.devkit/config.local.toml`은 이 체크아웃에만 적용되는 무시된 파일입니다. 받아들이는 키는 짧은 목록뿐입니다.
`[execution] environment`, `[mcp] register`, `[presentation] language`, `[shared] adapter`, `[playbooks]` 검색
설정, 번들 변수입니다. 그 밖의 키는 `CONFIG_LOCAL_KEY_FORBIDDEN`입니다. 개인 값은 무시된 위치에 있는 스킬, 지침,
서브에이전트, 플레이북의 바이트만 바꿀 수 있으며, 설치 기록은 정규 상태를 유지합니다.
`uv run devkit config show --effective`는 각 값과 그 출처를 보여 주고, `uv run devkit config template`은
`config.toml`에 없는 주석 처리된 템플릿 키를 기존 줄을 바꾸지 않고 추가합니다.

## 번들 작성하기

번들 매니페스트는 자산을 `(kind, id, source)`로 선언하고, 프리셋과 선택적 템플릿 변수를 선언합니다. 소스 디렉터리를
설치하기 전에 `uv run devkit bundle validate <source>`와 `uv run devkit bundle plan <source> --agent <name>`을
실행하십시오.
[CAP-DIST-manifest-spec](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-manifest-spec.md) (영어 원문)의
핵심은 다음과 같습니다.

- 스키마는 엄격합니다. 알 수 없는 키는 오류이며, 슬러그, 버전, 소스 경로를 검증합니다.
- `default_preset`은 `devkit add <bundle>`이 고르는 프리셋이고, `auto_select`는 패키지가 설치되는 즉시 번들을
  배치합니다. 거의 모든 설치자가 원하는 콘텐츠에만 사용하십시오.
- `guidance` 자산은 루트 `AGENTS.md` 블록에 최대 300바이트의 목록 항목을 추가합니다.
- 시드된 `document`는 `target`에 한 번 쓰인 뒤 프로젝트 소유가 됩니다.
- 명시적인 `.md.jinja` 파일은 선언된 `[variables.*]` 입력과 `execution.environment` 값으로 샌드박스에서 렌더링되며,
  일반 Markdown은 그대로 유지됩니다.

### 저장소 고유 자산 배포하기

저장소 전용 규칙, 스킬, 플레이북은 `tools/<repo>-devkit/` 아래에 일반 콘텐츠 패키지를 만들고 devkit 요구사항과 함께
dev 의존성 그룹에 추가합니다. 별도의 로컬 자산 디렉터리는 없습니다. 소스를 수정하고 `uv run devkit sync`를 실행한 뒤,
소스 변경과 갱신된 설치 기록을 함께 커밋합니다. 오래된 설치 기록은 Git 스냅샷 게이트에서 실패하므로, 규칙 수정은 항상
설치 기록과 함께 움직입니다. 레이아웃, `pyproject.toml`, 오버라이드와 저장소 내 번들 중 무엇을 쓸지 정하는 결정
표는
[CAP-DIST-in-repo-bundles](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md) (영어 원문)에
있습니다.

## 이 영역의 기능

| 기능 | 이럴 때 읽습니다 |
| --- | --- |
| `CAP-DIST-content-packages` | wheel, 엔트리 포인트, 설치, 내장 번들, 단독 실행 신호 |
| `CAP-DIST-manifest-spec` | `bundle.toml` 스키마, 자산 종류, 검증, 템플릿 |
| `CAP-DIST-sync-and-transactions` | 설치 기록, 선택, 트랜잭션, locked sync, 로컬 설정 |
| `CAP-DIST-workspace-ownership` | 경로별 소유자, 지침 블록, 시드 파일, 오버라이드와 드리프트 |
| `CAP-DIST-agent-projections` | 에이전트별 위치, 호출 설정, 역할 계약 |
| `CAP-DIST-context-and-playbooks` | `get-context`, 플레이북 검색과 정확한 조회 |
| `CAP-DIST-in-repo-bundles` | 저장소 고유 자산 패키징 |
