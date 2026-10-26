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
> 소스 커밋 `b44f759024a5` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

호스트 영역은 devkit을 여러분이 작업하는 에이전트 호스트(Codex CLI처럼 코딩 에이전트 자체의 런타임)와 연결합니다.
다음 세 가지를 다룹니다(`CAP-HOST-lifecycle-observation`).

- **네이티브 훅**: 번들은 호스트 수명 주기 이벤트(세션 시작, 프롬프트 제출, 도구 사용, 중지)에 대한 핸들러를 등록할
  수 있으며, devkit은 그 이벤트를 설치된 Python 핸들러로 전달합니다.
- **프로젝트 MCP 등록**: 선택형 MCP 런타임이 설치되어 있으면 `devkit sync`가 devkit을 위한 프로젝트의 로컬 MCP 항목을
  맞춰 둡니다. 그 규칙은 [MCP](mcp.md) 영역(`CAP-MCP-runtime-registration`)에 있습니다.
- **읽기 전용 진단**: `devkit host status`는 설치된 것과 관찰자가 마지막으로 본 것을 보여 줍니다.

훅과 등록은 다른 번들 에셋과 마찬가지로 `devkit sync`가 배포합니다. 번들, 동기화, 설치 기록은
[개념](../concepts.md)을 참고하세요. 호스트 모듈은 `devkit-dist`와 함께 배포되므로 훅은 `devkit-agt` 없이도 동작합니다.

## 훅인 것과 훅이 아닌 것

호스트 훅(host hook)은 권고일 뿐입니다. 핸들러는 에이전트의 턴에 컨텍스트를 더할 수 있지만, 무엇을 승인하거나 권한을
부여하거나 보안 경계를 강제할 수는 없습니다. 입력, 설정 또는 핸들러가 실패하면 훅은 stderr에 경고를 출력하고 빈
네이티브 응답을 반환한 뒤 `0`으로 종료하므로, 망가진 훅이 세션을 멈추는 일은 없습니다. 무언가를 바꿀 때는 도메인
서비스가 준비 상태와 권한을 여전히 직접 확인합니다.

이번 릴리스에서는 POSIX의 Codex CLI 명령 훅만 지원합니다. 훅이 설정되어 있다고 해서 호스트가 그 훅을 신뢰하거나
실행한다는 증거도 아닙니다. 실제 Codex 세션에서 확인하세요.

## 번들에 훅 추가하기

번들은 핸들러 등록마다 작은 TOML 파일을 가리키는 `hook` 에셋을 하나씩 선언합니다.

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

`host`, `event`, `handler`는 필수입니다. 지원하는 이벤트는 `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse`, `Stop`, `SessionEnd`입니다. `SessionEnd`에는 3초 이하의 명시적 타임아웃이 필요하며, `UserPromptSubmit`과
`Stop`은 matcher를 받지 않습니다. matcher는 호스트가 쓰인 그대로 해석하는 정규식입니다. 알 수 없는 필드는 오류입니다.

훅은 그 번들과 Codex 에이전트가 모두 선택되었을 때만 등록됩니다. 다른 에셋과 마찬가지로 오버라이드할 수 있으며,
sync는 호스트 설정을 건드리기 전에 실효 정의를 검증합니다.

## sync가 호스트 설정을 관리하게 하기

`devkit bundle plan`은 생성된 등록을 `host_hooks` 아래에 나열하고, `devkit sync --dry-run`이나 `--check`에도 이것이
포함됩니다. 그러면 sync는 `.codex/hooks.json`을 좁은 범위로만 편집합니다.

- 설치 기록(receipt)이 devkit의 것으로 기록한 matcher 그룹만 바꾸고, 나머지(외부 이벤트, 외부 그룹, 그 순서, 최상위
  메타데이터)는 모두 보존합니다.
- 훅을 제거하거나, 그 번들의 선택을 해제하거나, Codex를 빼면 해당 그룹만 정확히 제거됩니다.
- 소유한 그룹이 없거나, 편집되었거나, 중복되면 `HOST_HOOK_CONFLICT`이며, 아무것도 쓰기 전에 발생합니다.

