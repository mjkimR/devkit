---
sources:
  CAP-DOCS-document-lookup: null
  CAP-DOCS-document-model: null
  CAP-DOCS-document-search: null
  CAP-DOCS-namespaces: null
  UC-find-the-right-documents: null
title: 알맞은 문서 찾기
translated_from: en/journeys/find-the-right-documents.md@8fcbc9dcb661bfab
---

# 알맞은 문서 찾기

<!-- handbook:provenance -->
> 소스 커밋 `18b834c35c0c` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](incubate-an-idea.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
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

에이전트가 코드를 수정하기 전에는 해당 코드를 규율하는 계약 문서(capability, 유스케이스, 아키텍처 결정, 기능 스펙 등)를
먼저 파악해야 합니다. 하지만 `docs/` 디렉터리 트리 전체를 무작정 읽으면 컨텍스트 윈도우가 크게 낭비됩니다. 대신 에이전트는
이미 확보한 단서(ID, 변경 파일 경로, 자연어 설명 등)를 바탕으로 `devkit docs`에 꼭 필요한 문서만 정확하게 조회합니다.
이 페이지에서 소개하는 모든 명령어는 읽기 전용이며, 기존 파일을 변경하지 않습니다.

유스케이스는
[`UC-find-the-right-documents`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/documents/UC-find-the-right-documents.md) (영어 원문)입니다.
문서, ID, Living Spec의 기본 개념은 [개념](../concepts.md)과 [문서](../areas/documents.md) 영역 문서를
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

워크스페이스 루트 기준 상대 경로가 포함된 `[DOCUMENT: <id> kind= status= path=]` 단일 라인이 출력됩니다. 별칭(alias)을 조회한 경우
정식 표준 문서로 자동 해석되며 해당 줄에 `alias=`가 함께 표시됩니다. 여러 ID를 공백으로 구분하여 한 번에 전달할 수도 있습니다.
지원하는 문서 ID 체계와 종류는
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)에
정의되어 있습니다.

## 2. 참조 관계 추적 (References)

```bash
uv run devkit docs refs CAP-DOCS-document-model --direction in   # who cites it
uv run devkit docs refs CAP-DOCS-document-model                  # what it cites
```

`[REF: ...]` 라인마다 연결된 대상 문서와 해당 참조를 포함하는 프론트매터 필드가 출력됩니다. 조회 결과는 페이지 단위로 제공되며,
하단에 `[PAGE: ...]` 라인과 함께 다음 페이지를 조회할 수 있는 정확한 명령어가 담긴 `[NEXT_CMD: ...]` 라인이 표시됩니다
([`CAP-DOCS-document-lookup`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-lookup.md) (영어 원문)).

## 3. 문서 확인 및 명세 인용

식별된 계약 문서를 정독한 후 이에 맞추어 코드를 구현합니다. 작업 내역 및 커밋 메시지에서는 `CAP-DOCS-document-model`과 같이
백틱 코드 스팬 내에 정확한 문서 ID를 명시하여 인용합니다.

## 다양한 검색 및 탐색 방법

**자연어 의미 검색:** 구현하려는 기능 의도나 개념만 알고 있을 때 활용합니다.

```bash
uv run devkit docs search "keep references between documents valid"
```

검색 랭킹 엔진은 각 문서의 ID와 영문 요약(summary), 그리고 제목·영역·본문의 어휘 일치도를 종합 평가하므로, 문서 본문이 한국어 등
다른 언어로 작성되어 있어도 유효하게 동작합니다. 질의어가 특정 문서의 ID, 별칭, 경로, 파일 이름과 정확히 일치하면 해당 문서가
`score=-`와 함께 최우선으로 배치됩니다. 선택 패키지(`uv add 'devkit-docs[search]'`, `devkit-spec[search]`에도 포함)가 설치되어 있으면 벡터 임베딩이 결합된 하이브리드
검색을 수행하며, 미설치 시 어휘(BM25 기반) 랭킹으로 동작합니다
([`CAP-DOCS-document-search`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-search.md) (영어 원문)).
검색 결과에서 적합한 문서를 확인한 후 2단계(참조 추적)로 이어가십시오.

