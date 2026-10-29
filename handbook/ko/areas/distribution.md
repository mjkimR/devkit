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
translated_from: en/areas/distribution.md@dc4ecbab9acd239a
---

# 배포

<!-- handbook:provenance -->
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

배포(distribution)는 에이전트 자산(스킬, 서브에이전트, 지침, 플레이북, 규칙, 워크플로, 게이트, 훅, 문서 등)을 Python 패키지에서
대상 저장소 및 각 코딩 에이전트의 전용 디렉터리로 배포하고 동기화하는 메커니즘입니다. `uv`로 패키지를 설치하고 `.devkit/config.toml`에서
원하는 번들을 지정한 후 `uv run devkit sync`를 실행합니다. 이 명령은 관리 파일(managed copies), 네이티브 프로젝션(native projections),
커밋 대상인 설치 기록(receipt)을 단일 트랜잭션으로 안전하게 작성합니다. 번들, 동기화(sync), 설치 기록의 기본 개념은
[개념](../concepts.md)을 참고하십시오.

배포 모델의 핵심 구조는 다음과 같습니다. **번들**(bundle)은 `bundle.toml` 매니페스트를 포함한 자산 디렉터리이며, `devkit.bundles`
진입점(entry point)을 선언한 Python wheel 패키지에 담겨 제공됩니다. 해당 wheel을 설치하면 번들이 *사용 가능(available)* 상태가 되며,
`.devkit/config.toml`에 번들을 명시하거나 번들 자체에 `auto_select`가 선언되어 있으면 *선택(selected)* 상태가 됩니다. 이후
`devkit sync`를 실행하면 선택된 프리셋(preset)이 배포되고, 각 코딩 에이전트별 형식에 맞추어 스킬과 서브에이전트가 프로젝션(projection)되며,
배포된 모든 관리 파일의 소유권 정보가 `.devkit/installation.json`(설치 기록)에 기록됩니다.

## devkit 설치와 번들 선택

프로젝트의 개발(dev) 의존성에는 devkit 패키지를 정확히 하나만 선언해야 합니다. 단순 자산 배포 기능만 필요한 경우에는 `devkit-dist`를,
거버넌스 하네스(규칙, 워크플로, 커밋 게이트, 워크트리, 통합 등)까지 필요한 경우에는 `devkit-agt`를 선언합니다. `devkit-agt`는 동일한 버전의
`devkit-dist`에 이미 의존하므로 두 패키지를 동시에 선언하지 마십시오(`ADR-package-split-and-namespaces`). CLI 명령어는 항상 프로젝트
가상환경 내에서 `uv run devkit ...` 형태로 실행하십시오. 시스템에 전역(global)으로 설치된 devkit은 프로젝트의 로컬 콘텐츠 패키지를
인식하지 못합니다. 기존 코드베이스에 devkit을 처음 도입하는 단계별 가이드는
[기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)를 참고하십시오.

```bash
uv run devkit sync               # deploys auto-selected bundles (devkit, advisory, harness)
uv run devkit add starter        # selects a bundle that is not auto-selected, then syncs
uv run devkit add advisory:python  # joins another preset of a bundle
uv run devkit remove starter     # deselects; unchanged deployed files are removed
```

번들을 구성할 때 알아 두면 유용한 사항은 다음과 같습니다.

- `devkit add`는 *최종 확정된(resolved)* 프리셋 이름을 기록하므로, 추후 업스트림 패키지에서 `default_preset` 기본값이 변경되더라도
  기존의 명시적 선택이 영향받지 않습니다. 별도 지정이 없는 자동 선택 번들은 업스트림의 기본 프리셋을 그대로 따릅니다.
- 원치 않는 자동 선택 번들은 `devkit remove <bundle>` 명령어로 비활성화할 수 있으며, 이 경우 설정에 `<bundle> = false`가 기록됩니다.
- `sync` 실행 시 설치는 되어 있으나 선택되지 않은 번들 목록이 `unselected` 항목에 표시되며, 신규 번들이 감지되면 클론당 1회
  `BUNDLE_UNSELECTED` 알림을 출력합니다.
- 패키지 업그레이드는 `uv lock --upgrade-package <package>` 실행 후 `uv run devkit sync`를 수행합니다. 번들 제거는 항상 명시적인 절차를
  따릅니다. 설치된 패키지가 제거되어 더 이상 찾을 수 없는 배포 번들이 있다면, 파일을 임의로 삭제하지 않고 동기화 실패(`SELECTION_INVALID`)를
  보고합니다.

