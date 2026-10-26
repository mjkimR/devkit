---
sources:
  ADR-document-id-aliases: null
  ADR-terminal-statuses-are-historical: null
  CAP-DOCS-document-lookup: null
  CAP-DOCS-document-model: null
  CAP-DOCS-document-search: null
  CAP-DOCS-namespaces: null
  UC-find-the-right-documents: null
  UC-keep-the-living-spec-consistent: null
title: 문서
translated_from: en/areas/documents.md@17d001b4c7d486b4
---

# 문서

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
- [협업](collaboration.md)
- [컴팩트 명령 출력](compact.md)
- [전달](delivery.md)
- [배포](distribution.md)
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

문서(documents) 영역은 devkit-spec이 무엇을 Living Spec 문서로 인식하고 사용자가 이를 어떻게 찾는지 정의합니다. 모든 기능,
유스케이스, 결정, 제안, 스펙, 피드백 기록은 프런트매터에 ID가 선언된 Markdown 파일입니다. devkit은 호출할 때마다 색인을
생성하며, 이를 기반으로 `resolve`, `refs`, `list`, `search` 네 가지 명령을 제공합니다. Living Spec 자체는
[개념](../concepts.md)에서 소개하며, 변경 작업에 필요한 문서를 찾는 엔드투엔드 과정은
[알맞은 문서 찾기](../journeys/find-the-right-documents.md)(`UC-find-the-right-documents`) 여정에서 다룹니다.

## 문서의 판별 기준

다음 조건을 모두 만족해야 문서로 취급됩니다
([CAP-DOCS-document-model](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)).

- `docs/` 또는 `specs/` 디렉터리 아래의 `*.md` 파일이어야 하며, `README.md`, 템플릿, 심볼릭 링크가 아니고 숨김(dot) 디렉터리 아래에
  있지 않아야 합니다.
- 프런트매터의 `id`(조정 기록인 경우 `reconcile_id`)에 올바른 형식의 ID를 선언해야 합니다.

용어집이나 가이드처럼 ID가 없는 파일은 별도 알림 없이 색인 대상에서 제외됩니다. 프런트매터가 손상된 파일은 `SPEC_DOCUMENT_INVALID`
경고와 함께 제외되며, 나머지 모든 문서는 정상적으로 계속 사용할 수 있습니다.

ID 접두사는 문서의 종류를 나타냅니다. `CAP`은 기능(capability), `UC`는 유스케이스(use case), `ARCH`는 아키텍처(architecture), `ADR`은
결정(decision), `PROP`은 제안(proposal), `PADR`은 제안 결정(proposal decision), `SPEC`/`PLAN`/`TASKS`/`REC`는 스펙 번들 파일,
`FB`는 피드백(feedback), `MAT`는 자료(material), `MS`는 마일스톤(milestone)입니다. ID는 저장소 전체에서 고유해야 합니다.
색인은 ID가 선언된 위치와 상관없이 모두 수집하며, 각 파일이 종류에 맞는 올바른 디렉터리에 있는지는 spec 규칙에서 검사합니다.

기능, 유스케이스, 결정, 아키텍처 문서, 마일스톤, 제안, 스펙에는 한두 문장의 영문 `summary`를 작성해야 합니다. 검색의
핵심 단서로 쓰이므로, 제목과 본문은 어떤 언어로 작성해도 무방합니다.

## 다른 문서 참조하기

- 문서는 항상 Markdown 경로가 아니라 전체 ID로 참조해야 합니다. 프런트매터의 관계 필드(`usecases`, `capabilities`,
  `spec`, `plan` 등)에 명시하거나, 본문에서는 단 하나의 ID만 포함하는 인라인 코드 스팬으로 작성합니다.
