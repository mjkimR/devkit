---
sources:
  CAP-COLL-shared-artifacts: null
  CAP-HOST-lifecycle-observation: null
  CAP-INT-mcp-services: null
  CAP-MCP-runtime-registration: null
  UC-drive-development-to-integration: null
title: MCP
translated_from: en/areas/mcp.md@c8130ad29347978e
---

# MCP

<!-- handbook:provenance -->
> 소스 커밋 `18b834c35c0c` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](../journeys/adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](../journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](../journeys/handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](../journeys/incubate-an-idea.md)
- [제안 숙성 후 넘기기](../journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](../journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](../journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](../journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](../journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](../journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](../journeys/run-parallel-work-safely.md)
- [선택한 느린 작업 빠르게 하기](../journeys/speed-up-selected-slow-operations.md)
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
- [호스트](host.md)
- [통합](integration.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

`devkit-mcp`는 Model Context Protocol(stdio)을 통해 에이전트 호스트에 devkit의 도구를 제공하고, 프로젝트의 로컬 MCP 등록
상태를 자동으로 동기화하여 유지하는(`CAP-MCP-runtime-registration`) 선택형 패키지입니다. devkit을 사용하는 데 이 패키지가 필수적인
것은 아닙니다. 통합을 포함한 모든 수명 주기 작업은 CLI를 통해 직접 실행할 수 있습니다. 이번 릴리스에서 주된 용도는 공유 아티팩트(shared artifact)
도구 지원입니다([협업](collaboration.md) 참고).

워크플로에서 Host와 승인 절차가 맡는 역할은 [개념](../concepts.md)과
[개발부터 통합까지 진행하기](../journeys/drive-development-to-integration.md) 여정을 참고하세요.

## 설치와 등록

`devkit-mcp`는 유지되는 런타임(retained runtime), 즉 베이스 체크아웃 환경이나 별도의 도구 전용 환경에 설치해야 합니다. 작업 워크트리의
`.venv`나 편집 가능(editable) 링크로 연결된 워크트리 소스에는 절대 설치하지 마십시오. 설치 후에는 sync 명령으로 자동 등록하거나, 다음과 같이
직접 등록할 수 있습니다.

| 작업 목적 | 실행 명령 |
| --- | --- |
| 어떤 런타임이 사용되는지 확인 | `devkit mcp status --descriptor [--executable <python>] --format json` |
| 프로젝트 항목 등록 | `devkit mcp setup [--executable <python>] [--host codex\|claude\|antigravity ...]` |
| 목표 등록, 기록된 등록, 프로젝트 등록 상태 확인 | `devkit mcp status --format json` |
| devkit 자체 등록 항목 제거 | `devkit mcp remove` |

런타임이 설치되어 있으면 일반적인 `devkit sync` 명령이 선택된 각 에이전트의 프로젝트 파일에 있는 devkit 등록 항목을 자동으로 맞춥니다.
Codex는 `.codex/config.toml`, Claude Code는 `.mcp.json`, Antigravity는 `.agents/mcp_config.json`을 사용합니다. 자동 등록을
해제하려면 `[mcp] register = false`로 설정하세요. 새로 생성된 작업 워크트리는 잠긴 에셋 복원 직후 `devkit sync --registrations-only`를
통해 필요한 항목을 설정합니다([워크트리](worktree.md) 참고).

검증된 런타임이 없으면 `mcp setup`은 아무것도 쓰기 전에 `MCP_RUNTIME_UNAVAILABLE`로 거부합니다. 일반 sync 뒤에는 같은 코드가
경고로만 보고됩니다. `--host`(반복 가능)는 지정한 호스트로 등록을 제한하며, setup은 프로젝트 전체를 맞추므로 지정하지 않은
호스트의 소유 항목은 제거됩니다. 이후 `--host` 없이 실행하면 설정된 에이전트가 다시 등록됩니다.

`devkit status`는 MCP 등록을 전혀 검사하지 않습니다. locked sync가 원래 했을 등록 쓰기를 보류하면
`uv run devkit sync --registrations-only`를 해결 방법으로 하는 `MCP_REGISTRATION_PENDING`을 보고합니다. 실제 등록 계획은
`devkit mcp status`, `mcp setup`, 그리고 두 가지 sync 모드에서 진단합니다. 호스트별 상세 설정 절차는
[MCP setup](https://github.com/mjkimR/devkit/blob/v0.1.5/guides/install/mcp.md) (영어 원문) 가이드를 참고하세요.

## 등록 작업의 파일 변경 원칙

등록 작업은 자체 소유가 아닌 파일을 매우 신중하게 다룹니다.

- 추적되지 않는(untracked) 파일 중에서도 gitignore 대상 원장인 `.devkit/transient/mcp/registrations.json`에 devkit 소유로
  기록된 항목에만 씁니다. 추적 중인 파일이나 기존 외부 파일은 변경되지 않습니다.
- 대상 파일이 존재하지 않는 경우, 기존 ignore 규칙이 설정되어 있어야 합니다. 그렇지 않다면 devkit은 연결된 모든 워크트리를 검사하여
  의도치 않게 숨겨지는 파일이 없는지 확인한 후, 클론 로컬에 한정된 좁은 범위의 제외 규칙을 하나 추가합니다.
- devkit이 소유한 항목이 누락되었거나 수정 또는 중복된 경우 충돌(`MCP_REGISTRATION_CONFLICT`)로 처리됩니다. devkit이 소유하지 않은
  동일한 내용의 항목을 임의로 넘겨받지 않습니다.
- 호스트의 신뢰 설정, 권한, 전역 설정은 호스트 고유 영역으로 유지됩니다. 사용자 설정이나 관리 설정에 선언된 동일한 이름의 항목은
  충돌로만 보고되며 읽기 전용으로 취급됩니다.
- 변경 작업이 중간에 중단되면 다음 작업 전에 먼저 복구됩니다(`MCP_REGISTRATION_INTERRUPTED`, `uv run devkit sync`로 해결).
  `--dry-run` 및 `--check` 옵션은 실제 쓰기 없이 계획만 수립하며, locked sync는 호스트 파일을 변경하지 않고 유효성만 검증합니다.
- devkit이 마지막 소유 항목을 제거할 때, 유지되는 좁은 범위의 제외 규칙을 한 번 알려 줍니다(`MCP_EXCLUSIONS_RETAINED`). 더 이상
  필요 없다면 직접 제거하세요.

등록이 완료되었다고 해서 실제 연결까지 확인된 것은 아닙니다. `devkit mcp status`는 실제 연결 상태, 신뢰 및 권한 상태를 알 수
없음(unknown)으로 보고합니다(JSON). 텍스트 출력은 `[MCP: ...]` 한 줄과 호스트마다 `[MCP_HOST: ...]` 한 줄을 출력합니다.

## 서버 보호 메커니즘

`devkit mcp serve`는 모든 호출을 세 가지 위치에 바인딩합니다. 바로 유지되는 런타임, 실행자 체크아웃, 그리고 설정이 적용되는
소유 설정 작업 공간(owning configuration workspace)입니다. 도구 입력을 통해서는 작업 공간을 변경할 수 없습니다.

- **실행 클래스(Execution classes).** 각 도구는 `read_only`, `bounded_write`, `preflight`, `interactive`, `approved_resume`
  중 하나로 선언되며, 선언되지 않은 도구는 `interactive`로 취급됩니다. 전송 계층은 확인 폼을 요청하지 않으며 비즈니스 권한도
  부여하지 않습니다. 승인은 Host가 권한을 부여한 CLI의 몫입니다.
- **클라우드 환경**에서는 읽기 전용 도구만 노출되며, 쓰기 작업은 거부됩니다. 가드 검사는 잠금 대기 후 및 실제 영향이 발생하기
  직전에 반복 수행됩니다.
- **코드 변경 감지(Stale code).** 서버는 로드된 devkit 코드의 해시를 기록합니다. 디스크의 코드가 변경되면 읽기 전용이 아닌 모든 호출이
  `MCP_RUNTIME_STALE` 오류로 거부됩니다. 이 경우 서비스를 재시작하거나 다시 연결해야 합니다. 읽기 전용 도구는 정상 작동합니다.
- **작업 공간 유실.** 소유 작업 공간이 없거나 형식이 잘못된 경우 안전하게 실패(fail closed) 처리됩니다(`MCP_WORKSPACE_UNAVAILABLE`).

## 비즈니스 승인은 대화에서 결정됩니다

수명 주기 변경 작업(통합, 정리 등)은 MCP 도구로 제공되지 않습니다. Host가 작업 내용을 확인하고 정확한 보고서와 대상, 작업 영향을
제시한 뒤, `ask` 정책에 따라 사용자의 결정을 받아 CLI를 직접 호출합니다(`CAP-INT-mcp-services`, [통합](integration.md) 참고).
호스트의 도구 신뢰 프롬프트나 샌드박스 확인 등은 이 비즈니스 승인 결정과 별개의 문제입니다.

도구가 반환하는 도메인 텍스트의 언어는 소유 작업 공간의 설정을 따릅니다. 언어나 작업 공간을 고르는 도구 인자는 없으며, 이
설정이 가드 검사나 등록 자체를 변경하지는 않습니다.

## 공유 아티팩트 도구

공유 아티팩트 서비스는 `shared_put`(승인이 필요 없는 범위 한정 쓰기)과 읽기 전용 도구인 `shared_get`, `shared_list`를
제공합니다. 이 도구들은 `devkit shared` CLI와 동일한 식별자, 보존 주기, 어댑터 규칙을 따릅니다(`CAP-COLL-shared-artifacts`).
클라우드 환경에서는 쓰기 도구가 목록에 노출되지 않으며 호출도 거부됩니다.

## 주요 에러 코드

| 코드 | 조치 방법 |
| --- | --- |
| `MCP_RUNTIME_UNAVAILABLE` | 서비스 패키지와 일치하는 유지 런타임을 설치하거나 선택한 뒤 다시 동기화합니다. |
| `MCP_RUNTIME_STALE` | 서비스를 재시작하거나 다시 연결한 뒤 명령을 다시 호출합니다. |
| `MCP_REGISTRATION_CONFLICT` | 지목된 파일(수정되었거나 형식이 잘못되었거나 소유권이 없는 항목)을 어떻게 복원할지 사용자가 결정한 뒤 동기화합니다. |
| `MCP_REGISTRATION_UNAVAILABLE` | 대상이 추적 중이거나, 보이는 파일이거나, 외부 파일을 숨기게 됩니다. 그대로 두고 호스트 설정 절차를 사용합니다. |
| `MCP_REGISTRATION_INTERRUPTED`, `MCP_LEDGER_UNIGNORED` | `uv run devkit sync`를 실행합니다. |
| `MCP_REGISTRATION_PENDING` | locked sync가 쓰기를 보류했습니다. `uv run devkit sync --registrations-only`를 실행합니다. |
| `MCP_HOST_UNSUPPORTED`, `MCP_REGISTRATION_SHADOWED` | 선택된 호스트에 어댑터가 없거나, 같은 이름의 사용자·관리 항목이 프로젝트 항목을 가립니다. 호스트 고유 도구로 해결합니다. |
| `MCP_CHECKOUT_REQUIRED` | `--workspace-root`가 `.devkit/`을 가진 Git 체크아웃의 최상위를 가리키게 합니다. |
| `MCP_INTERACTIVE_UNAVAILABLE` | 로컬 대화형 Host나 CLI 경로를 사용합니다. |

## 출처

- [CAP-MCP-runtime-registration](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/mcp/CAP-MCP-runtime-registration.md) (영어 원문):
  런타임 계약, 등록, Host 워크플로와 공유 아티팩트 서비스.
- [CAP-HOST-lifecycle-observation](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/host/CAP-HOST-lifecycle-observation.md)
  (프로젝트 MCP 등록 경계)과
  [host quick reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/host.md#mcp-services).
- 관련 문서: [호스트](host.md), [협업](collaboration.md), [통합](integration.md).
