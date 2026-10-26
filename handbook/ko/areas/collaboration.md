---
sources:
  CAP-COLL-shared-artifacts: null
  CAP-COLL-work-scope-registry: null
  CAP-DLV-project-policy: null
  CAP-MCP-runtime-registration: null
  CAP-TRACE-code-entrypoints: null
  CAP-WT-task-worktrees: null
  UC-run-parallel-work-safely: null
title: 협업
translated_from: en/areas/collaboration.md@44abadac005cb5c7
---

# 협업

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
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

협업 영역은 여러 작업, 세션, 에이전트가 서로 방해하지 않고 하나의 저장소를 함께 쓸 수 있게 해 주는 것들을 다룹니다.
두 부분으로 이루어집니다.

- **작업 범위 비교**(`CAP-COLL-work-scope-registry`): 작업을 병렬로 실행하기 전과 실행하는 동안, 두 작업이 함께
  건드리는 문서와 코드 경로를 볼 수 있습니다. 이 근거는 일정과 통합 순서를 정하는 데 참고될 뿐, 쓰기를 막지는 않습니다.
- **공유 아티팩트**(shared artifact, `CAP-COLL-shared-artifacts`): 다시 생성할 수 있는 Markdown 보고서(예: 제안
  리뷰)를 위한 7일짜리 불변 저장소로, 저장소에 연결된 모든 워크트리가 읽을 수 있는 정확한 URI로 주소를 지정합니다.

