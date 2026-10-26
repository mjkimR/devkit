---
sources:
  CAP-HOST-lifecycle-observation: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
title: 호스트
translated_from: en/areas/host.md@c39331657384ce21
---

# 호스트

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
- [커밋 게이트](gate.md)
- [생성 파일](generated.md)
- [거버넌스 규칙](governance.md)
- [하네스](harness.md)
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

호스트 영역은 devkit과 사용자가 작업 중인 에이전트 호스트(Codex CLI 등 코딩 에이전트 자체의 실행 환경)를 연결합니다.
다음 세 가지 핵심 기능을 제공합니다(`CAP-HOST-lifecycle-observation`).

- **네이티브 훅**: 번들은 호스트의 수명 주기 이벤트(세션 시작, 프롬프트 제출, 도구 사용, 세션 중지 등)를 가로채는
  핸들러를 등록할 수 있으며, devkit은 해당 이벤트를 설치된 Python 핸들러로 디스패치합니다.
- **프로젝트 MCP 등록**: 선택 사항인 MCP 런타임이 설치되어 있는 경우, `devkit sync`가 devkit 도구를 호출하기 위한 프로젝트
  로컬 MCP 설정을 항상 최신 상태로 유지합니다. 관련 세부 규칙은 [MCP](mcp.md) 영역(`CAP-MCP-runtime-registration`)에서
  다룹니다.
- **읽기 전용 상태 진단**: `devkit host status` 명령을 통해 현재 설치된 훅 목록과 최근 관찰된 이벤트 내역을 확인할 수 있습니다.

훅과 MCP 등록 설정은 다른 번들 에셋과 마찬가지로 `devkit sync`를 통해 배포됩니다. 번들 구조, 동기화 메커니즘, 설치 기록에
관한 내용은 [개념](../concepts.md)을 참고하십시오. 호스트 모듈은 `devkit-dist`에 포함되어 배포되므로 `devkit-agt`가 설치되어
있지 않아도 훅 기능이 정상 동작합니다.

## 훅의 역할과 한계

호스트 훅(host hook)은 정보 제공 목적(advisory)으로만 동작합니다. 핸들러는 에이전트의 대화 턴에 추가 컨텍스트를 주입할 수는
있지만, 특정 동작을 승인하거나 권한을 부여하거나 보안 경계를 강제할 수는 없습니다. 이벤트 입력, 설정 또는 핸들러 실행이
실패하더라도 훅은 stderr에 경고만 출력하고 빈 네이티브 응답을 반환한 뒤 종료 코드 `0`으로 정상 종료하므로, 훅에 문제가 생겨도
사용자의 에이전트 세션이 중단되지 않습니다. 실제 데이터나 상태를 변경할 때는 도메인 서비스가 준비 상태와 실행 권한을 자체적으로
엄격히 검증합니다.

이번 릴리스에서는 POSIX 환경의 Codex CLI 명령 훅만 지원합니다. 또한 훅이 설정되어 있다고 해서 호스트가 해당 훅을 신뢰하고
실제로 실행한다는 보장은 아니므로, 실제 Codex 세션에서 정상 동작 여부를 확인하십시오.

## 번들에 훅 추가하기

번들은 핸들러 등록마다 소형 TOML 파일을 가리키는 `hook` 에셋을 하나씩 선언합니다.

```toml
[[assets]]
id = "trace-tools"
kind = "hook"
source = "hooks/trace-tools.toml"
```

```toml
host = "codex"
event = "PreToolUse"
handler = "observe"
matcher = "^Bash$"
timeout = 10
```

`host`, `event`, `handler`는 필수 속성입니다. 지원되는 이벤트는 `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse`, `Stop`, `SessionEnd`입니다. `SessionEnd` 이벤트에는 최대 3초 이하의 명시적인 타임아웃을 지정해야 하며,
`UserPromptSubmit`과 `Stop`은 matcher를 지원하지 않습니다. matcher는 호스트가 표기된 그대로 해석하는 정규표현식입니다.
알 수 없는 필드가 선언되면 오류로 처리됩니다.

훅은 해당 번들과 Codex 에이전트가 둘 다 활성화되었을 때만 등록됩니다. 다른 에셋과 마찬가지로 오버라이드할 수 있으며,
sync 실행 시 호스트 설정을 수정하기 전에 실효 정의의 유효성을 먼저 검증합니다.

## sync를 통한 호스트 설정 자동 관리

`devkit bundle plan`은 생성 예정인 등록 항목을 `host_hooks` 아래에 표시하며, `devkit sync --dry-run`이나 `--check`를
실행해도 동일하게 포함됩니다. 이후 sync는 `.codex/hooks.json` 파일을 필요한 최소 범위 내에서만 정밀하게 수정합니다.

- 설치 기록(receipt)에 devkit 소유로 명시된 matcher 그룹만 변경하며, 그 외의 항목(외부 이벤트, 외부 그룹, 정의 순서,
  최상위 메타데이터 등)은 모두 안전하게 보존합니다.
- 훅을 제거하거나, 해당 번들 선택을 해제하거나, Codex 에이전트를 제외하면 devkit이 소유했던 해당 그룹만 정확히 제거됩니다.
- devkit이 소유한 그룹이 누락되었거나, 수동으로 수정되었거나, 중복 정의된 경우 `HOST_HOOK_CONFLICT` 오류가 발생하며 어떤 파일도
  변경하지 않고 즉시 중단됩니다.

