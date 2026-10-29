---
sources:
  CAP-DIST-sync-and-transactions: null
  CAP-GATE-commit-gates: null
  CAP-GEN-tracked-artifacts: null
title: 생성 파일
translated_from: en/areas/generated.md@5d8011da4228aecc
---

# 생성 파일

<!-- handbook:provenance -->
> 소스 커밋 `18b834c35c0c` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

`uv.lock`, devkit 자체의 설치 기록(`.devkit/installation.json`), 자동 생성된 클라이언트 코드, 렌더링된 스냅샷처럼 특정
명령어로 생성되지만 Git으로 버전 관리(추적)되는 파일들이 있습니다. Git은 이러한 파일을 일반 텍스트로 병합하기 때문에, 양쪽
브랜치에서 각각 파일을 재생성한 경우 원본 입력 파일들이 충돌 없이 병합되더라도 생성 파일에서 충돌이 발생하기 쉽습니다. 게다가 단순
텍스트 병합 결과는 생성기가 실제로 출력했을 내용과 일치하지 않는 경우가 대부분입니다. `devkit generated`(`devkit-agt` 제공)는
이러한 충돌을 텍스트 병합 대신 '명령어 재생성' 방식으로 깔끔하게 해결하며, 커밋된 파일이 최신 상태인지도 검사합니다. 관련 규약은
[CAP-GEN-tracked-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/generated/CAP-GEN-tracked-artifacts.md) (영어 원문)을
참고하십시오.

이 작업은 자동으로 실행되지 않습니다. merge, rebase, cherry-pick 도중 충돌이 발생해 중단되면 사용자 또는 에이전트가 `resolve`
명령을 실행하고, CI 파이프라인에서는 `check` 명령을 실행합니다. 브랜치 생명주기에서 이 과정이 차지하는 위치는
[개념](../concepts.md)에서 설명합니다.

## 아티팩트 등록하기

아티팩트는 단일 명령어가 소유하는 파일 경로들의 묶음입니다. `.devkit/config.toml`과 같은 위치에 있는 Git 추적 파일인
`.devkit/generated.toml`에 선언합니다.

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]
command = "uv lock && uv sync"