내장 번들(`devkit`, `advisory`, `git-commits`, `harness`, `authoring`)과 `devkit-catalog`의 선택형 번들(`response-style`,
`maintenance`)은
[CAP-DIST-content-packages](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)에
콘텐츠 패키지 간의 계층형 의존성 규칙과 함께 정리되어 있습니다. 방법론 계층도 같은 방식으로 자동 선택 번들을 추가합니다.
`devkit-docs`는 `docs`를, `devkit-spec`은 `spec`을 제공합니다([하네스](harness.md)).

## sync가 쓰는 파일과 커밋 대상

| 경로 | 소유자 | 커밋 여부 |
| --- | --- | --- |
| `.devkit/config.toml` | 사용자 | 예 |
| `.devkit/installation.json` (설치 기록) | devkit | 예 |
| `.devkit/overrides/` | 사용자 | 예 |
| 루트 `AGENTS.md` | 사용자(`DEVKIT:START/END` 관리 블록 제외) | 예 |
| 시드 파일(초기 1회 생성 파일, 예: docs 골격) | 첫 기록 이후 사용자 | 예 |
| `.devkit/managed/`, `.devkit/transient/` | devkit | 아니요(Git 무시 대상) |
| `.agents/`, `.claude/`, `.codex/` 프로젝션 | devkit | 저장소 정책에 따라 결정 |

devkit은 설치 기록(receipt)에 등록된 파일만 안전하게 관리합니다. 설치 기록에 없는 기존 파일이 있는 위치에 새로 쓰기를 시도할 경우,
기존 파일의 내용이 배포 대상과 완전히 일치하지 않는 한 단 1바이트도 수정하지 않고 즉시 동기화를 중단합니다(`SYNC_CONFLICT`). devkit이
관리해야 하는 파일을 사용자가 임의로 수정한 경우에도 `SYNC_CONFLICT` 오류가 발생하며, 배포 대상에서 제외된 이전 파일은 디스크에 고아
파일(orphan)로 보존됩니다(`ORPHAN_LEFT`). devkit은 `CLAUDE.md`를 직접 생성하거나 덮어쓰지 않으므로, 필요한 경우 사용자가 직접
`AGENTS.md`를 참조하도록 설정하십시오. 자세한 내용은
[CAP-DIST-workspace-ownership](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md) (영어 원문)에
있습니다.

## 클론, 워크트리, CI 환경의 정합성 유지하기

설치 기록, 안내 블록, 시드 파일은 Git을 통해 팀 전체에 공유되며, 로컬 관리 사본은 각 클론 환경마다 독립적으로 재생성됩니다.

- 새 저장소 복제본(clone), 새 작업 워크트리, CI 환경에서는 `uv sync` 실행 후 `uv run devkit sync --locked`를 실행합니다.
  `--locked` 옵션은 커밋된 설치 기록을 바탕으로 Git 무시 대상인 로컬 관리 파일들을 그대로 복원하기만 합니다. 만약 설치 기록 자체가 변경되어야
  하는 상황이라면 아무 파일도 쓰지 않고 `RECEIPT_STALE` 오류와 함께 종료 코드 `1`로 실패합니다. 이는 번들 소스, 락 파일, 번들 선택
  설정이 변경되었음에도 갱신된 설치 기록이 커밋되지 않았음을 의미합니다. 이 경우 일반 `uv run devkit sync`를 실행하여 변경 사항을
  커밋하십시오(에이전트가 단순 재시도로 우회할 수 없습니다).
- `uv run devkit sync --check`는 변경 사항이 대기 중인지 확인하는 읽기 전용 검사 명령입니다. 동기화가 필요하면
  `NOT_SYNCHRONIZED`와 함께 종료 코드 `1`로 끝나며, 조치는 `uv run devkit sync`입니다. `--dry-run`은 수행 예정인 파일 작업을 미리
  보여 주며, 커밋 게이트 훅 같은 sync 후 확장이 바꿀 내용도 포함합니다.
- `uv run devkit status`는 현재 설치 상태, 오류, 드리프트 현황을 종합 보고합니다. 설치된 패키지가 읽기 전용 검사를 추가할 수
  있으며, `devkit-agt`가 있으면 망가진 커밋 게이트 훅도 경고합니다([커밋 게이트](gate.md)).

## sync가 중단되었을 때의 복구

쓰기 작업을 수행하는 모든 명령어는 프로젝트 락을 획득하고, 변경 사항을 저널에 기록하며, 파일을 원자적(atomic)으로 교체합니다.
따라서 비정상적으로 종료되더라도 작업 트리가 절반만 쓰인 불완전한 상태로 남지 않습니다.

