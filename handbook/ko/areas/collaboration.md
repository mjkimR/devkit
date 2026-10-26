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
translated_from: en/areas/collaboration.md@13c3ea83bffe4d1b
---

# 협업

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

협업(collaboration) 영역은 여러 작업, 세션, 에이전트가 단일 저장소 내에서 상호 간섭 없이 동시에 작업할 수 있도록 지원하는 기능을 다룹니다.
크게 두 가지 구성 요소로 나뉩니다.

- **작업 범위 비교**(`CAP-COLL-work-scope-registry`): 작업을 병렬로 실행하기 전이나 실행하는 동안, 둘 이상의 작업이 동시에
  수정하는 문서 및 코드 경로를 명확히 파악할 수 있습니다. 이 근거 데이터는 작업 스케줄링과 통합 순서를 결정하는 데 활용되며, 파일 쓰기 자체를
  인위적으로 차단하지는 않습니다.
- **공유 아티팩트**(shared artifact, `CAP-COLL-shared-artifacts`): 재생성 가능한 Markdown 보고서(예: 제안 리뷰 등)를 위한
  7일 보존 주기의 불변(immutable) 저장소로, 저장소에 연결된 모든 워크트리에서 일관되게 접근할 수 있는 정확한 고유 URI를 부여합니다.

두 기능 모두 저장소의 Git 공통 메타데이터 영역에 위치하므로, 모든 [작업 워크트리](worktree.md)가 별도 설정 없이 즉시 공유합니다.
전체적인 흐름은 [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)(`UC-run-parallel-work-safely`) 가이드를 참고하십시오.
본문에서 사용되는 기본 용어(워크트리, 스펙 번들, 제안 등)는 [개념](../concepts.md)에서 자세히 설명합니다.

## 병렬 작업을 시작하기 전에 범위 비교하기

작업 범위는 문서에 선언된 명세와 Git이 추적한 실제 변경 사항을 바탕으로 취합됩니다.

- 문서: 제안의 `target-docs.md` 또는 스펙 번들의 `reconcile.md`에 명시된 `targets` 목록
- 코드: 다른 스펙 번들의 피드백 파일 경로를 포함하여 `tasks.md`의 `_Boundary` 항목에 선언된 경로. 번들 내에 아직 코드가 선언되지 않은
  상태라면, 대상 capability 및 유스케이스의 `entrypoints`를 잠정적 후보 경로로 간주합니다.
- Git 추적 코드: 작업 워크트리가 분기점(fork point) 이후 실제로 수정한 파일(커밋됨, 스테이징됨, 미스테이징됨, 추적되지 않음)

계획 중인 둘 이상의 작업 간 충돌 여부를 사전에 확인하려면 각 작업의 선언 범위를 비교합니다. 이때 디스크에 아무것도 기록되지 않으며
레지스트리나 Git 저장소 상태도 변경되지 않습니다.

```sh
devkit spec scope compare --proposal login-flow --spec specs/2026-10/20261020-audit-log
```

비교 대상 쌍마다 `[PAIR: ... docs= code= unresolved=]` 줄이 출력되고, 공유되는 경로마다 `[EVIDENCE: ...]` 줄이 뒤따릅니다.
`unresolved` 개수는 중복(겹침) 항목만큼이나 주의 깊게 살펴봐야 합니다. 실제 경로로 변환할 수 없는 입력(아직 생성되지 않은 계획 문서,
`entrypoints`가 지정되지 않은 대상, `_Boundary`가 `N/A`인 항목 등)도 누락 없이 집계되며, 이를 단순히 "중복 없음"으로 간주하여
무시하지 않습니다. `[DIFF: ...]` 줄은 `reconcile.md`와 `target-docs.md`의 내용이 서로 불일치함을 의미하며, devkit이 이를 임의로
병합하지 않습니다. 모든 경로는 `CAP-TRACE-code-entrypoints`에 정의된 리터럴 경로 규칙을 엄격히 따릅니다.

## 실행 중인 작업을 등록하고 겹침 지켜보기

실행 중인 작업은 저장소의 모든 워크트리가 공유하는 레지스트리에 작업 범위를 보관합니다. 일반적인 워크플로에서는 이 명령어를
직접 호출할 일이 드뭅니다. 연결된 워크트리에서 `devkit spec proposal handoff`를 실행하면 새 번들이 등록되고,
`spec-tasks`와 `spec-sync` 스킬이 `tasks.md`와 `reconcile.md`를 작성한 뒤 기록을 자동으로 갱신합니다. 수동으로 실행할 때는
다음 명령어를 사용합니다.

