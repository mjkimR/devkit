---
sources:
  CAP-DIST-context-and-playbooks: null
  CAP-DOCS-document-search: null
  CAP-SRCH-document-search: null
  UC-find-the-right-documents: null
title: 검색
translated_from: en/areas/search.md@ece317be47783ab8
---

# 검색

<!-- handbook:provenance -->
> 소스 커밋 `18b834c35c0c` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

검색(search) 기능은 `devkit playbook search` 및 `devkit docs search` 명령을 지원하는 랭킹 엔진입니다. 문서를
문서 ID, 메타데이터 텍스트, 선택적인 본문으로만 인식하며, 검색 질의에 대해 어휘적(lexical) 방식, 의미적(semantic) 방식,
또는 두 방식을 결합하여 순위를 매깁니다. 어떤 문서를 검색 후보로 삼을지, 정확히 일치하는 문서를 맨 앞에 고정할지는
랭킹 엔진을 호출하는 상위 명령이 결정합니다. 상세 계약은
[CAP-SRCH-document-search](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/search/CAP-SRCH-document-search.md) (영어 원문)에 정의되어 있습니다.

## 관련 명령 및 대상

| 명령 | 대상 후보 | 사양 계약 |
| --- | --- | --- |
| `uv run devkit playbook search "<query>"` | 동기화된 플레이북 헤더(`name`, `description`) | `CAP-DIST-context-and-playbooks` |
| `uv run devkit docs search <query>` | 현재 Living Spec 문서 | `CAP-DOCS-document-search` |

Living Spec 문서를 종합적으로 탐색하는 전체 과정은 여정
[알맞은 문서 찾기](../journeys/find-the-right-documents.md)(`UC-find-the-right-documents`)에서 다룹니다. 플레이북
탐색 방법은 [배포](distribution.md)를, 문서 검색 명령은 [문서](documents.md)를 참고하세요.

## 검색 모드 선택

| 모드 | 동작 방식 | 요구 조건 |
| --- | --- | --- |
| `auto`(기본값) | search extra가 설치되어 있으면 `hybrid`, 없으면 `lexical` | 없음 |
| `lexical` | 메타데이터와 본문에 대한 BM25 어휘 검색 | 표준 라이브러리만으로 동작 |
| `dense` | 질의와 메타데이터 임베딩 간 코사인 유사도 기반 검색 | `search` extra 필요 |
| `hybrid` | 두 순위 결과를 Reciprocal Rank Fusion으로 결합 | `search` extra 필요 |

두 명령 모두 `--mode` 옵션을 지원합니다. 대체(fallback) 동작은 `auto` 모드에서만 이루어집니다. extra가 설치되지 않은 상태에서
`dense`나 `hybrid`를 명시적으로 지정하면 `SEARCH_EXTRA_MISSING`(또는 `SEARCH_MODEL_NOT_FOUND`) 오류가 발생합니다. 모든 검색 결과에는
실제로 사용된 모드가 표시되므로, 어떤 방식으로 순위가 매겨졌는지 항상 명확히 알 수 있습니다.

extra를 사용할 수 있는 환경이라면 hybrid 모드가 더 우수한 기본값입니다. devkit 자체 영문 문서를 대상으로 측정한 결과,
dense 단독 모드는 BM25보다 순위가 약간 낮았지만, hybrid 모드는 1위 검색 결과를 안정적으로 유지하면서 상위 5개 및 10개 결과의
재현율(recall)을 향상시켰습니다. 즉, 질의와 다른 어휘로 작성된 관련 문서도 효과적으로 찾아냅니다.

## search extra 설치

extra 의존성은 별도의 독립적인 요구사항으로 추가하지 말고, 프로젝트에 이미 선언된 devkit 패키지에 붙여서 지정해야 합니다. 즉,
`devkit-agt[search]` 또는 `devkit-dist[search]`, 문서 검색의 경우 `devkit-docs[search]`(`devkit-spec[search]`에 포함됨) 형태로 선언합니다. 이를 통해
`numpy`, `tokenizers`, 그리고 기본 모델인 `potion-base-8m`을 제공하는 `devkit-embed` 모델 패키지가 함께 설치됩니다. 이 모델은
정적이고 로컬에서 동작하므로 네트워크 통신이 필요 없고, 수십 밀리초 이내에 빠르게 로드됩니다. 또한 dense, hybrid 또는 `auto` 검색을
처음 실행할 때만 임포트되며, lexical 검색 시에는 전혀 임포트되지 않습니다.

## 검색 품질을 높이는 문서 작성법

- 임베딩 모델은 영어 전용이며 메타데이터만 읽습니다. 따라서 모든 문서에 영문 메타데이터를 작성하세요. 플레이북은 `name`과
  `description`, Living Spec 문서는 `summary`에 해당합니다. 본문은 어떤 언어로 작성해도 어휘 검색 점수에는 정상적으로 반영됩니다.
- 토크나이저는 대소문자를 일원화(casefold)하고 라틴 악센트를 제거하며, `_`, `-` 등 문자가 아닌 모든 기호를 기준으로 단어를
  분리합니다(예: `RULE-file_length`는 `rule`, `file`, `length`로 분리). 별도의 어간 추출이나 불용어 목록은 적용되지 않습니다.
- `dense` 및 `hybrid` 모드에서는 무관한 텍스트도 대부분 약간의 양수 유사도 값을 갖게 되므로 유사도 하한선 설정이 중요합니다.
  두 명령 모두 `--min-similarity` 기본값으로 `0.35`를 사용하며, 이는 hybrid의 검색 품질 향상 효과를 유지하면서 연관성이 떨어지는
  긴 꼬리(long tail) 결과를 효과적으로 걸러내도록 조율된 값입니다.

## 다른 모델 사용하기

모델은 `devkit.embedding_models` 진입점에 모듈을 등록하고, 그 옆에 `model.json`, `tokenizer.json`, `model.safetensors`를 함께
배치한 데이터 전용 Python 패키지입니다. 다른 이름의 패키지를 설치하면 라이브러리에서 해당 모델을 선택하여 사용할 수 있습니다. 기본
패키지는 `models/devkit-embed`에 위치하며, `just model-build`로 빌드된 재현 가능한 wheel 파일이 커밋되어 있어 작업 공간 명령과 테스트가
오프라인에서도 완전하게 동작합니다. 모델 패키지가 손상된 경우 모든 검색 모드에서 `SEARCH_MODEL_INVALID` 오류로 실패합니다.
