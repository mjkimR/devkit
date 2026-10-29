---
sources:
  ARCH-05-3-command-plugins: null
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
  CAP-CLI-agent-cli-toolkit: null
title: 에이전트 우선 CLI 도구 키트
translated_from: en/areas/cli.md@769efa12f3b66406
---

# 에이전트 우선 CLI 도구 키트

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

저장소 내의 명령줄 도구는 사람이 직접 실행하기보다 AI 에이전트가 개발자를 대신해 실행하는 경우가 점점 늘고 있습니다.
`devkit-cli`(`devkit_cli`)는 일반 click 도구에도 `devkit` 자체와 동일한 에이전트 친화적 출력 계약을 손쉽게 적용해 주며,
`devkit-catalog`의 선택형 `cli-tool` 번들은 에이전트에게 이러한 도구의 아키텍처를 안내하고 5가지 거버넌스 규칙으로 그 구조적 정합성을
검증합니다. 이 출력 계약은 `ARCH-08-1-agent-output` 규격을 따르며, 모든 오류와 경고는 어드바이저리로 전달됩니다([어드바이저리](advisory.md)).
에이전트 우선 출력의 배경과 설계 철학은 [개념](../concepts.md)을 참고하십시오.

## 도구에 적용되는 계약

| 채널 | 전달 내용 |
| --- | --- |
| stdout | 결과: 한 줄짜리 `[KIND: ...]` 센티널, 또는 `--format json` 지정 시 정확히 하나의 JSON 객체 |
| stderr | 어드바이저리 블록과, `-v` 옵션 활성화 시의 `[INFO]` 로그 라인 |
| 종료 코드 | `0` 성공, `1` 부정적인 결과(또는 `--strict` 환경에서의 경고), `2` 실행 불가 오류 |

색상 강조, 서식 표, 진행 표시 막대, 사용자 입력 프롬프트는 배제되며, 터미널 환경에 의존하는 요소가 전혀 없습니다.
stdout과 stderr는 운영체제 로캘 설정과 관계없이 항상 UTF-8 인코딩을 사용하며, 출력 파이프를 읽는 프로세스가 stdout을 조기에 닫더라도
명령어는 불필요한 오류 메시지 없이 종료 코드 `2`로 안전하게 종료됩니다.

## click 명령 감싸기

```python
import click
from devkit_cli import FORMAT_OPTION, Boundary, echo_json, echo_notices, is_json

boundary = Boundary("mytool")          # MYTOOL_QUIET, MYTOOL_VERBOSE, MYTOOL_STRICT 환경 변수를 읽음

@click.command()
@FORMAT_OPTION
@boundary                              # click 데코레이터 아래에 적용하며, -q, -v, --strict 플래그를 추가함
def scan(output_format: str) -> None:
    result, notices = run_scan()
    if is_json(output_format):
        echo_json({"result": result, "notices": [n.to_dict() for n in notices]})
    else:
        click.echo(f"[SCAN: files={result.count}]")
        echo_notices(notices)
```

나머지 입출력 제어는 경계(boundary)가 자동으로 처리합니다.

- 명령어가 발생시킨(raise) `ERROR` 어드바이저리는 1회 서식화되어 출력되며 적절한 종료 코드를 설정합니다. JSON 모드에서는
  stdout에 `{"error": {...}}` 형태로 출력되고 stderr에는 아무것도 출력되지 않습니다.
- 그 외에 처리되지 않고 발생한 예외(버그, `SystemExit` 등)는 종료 코드 `2`의 `UNEXPECTED_ERROR`로 전환되며, 트레이스백은
  `-v` 옵션 확인용 로그로 기록됩니다.
- CLI 플래그가 환경 변수 설정보다 항상 우선합니다. 환경 변수 값은 정확히 `1`일 때만 활성화된 것으로 간주하며, `-q`와 `-v`를
  동시에 지정하면 `ARGUMENT_INVALID` 오류가 발생합니다.
- 인자의 의미론적 유효성 검사(semantic check) 실패 시에는 `devkit.advisory.ArgumentError`를 발생시킵니다.
- 항상 JSON만 출력하는 명령어는 `FORMAT_OPTION` 대신 `@boundary(json_only=True)`를 사용합니다. 이때 바운더리는 `--format json`을
  아무 동작도 하지 않는 옵션으로 받아 주므로, 에이전트는 모든 명령어에 이 옵션을 붙일 수 있습니다.