| 작업 목적 | 실행 명령어 |
| --- | --- |
| 현재 워크트리의 작업 등록(소유자 토큰 1회 출력) | `devkit spec scope register --spec <dir>` |
| 모든 작업 기록과 현재 워크트리의 겹침 현황 확인 | `devkit spec scope query` |
| 시작 예정인 번들과 실행 중인 작업 간의 충돌 검사 | `devkit spec scope query --spec <dir>` |
| 변경 사항 발생 후 작업 범위 재수집 | `devkit spec scope update --spec <dir>` |
| 작업 이벤트 히스토리 조회 | `devkit spec scope query --history [--task <id>]` |
| 중단된 작업의 등록 철회 | `devkit spec scope release -w <worktree>` |
| 워크트리가 삭제된 잔여 기록 정리 | `devkit spec scope sweep --apply` |

알아 두면 유용한 핵심 동작 방식은 다음과 같습니다.

- 워크트리당 하나의 토큰만 보유합니다. 동일한 워크트리에서 중복 등록을 시도하면 거부되므로(`SPEC_SCOPE_TOKEN_EXISTS`)
  기록이 고아 상태로 남지 않습니다.
- `update`는 낙관적 동시성 제어(optimistic concurrency) 방식으로 동작합니다. 토큰과 함께 사전에 읽은 리비전을 제시하며,
  그 사이에 기록이 변경되었다면 `SPEC_SCOPE_STALE_REVISION` 오류와 함께 쓰기 작업이 취소됩니다. 업데이트 도중 타임아웃이 발생하여
  결과를 확인하지 못했다면 동일한 `--request-id`로 재시도하십시오. 추가 쓰기 없이 기존에 저장된 응답이 그대로 반환됩니다.
- 조회 작업은 일체의 부작용(side-effect)을 유발하지 않습니다. 디렉터리, 잠금, 파일을 생성하지 않습니다. 응답이 비어 있거나
  일부만 읽을 수 있는 상태라 하더라도 작업 간에 충돌이 전혀 없음을 보증하는 증거는 아닙니다.
- 저널(`journal.jsonl`)은 단순 진단용입니다. 작업 겹침 여부를 판정하는 데는 전혀 관여하지 않으며, 저널 기록 추가에 실패하더라도
  `SPEC_SCOPE_JOURNAL_UNAVAILABLE` 경고만 출력됩니다.
- 작업이 `devkit worktree finish` 또는 `devkit integration integrate`를 통해 통합되면, devkit-spec의 완료 후 정리 루틴이
  해당 작업의 레지스트리 기록을 제거하고 인계된 제안 디렉터리를 정리합니다. 그 외의 오래된 잔여 기록은 명시적인 `sweep` 실행을 통해 정리합니다.

중복 감지 결과는 문서 선언과 Git 추적 데이터를 결합한 참고 지표입니다. 이는 Git 병합 충돌 가능성이나 완전한 작업 독립성을 단정하는 것이
아니며, 자원에 대한 배타적 점유를 의미하지도 않습니다. 병렬 실행 여부에 대한 최종 판단은 오케스트레이터의 역할입니다.

### 레지스트리 설정하기

기본적으로 레지스트리는 Git 공통 디렉터리 내의 `devkit-spec-scope/`에 위치하며, 네임스페이스는 해당 디렉터리의 절대 경로로부터
도출됩니다. 여러 클론이나 호스트 환경에서 단일 레지스트리를 공유하려면 각 환경의 `[tool.spec.scope]` 테이블 아래에 동일한 절대 경로
`shared_path`와 `namespace`를 지정하십시오(`CAP-DLV-project-policy`가 유효성을 검증합니다).

```toml
[tool.spec.scope]
shared_path = "/srv/devkit-scope"
namespace = "team"
timeout = 10
```

파일 잠금은 로컬 파일 시스템의 POSIX `flock` 메커니즘에 의존합니다. Windows 환경 및 네트워크 파일 시스템(NFS 등)은 지원 대상에서 제외됩니다.

## 워크트리 사이에서 보고서 공유하기

