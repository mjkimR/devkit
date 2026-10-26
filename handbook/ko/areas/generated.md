---
sources:
  CAP-DIST-sync-and-transactions: null
  CAP-GATE-commit-gates: null
  CAP-GEN-tracked-artifacts: null
title: 생성 파일
translated_from: en/areas/generated.md@eb9c20a6124c013e
---

# 생성 파일

<!-- handbook:provenance -->
> 소스 커밋 `c94b6a08710e` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

어떤 파일은 명령이 만들어 내지만 Git이 추적합니다. `uv.lock`, devkit 자체의 설치 기록(receipt)
`.devkit/installation.json`, 생성된 클라이언트, 렌더링된 스냅샷 같은 것들입니다. Git은 이 파일들을 텍스트로
병합하므로, 각자 파일을 다시 생성한 두 브랜치는 입력이 깔끔하게 병합되더라도 충돌하며, 텍스트 병합 결과가 생성기가 쓸
내용과 같은 경우는 드뭅니다. `devkit generated`(`devkit-agt` 제공)는 이런 충돌을 병합 대신 재생성으로 해결하고, 커밋된
사본이 최신인지 검사합니다. 계약은
[CAP-GEN-tracked-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/generated/CAP-GEN-tracked-artifacts.md) (영어 원문)입니다.

자동으로 실행되는 것은 없습니다. merge, rebase, cherry-pick이 멈추면 사용자나 에이전트가 `resolve`를 실행하고, CI는
`check`를 실행합니다. 이것이 브랜치의 생애에서 어디에 놓이는지는 [개념](../concepts.md)에서 설명합니다.

## 아티팩트 등록하기

아티팩트는 하나의 명령이 소유하는 경로의 집합입니다. `.devkit/config.toml` 옆의 추적 파일 `.devkit/generated.toml`에
선언합니다.

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]
command = "uv lock && uv sync"

[artifacts.devkit-receipt]
after = ["uv-lock"]
```

- `paths`는 명령이 소유하는 파일입니다. `command`는 프로젝트 루트에서 `sh -c`로 실행되며, `{devkit}`은 실행 중인
  devkit을 가리킵니다.
- `inputs`는 명령이 읽는 파일입니다. 어떤 충돌이든 `resolve`를 막아야 할 때만 비워 둡니다.
- `updates`는 명령이 소유하지 않으면서 다시 쓰는 파일을 나열합니다. 예를 들어 `AGENTS.md`의 관리 블록입니다.
- `after`는 아티팩트의 순서를 정하고, `seed`는 명령이 충돌의 어느 쪽에서 시작할지 고르며(기본값 `ours`),
  `optional`은 추적 경로가 없는 아티팩트를 건너뛰고, `enabled = false`는 아티팩트를 뺍니다.

devkit은 명령이 `{devkit} sync`인 내장 아티팩트 `devkit-receipt` 하나를 등록합니다. 설치 기록은 설치된 패키지를
기록하므로, uv 프로젝트는 위 예처럼 이를 락 파일 뒤에 두어 설치 기록을 다시 만들기 전에 환경이 먼저 갱신되게 합니다.
네이티브 프로젝션을 추적하는 프로젝트는 그것을 설치 기록의 `paths`가 아니라 `updates`에 추가합니다.
`uv run devkit generated list`는 내장 아티팩트를 포함해 등록된 아티팩트를 보여 줍니다.

명령은 결정적이어야 합니다. 같은 입력이면 같은 바이트를 내야 합니다. 타임스탬프나 절대 경로를 쓰는 명령은 `check`에서
항상 오래된 것으로 보고됩니다.

## 병합 충돌 해결하기

Git이 충돌로 멈추면 다음을 실행합니다.

```bash
uv run devkit generated resolve --dry-run   # show the plan, change nothing
uv run devkit generated resolve             # seed, regenerate, stage
```

`resolve`는 병합되지 않은 각 경로를 아티팩트 소유인지 아닌지로 분류하고, 소유한 충돌을 각자의 `seed` 쪽으로 채운 뒤,
명령을 순서대로 실행하고 결과를 스테이징합니다. 커밋은 절대 하지 않습니다. 그다음은 이렇습니다.

- 충돌이 남지 않으면 `[NEXT_CMD: git <operation> --continue]`를 출력합니다.
- 소유하지 않은 충돌이 남으면 `GENERATED_CONFLICTS_REMAIN` 경고에 나열하므로 직접 해결합니다.
- rebase 중에는 재적용되는 커밋마다 다시 멈출 수 있으므로, 멈출 때마다 `resolve`를 실행합니다.

소유하지 않은 충돌이 계획에 포함된 아티팩트의 *입력*이면 아무것도 바꾸기 전에 거부합니다
(`GENERATED_INPUTS_CONFLICTED`). 명령이 충돌 표식을 읽지 않도록 그 입력을 먼저 해결해 스테이징한 뒤 다시 실행하십시오.
명령이 실패하면 `GENERATED_COMMAND_FAILED`이고, 선언하지 않은 파일을 바꾼 명령은 `GENERATED_OUTPUT_UNDECLARED`이며 그
변경은 검토를 위해 작업 트리에 남습니다. 어느 경우든 아무것도 스테이징되지 않고, 다시 실행하면 깨끗하게 처음부터
시작합니다.

## 병합 밖에서 검사하고 재생성하기

깔끔한 텍스트 병합은 충돌이 아니므로 `resolve`가 건드리지 않지만, 그 파일이 병합된 입력과 여전히 맞지 않을 수 있습니다.
이를 다루는 명령이 두 개 있습니다.

- `uv run devkit generated check`는 `HEAD`(또는 `--rev REV`)의 임시 분리 워크트리에서 모든 아티팩트를 재생성하고,
  오래된 것을 각각 `GENERATED_STALE`로 보고하며 `1`로 종료합니다. 체크아웃은 건드리지 않고 명령은 새 클론에서처럼
  실행되므로, 무시된 파일 없이도 동작해야 합니다. CI에서 실행하십시오.
- `uv run devkit generated regen [ID...]`는 그 자리에서 명령을 다시 실행하고 아무것도 스테이징하지 않습니다. 인덱스에
  충돌이 있는 동안에는 `GENERATED_UNMERGED`로 거부하므로, 그때는 `resolve`를 사용합니다.

## 한계와 신뢰

- 아티팩트는 파일 전체를 소유합니다. 루트 `AGENTS.md`처럼 일부만 사용자 소유인 파일은 아티팩트가 될 수 없습니다. 그
  충돌은 직접 해결하고, 소유 명령이 `updates`를 통해 자기 부분을 다시 씁니다.
- 병합 드라이버는 없습니다. Git은 트리가 병합되기 전에 파일마다 드라이버를 실행하므로 재생성을 할 수 없습니다. 기준
  브랜치를 풀 리퀘스트에 병합하고 `resolve`를 실행하는 CI 봇은 각 저장소의 몫이며, 호스팅 서비스의 병합 버튼은 사용자
  정의 해결을 실행하지 않습니다.
- 명령은 추적되는 `.devkit/generated.toml`에서 오고, 게이트 명령(`CAP-GATE-commit-gates`)처럼 사용자의 권한으로
  실행됩니다. 신뢰할 수 없는 기여에 대해 `resolve`나 `check`를 실행하는 CI 작업은 신뢰할 수 있는 커밋에서 설정을
  가져옵니다.

설치 기록 자체가 어떻게 쓰이고 클론 사이에서 어떻게 일치하게 유지되는지는 [배포](distribution.md)와
`CAP-DIST-sync-and-transactions`에서 설명합니다.