둘 다 저장소의 Git 데이터 옆에 있으므로, 모든 [작업 워크트리](worktree.md)(task worktree)가 설정 없이 이를 공유합니다.
처음부터 끝까지의 이야기는 [병렬 작업을 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`) 여정에 있으며, 여기서 쓰는 용어(워크트리, 스펙 번들, 제안)는
[개념](../concepts.md)에서 설명합니다.

## 병렬 작업을 시작하기 전에 범위 비교하기

작업의 범위는 문서가 선언한 것과 Git이 관찰한 것으로 구성됩니다.

- 문서: 제안의 `target-docs.md` 또는 스펙 번들의 `reconcile.md`에 있는 `targets`
- 코드: `tasks.md`의 `_Boundary` 항목. 번들이 코드를 선언하지 않은 동안에는 대상 capability와 use case의
  `entrypoints`가 후보로 대신 쓰입니다.
- 관찰된 코드: 작업의 워크트리가 분기 지점 이후 바꾼 것(커밋, 스테이징, 미스테이징, 미추적)

계획 중인 둘 이상의 작업이 충돌하는지 보려면 그 선언을 비교합니다. 아무것도 쓰지 않으며 레지스트리나 Git도 관여하지
않습니다.

```sh
devkit spec scope compare --proposal login-flow --spec specs/2026-10/20261020-audit-log
```

각 쌍마다 `[PAIR: ... docs= code= unresolved=]` 줄이 출력되고, 공유되는 경로마다 `[EVIDENCE: ...]` 줄이 뒤따릅니다.
`unresolved` 수는 겹침만큼 주의 깊게 읽으세요. 경로가 될 수 없었던 입력(아직 없는 계획 문서, `entrypoints`가 없는
대상, `N/A`인 `_Boundary`)은 집계되며, 결코 조용히 "겹침 없음"으로 취급되지 않습니다. `[DIFF: ...]` 줄은
`reconcile.md`와 `target-docs.md`가 일치하지 않는다는 뜻이며, devkit은 두 목록을 대신 합치지 않습니다. 경로는
`CAP-TRACE-code-entrypoints`의 리터럴 경로 규칙을 따릅니다.

## 실행 중인 작업을 등록하고 겹침 지켜보기

실행 중인 작업은 저장소의 모든 워크트리가 공유하는 레지스트리에 범위를 보관합니다. 일반적인 워크플로에서는 이 명령을
직접 호출할 일이 드뭅니다. 연결된 워크트리에서 `devkit spec proposal handoff`를 실행하면 새 번들이 등록되고,
`spec-tasks`와 `spec-sync` 스킬이 `tasks.md`와 `reconcile.md`를 쓴 뒤 기록을 갱신합니다. 직접 하려면 다음과 같습니다.

| 하려는 일 | 실행 |
| --- | --- |
| 이 워크트리의 작업 등록(소유자 토큰을 한 번 출력) | `devkit spec scope register --spec <dir>` |
| 모든 기록과 이 워크트리의 겹침 확인 | `devkit spec scope query` |
| 시작하려는 번들을 실행 중인 작업과 대조 | `devkit spec scope query --spec <dir>` |
| 변경 후 범위 다시 수집 | `devkit spec scope update --spec <dir>` |
| 이벤트 기록 읽기 | `devkit spec scope query --history [--task <id>]` |
| 버려진 작업 철회 | `devkit spec scope release -w <worktree>` |
| 워크트리가 사라진 기록 제거 | `devkit spec scope sweep --apply` |

알아 두면 좋은 동작이 몇 가지 있습니다.

- 워크트리 하나는 토큰 하나를 가집니다. 같은 워크트리에서 두 번째 등록은 거부되므로(`SPEC_SCOPE_TOKEN_EXISTS`)
  기록이 고아가 되지 않습니다.
- `update`는 낙관적으로 동작합니다. 토큰과 읽어 온 리비전을 제시하며, 그 사이에 기록이 바뀌었다면
  `SPEC_SCOPE_STALE_REVISION`을 받고 아무것도 쓰이지 않습니다. 업데이트가 타임아웃되어 결과를 보지 못했다면 같은
  `--request-id`로 재시도하세요. 두 번째 쓰기 없이 저장된 응답이 반환됩니다.
- 조회에는 부작용이 없습니다. 디렉터리, 잠금, 파일을 만들지 않습니다. 비어 있거나 일부만 읽을 수 있는 응답은 겹치는
  것이 없다는 증거가 아닙니다.
- 저널(`journal.jsonl`)은 진단용일 뿐입니다. 겹침 판정에는 결코 쓰이지 않으며, 추가에 실패해도
  `SPEC_SCOPE_JOURNAL_UNAVAILABLE` 경고에 그칩니다.
- 작업이 `devkit worktree finish`나 `devkit integration integrate`로 통합되면, devkit-spec의 완료 후 정리가 그 작업의
  기록을 제거하고 넘겨진 제안 디렉터리를 정리합니다. 다른 오래된 기록은 명시적인 `sweep`을 기다립니다.

겹침 근거는 선언과 Git 관찰을 결합한 것입니다. 병합 충돌도 독립성도 증명하지 않으며 배타적 점유도 아닙니다. 무엇을
병렬로 실행할지 결정하는 것은 오케스트레이터의 몫입니다.

### 레지스트리 설정하기

기본적으로 레지스트리는 Git 공통 디렉터리 안의 `devkit-spec-scope/`이며, 네임스페이스는 그 디렉터리의 경로에서
도출됩니다. 여러 클론이나 호스트가 레지스트리 하나를 공유하게 하려면 각각에 `[tool.spec.scope]` 아래 같은 절대 경로
`shared_path`와 `namespace`를 지정하세요(`CAP-DLV-project-policy`가 검증합니다).

```toml
[tool.spec.scope]
shared_path = "/srv/devkit-scope"
namespace = "team"
timeout = 10
```

잠금은 로컬 파일 시스템의 POSIX `flock`에 의존합니다. Windows와 네트워크 파일 시스템은 범위 밖입니다.

## 워크트리 사이에서 보고서 공유하기

공유 아티팩트는 한 워크트리가 만들고 다른 워크트리가 소비하는 보고서를 나릅니다. 예를 들어 Planning 워커가 쓰고
오케스트레이션하는 Host가 읽는 제안 리뷰가 그렇습니다. stdin으로 Markdown을 게시하면 정확한 URI를 돌려받습니다.

```sh
printf '# Review\n' | devkit shared put --kind proposal-review --slug example \
  --source-sha <full-commit-sha> --language en --format json
devkit shared get <artifact-uri> --format json
devkit shared list --kind proposal-review --slug example --format json
```

예상할 수 있는 동작은 다음과 같습니다.

- **불변이며 정확합니다.** 아티팩트의 정체성은 저장소 네임스페이스, kind, slug, 전체 `source_sha`, 언어, 본문
  다이제스트입니다. "최신" 조회나 덮어쓰기는 없으며, 본문이 다르면 새 아티팩트입니다. 같은 유효 내용을 다시 게시하면
  원래 메타데이터가 반환됩니다.
- **7일입니다.** 7일이 지나면 `get`은 `SHARED_ARTIFACT_EXPIRED`로 응답하고 `list`는 이를 생략합니다. 물리적 삭제는
  `devkit shared sweep --apply`로만 일어나며, 그냥 `sweep`은 삭제하지 않고 보고만 합니다.
- **내용은 데이터입니다.** 보고서는 자신이 가리키는 커밋에 대한 근거일 뿐, 결코 지시나 승인이 아닙니다. 보고서에 따라
  행동하기 전에 그 `source_sha`와 언어를 여러분이 실제로 리뷰한 커밋과 비교하세요.
- **로컬 저장소입니다.** 내장 `local` 어댑터는 메인 체크아웃의 `.devkit/.shared/artifacts`(같은 사용자, POSIX,
  모드 0600/0700) 아래에 저장하며, 어떤 워크트리도 그곳에 외부 내용을 두고 있지 않음을 확인한 뒤에만 좁은 범위의
  클론 로컬 Git 제외 규칙을 추가합니다(그렇지 않으면 `SHARED_EXCLUSION_CONFLICT`).

선택형 MCP 런타임이 설치되어 있으면 같은 put, get, list 작업이 로컬 MCP 도구 `shared_put`, `shared_get`,
`shared_list`로 제공됩니다([MCP](mcp.md)와 `CAP-MCP-runtime-registration` 참고). 정리(sweep)는 CLI 작업으로 남습니다.
이 도구들을 기대한 local-orchestrated 호출자가 도구를 찾지 못하면, 조용히 CLI로 대체하지 않고 연결을 복구해 달라고
여러분에게 요청합니다.

### 원격 어댑터 연결하기

`[shared] adapter`(또는 `DEVKIT_SHARED_ADAPTER`)는 `devkit_dist.features.shared.adapters` 진입점 그룹에 등록된
어댑터를 선택합니다. 알 수 없거나 형식이 잘못된 어댑터는 로컬로 대체하지 않고 `SHARED_ADAPTER_UNAVAILABLE`로
실패합니다. 어댑터 작성자는 재사용 가능한 `assert_conformance` 보조 도구를 실행하며, 인증, 네임스페이스 준비, 호스트 간
일관성은 작성자의 몫입니다. 이번 릴리스에는 원격 백엔드가 포함되어 있지 않습니다.

## 출처

- [CAP-COLL-work-scope-registry](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md) (영어 원문):
  범위 입력, 비교, 레지스트리, 명령, 출력과 코드.
- [CAP-COLL-shared-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md):
  아티팩트 정체성, 보존, 저장소와 어댑터 확장.
- [UC-run-parallel-work-safely](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/collaboration/UC-run-parallel-work-safely.md):
  병렬 작업 시나리오.
- 관련 문서: [워크트리](worktree.md)(`CAP-WT-task-worktrees`), [MCP](mcp.md).