**코드 파일 경로로 찾기:** `uv run devkit docs list capability --file src/<package>/engine.py` 명령은 문서 프론트매터의 `entrypoints`에
해당 파일 경로와 일치하거나, 상위/하위 관계에 있는 모든 규정 문서를 나열합니다. 이미 삭제된 파일 경로에 대해서도 정상 조회됩니다.

**모노레포 패키지 범위 지정:** 모노레포 환경에서 각 패키지를 네임스페이스로 등록해 둔 경우(`.devkit/config.toml`의
`[[tool.docs.namespaces]]`), `devkit docs list` 및 `devkit docs search`는
현재 작업 디렉터리의 네임스페이스 문서와 전역 공통 문서만 선별하여 보여주며 각 줄에 `namespace=`가 표시됩니다.
`--namespace <name>` 옵션으로 특정 네임스페이스를 지정하거나, `--all-namespaces` 옵션으로 전체 문서를 조회할 수 있습니다.
네임스페이스 필터는 목록 탐색 범위를 좁히는 용도로만 동작합니다. `resolve` 및 `refs` 명령어는 항상 저장소 전역을 대상으로 수행되므로,
다른 패키지에 선언된 문서 ID도 정상적으로 해석됩니다
([`CAP-DOCS-namespaces`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-namespaces.md) (영어 원문)).

## 완료 및 종료된 이력 문서 제외

이미 완료된 스펙 번들, 종료되거나 중단된 마일스톤, 최종 완료/폐기 상태의 문서는 과거 이력으로 분류됩니다. `list` 및 `search`
명령어는 활성 작업에 집중할 수 있도록 이러한 이력 문서를 기본 검색 결과에서 제외합니다. `list` 명령어는 제외된 문서 개수를 페이지
라인의 `hidden=` 항목으로 알려주며, 이력 문서까지 포함하여 조회할 수 있는 명령어를 `[HISTORY_CMD: ...]` 라인으로 안내합니다.

## 문제 해결

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `DOCS_ID_UNRESOLVED` | 해당 ID를 선언한 문서가 저장소에 존재하지 않습니다. 함께 전달한 ID 중 정상 해석된 항목이 먼저 출력됩니다. | `devkit docs search` 명령으로 자연어 의미 검색을 시도하십시오. |
| `DOCS_ID_DUPLICATE` | 동일한 ID를 선언한 중복 문서가 여러 개 존재합니다. `[TARGET]`에 대상 파일 목록이 출력됩니다. | 중복된 ID를 수동으로 수정하십시오. 시스템이 임의로 어느 한쪽을 올바른 문서로 추측하지 않습니다. |
| `DOCS_ENTRYPOINTS_PATH_INVALID` | `--file` 경로가 절대 경로이거나, 와일드카드(glob) 또는 `..` 상위 디렉터리 경로를 포함하고 있습니다. | 워크스페이스 루트 기준의 정규 상대 경로를 전달하십시오. |
| `ARGUMENT_INVALID` | 등록되지 않은 `--namespace`를 지정했거나, `--namespace`와 `--all-namespaces` 옵션을 동시에 사용했습니다. | 오류 메시지에 안내된 유효한 네임스페이스 이름 중 하나를 지정하십시오. |
| `DOCS_CONFIG_INVALID` | `[tool.docs]` 네임스페이스 테이블 형식이 잘못되었습니다. | `.devkit/config.toml`의 테이블을 바로잡으십시오. |
| `DOCS_DOCUMENT_INVALID` (경고) | 특정 문서 파일을 읽을 수 없거나 프론트매터 형식이 손상되었습니다. | 해당 손상 파일만 결과에서 제외되며 나머지 정상 문서는 계속 사용할 수 있습니다. 손상된 파일을 검토하고 수정하십시오. |

경고(`DOCS_DOCUMENT_INVALID`)는 종료 코드 `0`을 반환하며, 나머지 오류는 모두 종료 코드 `2`(실행 불가)로 종료합니다.
에이전트는 사람이 읽는 메시지 텍스트가 아니라 표준 대문자 오류 코드로 분기 처리해야 합니다.

## 관련 페이지

- 내부 랭킹 엔진에 대한 자세한 내용은 [검색](../areas/search.md) 영역 문서.
- 본 조회 절차를 바탕으로 실제 개발을 진행하는 [개발부터 통합까지 진행하기](drive-development-to-integration.md).
