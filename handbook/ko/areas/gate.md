---
sources:
  CAP-GATE-commit-gates: null
  UC-keep-the-living-spec-consistent: null
title: 커밋 게이트
translated_from: en/areas/gate.md@36c9376a8b13e3d3
---

# 커밋 게이트

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
- [문서](documents.md)
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

커밋 게이트(commit gate)는 Git의 `pre-commit`, `commit-msg`, `post-commit` 훅에서 정책을 실행합니다. devkit은
시스템(훅 디스패처, 설정 계층, 탐색, 단계 실행기)을 소유하고, 정책 자체는 규칙과 마찬가지로 번들 안의
`kind = "gate"` 에셋으로 배포됩니다. 번들을 선택하고 `devkit sync`를 실행하면 그 번들의 게이트가 추가되며, 게이트별
설치 단계는 따로 없습니다. 게이트는 에이전트의 기억에 기대지 않고 작업을 정직하게 유지하는 검사 가운데 하나입니다.
[개념](../concepts.md)을 참고하세요.

## 훅 설치하기

대개는 아무것도 할 필요가 없습니다. 파일을 쓰는 모든 `devkit sync`가 `gate-hooks` 동기화 후 확장을 통해 디스패처를
설치합니다. 직접 설치하거나 살펴보려면 다음 명령을 씁니다.

| 하려는 일 | 실행 |
| --- | --- |
| 훅과 설정 템플릿을 설치하거나 복구 | `devkit gate install` |
| 모든 게이트, 그 실효 상태, 커밋을 실패시킬 요인 확인 | `devkit gate status` |
| devkit의 훅 항목을 제거하고 옮겨 둔 훅을 복원 | `devkit gate uninstall` |
| 훅이 하듯이 한 단계를 직접 실행 | `devkit gate run pre-commit` |

훅은 공통 Git 디렉터리에 있으므로 한 클론의 모든 워크트리가 이를 공유합니다. 각 단계에는 `<hook>.d/` 안의 실행
파일을 이름 순으로 실행하는 작은 디스패처가 붙습니다. devkit의 항목은 `20-devkit`이며, 직접 만든 스크립트를 그 앞이나
뒤(`10-custom-check`, `30-custom-check`)에 둘 수 있습니다. 기존 훅은 `<hook>.legacy`로 옮겨져 `00-legacy`를 통해
연결되고, `GATE_HOOK_PRESERVED` 경고가 표시됩니다.

`core.hooksPath`가 다른 곳을 가리키면 devkit은 이를 건드리지 않으며, `devkit gate status`가 `GATE_HOOKS_PATH_SET`으로
활성화된 게이트가 실행되지 않는다고 경고합니다. 아직 항목이 없는 단계에서 게이트를 활성화했다면 `devkit sync`를 다시
실행하세요. 그 전까지 status는 `GATE_HOOK_ENTRY_MISSING`을 보고합니다.

## 모든 커밋에서 실행되는 것

세 개의 게이트가 내장되어 있으며 모두 기본으로 켜져 있습니다.

| 게이트 | 단계 | 하는 일 |
| --- | --- | --- |
| `rules-check` | `pre-commit` | 커밋 대상에 `devkit rules check --staged`를 실행하고, error 심각도 위반이 있으면 거부합니다(`GATE_RULES_FAILED`) |
| `verify-commands` | `pre-commit` | 프로젝트 자체의 검증 명령을 실행하고, 하나라도 실패하면 거부합니다(`GATE_VERIFY_FAILED`) |
| `message-nonempty` | `commit-msg` | 빈 메시지를 거부합니다 |

`rules-check`는 커밋되는 내용만 정확히 평가하므로, 스테이징하지 않은 편집이 발견 사항을 숨기거나 만들어 낼 수
없습니다. 평가할 규칙은 게이트가 아니라 `[rules]`에서 조정합니다. [거버넌스 규칙](governance.md)을 참고하세요.

`verify-commands`에는 여러분의 명령이 필요합니다.

```toml
# .devkit/config.toml
[gates.settings.verify-commands]
commands = ["just lint-check", "just check"]
```

훅은 Git의 환경에서 실행되며, 이 환경에서는 대개 `.venv/bin`이 `PATH`에 없으므로 도구를 `uv run`이나 `just`로
호출하세요. 모든 명령은 devkit의 제한된 실행기를 거쳐 앞의 명령이 실패한 뒤에도 실행되므로, 한 번의 거부로 실패한
모든 명령과 그 로그 경로가 나열됩니다([컴팩트 명령 출력](compact.md) 참고). 명령은 인덱스가 아니라 작업 트리를 보며,
둘이 다를 수 있으면 `GATE_VERIFY_UNSTAGED` 알림이 그렇다고 알려 줍니다. 목록에는 빠른 검사만 두고 느린 테스트
모음은 CI에 맡기세요.