`echo_json`은 압축된 JSON(들여쓰기 없음, 구분자 뒤 공백 없음)을 출력합니다. 모든 바이트가 에이전트의 컨텍스트로 들어가기
때문입니다. 출력 크기를 예산 안에서 관리해야 하는 호출자는 `render_json`으로 같은 텍스트를 받을 수 있습니다.

그 밖의 지원 유틸리티로는 `exit_on_warnings`(`--strict` 모드에서 경고 발생 시 종료 코드 `1`로 종료), 수집한 문제를 보고하는 명령어를
위한 `exit_on_problems`와 `report_exit_code`, 하위 명령 모듈을 실제로 실행할 때만 지연 로딩하는 `LazyGroup`, 그리고 테스트 검증용
`devkit_cli.testing.invoke`와 `Outcome.json()`, `Outcome.codes()`가 제공됩니다.

`devkit` 자체도 이 구조로 구현되었습니다. `devkit_dist.adapters.cli`가 `Boundary("devkit")`(`DEVKIT_QUIET`, `DEVKIT_VERBOSE`,
`DEVKIT_STRICT`)를 연결하고, 루트 그룹은 `devkit.commands` 플러그인으로 확장 가능한 `LazyGroup`으로 구성됩니다(`ARCH-05-3-command-plugins`).
`devkit docs`, `devkit spec`, `devkit run` 명령어도 이 방식으로 마운트됩니다([하네스](harness.md)).

## 도구 구조의 건전성 유지하기

`devkit add cli-tool` 명령어로 `cli-tool` 번들을 추가합니다. 기본 프리셋은 `cli-tool-structure` 지침 문서와 5개의 거버넌스 규칙을
배치하며, `guide` 프리셋은 지침 문서만 배치합니다. 각 규칙의 검증 내용은 다음과 같습니다.

| 규칙 | 검증 내용 |
| --- | --- |
| `RULE-cli-tool-layout` | 모듈을 평면적인 패키지 구조가 아니라 기능별 레이아웃(`features/<feature>/cli`, `usecases`, `services`, `repositories`, `models` 등)에 배치하도록 강제합니다 |
| `RULE-cli-tool-layers` | CLI 모듈만 `click`이나 `devkit_cli`를 임포트할 수 있고, 기능 계층은 동급 이하의 레이어만 임포트하며, 루트 `cli`는 지연 임포트(lazy)를 유지하도록 합니다 |
| `RULE-cli-tool-command-boundary` | 모든 click 명령어에 boundary 데코레이터를 적용하도록 합니다 |
| `RULE-cli-tool-library-output` | CLI 모듈 외에서는 `print`나 `click.echo`, `sys.stdout.write`를 통한 직접 출력을 금지합니다 |
| `RULE-cli-tool-heavy-imports` | CLI 모듈이 초기 임포트 시점에 무거운 모듈을 로드하지 않도록 제한합니다 |

각 규칙은 `include`와 `exclude` 경로 패턴을 인자로 받으며, 세부 설정 옵션은 규칙별 가이드에 문서화되어 있습니다
(`devkit rules explain RULE-cli-tool-layers`). 다른 거버넌스 규칙과 마찬가지로 `.devkit/config.toml`의 `[rules]` 테이블에서
설정값을 조정할 수 있습니다([거버넌스 규칙](governance.md)).

## 버전 관리

`devkit-cli`는 `click`과 `devkit-advisory`에만 의존하며, 임포트 시 다른 불필요한 의존성을 로드하지 않습니다. 이미 다른 저장소에서
런타임에 널리 활용하고 있으므로, 이 패키지는 `devkit-dist`, `devkit-agt`, `devkit-advisory`와 동일한 릴리스 주기를 갖는 semver 계약입니다.
`0.x` 버전 범위 내에서도 공개 API 이름을 삭제하거나 변경하면 마이너 버전이 증가합니다.

## 출처

- [CAP-CLI-agent-cli-toolkit](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md) (영어 원문):
  boundary 데코레이터, 헬퍼 유틸리티, 테스트 도구 및 `cli-tool` 거버넌스 규칙 규격.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md):
  툴킷이 구현하는 에이전트 우선 출력 계약.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  툴킷이 렌더링하는 어드바이저리 프로토콜 규격.
- [ARCH-05-3-command-plugins](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-05-3-command-plugins.md):
  `devkit`이 하위 명령 플러그인을 동적으로 마운트하는 방식.
