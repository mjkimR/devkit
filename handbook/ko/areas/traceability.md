---
sources:
  CAP-DLV-drift-reconciliation: null
  CAP-DOCS-document-lookup: null
  CAP-TRACE-code-entrypoints: null
  UC-keep-the-living-spec-consistent: null
  UC-run-parallel-work-safely: null
title: 추적성
translated_from: en/areas/traceability.md@9ace858586f2f773
---

# 추적성

<!-- handbook:provenance -->
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

추적성(traceability)은 Living Spec 문서와 코드를 연결합니다. capability나 use case 문서는 해당 기능의 구현이
시작되는 파일 및 디렉터리 경로인 `entrypoints`를 선언할 수 있습니다. 이 필드를 통해 문서에서 실제 구현 코드로, 반대로
코드 경로에서 관련 문서로 쉽게 추적할 수 있으며, 문서에 연결된 코드가 삭제되었을 때 커밋 게이트(commit gate)가 이를 즉시
감지할 수 있습니다. 경로 계약, 규칙, 역방향 조회는 devkit-docs가 맡고, devkit-spec은 스펙 번들에서 선언을 도출하는 기능을
더합니다. 상세 사양 계약은
[CAP-TRACE-code-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)을 참고하세요.

엔트리포인트는 코드 탐색을 시작하는 진입점일 뿐이며, 전체 구현 파일 목록이나 문서의 명세대로 코드가 동작함을 보증하는 증거는
아닙니다. 테스트 범위와 코드의 정확성은 테스트와 코드 리뷰를 통해 검증해야 합니다. Living Spec과 문서 체계에 대한 기본 개념은
[개념](../concepts.md)에서 다룹니다.

## 엔트리포인트 선언 방법

```yaml
entrypoints:
  - src/example/engine.py
  - src/example/cli/
```

- 이 필드는 `docs/capabilities/` 및 `docs/usecases/`(그리고 패키지 네임스페이스 루트인 `docs/packages/<name>/` 하위의
  동일한 디렉터리) 아래의 Markdown 파일에만 지정합니다.
- 경로는 `/`를 사용하는 작업 공간(workspace) 상대 경로로 명시해야 하며, 네임스페이스 문서에서도 마찬가지입니다. 패키지 상대
  경로는 허용되지 않습니다. 파일과 디렉터리 경로 모두 선언할 수 있습니다.
- 절대 경로, `..`, 역슬래시(`\`), 드라이브 콜론, 와일드카드(glob) 문자는 사용할 수 없습니다. 경로는 전체 세그먼트 단위로
  대소문자를 엄격히 구분하여 비교합니다. 예를 들어 `src/a`는 `src/a/b.py`를 포함하지만, `src/ab`는 포함하지 않습니다.

동일한 경로 규칙이 작업 범위 비교의 코드 경로에도 적용되며, 이를 통해 Host는 병렬 작업들이 동일한 코드를 수정하고 있는지
파악합니다. 자세한 내용은 [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`)를 참고하세요.

## 경로와 연결된 문서 찾기

파일을 수정하기 전에, 해당 경로를 참조하는 문서가 무엇인지 확인할 수 있습니다.

```bash
uv run devkit docs list capability --file src/engine/
uv run devkit docs list usecase --file src/engine/parse.py
```

이 명령은 엔트리포인트가 지정한 경로와 일치하거나, 해당 경로 하위에 있거나, 해당 경로를 포함하는 디렉터리로 선언된 문서를 모두
나열합니다. 파일이 실제로 디스크에 존재하지 않아도 조회가 가능하므로, 방금 삭제한 파일에 연결되어 있던 문서도 찾아낼 수 있습니다.
경로 규칙을 위반한 경우 문서를 읽기 전에 `DOCS_ENTRYPOINTS_PATH_INVALID` 오류로 실패합니다. `devkit docs list`의 다른 기능에
대한 설명은 [문서](documents.md)와 `CAP-DOCS-document-lookup`을 참고하세요.

## 선언의 최신 상태 유지

`RULE-code-entrypoints`(linter 페이즈, 심각도 error, 자동 수정 불가) 규칙은 선언된 모든 경로가 작업 공간 내에 실제로 존재하는
유효한 파일이나 디렉터리인지 검사합니다. 커밋 게이트나 CI 실행 시에는 해당 스냅샷 트리를 직접 검사하며, diff를 통해 삭제되는
경로를 선언하고 있는 현재 문서도 모두 감지하여 보고합니다. 따라서 문서를 갱신하지 않은 채 코드를 삭제하면 커밋 게이트 검사에서
실패합니다.