충돌을 해결하려면 로컬 편집을 검토하고, `.devkit/installation.json`에서 기록된 그룹을 복원한 뒤 sync를 다시
실행하세요. force나 adopt 모드는 의도적으로 없습니다. `sync --locked`는 기존 호스트 파일을 결코 편집하지 않으며, 그
상태에서 선택이나 정의가 바뀌었다면 `RECEIPT_STALE`입니다. sync가 실행되는 동안에는 호스트 설정을 직접 편집하지 마세요.

자격 증명, 프로젝트와 훅의 신뢰, 사용자 설정, 권한 설정은 항상 호스트에 남습니다.

## 훅이 실행될 수 있게 하기

생성되는 명령은 `devkit host hook --host codex --asset <bundle:id>`입니다. Codex 프로세스의 PATH에 설치된 `devkit`이
있어야 합니다. 프로젝트 로컬 설치라면 프로젝트의 `.venv/bin`을 PATH 맨 앞에 두고 Codex를 실행하세요. 훅은 아무것도
설치하지 않으며 네트워크 호출도 하지 않습니다. 이벤트의 작업 디렉터리에서 devkit 프로젝트를 찾고, 설치 기록과 이벤트를
대조한 뒤, 정확히 하나의 핸들러를 호출합니다. 중단된 sync가 있으면 전달하지 않습니다.

## 핸들러 작성하기

서비스 패키지는 `devkit.host.handlers` 진입점 그룹에 호출 가능한 객체를 등록합니다.

```toml
[project.entry-points."devkit.host.handlers"]
my-context = "my_package.host:context"
```

```python
from devkit_dist.features.host import HookEvent, HookResponse

def context(event: HookEvent) -> HookResponse:
    return HookResponse(additional_context="Read the repository's delivery contract.")
```

핸들러는 호스트, 네이티브 이벤트 이름, 프로젝트 루트, 한정된 에셋 이름, 네이티브 페이로드를 받습니다. 빈 응답을
반환하거나, `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`에 대해서는 최대 4096자의 컨텍스트를
반환합니다. 핸들러는 조용하게 유지하세요. 출력한 내용은 버려지며, 민감한 이벤트 내용을 로그에 남기거나, 백그라운드
작업을 띄우거나, 이벤트 입력을 승인으로 취급해서는 안 됩니다. 없거나, 중복되거나, 실패한 핸들러는
`HOST_HOOK_DISPATCH_FAILED`로 보고됩니다. 오버라이드를 다른 핸들러로 바꾸면 전달되기 전에 sync가 필요합니다.

## 설치된 것 살펴보기

내장 `observe` 핸들러는 가장 최근 이벤트의 호스트, 에셋, 이벤트, UTC 시각만 `.devkit/transient/host/` 아래에
기록합니다. 프롬프트, 명령, 세션 내용은 저장하지 않으며 감사 로그도 아닙니다.

```sh
devkit host status --format json
```

이 명령은 각 등록과, 그 출처와 핸들러가 유효한지, 마지막 관찰을 보고합니다. 신뢰와 실행 권한은 항상 `unknown`이며,
`runtime_on_path`는 살펴보는 프로세스에 대해서만 설명합니다. `devkit status`도 훅 설치 문제를 나열합니다. 어느 명령도
호스트가 훅을 활성화했다는 것을 증명하지는 않습니다.

다른 명령과 달리 `devkit host hook`은 결과 센티널 없이 호스트의 네이티브 응답을 stdout에 씁니다.
`devkit host status`는 일반적인 에이전트 출력 계약을 따릅니다.

## 승인은 별개입니다

작업 통합 같은 업무 승인은 훅도 아니고 호스트 프롬프트도 아닙니다. `ask` 정책에서는 Host가 대화에서 내린 여러분의
결정을 통합 CLI로 전달합니다(`CAP-INT-mcp-services`, [통합](integration.md) 참고). 호스트 신뢰, 도구, 샌드박스
프롬프트는 그 결정과 독립적이며, 훅이 어느 쪽을 대신하는 일도 없습니다.

## 출처

- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/host/CAP-HOST-lifecycle-observation.md) (영어 원문):
  훅 에셋, 공유 설정의 소유권, 전달, 관찰자와 상태.
- [Host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/host.md): MCP
  서비스를 포함한 명령과 코드.
- 관련 문서: [MCP](mcp.md)(`CAP-MCP-runtime-registration`), [통합](integration.md).
