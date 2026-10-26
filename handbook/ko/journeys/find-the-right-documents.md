---
sources:
  CAP-DOCS-document-lookup: null
  CAP-DOCS-document-model: null
  CAP-DOCS-document-search: null
  CAP-DOCS-namespaces: null
  UC-find-the-right-documents: null
title: 알맞은 문서 찾기
translated_from: en/journeys/find-the-right-documents.md@7ee3273d70e5b086
---

# 알맞은 문서 찾기

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
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

에이전트가 코드를 바꾸기 전에는 그 코드를 규정하는 계약, 즉 capability, 유스케이스, 결정, 스펙이 필요합니다.
`docs/` 트리 전체를 읽으면 컨텍스트가 낭비됩니다. 대신 에이전트는 손에 쥔 단서에서 출발해 `devkit spec`에
꼭 필요한 문서만 요청합니다. 이 페이지의 모든 작업은 읽기 전용이며, 파일을 바꾸는 명령은 없습니다.

유스케이스는
[`UC-find-the-right-documents`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/documents/UC-find-the-right-documents.md) (영어 원문)입니다.
문서, ID, Living Spec이 무엇인지는 [개념](../concepts.md)과 [Documents](../areas/documents.md) 영역을
참고하십시오.

## 출발점 고르기

| 가진 것 | 시작할 명령 |
| --- | --- |
| 태스크나 리뷰에 인용된 ID | `devkit spec resolve <ID>` |
| 곧 바꿀 코드 경로 | `devkit spec list capability --file <path>` |
| 의도에 대한 설명뿐 | `devkit spec search "<intent>"` |
| 아직 아무것도 없고, 모노레포의 한 패키지 안에 있음 | `devkit spec list` |

## 1. ID 해석하기

```bash
uv run devkit spec resolve CAP-DOCS-document-model
```

워크스페이스 기준 상대 경로가 담긴 `[DOCUMENT: <id> kind= status= path=]` 한 줄이 출력됩니다. 별칭(alias)은
정식 문서로 해석되며, 그 줄에 `alias=`가 표시됩니다. ID 여러 개를 한 번에 넘길 수도 있습니다. ID와 종류가 어떻게
정의되는지는
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)에
있습니다.

## 2. 참조 따라가기

```bash
uv run devkit spec refs CAP-DOCS-document-model --direction in   # who cites it
uv run devkit spec refs CAP-DOCS-document-model                  # what it cites
```

`[REF: ...]` 줄마다 반대편 문서와 참조를 담은 필드가 표시됩니다. 결과는 한 페이지씩 나옵니다. 뒤이어 `[PAGE: ...]`
줄이 나오고, `[NEXT_CMD: ...]`가 다음 페이지를 가져올 정확한 명령을 알려 줍니다
([`CAP-DOCS-document-lookup`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-lookup.md) (영어 원문)).

## 3. 읽고 인용하기

필요한 문서를 읽고, 그 문서에 맞춰 코드를 바꾸고, 각 문서를 `CAP-DOCS-document-model`처럼 코드 스팬 안에 정확한
ID로 인용합니다.

## 다른 진입 방법

**의미로 찾기.** 의도만 알고 있을 때 사용합니다.

```bash
uv run devkit spec search "keep references between documents valid"
```

순위는 각 문서의 ID와 영어 요약, 그리고 제목, 영역, 본문의 어휘 일치를 사용하므로, 본문이 다른 언어로 쓰여 있어도
동작합니다. ID, 별칭, 경로, 파일 이름과 똑같은 질의는 그 문서를 `score=-`로 맨 앞에 둡니다. 선택 사항인 search
extra(`uv add 'devkit-spec[search]'`)가 있으면 하이브리드 순위를, 없으면 어휘 순위를 사용합니다
([`CAP-DOCS-document-search`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-search.md) (영어 원문)).
고른 결과로 2단계를 이어 가십시오.

**코드 경로로 찾기.** `uv run devkit spec list capability --file src/<package>/engine.py`는 `entrypoints`가 그
경로와 같거나, 그 경로를 포함하거나, 그 경로 아래에 있는 문서를 나열합니다. 삭제된 파일에도 동작합니다.

**모노레포 패키지 안에서.** 모노레포가 패키지를 네임스페이스로 등록하면, `devkit spec list`와 `devkit spec search`는
현재 디렉터리의 네임스페이스와 전역 문서를 보여 주며, 각 줄에 `namespace=`가 붙습니다. `--namespace <name>`으로
다른 네임스페이스를 고르고, `--all-namespaces`로 전부 볼 수 있습니다. 네임스페이스는 탐색 범위만 좁힙니다.
`resolve`와 `refs`는 저장소 전체를 대상으로 하므로, 다른 패키지의 ID도 해석됩니다
([`CAP-DOCS-namespaces`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-namespaces.md) (영어 원문)).

## 이력은 요청할 때만 포함

완료된 스펙 번들, 끝났거나 중단된 마일스톤, 종료 상태의 문서는 이력입니다. `list`와 `search`는 기본적으로 이를
제외합니다. `list`는 숨긴 개수를 알려 주고(페이지 줄의 `hidden=`), 같은 명령에 `--history`를 붙인
`[HISTORY_CMD: ...]` 줄을 출력합니다.

## 문제가 생겼을 때

| 코드 | 의미 | 해야 할 일 |
| --- | --- | --- |
| `SPEC_ID_UNRESOLVED` | 그 ID를 선언한 문서가 없습니다. 해석된 ID가 먼저 출력됩니다. | 대신 의미로 검색하십시오. |
| `SPEC_ID_DUPLICATE` | 여러 문서가 그 ID를 선언합니다. `[TARGET]`에 목록이 나옵니다. | 중복을 직접 고치십시오. 어느 쪽이 옳은지 추측하는 기능은 없습니다. |
| `SPEC_ENTRYPOINTS_PATH_INVALID` | `--file` 경로가 절대 경로이거나, glob이거나, `..`를 포함합니다. | 워크스페이스 기준 상대 경로를 넘기십시오. |
| `ARGUMENT_INVALID` | 알 수 없는 `--namespace`이거나, `--namespace`를 `--all-namespaces`와 함께 썼습니다. | 오류가 나열하는 유효한 이름 중 하나를 사용하십시오. |
| `SPEC_DOCUMENT_INVALID`(경고) | 어떤 파일을 읽을 수 없거나 프론트매터가 잘못되었습니다. | 그 파일은 제외되고 나머지 문서는 모두 사용할 수 있습니다. 파일을 고치십시오. |

경고는 `0`으로 종료하고, 나머지는 모두 `2`로 종료합니다. 메시지 텍스트가 아니라 코드로 분기하십시오.

## 관련 페이지

- 그 아래에서 동작하는 순위 엔진은 [Search](../areas/search.md) 영역.
- 이 조회 결과가 작업으로 이어지는 [개발부터 통합까지 진행하기](drive-development-to-integration.md).
