---
sources:
  CAP-GATE-commit-gates: null
  UC-keep-the-living-spec-consistent: null
title: 커밋 게이트
translated_from: en/areas/gate.md@36c9376a8b13e3d3
---

# 커밋 게이트

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

커밋 게이트(commit gate)는 Git의 `pre-commit`, `commit-msg`, `post-commit` 훅에서 정책을 실행합니다. devkit이
훅 디스패처, 설정 계층, 디스커버리, 단계 실행기 등 전체 프레임워크를 제공하며, 정책 자체는 거버넌스 규칙과 마찬가지로 번들
내 `kind = "gate"` 에셋 형태로 배포됩니다. 번들을 지정하고 `devkit sync`를 실행하면 해당 번들의 게이트가 함께 추가되므로
별도의 개별 설치 과정이 필요하지 않습니다. 게이트는 에이전트의 기억에 의존하지 않고도 작업의 무결성을 엄격하게 유지해 주는
검사 체계 중 하나입니다. 자세한 내용은 [개념](../concepts.md)을 참고하십시오.

## 훅 설치 및 관리

일반적으로는 수동으로 작업할 필요가 없습니다. 파일을 변경하는 모든 `devkit sync` 실행 시 `gate-hooks` 사후 동기화 확장을
통해 디스패처가 자동으로 설치됩니다. 수동으로 설치하거나 상태를 점검하려면 다음 명령을 사용합니다.

| 작업 내용 | 실행 명령 |
| --- | --- |
| 훅과 설정 템플릿 설치 또는 복구 | `devkit gate install` |
| 모든 게이트의 실효 상태 및 커밋 실패 요인 확인 | `devkit gate status` |
| devkit 훅 항목 제거 및 백업된 기존 훅 복원 | `devkit gate uninstall` |
| 훅과 동일하게 특정 단계를 수동 실행 | `devkit gate run pre-commit` |

훅은 공통 Git 디렉터리에 위치하므로 동일한 클론에 속한 모든 워크트리가 이를 공유합니다. 각 단계마다 `<hook>.d/` 디렉터리 내의
실행 파일들을 알파벳 순으로 실행하는 경량 디스패처가 배치됩니다. devkit의 기본 항목은 `20-devkit`이며, 사용자 정의 스크립트를
그 앞이나 뒤(`10-custom-check`, `30-custom-check`)에 자유롭게 배치할 수 있습니다. 기존에 존재하던 훅은 `<hook>.legacy`로
안전하게 백업된 후 `00-legacy`를 통해 연쇄 실행되며, 이때 `GATE_HOOK_PRESERVED` 경고가 출력됩니다.

만약 `core.hooksPath`가 다른 경로로 설정되어 있다면 devkit은 이를 덮어쓰지 않으며, `devkit gate status` 실행 시
`GATE_HOOKS_PATH_SET` 경고를 통해 활성화된 게이트가 동작하지 않음을 알립니다. 아직 디스패처 항목이 생성되지 않은 단계에서 새
게이트를 활성화한 경우에는 `devkit sync`를 다시 실행하십시오. 그전까지는 상태 확인 시 `GATE_HOOK_ENTRY_MISSING`이 보고됩니다.

## 매 커밋마다 실행되는 기본 게이트

다음 세 가지 게이트가 내장되어 있으며, 모두 기본적으로 활성화되어 있습니다.

| 게이트 | 단계 | 주요 역할 |
| --- | --- | --- |
| `rules-check` | `pre-commit` | 커밋 대상(staged)에 `devkit rules check --staged`를 실행하고, 오류(error) 수준 위반이 있으면 커밋을 차단합니다(`GATE_RULES_FAILED`) |
| `verify-commands` | `pre-commit` | 프로젝트 자체 검증 명령을 실행하고, 하나라도 실패하면 커밋을 차단합니다(`GATE_VERIFY_FAILED`) |
| `message-nonempty` | `commit-msg` | 커밋 메시지가 비어 있으면 커밋을 차단합니다 |

`rules-check`는 스테이징된 변경 사항만을 정확히 평가하므로, 스테이징되지 않은 수정 사항이 위반을 숨기거나 불필요한 위반을
일으키지 않습니다. 평가 대상 규칙은 게이트가 아니라 `[rules]` 설정에서 조정합니다. 자세한 내용은
[거버넌스 규칙](governance.md)을 참고하십시오.

`verify-commands`를 동작시키려면 프로젝트 고유의 검증 명령을 설정해야 합니다.

```toml
# .devkit/config.toml
[gates.settings.verify-commands]
commands = ["just lint-check", "just check"]
```

훅은 Git 환경에서 실행되므로 보통 `.venv/bin`이 `PATH`에 포함되어 있지 않습니다. 따라서 도구 호출 시 `uv run`이나
`just`를 사용하십시오. devkit의 바운디드 러너(bounded runner)를 통해 앞선 명령이 실패하더라도 모든 검증 명령이 끝까지
실행되므로, 한 번의 거부만으로 실패한 모든 명령과 로그 파일 경로를 한눈에 파악할 수 있습니다([컴팩트 명령 출력](compact.md)
참고). 검증 명령은 Git 인덱스가 아니라 작업 트리의 파일을 직접 읽으므로, 둘 사이에 차이가 있을 경우 `GATE_VERIFY_UNSTAGED`
안내가 표시됩니다. 이곳에는 신속하게 끝나는 검사만 지정하고, 시간이 오래 걸리는 테스트 스위트는 CI 파이프라인에 위임하는 것이 좋습니다.