| 오류 코드 | 원인 상황 | 조치 방법 |
| --- | --- | --- |
| `LOCK_HELD` | 다른 프로세스가 프로젝트 락을 점유 중임 | 실행 종료를 기다린 후 재실행 |
| `TRANSACTION_PENDING` | 이전 sync 작업이 중단되었음 | `uv run devkit recover` 실행 |
| `RECOVERY_BLOCKED` | 중단된 sync 이후 파일이 변경되었음 | `[FIX]` 지침에 따라 유지할 내용을 결정 |
| `SYNC_CONFLICT` | 소유되지 않은 파일이나 사용자 수정 파일이 위치함 | 파일을 이동하거나 수정 내용을 프로젝트 오버라이드로 전환 |
| `WORKSPACE_UNSAFE` | devkit 쓰기 대상 위치에 심볼릭 링크나 기존 파일이 존재함 | 해당 위치의 파일이나 심볼릭 링크를 제거하거나 다른 곳으로 이동 |
| `HARNESS_ENGINE_MISSING` | `devkit-agt` 없이 규칙, 게이트, 워크플로 자산이 배포됨 | 해당 기능을 실행하려면 `devkit-agt`를 의존성에 추가 |

전체 트랜잭션 단계, 알림 목록 및 sync 후 확장 훅은
[CAP-DIST-sync-and-transactions](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)을
참고하십시오.

## 포크 없이 업스트림 자산 수정하기

`.devkit/managed/` 내부 파일은 절대로 직접 편집하지 마십시오. 배포된 자산을 커스터마이징하려면 프로젝트에서 직접 소유하는 완전한 파일 세트인
프로젝트 오버라이드(project override)를 생성합니다.

```bash
uv run devkit override create starter:development   # 파일을 .devkit/overrides/starter/ 디렉터리로 복사
uv run devkit override list                         # 추적 중인 오버라이드 목록과 드리프트 상태 조회
uv run devkit override diff starter:development     # 업스트림 원본 변경점과 사용자 변경점 비교
uv run devkit override accept starter:development   # 최신 업스트림 내용을 새 기준선으로 승인
uv run devkit override remove starter:development   # 오버라이드를 제거하고 업스트림 원본으로 복귀
```

오버라이드된 자산의 원본(업스트림) 내용이 변경되면, 동기화 시 실행할 `override diff`와 `override accept` 명령과 함께
`OVERRIDE_DRIFT`가 보고됩니다. 기본 설정인 `override_drift = "warn"`에서는 경고만 출력하고 계속 진행합니다. 거버넌스 규칙과 같이
중요한 자산을 오버라이드한 경우에는 `"block"`으로 설정하면, 사용자가 결정할 때까지 아무것도 쓰지 않고 동기화를 멈춥니다.
`devkit status`도 같은 정책을 따릅니다. 업스트림 변경을 자신의 파일에 병합한 뒤 `override accept`를 실행하면 새 기준선을 기록하고
한 번에 동기화까지 합니다(`"block"`에서는 다른 오버라이드에 남은 드리프트가 없을 때만). `devkit remove <bundle>`은 번들의
오버라이드 디렉터리를 남겨 두며 `OVERRIDE_RETAINED`로 이를 알립니다. 배포된 규칙의 파라미터나 옵션을 조정할 때는 오버라이드를 만들기보다 `.devkit/config.toml`의 `[rules]` 테이블에서 설정값을 변경하는
방식을 권장합니다.

## 컨텍스트 로드와 플레이북 탐색