[artifacts.devkit-receipt]
after = ["uv-lock"]
```

- `paths`: 해당 명령어가 소유하고 관리하는 파일 목록입니다. `command`는 프로젝트 루트 디렉터리에서 `sh -c`로 실행되며,
  `{devkit}`은 현재 실행 중인 devkit 경로로 치환됩니다.
- `inputs`: 명령어 실행 시 읽어들이는 입력 파일 목록입니다. 충돌 발생 시 무조건 `resolve` 실행을 차단해야 하는 특별한 경우가
  아니라면 비워두지 않습니다.
- `updates`: 명령어가 파일 전체를 소유하지는 않지만 일부 내용을 갱신하는 대상 파일 목록입니다. 예를 들어 `AGENTS.md`의
  devkit 관리 블록이 이에 해당합니다.
- `after`는 아티팩트 간 실행 순서를 지정합니다. `seed`는 충돌 해결 시 어느 쪽 파일 내용을 시작점으로 삼을지 선택하며(기본값
  `ours`), `optional`은 추적 대상 파일이 없으면 해당 아티팩트를 건너뛰고, `enabled = false`는 아티팩트 자체를 비활성화합니다.

devkit은 기본적으로 `{devkit} sync`를 실행하는 `devkit-receipt` 내장 아티팩트를 등록합니다. 설치 기록에는 실제 설치된
패키지 정보가 담기므로, 위 예시처럼 uv 프로젝트에서는 락 파일 아티팩트 뒤(`after = ["uv-lock"]`)에 배치하여 환경이 먼저
갱신된 후 설치 기록이 재생성되도록 설정합니다. 네이티브 프로젝션을 Git으로 추적하는 프로젝트라면 이를 설치 기록의 `paths`가
아닌 `updates`에 추가해야 합니다. `uv run devkit generated list`를 실행하면 내장 아티팩트를 포함하여 등록된 모든 아티팩트
목록을 확인할 수 있습니다.

명령어는 반드시 결정적(deterministic)이어야 합니다. 즉, 동일한 입력이 주어지면 언제나 정확히 동일한 바이트를 출력해야 합니다.
실행할 때마다 타임스탬프나 절대 경로를 기록하는 명령어는 `check` 실행 시 항상 오래된(stale) 상태로 판정됩니다.

## 병합 충돌 해결하기

Git 작업 도중 충돌이 발생해 중단되었을 때:

```bash
uv run devkit generated resolve --dry-run   # 계획만 확인하고 파일은 변경하지 않음
uv run devkit generated resolve             # 기준 파일 초기화(seed), 재생성, 스테이징
```

`resolve`는 충돌 상태인 각 경로가 등록된 아티팩트 소유인지 여부를 판별합니다. 아티팩트가 소유한 파일의 충돌은 지정된 `seed`
쪽 내용으로 초기화한 뒤, 등록된 명령어들을 순서대로 실행하고 그 결과를 자동으로 스테이징합니다. 단, 커밋은 자동으로 수행하지
않습니다. 실행 후 상황은 다음과 같이 나뉩니다.

- 남은 충돌이 없으면 `[NEXT_CMD: git <operation> --continue]` 안내가 출력됩니다.
- 아티팩트가 소유하지 않은 일반 파일의 충돌이 남아 있으면, `GENERATED_CONFLICTS_REMAIN` 경고와 함께 목록이 표시되므로 수동으로
  해결해야 합니다.
- rebase 진행 중에는 커밋이 순차적으로 다시 적용되면서 매 커밋마다 멈출 수 있으므로, 멈출 때마다 `resolve`를 반복 실행하십시오.

아티팩트가 소유하지 않은 충돌 파일이 현재 해결하려는 아티팩트의 *입력(inputs)* 파일이거나 그 아티팩트가 `updates`로 고쳐 쓰는
파일이라면, 파일을 수정하기 전에 즉시 실행을 거부합니다(`GENERATED_INPUTS_CONFLICTED`). 명령어가 Git 충돌 마커를 잘못
읽어들이거나 마커가 남은 파일을 스테이징하지 않도록, 먼저 해당 파일의 충돌을 수동으로 해결하고 스테이징한 후 `resolve`를 다시
실행하십시오. 거부 메시지의 `[FIX]`가 실행할 `git add`와 `resolve` 명령을 정확히 알려 줍니다. 명령어 실행이 실패하면 `GENERATED_COMMAND_FAILED`가
발생하며, 선언되지 않은 파일을 수정한 명령어는 `GENERATED_OUTPUT_UNDECLARED` 오류를 내고 변경 사항은 검토할 수 있도록 작업
트리에 그대로 남겨둡니다. 두 경우 모두 아무것도 스테이징되지 않으므로, 원인을 조치한 후 깨끗하게 다시 실행할 수 있습니다.

## 병합 상황 외에서의 검사 및 재생성

충돌 없이 텍스트 병합이 깔끔하게 끝난 경우 Git 충돌로 간주되지 않으므로 `resolve`가 개입하지 않습니다. 하지만 병합된 입력
파일의 내용과 생성 파일의 내용이 불일치할 수 있습니다. 이를 점검하고 해결하기 위한 두 가지 명령이 있습니다.

- `uv run devkit generated check`: `HEAD`(또는 `--rev <REV>`)의 임시 분리(detached) 워크트리에서 모든 아티팩트를 처음부터
  다시 생성해 보고, 오래된(stale) 아티팩트가 발견되면 각각 `GENERATED_STALE`로 보고하며 정확한 `regen` 명령을 조치로
  제시하고 종료 코드 `1`로 끝납니다. 아티팩트가 소유한 파일(`paths`)이 바뀐 경우에만 오래된 것으로 판단하며, `updates`로만 고쳐
  쓰는 파일의 변경은 목록에 나오지만 판정에는 영향을 주지 않습니다. 텍스트 출력에는 오래된 아티팩트만 표시됩니다. 현재
  체크아웃된 작업 공간에는 전혀 영향을 주지 않으며, 새로 클론한 환경처럼 실행되므로 Git 무시(ignored) 파일 없이도 정상 동작해야
  합니다. 이 명령은 CI 파이프라인에서 실행하십시오.
- `uv run devkit generated regen [ID...]`: 현재 작업 트리에서 명령어를 직접 다시 실행하며, 결과를 자동으로 스테이징하지는
  않습니다. Git 인덱스에 충돌이 남아 있는 상태에서는 `GENERATED_UNMERGED` 오류와 함께 실행을 거부하며, 이 오류의 `[FIX]`는
  `uv run devkit generated resolve`입니다.

## 제약 사항과 신뢰성

- 아티팩트는 파일 단위 전체를 소유합니다. 루트 `AGENTS.md`처럼 파일의 일부만 사용자가 직접 관리하는 파일은 독립 아티팩트로 등록할
  수 없습니다. 이러한 파일의 충돌은 수동으로 해결해야 하며, 소유 명령어는 `updates` 설정을 통해 자신이 관리하는 블록만 부분
  갱신합니다.
- 전용 Git 병합 드라이버(merge driver)는 제공되지 않습니다. Git의 병합 드라이버는 전체 트리가 병합되기 전에 개별 파일 단위로
  호출되므로, 여러 파일이 관련된 재생성 명령을 온전히 실행할 수 없기 때문입니다. 베이스 브랜치를 PR에 병합하고 `resolve`를
  호출하는 자동화 CI 봇 구성은 각 저장소의 환경에 맞게 구현해야 하며, 일반적인 Git 호스팅 서비스의 웹 병합 버튼은 이러한
  사용자 정의 해결 로직을 지원하지 않습니다.
- 명령어는 Git으로 버전 관리되는 `.devkit/generated.toml`에서 로드되며, 게이트 명령어(`CAP-GATE-commit-gates`)와 마찬가지로
  현재 사용자의 권한으로 실행됩니다. 신뢰할 수 없는 외부 기여에 대해 `resolve`나 `check`를 실행하는 CI 작업은 반드시 신뢰할 수
  있는 커밋의 설정 파일을 기반으로 실행해야 합니다.

설치 기록 자체가 작성되는 원리와 여러 클론 간 일관성을 유지하는 메커니즘은 [배포](distribution.md) 및
`CAP-DIST-sync-and-transactions`에서 자세히 다룹니다.
