---
sources:
  CAP-DIST-context-and-playbooks: null
  CAP-DOCS-document-search: null
  CAP-SRCH-document-search: null
  UC-find-the-right-documents: null
title: 검색
translated_from: en/areas/search.md@6d61be7017a9b89c
---

# 검색

<!-- handbook:provenance -->
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

검색(search) 영역은 `devkit playbook search`와 `devkit spec search` 뒤에서 동작하는 순위 엔진입니다. 이 엔진은
문서를 ID, 약간의 메타데이터 텍스트, 선택적 본문으로만 알고, 질의에 대해 어휘 기준, 의미 기준 또는 둘 다로 순위를
매깁니다. 어떤 문서가 후보인지, 정확히 일치하는 문서를 맨 앞에 고정할지는 엔진을 호출하는 명령이 정합니다. 계약은
[CAP-SRCH-document-search](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/search/CAP-SRCH-document-search.md) (영어 원문)입니다.

## 어디에서 만나는가

| 명령 | 후보 | 계약 |
| --- | --- | --- |
| `uv run devkit playbook search "<query>"` | 동기화된 플레이북 헤더(`name`, `description`) | `CAP-DIST-context-and-playbooks` |
| `uv run devkit spec search <query>` | 현재 Living Spec 문서 | `CAP-DOCS-document-search` |

Living Spec 문서를 처음부터 끝까지 찾는 과정은 여정
[알맞은 문서 찾기](../journeys/find-the-right-documents.md)(`UC-find-the-right-documents`)에서 다룹니다. 플레이북
탐색은 [배포](distribution.md)에서, spec 명령은 [문서](documents.md)에서 설명합니다.

## 모드 고르기

| 모드 | 동작 | 필요 조건 |
| --- | --- | --- |
| `auto`(기본값) | search extra가 설치되어 있으면 `hybrid`, 아니면 `lexical` | 없음 |
| `lexical` | 메타데이터와 본문에 대한 BM25 | 표준 라이브러리만 |
| `dense` | 질의와 메타데이터 임베딩의 코사인 유사도 | `search` extra |
| `hybrid` | 두 순위의 Reciprocal Rank Fusion | `search` extra |

두 명령 모두 `--mode`를 받습니다. 대체 동작은 `auto`에만 있습니다. extra 없이 `dense`나 `hybrid`를 명시하면
`SEARCH_EXTRA_MISSING`(또는 `SEARCH_MODEL_NOT_FOUND`)으로 실패하고, 모든 결과에 실제로 실행된 모드가 적히므로 어떤
순위를 받았는지 항상 알 수 있습니다.

사용할 수 있다면 hybrid가 더 나은 기본값입니다. devkit 자체의 영어 문서에서 dense 단독은 BM25보다 약간 낮은 순위를
보였지만, hybrid는 첫 번째 결과를 유지하면서 상위 5개와 상위 10개의 재현율을 높였습니다. 질의와 다른 표현으로 쓰인
문서도 찾아낸다는 뜻입니다.

## search extra 설치하기

extra는 두 번째 요구사항으로 추가하지 말고, 프로젝트가 이미 선언한 devkit 요구사항에 붙입니다. `devkit-agt[search]`
또는 `devkit-dist[search]`이며, spec 검색에는 `devkit-spec[search]`도 필요합니다. 이 extra는 `numpy`, `tokenizers`와
기본 모델 `potion-base-8m`을 제공하는 `devkit-embed` 모델 패키지를 가져옵니다. 모델은 정적이고 로컬에서 동작합니다.
네트워크가 필요 없고, 수십 밀리초 안에 로드되며, 첫 dense, hybrid 또는 `auto` 검색에서만 import되고 lexical
검색에서는 절대 import되지 않습니다.

## 검색이 잘 되는 문서 쓰기

- 임베딩 모델은 영어 전용이며 메타데이터만 읽습니다. 모든 문서에 영어 메타데이터를 다십시오. 플레이북은 `name`과
  `description`, Living Spec 문서는 `summary`입니다. 본문은 어떤 언어로 써도 어휘 기준 점수에는 반영됩니다.
- 토크나이저는 대소문자를 접고, 라틴 악센트를 없애며, `_`, `-` 및 문자가 아닌 모든 문자에서 분리합니다
  (`RULE-file_length`는 `rule`, `file`, `length`가 됩니다). 어간 추출이나 불용어 목록은 없습니다.
- `dense`와 `hybrid`에서는 관련 없는 텍스트 대부분도 어느 정도 양의 유사도를 받으므로 하한선이 중요합니다.
  `--min-similarity`는 두 명령 모두 기본값이 `0.35`이며, hybrid의 이점을 유지하면서 긴 꼬리를 걸러 내도록 측정된
  값입니다.

## 다른 모델 사용하기

모델은 `devkit.embedding_models` 엔트리 포인트에 모듈을 등록하고 그 옆에 `model.json`, `tokenizer.json`,
`model.safetensors`를 두는 데이터 전용 Python 패키지입니다. 다른 이름의 패키지를 설치하면 라이브러리에서 그 모델을
선택할 수 있습니다. 기본 패키지는 `models/devkit-embed`에 있으며, `just model-build`로 빌드한 재현 가능한 wheel이
커밋되어 있어 작업 공간 명령과 테스트가 오프라인에서 동작합니다. 손상된 모델 패키지는 모든 모드에서
`SEARCH_MODEL_INVALID`로 실패합니다.
