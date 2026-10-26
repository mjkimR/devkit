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
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

문서(documents) 영역은 devkit-spec이 Living Spec 문서가 무엇인지 알고, 그것을 찾게 해 주는 방식입니다. 모든 기능,
유스케이스, 결정, 제안, 스펙, 피드백 기록은 프런트매터에 ID가 있는 Markdown 파일입니다. devkit은 호출할 때마다 이
문서들의 색인을 만들고, 그 위에서 `resolve`, `refs`, `list`, `search` 네 명령을 제공합니다. Living Spec 자체는
[개념](../concepts.md)에서 소개하고, 변경에 필요한 문서를 찾는 전체 과정은 여정
[알맞은 문서 찾기](../journeys/find-the-right-documents.md)(`UC-find-the-right-documents`)에서 다룹니다.

## 무엇이 문서인가

다음 조건을 모두 만족하는 파일이 문서입니다
([CAP-DOCS-document-model](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)).

- `docs/` 또는 `specs/` 아래의 `*.md` 파일이며, `README.md`, 템플릿, 심볼릭 링크가 아니고 점(.) 디렉터리 아래에
  있지 않습니다.
- 프런트매터의 `id`(조정 기록이라면 `reconcile_id`)에 올바른 형식의 ID를 선언합니다.

용어집이나 가이드처럼 ID가 없는 파일은 조용히 제외됩니다. 프런트매터가 깨진 파일은 `SPEC_DOCUMENT_INVALID` 경고와
함께 제외되고, 나머지 문서는 모두 그대로 사용할 수 있습니다.

ID 접두사가 종류를 나타냅니다. `CAP` 기능, `UC` 유스케이스, `ARCH` 아키텍처, `ADR` 결정, `PROP` 제안, `PADR` 제안
결정, `SPEC`/`PLAN`/`TASKS`/`REC` 스펙 번들 파일, `FB` 피드백, `MAT` 자료, `MS` 마일스톤입니다. ID는 저장소 전체에서
고유합니다. 색인은 ID가 어디에 선언되어 있든 받아들이며, 각 파일이 자기 종류에 맞는 위치에 있는지는 spec 규칙이
검사합니다.

기능, 유스케이스, 결정, 아키텍처 문서, 마일스톤, 제안, 스펙에는 한두 문장의 영어 `summary`를 씁니다. 이것이 검색의
주된 신호이므로 제목과 본문은 어떤 언어로 써도 됩니다.

## 다른 문서 참조하기

- 문서는 항상 Markdown 경로가 아니라 전체 ID로 참조합니다. 프런트매터의 관계 필드(`usecases`, `capabilities`,
  `spec`, `plan` 등)에 쓰거나, 본문에서는 ID 하나만 담은 코드 스팬으로 씁니다.