규칙 위반이 감지되면 상황에 맞는 조치를 직접 결정해야 합니다. 이 규칙은 변경 사유를 임의로 추측하지 않습니다.

- 코드가 다른 위치로 이동한 경우: 선언 경로를 새 위치로 수정합니다.
- 코드를 의도적으로 삭제한 경우: 더 이상 유효하지 않은 선언을 문서에서 제거합니다.
- 실수로 코드가 삭제된 경우: 삭제된 코드를 복원합니다.

이는 [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)(`UC-keep-the-living-spec-consistent`)의
핵심 활동입니다. 엔트리포인트는 `CAP-DLV-drift-reconciliation`에 따른 수동 드리프트 점검 시 관련 근거를 찾는 데도 유용하지만,
경로 검사를 통과했다고 해서 문서 내용이 최신 상태임을 완전히 보증하는 것은 아닙니다.

## 완료된 스펙에서 선언 도출하기

스펙 번들에는 이미 코드와 문서 간의 연결 정보가 담겨 있습니다. `tasks.md`의 `_Boundary` 항목에는 각 작업이 수정한 코드 경로가
나열되어 있고, `reconcile.md`에는 해당 변경에 따라 조정한 Living Spec 문서가 기록되어 있습니다. `devkit spec entrypoints derive`
명령은 이 두 정보를 결합하여 문서-경로 쌍을 자동으로 도출합니다.

```bash
uv run devkit spec entrypoints derive --spec <bundle-dir>     # 단일 번들 대상 후보 확인 (파일 변경 없음)
uv run devkit spec entrypoints derive --all --min-count 2      # 여러 번들에 걸친 역방향 보완(backfill)
uv run devkit spec entrypoints derive --spec <bundle-dir> \
  --apply --target <ID> --code src/engine/                     # 선택한 경로 반영
```

효과적인 활용 방법은 다음과 같습니다.

1. 먼저 `--apply` 없이 실행합니다. 출력되는 각 `[CANDIDATES: ...]` 줄은 문서별로 도출된 경로와 상태(`new`, `missing`,
   더 짧은 상위 경로에 포함된 `folded`, 이미 선언된 `declared`)를 보여 줍니다. 문서는 한 번에 20개씩 페이지로 나뉘며
   (`--limit`, `--offset`, 다음 페이지용 `[NEXT_CMD: ...]`), 건너뛴 입력은 사유별로 집계됩니다(`[SKIPPED_COUNT: ...]`,
   `--skipped`로 하나씩 나열).
2. 실제 반영 전에 후보를 검토합니다. 단순 문구 수정 차원에서 capability를 수정한 번들이라도, 해당 작업이 명시한 모든 경로와
   짝지어질 수 있습니다. 이러한 문서는 제외하고, 디렉터리 후보는 해당 패키지를 실제로 소유한 문서에만 선언하며, 모든 번들이
   공통으로 수정하는 허브 파일은 `--exclude` 옵션으로 제외하세요. 이 검토 절차는 `spec-entrypoints` 스킬이 안내하며, `spec-sync`
   단계에서 현재 번들을 대상으로 자동 수행됩니다.
3. 문서별로 `--apply --target <ID>` 및 `--code <path>` 옵션을 지정하여 선별적으로 반영합니다. `--code` 경로로 `folded`
   후보를 그대로 쓰거나, 디렉터리 후보 아래의 파일(진입 파일)을 지정할 수도 있습니다. 어떤 후보와도 맞지 않는 `--code` 경로가
   있으면 아무것도 쓰기 전에 `SPEC_ENTRYPOINTS_CODE_UNMATCHED`로 실행 전체가 거부되므로, 오타 하나 때문에 나머지 선택만
   반영되는 일은 없습니다. 프런트매터의 `entrypoints` 블록만 갱신되며 다른 내용은 그대로 보존됩니다. 이미 반영된 상태에서 다시
   실행해도 불필요한 파일 쓰기는 일어나지 않습니다. 페이지 나눔은 `--apply`가 쓰는 범위를 제한하지 않습니다.

과거 문서를 일괄 보완할 때는 `--all`과 `--min-count` 옵션을 함께 사용하세요. 여러 스펙에서 반복적으로 도출된 쌍일수록 신뢰할 수
있는 강력한 후보입니다. 상세 오류 코드와 전체 옵션 목록은 관련 사양 계약에서 확인할 수 있습니다.
