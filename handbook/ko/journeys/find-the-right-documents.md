---
sources:
  CAP-DOCS-document-lookup: null
  CAP-DOCS-document-model: null
  CAP-DOCS-document-search: null
  CAP-DOCS-namespaces: null
  UC-find-the-right-documents: null
title: 알맞은 문서 찾기
translated_from: en/journeys/find-the-right-documents.md@ecea50d17c89b0da
---

# 알맞은 문서 찾기

<!-- handbook:provenance -->
> 소스 커밋 `93e3808721b4` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [적응형 개발에서 SDD 도입하기](adopt-sdd-from-adaptive-development.md)
- [아이디어 발전시키기](advance-an-idea.md)
- [선택한 테스트 스위트 평가하기](assess-test-management.md)
- [필요한 명령 진입점 설계하기](design-command-entrypoints.md)
- [아이디어 발굴하고 구체화하기](discover-and-refine-an-idea.md)
- [개발에서 통합까지 진행하기](drive-development-to-integration.md)
- [격리된 명령 실행하기](execute-an-isolated-command.md)
- [설계 문제 탐색하기](explore-a-design-problem.md)
- [최신 유지보수 실행 찾기](find-the-latest-maintenance-run.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [선택한 외부 에이전트 자산 가져오기](import-third-party-agent-assets.md)
- [인터페이스와 사용 흐름 개선하기](improve-an-interface-and-user-flow.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [제안 계획 후 넘기기](plan-and-hand-off-a-proposal.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [결정 대체 관계 읽기](read-decision-supersession.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [유지보수 실행 기록하기](record-a-maintenance-run.md)
- [아이디어 조사와 로드맵 구체화하기](research-an-idea-and-shape-a-roadmap.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [번들 소스를 로컬로 도입하고 갱신하기](snapshot-bundle-sources.md)
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

에이전트가 코드를 수정하기 전에는 해당 코드를 규율하는 계약 문서(capability, 유스케이스, 결정, 스펙)를
먼저 파악해야 합니다. `docs/` 트리 전체를 읽으면 컨텍스트가 낭비되므로, 에이전트는 이미 확보한 단서를 바탕으로
`devkit docs`에 꼭 필요한 문서만 요청합니다.
이 페이지의 모든 명령어는 읽기 전용이며 파일을 변경하지 않습니다.

유스케이스는
[`UC-find-the-right-documents`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/documents/UC-find-the-right-documents.md) (영어 원문)입니다.
문서, ID, Living Spec의 개념은 [개념](../concepts.md)과 [문서](../areas/documents.md) 영역을
참고하십시오.

## 출발점 고르기

| 현재 확보한 단서 | 시작 명령어 |
| --- | --- |
| 태스크나 코드 리뷰에 언급된 문서 ID | `devkit docs resolve <ID>` |
| 수정할 대상 코드 파일 경로 | `devkit docs list capability --file <path>` |
| 작업 목적이나 의도에 대한 자연어 설명뿐인 경우 | `devkit docs search "<intent>"` |
| 구체적 단서가 없고 모노레포 내 특정 패키지 위치에 있는 경우 | `devkit docs list` |

## 1. 문서 ID 해석 (Resolve)

```bash
uv run devkit docs resolve CAP-DOCS-document-model
```

워크스페이스 상대 경로가 포함된 `[DOCUMENT: <id> kind= status= path=]` 단일 라인이 출력됩니다. 별칭(alias)은
정식 문서로 해석되며 해당 줄에 `alias=`가 함께 표시됩니다. 여러 ID를 한 번에 전달할 수도 있습니다.
ID와 종류의 정의는
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)에
있습니다.

## 2. 참조 관계 추적

```bash
uv run devkit docs refs CAP-DOCS-document-model --direction in   # who cites it
uv run devkit docs refs CAP-DOCS-document-model                  # what it cites
```

`[REF: ...]` 라인마다 연결된 대상 문서와 해당 참조를 포함하는 필드가 출력됩니다. 결과는 한 번에 한 페이지씩 반환되며,
`[PAGE: ...]` 라인과 다음 페이지용 정확한 명령어가 담긴 `[NEXT_CMD: ...]` 라인이 뒤따릅니다
([`CAP-DOCS-document-lookup`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-document-lookup.md) (영어 원문)).

## 3. 문서 확인 및 인용

필요한 문서를 읽고 이에 맞추어 코드를 수정합니다. `CAP-DOCS-document-model`과 같이
코드 스팬 내에 정확한 문서 ID를 명시하여 인용합니다.

## 다양한 검색 및 탐색 방법

**의미로 찾기:** 의도만 알고 있을 때 활용합니다.

```bash
uv run devkit docs search "keep references between documents valid"
```

랭킹은 각 문서의 ID와 영문 요약, 그리고 제목·영역·본문의 어휘 일치를 사용하므로 본문이 다른 언어로
작성되어 있어도 동작합니다. 질의어가 ID, 별칭, 경로, 파일 이름과 정확히 일치하면 해당 문서가
`score=-`와 함께 맨 앞에 놓입니다. 선택 extra(`uv add 'devkit-docs[search]'`, `devkit-spec[search]`에도 포함)가 설치되어 있으면
하이브리드 랭킹을 수행하며, 미설치 시 어휘 랭킹으로 동작합니다
([`CAP-DOCS-document-search`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-document-search.md) (영어 원문)).
선택한 결과로 2단계부터 이어갑니다.

**코드 경로로 찾기:** `uv run devkit docs list capability --file src/<package>/engine.py` 명령은 `entrypoints`가
해당 파일 경로와 일치하거나 포함하거나 그 아래에 놓이는 문서를 나열합니다. 삭제된 파일 경로에서도 동작합니다.

**모노레포 패키지 내부:** 모노레포가 패키지를 네임스페이스로 등록해 둔 경우(`.devkit/config.toml`의
`[[tool.docs.namespaces]]`), `devkit docs list` 및 `devkit docs search`는
현재 디렉터리의 네임스페이스 문서와 전역 문서를 보여주며 각 줄에 `namespace=`가 표시됩니다.
`--namespace <name>`으로 다른 네임스페이스를 고르거나 `--all-namespaces`로 전체를 조회합니다.
네임스페이스는 목록 탐색 범위만 좁힙니다. `resolve` 및 `refs`는 저장소 전역으로 동작하므로
다른 패키지의 ID도 그대로 해석됩니다
([`CAP-DOCS-namespaces`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-namespaces.md) (영어 원문)).

## 요청하지 않으면 제외되는 이력 문서

완료된 스펙 번들, 완료·중단된 마일스톤, 최종 상태의 문서는 이력으로 분류됩니다. `list` 및 `search`는
기본적으로 이를 제외합니다. `list`는 숨긴 문서 개수를 페이지 라인의 `hidden=`으로 알리고
같은 명령에 `--history`를 붙인 `[HISTORY_CMD: ...]` 라인을 출력합니다.

## 문제 해결

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `DOCS_ID_UNRESOLVED` | 해당 ID를 선언한 문서가 없습니다. 해석된 ID들이 먼저 출력됩니다. | 대신 의미 검색을 실행하십시오. |
| `DOCS_ID_DUPLICATE` | 여러 문서가 동일한 ID를 선언합니다. `[TARGET]`에 목록이 출력됩니다. | 중복을 수동으로 수정하십시오. 어떤 쪽이 맞는지 추측하지 않습니다. |
| `DOCS_ENTRYPOINTS_PATH_INVALID` | `--file` 경로가 절대 경로이거나 glob 또는 `..`를 포함합니다. | 워크스페이스 상대 경로를 전달하십시오. |
| `ARGUMENT_INVALID` | 알 수 없는 `--namespace`이거나 `--namespace`와 `--all-namespaces`를 함께 사용했습니다. | 오류에 나열된 유효한 이름 중 하나를 사용하십시오. |
| `DOCS_CONFIG_INVALID` | `[tool.docs]` 네임스페이스 테이블 형식이 잘못되었습니다. | `.devkit/config.toml`의 테이블을 수정하십시오. |
| `DOCS_DOCUMENT_INVALID` (경고) | 파일 하나를 읽을 수 없거나 프론트매터 형식이 잘못되었습니다. | 해당 파일은 제외되며 나머지 문서는 계속 사용할 수 있습니다. 파일을 수정하십시오. |

경고(`DOCS_DOCUMENT_INVALID`)는 종료 코드 `0`을 반환하며, 나머지는 모두 `2`로 종료합니다.
메시지 텍스트가 아니라 오류 코드로 분기합니다.

## 관련 페이지

- 내부 랭킹 엔진에 대한 자세한 내용은 [검색](../areas/search.md) 영역 문서.
- 본 조회 절차를 바탕으로 실제 개발을 진행하는 [개발부터 통합까지 진행하기](drive-development-to-integration.md).