## 거부 읽기

모든 거부는 Agent Advisory Protocol 오류([어드바이저리](advisory.md))이므로, 코드만 보고도 여러분과 에이전트가 어떤
종류의 문제인지 알 수 있습니다.

- `BLOCKED`(종료 코드 `1`): 게이트가 실행되어 거부했습니다. 원인을 고친 뒤 다시 커밋하세요. 정책을 바꾸는 것은
  사용자의 결정입니다.
- `AUTO`(종료 코드 `2`): 게이트가 판단할 수 없었고 하나의 수정으로 해결됩니다. 보통 관리 규칙 파일이 없는 새
  워크트리나 클론에서 `devkit sync`를 실행하면 됩니다(`RULES_RUN_FAILED`, `GATE_VERIFY_NOT_RUN`).
- 설정 오류(종료 코드 `2`): 게이트 설정 자체가 망가졌으며 오류의 `[FIX]`가 복구 방법을 알려 줍니다. 예를 들어
  `GATE_CONFIG_INVALID`(잘못된 `[gates]` 테이블), `ASSET_FILE_INVALID`(드리프트가 생긴 게이트 파일: `devkit sync`),
  `GATE_LOAD_FAILED`(임포트되지 않는 게이트 패키지), `GATE_INTERPRETER_UNAVAILABLE`(훅의 Python이 devkit을 임포트할
  수 없음)이 있습니다.

`pre-commit`과 `commit-msg`는 실패 시 닫힌 상태로 동작합니다(fail closed). 거부, 설정 오류, 드리프트가 생긴 게이트
파일은 커밋을 막습니다. `post-commit`은 커밋이 생긴 뒤에 실행되므로 경고만 보고하고 항상 `0`으로 종료합니다. 실패한
게이트가 같은 단계의 나머지를 멈추지 않으므로, 한 번의 시도로 모든 거부가 보고됩니다. `git commit --no-verify`는 Git이
정의한 대로 차단 단계를 건너뜁니다.

## 팀과 개인을 위한 게이트 설정

두 계층이 `[gates]` 테이블을 제공하며, 나중 계층이 우선합니다.

| 계층 | 추적 여부 | 용도 |
| --- | --- | --- |
| `.devkit/config.toml` | 예 | 모든 클론이 공유하는 팀 정책 |
| `<common-git-dir>/devkit.config` | 아니요 | 이 클론과 그 워크트리를 위한 개인 오버라이드 |

`devkit gate install`은 설치된 모든 게이트를 주석 처리된 테이블로 `devkit.config`에 씁니다. 클론의 설정을 바꾸려면
테이블 헤더와 바꿀 키만 주석을 해제하세요. 팀이 이미 설정한 키는 실수로 복사하지 않도록 값 없이 표시됩니다. 이 파일은
추가 전용이어서 새 게이트에는 새 테이블이 생기고, 여러분이 쓴 줄은 다시 쓰이지 않습니다.

`enabled`는 모든 게이트 테이블에서 동작합니다. 설치되지 않은 게이트에 대한 항목은 차단 단계를 실패시키므로, 오타나
잊어버린 `devkit sync` 때문에 정책이 조용히 꺼질 수 없습니다.

## 직접 만든 게이트 배포하기

게이트는 규칙과 같은 플러그인 패키지 디렉터리입니다. `BaseGate` 하위 클래스(`id`, `stage`, `order`,
`enabled_by_default`, 타입이 지정된 `settings`, `run(ctx)`)를 담은 `gate.py`, 상대 경로로 임포트하는 보조 모듈,
그리고 그 옆의 `tests/`로 구성됩니다. `GateResult.passed()`나 `GateResult.skipped()`를 반환하고, 거부하려면 코드와
`fix`를 담아 `GateRefusedError`를 발생시킵니다. 번들에는 다음처럼 선언합니다.

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit"

[presets.commit]
assets = ["staged-file-limit"]
```

한 단계의 게이트는 `order`, 다음으로 `id` 순으로 실행됩니다. 메시지 변환은 `100` 미만, 검사는 `100`, 그리고
`message-nonempty`는 최종 메시지를 볼 수 있도록 `900`입니다.

## 출처

- [CAP-GATE-commit-gates](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md) (영어 원문):
  훅 래퍼, 내장 게이트, 게이트 계약, 배포와 설정 계층.
- [Gate reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/gate.md): 명령, 종료
  코드와 오류 코드.
- 게이트는 [Living Spec 일관성 유지](../journeys/keep-the-living-spec-consistent.md)의 일상적인 흐름에 포함됩니다.