충돌이 발생하면 로컬 수정 사항을 검토한 뒤, `.devkit/installation.json`에 기록된 원래 그룹 내용을 복원하고 sync를 다시
실행하십시오. 안전을 위해 강제 덮어쓰기(force)나 임의 흡수(adopt) 모드는 의도적으로 제공하지 않습니다. `sync --locked` 모드는
기존 호스트 설정 파일을 절대 수정하지 않으므로, 이 상태에서 선택 항목이나 정의가 변경되었다면 `RECEIPT_STALE` 오류가
발생합니다. sync가 실행 중일 때는 호스트 설정 파일을 수동으로 편집하지 마십시오.

인증 정보, 프로젝트 및 훅에 대한 신뢰 여부, 사용자 환경 설정, 권한 정책은 언제나 호스트 측에서 독립적으로 관리됩니다.

## 훅 실행 환경 보장

자동 생성되는 실행 명령어는 `devkit host hook --host codex --asset <bundle:id>` 형식입니다. 따라서 Codex 프로세스의 `PATH`
환경 변수에 설치된 `devkit` 바이너리가 포함되어 있어야 합니다. 프로젝트 로컬 환경에 설치된 경우라면 프로젝트의 `.venv/bin`
디렉터리를 `PATH`의 맨 앞에 두고 Codex를 실행하십시오. 훅 자체는 아무것도 추가 설치하지 않으며 외부 네트워크 호출도 수행하지
않습니다. 이벤트 발생 시 작업 디렉터리를 기반으로 devkit 프로젝트를 식별하고, 설치 기록과 이벤트를 대조 검증한 후 정확히 하나의
핸들러만을 호출합니다. 동기화(sync)가 비정상 중단된 상태에서는 핸들러 호출이 차단됩니다.

## 핸들러 작성하기

서비스 패키지는 `devkit.host.handlers` 진입점(entry-point) 그룹에 호출 가능한 함수(callable)를 등록합니다.

```toml
[project.entry-points."devkit.host.handlers"]
my-context = "my_package.host:context"
```

```python
from devkit_dist.features.host import HookEvent, HookResponse

def context(event: HookEvent) -> HookResponse:
    return HookResponse(additional_context="Read the repository's delivery contract.")
```

핸들러는 호스트 식별자, 네이티브 이벤트 이름, 프로젝트 루트 경로, 네임스페이스가 포함된 정규 에셋 이름(qualified asset name),
네이티브 페이로드를 인자로 받습니다. 빈 응답을 반환하거나, `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`
이벤트에 대해서는 최대 4,096자까지 추가 컨텍스트를 반환할 수 있습니다. 핸들러는 간결하고 조용하게 작성해야 합니다. 표준
출력으로 출력된 내용은 무시되며, 민감한 이벤트 내용을 로깅하거나 백그라운드 작업을 실행하거나 이벤트 입력을 사용자 승인으로
간주해서는 안 됩니다. 핸들러가 누락되었거나 중복되거나 실행 중 실패하면 `HOST_HOOK_DISPATCH_FAILED`로 보고됩니다.
오버라이드를 통해 핸들러를 변경한 경우 sync를 다시 실행해야 새 핸들러로 디스패치됩니다.

## 설치 상태 및 관찰 이력 확인

내장 `observe` 핸들러는 가장 최근에 발생한 이벤트의 호스트, 에셋, 이벤트 종류, UTC 시각만을 `.devkit/transient/host/`
디렉터리에 기록합니다. 프롬프트 내용, 실행 명령, 대화 세션 등은 일절 저장하지 않으므로 감사 로그로 사용되지 않습니다.

```sh
devkit host status --format json
```

이 명령은 등록된 각 훅의 목록, 소스 및 핸들러의 유효성 여부, 가장 최근의 관찰 기록을 보고합니다. 신뢰 상태와 실행 권한은
항상 `unknown`으로 표시되며, `runtime_on_path` 항목은 현재 상태를 검사 중인 프로세스의 환경만을 나타냅니다. `devkit status`
명령 역시 훅 설치와 관련된 문제점을 함께 표시합니다. 단, 두 명령 모두 호스트가 해당 훅을 실제로 활성화했는지까지 보장하지는
않습니다.

다른 devkit 명령과 달리 `devkit host hook`은 결과 센티널 없이 호스트 고유의 네이티브 응답 포맷을 stdout으로 직접 출력합니다.
반면 `devkit host status`는 표준 에이전트 출력 규약을 준수합니다.

## 비즈니스 승인과의 분리

작업 통합과 같은 비즈니스 승인은 호스트 훅의 대상이 아니며 호스트 프롬프트로 처리되지도 않습니다. `ask` 정책 환경에서 Host는
사용자가 대화창에서 내린 명시적인 결정을 전달받아 통합 CLI로 넘깁니다(`CAP-INT-mcp-services`, [통합](integration.md) 참고).
호스트에 대한 신뢰, 도구 실행 승인, 샌드박스 보안 프롬프트는 이러한 비즈니스 결정과 완전히 독립적으로 작동하며, 훅이 이를
대신할 수 없습니다.

## 관련 자료

- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/host/CAP-HOST-lifecycle-observation.md) (영어 원문):
  훅 에셋 규약, 공유 설정 소유권, 디스패치 메커니즘, 관찰자 및 상태 진단.
- [Host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/host.md): MCP 서비스를 포함한
  명령어 및 오류 코드 레퍼런스.
- 관련 문서: [MCP](mcp.md)(`CAP-MCP-runtime-registration`), [통합](integration.md).