- 코드 블록, 링크 레이블, HTML 주석, 그 밖의 인라인 코드는 참조가 아닙니다.
- `proposal`, `decomposed_from`, `supersedes`는 출처를 기록하며 참조 그래프에서 제외됩니다.
- 참조의 유효성(해석 불가, 중복, 잘못된 종류)은 색인이 아니라 spec 규칙이 보고합니다.
  [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
  (`UC-keep-the-living-spec-consistent`)를 참고하십시오.

### 문서 이름 바꾸기

파일을 옮기고 새 ID를 설정한 뒤 이전 ID는 `aliases`에 남깁니다. 별칭(alias)은 ID 인자를 받는 모든 곳에서 해당 문서로
해석되며, 이어서 `uv run devkit rules fix`가 현재 참조를 새 ID로 다시 씁니다(`ADR-document-id-aliases`). 두 문서가
같은 별칭을 주장하면 충돌로 간주되어 양쪽 모두에 보고됩니다.

## 이미 아는 것으로 조회하기

| 가진 것 | 명령 |
| --- | --- |
| ID(또는 별칭) | `uv run devkit spec resolve CAP-DOCS-document-model` |
| 문서가 참조하는 대상을 알고 싶을 때 | `uv run devkit spec refs <ID>` |
| 문서를 참조하는 대상을 알고 싶을 때 | `uv run devkit spec refs <ID> --direction in` |
| 코드 경로 | `uv run devkit spec list capability --file src/engine/` |
| 둘러볼 종류, 상태, 영역 | `uv run devkit spec list usecase --status active --area core` |
| 프런트매터 필드 값 | `uv run devkit spec list feedback --where severity=critical -n 0` |

`resolve`는 ID마다 `[DOCUMENT: ...]` 한 줄을 출력하고, 확정하지 못한 ID가 있으면 `SPEC_ID_UNRESOLVED` 또는
`SPEC_ID_DUPLICATE`와 함께 `2`로 종료합니다. `refs`와 `list`는 출력을 페이지로 나누므로, 다음 페이지는
`[NEXT_CMD: ...]` 줄을 따라가면 됩니다. 모든 명령은 `--format json`을 받습니다. 옵션, 줄 필드, JSON 키는
[CAP-DOCS-document-lookup](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-lookup.md) (영어 원문)에
있습니다.

### 이력은 기본적으로 숨겨집니다

둘러보기와 검색은 `--history`를 주지 않으면 이력 문서를 숨깁니다. 완료된 스펙 번들의 파일(피드백 제외), 완료되거나
중단된 마일스톤, 종료 상태에 있는 문서(피드백 `resolved`, `promoted`, `dismissed`, `forwarded`, 결정 `superseded`,
제안 `rejected`, `ADR-terminal-statuses-are-historical`)가 여기에 해당합니다. `list`는 숨긴 개수를 알려 주고, 그
문서를 보는 `[HISTORY_CMD: ...]` 줄을 출력합니다. `--status`로 상태를 지정하면 해당 문서도 보입니다. 이력 ID는 항상
해석할 수 있습니다.

## 의도만 알 때 검색하기

```bash
uv run devkit spec search "link integrity between documents"
uv run devkit spec search "cache policy" --kind decision --kind capability --history
```

질의가 문서의 ID, 별칭, 경로, 파일 이름과 같으면 그 문서가 맨 앞에 고정됩니다. 나머지 결과는 ID와 영어 요약(어휘와
의미 기준), 제목, 영역, 본문(어휘 기준)으로 순위가 매겨집니다. 프로젝트가 소유하는 선택적 `docs/glossary.yaml`은 질의
용어를 동의어로 확장하므로 다른 언어의 용어에 유용합니다. search extra가 없으면 순위는 어휘 기반이며,
`uv add 'devkit-spec[search]'`로 설치하면 하이브리드 순위를 씁니다. 자세한 내용은
[CAP-DOCS-document-search](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-search.md) (영어 원문)에
있고, 순위 엔진 자체는 [검색](search.md)에서 설명합니다.

## 네임스페이스로 모노레포 다루기

각 패키지를 `.devkit/config.toml`에 등록하고, `docs/`와 같은 레이아웃으로 `docs/packages/<name>/` 아래에 자체 Living
Spec을 둡니다.

```toml
[[tool.spec.namespaces]]
name = "api"
path = "services/api"
```

네임스페이스는 *둘러보는* 범위를 좁힐 뿐, 존재하는 문서를 바꾸지 않습니다
([CAP-DOCS-namespaces](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-namespaces.md) (영어 원문)).

- `list`와 `search`는 기본적으로 현재 디렉터리의 네임스페이스와 전역 문서를 보여 줍니다. `--namespace NAME`은 하나를
  고르고, `--namespace global`은 전역 문서만, `--all-namespaces`는 전부를 보여 줍니다.
- `resolve`, `refs`, 참조 규칙은 네임스페이스를 무시합니다. ID는 저장소 전체에서 유효하고 참조는 패키지를 자유롭게
  넘나듭니다. 패키지 간 영향을 보려면 `--all-namespaces`를 사용합니다.
- 스펙 번들이나 제안 번들은 `namespace` 필드에 적힌 네임스페이스에 속하며, 이 필드는 `devkit spec new --namespace`와
  `devkit spec proposal new --namespace`가 씁니다.

## 이 영역의 기능

| 기능 | 이럴 때 읽습니다 |
| --- | --- |
| `CAP-DOCS-document-model` | 문서의 정의, ID, 참조, 별칭, 색인과 파싱 메모 |
| `CAP-DOCS-document-lookup` | `resolve`, `refs`, `list`의 옵션, 출력, 코드 |
| `CAP-DOCS-document-search` | `devkit spec search`의 후보, 고정, 용어집, 모드 |
| `CAP-DOCS-namespaces` | 모노레포 네임스페이스와 그 선택 |