초기 로딩 파일의 크기는 작게 유지하고 세부 지침은 단계별로 로드합니다
([CAP-DIST-context-and-playbooks](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).

- 루트 `AGENTS.md` 블록에는 오리엔테이션 안내만 담깁니다: 설치된 번들 목록, 컨텍스트 로딩 규칙, 진입 스킬, 핵심 지침 포인터.
- `uv run devkit get-context <bundle>`은 번들의 헌장(constitution)과 지침 헤더를 반환하며, 번들이 컨텍스트 문서 디렉터리를
  선언했다면 그 안의 프로젝트 파일마다 제목과 요약도 함께 반환합니다(`docs` 번들은 이 방식으로 `docs/steering/`을 보여 줍니다).
  배포된 모든 스킬에는 에이전트 컨텍스트마다 번들당 1회 이 명령을 실행하라는 사전 요건이 선언되어 있습니다.
- 플레이북은 `get-context`에 포함되지 않는 비정기적 절차 가이드입니다. 생성된 `devkit-playbook` 스킬을 명시적으로 호출하면
  `uv run devkit playbook search "<query>"`를 실행하여 적절한 플레이북을 탐색하고 본문을 로드합니다.
  `uv run devkit playbook get <bundle>/<playbook>`은 자산 ID나 선언된 별칭(alias)을 통해 단일 플레이북을 정확히 반환합니다.

일반적인 프롬프트나 작업 지시 문구만으로는 플레이북이 자동으로 실행되지 않습니다. `spec`과 같은 진입 스킬이 접수(intake) 단계에서 적절한
플레이북 후보를 제안할 수 있으며, 사용자의 승인이 있어야만 명시적으로 실행됩니다. 자세한 내용은
[개발 요청 라우팅하기](../journeys/route-development-intent.md)(`UC-route-development-intent`) 및
[Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)(`UC-reconcile-living-spec-drift`)를 참고하십시오.
플레이북 검색 및 랭킹 알고리즘은 [검색](search.md)에 기술되어 있습니다.

## 스킬과 서브에이전트 프로젝션 대상 선택하기

기본적으로 지원되는 모든 코딩 에이전트(`codex`, `claude-code`, `antigravity`)가 프로젝션 대상입니다. `.devkit/config.toml`의 `agents`
목록으로 대상을 제한할 수 있으며, `uv run devkit sync --agent <name>`으로 특정 에이전트만 지정하거나 `--no-agents` 플래그로 프로젝션
생성을 비활성화할 수 있습니다. 스킬 파일은 `.claude/skills/` 또는 공용 `.agents/skills/`에 배치되고, 서브에이전트는 `.claude/agents/`,
`.codex/agents/`, `.agents/agents/`에 배치됩니다. `invocation = "user"`로 선언된 스킬은 각 에이전트 플랫폼 고유의 "명시적 사용자 호출 전용"
설정이 자동 적용됩니다. 서브에이전트는 에이전트별 전용 네이티브 파일로 배포되거나, 호스트 중립적인 단일 역할 계약(role contract)으로부터
에이전트별 형식으로 렌더링되어 배포됩니다. 지원 매트릭스와 역할 계약 규격은
[CAP-DIST-agent-projections](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md) (영어 원문)을
참고하십시오.

기본적으로 역할 계약은 호스트가 부여하는 모델과 추론 강도로 실행됩니다. 직접 정하려면 서브에이전트 모델 수준(subagent model
level)을 지정합니다. `inherit`, `minimal`, `compact`, `standard`, `deep`, `maximal` 중 하나이며, 각각 에이전트별 네이티브 모델과
추론 강도에 대응됩니다. 계약 자체가 수준을 지정할 수 있고(devkit의 `scout`는 `compact`를 요청), 최종 결정은 프로젝트가 추적되는
`[subagents]` 테이블에서 `default_level`, 호스트별 `levels` 재매핑, 역할별 `roles` 오버라이드로 내립니다.

```toml
[subagents]
default_level = "inherit"
[subagents.roles."spec:scout"]
level = "standard"
```

값을 바꾼 뒤에는 `uv run devkit sync`를 실행하십시오. 수준은 자원 프리셋일 뿐 품질을 보장하지 않습니다. 실제로 무엇이 실행될지는
여전히 호스트와 계정이 결정합니다.

## 로컬 체크아웃 전용 개인 설정

`config.toml`의 두 테이블은 개인 취향이 아니라 공유 정책입니다. 위의 `[subagents]`, 그리고 프로젝트 전체의 개발
방식(development approach)을 스펙 주도 전달(`sdd`, 기본값)과 `incubation` 중에서 고르는 `[development] approach`입니다
([하네스](harness.md) 참고). `uv run devkit config show`가 둘 다 보여 줍니다.

`.devkit/config.local.toml`은 현재 로컬 작업 환경(체크아웃)에만 적용되며 Git 추적에서 제외(무시)되는 설정 파일입니다. 이 파일은 지정된 일부
키만 허용합니다: `[execution] environment`, `[mcp] register`, `[presentation] language`, `[shared] adapter`, `[playbooks]`
검색 설정 및 번들 변수입니다. 허용되지 않은 키를 선언하면 `CONFIG_LOCAL_KEY_FORBIDDEN` 오류가 발생합니다. 로컬 개인 설정은 Git 무시 대상인
스킬, 지침, 서브에이전트, 플레이북의 텍스트 내용만 커스터마이징할 수 있으며, 공용 설치 기록(receipt)의 정합성에는 일절 영향을 주지 않습니다.
모든 클론이 같은 값을 가져야 하므로 `[subagents]`와 `[development]`도 이 파일에서는 거부됩니다.
`uv run devkit config show --effective`로 각 설정값과 출처를 확인할 수 있으며, `uv run devkit config template`은 기존 설정을
건드리지 않고 누락된 템플릿 설정 키들을 주석 형태로 채워 넣습니다.

## 번들 작성하기

번들 매니페스트는 자산을 `(kind, id, source)` 형식으로 선언하고, 프리셋과 선택적 템플릿 변수를 정의합니다. 소스 디렉터리를 정식 설치하기
전에 `uv run devkit bundle validate <source>`와 `uv run devkit bundle plan <source> --agent <name>` 명령어로 유효성을 사전에
검증하십시오.
[CAP-DIST-manifest-spec](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-manifest-spec.md) (영어 원문)의
핵심 사항은 다음과 같습니다.

- 매니페스트 스키마는 엄격하게 검증됩니다. 정의되지 않은 알 수 없는 키는 오류로 처리되며, 슬러그(slug), 버전, 소스 파일 경로의 유효성을 엄밀히 검사합니다.
- `default_preset`은 `devkit add <bundle>` 실행 시 기본 적용되는 프리셋이며, `auto_select`는 패키지 설치 즉시 번들을 자동 배포하도록 지정합니다.
  대다수의 사용자가 기본적으로 필요로 하는 핵심 자산에만 신중히 적용하십시오.
- `guidance` 자산은 루트 `AGENTS.md`의 관리 블록 내에 최대 300바이트 분량의 요약 안내 항목을 추가합니다.
- 시드 파일(seed document)은 지정된 `target` 경로에 최초 1회만 생성된 후 프로젝트 자체의 소유가 됩니다.
- `context_documents`는 `get-context`가 Markdown 제목과 요약을 나열할 프로젝트 디렉터리 하나를 지정합니다.
- 역할 계약은 네이티브 모델·추론 강도 필드 대신 `level`을 지정할 수 있으며, 둘을 함께 쓰면 유효하지 않습니다.
- 템플릿 파일(`.md.jinja`)은 선언된 `[variables.*]` 변수와 `execution.environment` 설정을 바탕으로 안전한 샌드박스 환경에서 렌더링되며,
  일반 Markdown 파일은 원문 그대로 복사됩니다.

### 저장소 전용 자산 패키징하기

저장소 고유의 거버넌스 규칙, 스킬, 플레이북을 관리할 때는 `tools/<repo>-devkit/` 경로에 독립된 콘텐츠 패키지를 생성하고, 기존 devkit 의존성과
나란히 dev 의존성 그룹에 등록합니다(별도의 비패키지 로컬 자산 디렉터리는 지원하지 않습니다). 패키지 소스를 수정한 후 `uv run devkit sync`를
실행하고, 소스 코드 변경과 함께 갱신된 설치 기록을 반드시 한 커밋으로 묶어 커밋하십시오. 설치 기록이 최신 상태가 아니면 Git 스냅샷 게이트
검사에서 실패하므로, 규칙 변경은 항상 설치 기록과 함께 동기화되어야 합니다. 패키지 디렉터리 레이아웃, `pyproject.toml` 설정 예시 및 오버라이드와
저장소 내 번들 간의 선택 기준은
[CAP-DIST-in-repo-bundles](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md) (영어 원문)에
기술되어 있습니다.

## 이 영역의 주요 기능 명세

| 기능 명세 | 참고 시점 |
| --- | --- |
| `CAP-DIST-content-packages` | wheel 패키징, 진입점(entry points), 패키지 설치, 내장 번들, 단독 실행 신호 |
| `CAP-DIST-manifest-spec` | `bundle.toml` 매니페스트 스키마, 자산 종류, 유효성 검증, 템플릿 처리 |
| `CAP-DIST-sync-and-transactions` | 설치 기록 구조, 번들 선택, 원자적 트랜잭션, locked sync, 공유 정책과 로컬 설정 |
| `CAP-DIST-workspace-ownership` | 경로별 소유권 구분, 안내 블록, 시드 파일, 오버라이드 및 드리프트 정책 |
| `CAP-DIST-agent-projections` | 에이전트별 프로젝션 경로, 호출 모드 설정, 역할 계약 규격, 서브에이전트 모델 수준 |
| `CAP-DIST-context-and-playbooks` | `get-context` 프로토콜, 플레이북 검색 및 정확한 조회 |
| `CAP-DIST-in-repo-bundles` | 저장소 자체 자산의 패키징 및 배포 |