공유 아티팩트는 한 워크트리에서 생성하고 다른 워크트리에서 소비하는 각종 보고서를 전달합니다. 예를 들어 Planning 워커가 작성하고
이를 오케스트레이션하는 Host가 읽는 제안 리뷰 보고서가 이에 해당합니다. stdin을 통해 Markdown 문서를 발행하면 고유한 URI를 반환받습니다.

```sh
printf '# Review\n' | devkit shared put --kind proposal-review --slug example \
  --source-sha <full-commit-sha> --language en --format json
devkit shared get <artifact-uri> --format json
devkit shared list --kind proposal-review --slug example --format json
```

공유 아티팩트의 주요 특성은 다음과 같습니다.

- **불변성과 정확성:** 아티팩트의 식별자는 저장소 네임스페이스, kind, slug, 전체 `source_sha`, 언어 코드, 본문 다이제스트의
  조합으로 결정됩니다. "최신 버전" 조회나 기존 파일 덮어쓰기는 지원하지 않으며, 본문 내용이 다르면 완전히 새로운 아티팩트로 취급됩니다.
  유효 기간 내에 동일한 내용을 다시 게시하면 기존 메타데이터가 그대로 반환됩니다.
- **7일 보존 주기:** 생성 후 7일이 경과하면 `get` 명령어는 `SHARED_ARTIFACT_EXPIRED`로 응답하고 `list` 목록에서 제외됩니다.
  물리적인 파일 삭제는 `devkit shared sweep --apply`를 통해서만 수행되며, 일반 `sweep` 명령어는 실제 삭제 없이 삭제 대상 현황만 보고합니다.
- **데이터로서의 내용:** 아티팩트 보고서는 해당 커밋 시점의 상태를 보여주는 증거 자료일 뿐이며, 그 자체로 실행 지시나 승인을 의미하지 않습니다.
  보고서 내용을 바탕으로 후속 작업을 진행하기 전에, 보고서에 명시된 `source_sha` 및 언어가 실제로 검토한 대상 커밋과 일치하는지 먼저 확인하십시오.
- **로컬 저장소 격리:** 기본 탑재된 `local` 어댑터는 메인 체크아웃의 `.devkit/.shared/artifacts` 디렉터리(동일 사용자 소유, POSIX,
  권한 모드 0600/0700)에 데이터를 저장하며, 어떤 워크트리도 해당 경로에 외부 파일이나 이물질을 두고 있지 않음을 검증한 후에만 좁은 범위의
  클론 로컬 Git 제외 규칙을 추가합니다(그렇지 않은 경우 `SHARED_EXCLUSION_CONFLICT` 오류 발생).

선택형 MCP 런타임이 설치되어 있다면 동일한 put, get, list 작업을 로컬 MCP 도구인 `shared_put`, `shared_get`, `shared_list`로도
수행할 수 있습니다([MCP](mcp.md) 및 `CAP-MCP-runtime-registration` 참고). 대량 정리(sweep)는 CLI 명령어로만 실행됩니다.

### 원격 어댑터 연결하기

`[shared] adapter`(또는 `DEVKIT_SHARED_ADAPTER` 환경 변수)를 통해 `devkit_dist.features.shared.adapters` 진입점 그룹에 등록된
커스텀 어댑터를 선택할 수 있습니다. 알 수 없거나 형식이 잘못된 어댑터가 지정되면 로컬 어댑터로 자동 폴백하지 않고 `SHARED_ADAPTER_UNAVAILABLE`
오류와 함께 즉시 실패합니다. 어댑터 개발자는 재사용 가능한 `assert_conformance` 헬퍼로 적합성을 검증할 수 있으며, 사용자 인증,
네임스페이스 프로비저닝, 분산 호스트 간의 정합성 보장은 어댑터 개발자의 책임입니다. 현재 릴리스에는 기본 원격 백엔드가 포함되어 있지 않습니다.

## 출처

- [CAP-COLL-work-scope-registry](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md) (영어 원문):
  작업 범위 입력 요소, 비교 알고리즘, 레지스트리 아키텍처, CLI 명령어, 출력 규격 및 어드바이저리 코드.
- [CAP-COLL-shared-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md):
  아티팩트 식별 체계, 보존 주기 정책, 로컬 저장소 구조 및 어댑터 확장 규격.
- [UC-run-parallel-work-safely](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/collaboration/UC-run-parallel-work-safely.md):
  안전한 병렬 작업 시나리오.
- 관련 문서: [워크트리](worktree.md)(`CAP-WT-task-worktrees`), [MCP](mcp.md).