## 거부(Refusal) 원인 분석

모든 커밋 차단은 Agent Advisory Protocol 오류([어드바이저리](advisory.md))로 보고되므로, 오류 코드만으로도 문제의 성격을
명확히 파악할 수 있습니다.

- `BLOCKED`(종료 코드 `1`): 게이트 검사가 실행되어 정책 위반으로 커밋을 거부했습니다. 원인을 수정한 뒤 다시 커밋하십시오.
  정책 자체를 수정할지 여부는 사용자가 결정해야 합니다.
- `AUTO`(종료 코드 `2`): 게이트가 정상 판정을 내릴 수 없는 상태이며, 단일 조치로 자동 해결할 수 있습니다. 주로 새 워크트리나
  클론에서 관리 대상 규칙 파일이 누락되어 발생하며, `devkit sync`를 실행하면 해결됩니다(`RULES_RUN_FAILED`, `GATE_VERIFY_NOT_RUN`).
- 환경 설정 오류(종료 코드 `2`): 게이트 설정 자체가 잘못된 상태이며, 오류 메시지의 `[FIX]` 항목에 복구 방법이 안내됩니다. 예를 들어
  `GATE_CONFIG_INVALID`(`[gates]` 테이블 설정 오류), `ASSET_FILE_INVALID`(게이트 파일 변경 드리프트 발생: `devkit sync` 필요),
  `GATE_LOAD_FAILED`(게이트 패키지 임포트 실패), `GATE_INTERPRETER_UNAVAILABLE`(훅 실행용 Python에서 devkit을 임포트할 수 없음) 등이
  있습니다.

`pre-commit`과 `commit-msg` 단계는 안전 우선(fail-closed) 원칙에 따라 동작합니다. 즉, 정책 위반이나 설정 오류, 게이트 파일
드리프트가 감지되면 커밋이 즉시 차단됩니다. 반면 `post-commit`은 커밋이 생성된 후에 동작하므로 경고만 보고하고 항상 종료 코드
`0`으로 끝납니다. 어떤 게이트가 실패하더라도 해당 단계의 나머지 게이트 실행을 중단하지 않으므로, 한 번의 시도로 모든 거부
사유를 확인할 수 있습니다. Git 기본 기능인 `git commit --no-verify`를 사용하면 차단 단계를 건너뛸 수 있습니다.

## 팀 및 로컬 게이트 설정

게이트 설정은 두 계층의 `[gates]` 테이블에서 읽어오며, 나중에 지정된 계층이 우선 적용됩니다.

| 계층 | Git 추적 여부 | 용도 |
| --- | --- | --- |
| `.devkit/config.toml` | 예 | 모든 클론이 공유하는 팀 공통 정책 |
| `<common-git-dir>/devkit.config` | 아니요 | 현재 클론 및 워크트리에만 적용되는 개인 오버라이드 |

`devkit gate install`을 실행하면 설치된 모든 게이트가 주석 처리된 테이블 형태로 `devkit.config`에 기록됩니다. 현재 클론의
설정을 변경하려면 테이블 헤더와 변경하려는 설정 키의 주석만 해제하십시오. 팀 공통으로 이미 설정된 키는 실수로 덮어쓰지 않도록
값 없이 표시됩니다. 이 파일은 추가 전용(append-only) 방식으로 관리되므로 새 게이트가 추가되면 새 테이블이 덧붙여지며, 기존에
작성한 내용은 덮어쓰이지 않습니다.

`enabled` 속성은 모든 게이트 테이블에서 공통으로 지원됩니다. 설치되지 않은 게이트를 활성화하도록 설정하면 차단 단계에서
오류가 발생하므로, 오타나 `devkit sync` 누락으로 인해 검증 정책이 의도치 않게 비활성화되는 것을 방지합니다.

## 사용자 정의 게이트 작성 및 배포

게이트는 거버넌스 규칙과 마찬가지로 플러그인 패키지 디렉터리 형태로 작성합니다. `BaseGate` 서브클래스(`id`, `stage`, `order`,
`enabled_by_default`, 타입 어노테이션이 적용된 `settings`, `run(ctx)`)가 정의된 `gate.py`, 상대 경로로 임포트되는 보조 모듈,
그리고 동일 디렉터리 내의 `tests/`로 구성됩니다. 통과 시에는 `GateResult.passed()` 또는 `GateResult.skipped()`를 반환하고,
커밋을 차단할 때는 오류 코드와 조치 가이드(`fix`)를 담아 `GateRefusedError`를 발생시킵니다. 번들 매니페스트에는 다음과 같이 선언합니다.

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit"

[presets.commit]
assets = ["staged-file-limit"]
```

한 단계 안에서 여러 게이트가 실행될 때는 `order` 순으로 정렬되고, 동일한 경우 `id` 순으로 실행됩니다. 메시지 변환 게이트는
`100` 미만, 일반 검증 게이트는 `100`, 최종 메시지를 검사하는 `message-nonempty`는 `900`의 우선순위를 갖습니다.

## 관련 자료

- [CAP-GATE-commit-gates](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md) (영어 원문):
  훅 래퍼, 내장 게이트, 게이트 인터페이스 규약, 배포 및 설정 계층.
- [Gate reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/gate.md): 명령어, 종료 코드 및
  오류 코드 레퍼런스.
- 커밋 게이트는 [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md) 여정의 일상적인 개발 루프에 포함되어 있습니다.