- 코드 블록, 링크 레이블, HTML 주석, 그 밖의 인라인 코드는 참조로 취급하지 않습니다.
- `proposal`, `decomposed_from`, `supersedes`는 출처 이력을 기록하기 위한 필드이므로 참조 그래프에서 제외됩니다.
- 참조의 유효성(해석 불가, 중복, 잘못된 종류)은 색인이 아니라 spec 규칙이 검사하고 보고합니다. 자세한 내용은
  [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
  (`UC-keep-the-living-spec-consistent`)를 참고하십시오.

### 문서 이름 바꾸기

파일 위치를 옮기고 새 ID를 설정한 뒤, 기존 ID는 `aliases`에 보존합니다. 별칭(alias)은 ID 인자를 받는 모든 곳에서 해당 문서로
정상 해석되며, 이후 `uv run devkit rules fix`를 실행하면 기존 참조를 새 ID로 자동 갱신합니다(`ADR-document-id-aliases`). 두 문서가
동일한 별칭을 선언하면 충돌이 발생하여 두 문서 모두에 보고됩니다.

## 이미 아는 정보로 조회하기

| 현재 알고 있는 정보 | 실행할 명령 |
| --- | --- |
| ID(또는 별칭) | `uv run devkit spec resolve CAP-DOCS-document-model` |
| 특정 문서가 참조하는 대상 목록 | `uv run devkit spec refs <ID>` |
| 특정 문서를 참조하는 대상 목록 | `uv run devkit spec refs <ID> --direction in` |
| 코드 경로 | `uv run devkit spec list capability --file src/engine/` |
| 탐색할 종류, 상태, 영역 | `uv run devkit spec list usecase --status active --area core` |
| 프런트매터 필드 값 | `uv run devkit spec list feedback --where severity=critical -n 0` |

`resolve`는 ID마다 `[DOCUMENT: ...]` 한 줄을 출력하며, 해석하지 못한 ID가 있으면 `SPEC_ID_UNRESOLVED` 또는
`SPEC_ID_DUPLICATE`와 함께 종료 코드 `2`로 끝납니다. `refs`와 `list`는 결과를 페이지 단위로 나누어 출력하므로, 안내되는
`[NEXT_CMD: ...]` 명령을 실행하여 다음 페이지를 조회할 수 있습니다. 모든 명령은 `--format json`을 지원합니다. 세부 옵션,
출력 필드, JSON 키는
[CAP-DOCS-document-lookup](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-lookup.md) (영어 원문)에서
확인할 수 있습니다.

### 이력 문서는 기본적으로 숨겨집니다

목록 조회와 검색 시 `--history` 플래그를 지정하지 않으면 이력 문서는 기본적으로 숨겨집니다. 완료된 스펙 번들의 파일(피드백 제외),
완료 또는 중단된 마일스톤, 종료 상태에 도달한 문서(피드백 `resolved`, `promoted`, `dismissed`, `forwarded`, 결정 `superseded`,
제안 `rejected` 등, `ADR-terminal-statuses-are-historical`)가 이에 해당합니다. `list`는 숨겨진 문서 수를 보고하고, 이를
확인할 수 있는 `[HISTORY_CMD: ...]` 명령을 출력합니다. `--status`로 특정 상태를 직접 지정하면 해당 이력 문서도 함께 표시됩니다.
이력 문서의 ID라 하더라도 조회(`resolve`)는 언제나 정상 처리됩니다.

## 검색 의도만으로 문서 찾기

```bash
uv run devkit spec search "link integrity between documents"
uv run devkit spec search "cache policy" --kind decision --kind capability --history
```

검색어가 문서의 ID, 별칭, 경로, 파일 이름과 정확히 일치하면 해당 문서가 최상단에 고정 표시됩니다. 나머지 검색 결과는 ID 및
영문 요약(어휘 및 의미 유사도 기반)과 제목, 영역, 본문(어휘 유사도 기반)을 종합하여 순위가 매겨집니다. 프로젝트별 선택 사항인
`docs/glossary.yaml`에 용어 동의어를 등록해 두면 검색어가 확장되어 다른 언어로 작성된 용어를 검색할 때 유용합니다.
search 엑스트라 패키지가 설치되지 않은 경우 어휘 기반으로만 순위가 매겨지며, `uv add 'devkit-spec[search]'`를 설치하면
하이브리드 검색 순위를 활용할 수 있습니다. 자세한 내용은
[CAP-DOCS-document-search](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-search.md) (영어 원문)를
참고하십시오. 순위 산정 엔진 자체의 동작 원리는 [검색](search.md)에서 설명합니다.

## 네임스페이스를 활용한 모노레포 지원

각 패키지를 `.devkit/config.toml`에 등록하고, `docs/`와 동일한 디렉터리 구조로 `docs/packages/<name>/` 아래에 패키지별
Living Spec을 구성합니다.

```toml
[[tool.spec.namespaces]]
name = "api"
path = "services/api"
```

네임스페이스는 문서를 *탐색(browse)*하는 범위를 좁혀줄 뿐, 존재하는 문서 자체를 제한하지는 않습니다
([CAP-DOCS-namespaces](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-namespaces.md) (영어 원문)).

- `list`와 `search`는 기본적으로 현재 작업 디렉터리의 네임스페이스 문서와 전역 문서를 함께 보여줍니다. `--namespace <NAME>`으로
  특정 네임스페이스를 지정하거나, `--namespace global`로 전역 문서만 조회하거나, `--all-namespaces`로 모든 네임스페이스의 문서를
  조회할 수 있습니다.
- `resolve`, `refs` 및 참조 유효성 검사 규칙은 네임스페이스를 무시합니다. ID는 저장소 전체에서 고유하게 유지되며, 패키지 경계를
  넘어 자유롭게 참조할 수 있습니다. 패키지 간 교차 영향도를 확인하려면 `--all-namespaces`를 사용하십시오.
- 스펙 번들이나 제안 번들은 프런트매터의 `namespace` 필드에 지정된 네임스페이스에 속하며, 이 필드는 `devkit spec new --namespace`와
  `devkit spec proposal new --namespace` 실행 시 자동으로 기록됩니다.

## 이 영역의 핵심 기능

| 기능 | 문서 확인이 필요한 경우 |
| --- | --- |
| `CAP-DOCS-document-model` | 문서의 정의, ID 규칙, 참조 방식, 별칭, 색인 및 파싱 메모 |
| `CAP-DOCS-document-lookup` | `resolve`, `refs`, `list` 명령의 세부 옵션, 출력 형식, 반환 코드 |
| `CAP-DOCS-document-search` | `devkit spec search`의 후보 선정, 최상단 고정, 용어집, 검색 모드 |
| `CAP-DOCS-namespaces` | 모노레포 네임스페이스 구성 및 범위 선택 |
