---
sources:
  CAP-DLV-drift-reconciliation: null
  CAP-DOCS-document-lookup: null
  CAP-TRACE-code-entrypoints: null
  UC-keep-the-living-spec-consistent: null
  UC-run-parallel-work-safely: null
title: 추적성
translated_from: en/areas/traceability.md@bcfd00b7a4d9c985
---

# 추적성

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

추적성(traceability)은 Living Spec 문서와 코드를 잇습니다. 기능이나 유스케이스는 구현이 시작되는 파일과 디렉터리인
`entrypoints`를 선언할 수 있습니다. 이 필드 하나로 문서에서 코드로, 코드 경로에서 문서로 이동할 수 있고, 문서 아래의
코드가 사라졌을 때 커밋 게이트(commit gate)가 이를 알아챌 수 있습니다. 계약은
[CAP-TRACE-code-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)입니다.

엔트리포인트는 읽기를 시작하는 곳일 뿐, 구현의 완전한 목록도 아니고 코드가 문서대로 동작한다는 증거도 아닙니다. 범위와
정확성은 여전히 테스트와 리뷰의 몫입니다. Living Spec과 그 문서는 [개념](../concepts.md)에서 소개합니다.

## 엔트리포인트 선언하기

```yaml
entrypoints:
  - src/example/engine.py
  - src/example/cli/
```

- 이 필드는 `docs/capabilities/`와 `docs/usecases/`(그리고 네임스페이스 루트 `docs/packages/<name>/`의 같은
  디렉터리) 아래의 Markdown 파일에만 둡니다.
- 경로는 `/`를 쓰는 작업 공간 기준의 리터럴 경로이며, 네임스페이스 문서에서도 마찬가지입니다. 패키지 기준 경로는 쓰지
  않습니다. 파일과 디렉터리 모두 가능합니다.
- 절대 경로, `..`, 역슬래시, 드라이브 콜론, glob 문자는 쓸 수 없습니다. 비교는 경로 세그먼트 단위이며 대소문자를
  구분합니다. `src/a`는 `src/a/b.py`를 포함하지만 `src/ab`는 포함하지 않습니다.

같은 경로 계약이 작업 범위 레지스트리의 코드 경로에도 적용되며, 병렬 작업은 이를 통해 같은 코드를 건드린다는 사실을
알게 됩니다. [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`)를 참고하십시오.

## 경로를 소유한 문서 찾기

파일을 바꾸기 전에 어떤 문서가 그 파일을 주장하는지 물어보십시오.

```bash
uv run devkit spec list capability --file src/engine/
uv run devkit spec list usecase --file src/engine/parse.py
```

엔트리포인트가 경로와 같거나, 경로 아래에 있거나, 경로를 포함하는 디렉터리인 문서를 나열합니다. 경로가 존재하지 않아도
되므로 방금 지운 파일로도 문서를 찾을 수 있습니다. 계약을 어긴 경로는 문서를 읽기 전에
`SPEC_ENTRYPOINTS_PATH_INVALID`로 실패합니다. `devkit spec list`의 나머지 기능은 [문서](documents.md)와
`CAP-DOCS-document-lookup`에서 설명합니다.

## 선언을 살아 있게 유지하기

`RULE-code-entrypoints`(linter 페이즈, 심각도 error, 자동 수정 불가)는 선언된 모든 경로가 작업 공간 안에 실제로
존재하는 올바른 파일이나 디렉터리인지 검사합니다. 커밋 게이트나 CI 실행에서는 스냅샷의 트리를 읽고, diff가 삭제하는
경로를 선언한 현재 문서도 모두 보고합니다. 따라서 문서를 건드리지 않고 코드를 지우면 게이트가 실패합니다.

규칙이 발동하면 무슨 일이 있었는지 판단하십시오. 규칙은 추측하지 않습니다.

- 코드가 옮겨졌다면, 선언이 새 위치를 가리키게 합니다.
- 코드를 의도적으로 제거했다면, 낡은 선언을 제거합니다.
- 실수로 지웠다면, 코드를 복원합니다.

이는 [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
(`UC-keep-the-living-spec-consistent`)의 일부입니다. 엔트리포인트는 `CAP-DLV-drift-reconciliation`의 수동 드리프트
점검에서 증거를 찾는 데도 도움이 되지만, 경로 검사를 통과했다고 해서 문서가 최신이라는 것이 증명되지는 않습니다.

## 완료된 스펙에서 선언 도출하기

스펙 번들은 이미 연결의 양쪽을 담고 있습니다. `tasks.md`는 각 작업이 건드릴 수 있는 코드를 `_Boundary` 줄에
나열하고, `reconcile.md`는 변경이 조정한 Living Spec 문서를 나열합니다. `devkit spec entrypoints derive`는 이 둘을
문서와 경로의 쌍으로 결합합니다.

```bash
uv run devkit spec entrypoints derive --spec <bundle-dir>     # one bundle, nothing written
uv run devkit spec entrypoints derive --all --min-count 2      # backfill across bundles
uv run devkit spec entrypoints derive --spec <bundle-dir> \
  --apply --target <ID> --code src/engine/                     # write the chosen ones
```

잘 쓰는 방법은 다음과 같습니다.

1. 먼저 `--apply` 없이 실행합니다. 각 `[CANDIDATES: ...]` 줄은 문서 하나와 그 경로를 상태별로 보여 줍니다. `new`,
   `missing`, `folded`(더 짧은 후보에 포함됨), `declared`입니다.
2. 적용하기 전에 검토합니다. 문구 때문에만 기능을 건드린 번들도 그 기능을 작업이 명시한 모든 경로와 짝짓습니다. 그런
   문서는 빼고, 디렉터리 후보는 해당 패키지를 소유한 문서에만 남기며, 모든 번들이 건드리는 허브 파일은 `--exclude`로
   제외합니다. 이 검토는 `spec-entrypoints` 스킬이 담당하며, `spec-sync`가 현재 번들에 대해 실행합니다.
3. 문서별로 `--apply --target <ID>`와 `--code <path>`로 적용합니다. 프런트매터의 `entrypoints` 블록만 다시 쓰고 나머지
   바이트는 모두 유지하며, 다시 실행해도 아무것도 쓰지 않습니다.

오래된 문서를 채울 때는 `--all`과 `--min-count`를 함께 씁니다. 여러 스펙에서 나온 쌍일수록 강한 후보입니다. 오류 코드와
전체 옵션 목록은 계약에 있습니다.
