---
sources:
  ARCH-05-3-command-plugins: null
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
  CAP-CLI-agent-cli-toolkit: null
title: 에이전트 우선 CLI 도구 키트
translated_from: en/areas/cli.md@486c0e54011f4135
---

# 에이전트 우선 CLI 도구 키트

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

저장소의 명령줄 도구는 점점 더 AI 에이전트가 여러분을 대신해 실행하게 됩니다. `devkit-cli`(`devkit_cli`)는 어떤 click
도구에든 `devkit` 자신이 따르는 것과 같은 출력 계약을 제공하며, `devkit-catalog`의 선택형 `cli-tool` 번들은 그런
도구를 어떻게 구성할지 에이전트에게 알려 주고 다섯 개의 규칙으로 그 구조를 검사합니다. 계약은
`ARCH-08-1-agent-output`의 것이며, 오류와 경고는 어드바이저리입니다([어드바이저리](advisory.md)). 에이전트 우선 출력이라는
개념의 맥락은 [개념](../concepts.md)을 참고하세요.

## 도구가 얻는 계약

| 채널 | 담는 내용 |
| --- | --- |
| stdout | 결과: 한 줄짜리 `[KIND: ...]` 센티널, 또는 `--format json`에서 정확히 하나의 JSON 객체 |
| stderr | 어드바이저리 블록과, `-v`에서의 `[INFO]` 로그 줄 |
| 종료 코드 | `0` 성공, `1` 부정적인 결과(또는 `--strict`에서의 경고), `2` 실행할 수 없음 |

색상, 표, 진행 막대, 프롬프트는 없으며 어떤 것도 터미널에 의존하지 않습니다. stdout과 stderr는 로캘과 관계없이
UTF-8이며, 읽는 쪽이 stdout을 일찍 닫으면 명령은 아무 잡음 없이 종료 코드 `2`로 끝납니다.

## click 명령 감싸기

```python
import click
from devkit_cli import FORMAT_OPTION, Boundary, echo_json, echo_notices, is_json

boundary = Boundary("mytool")          # reads MYTOOL_QUIET, MYTOOL_VERBOSE, MYTOOL_STRICT

@click.command()
@FORMAT_OPTION
@boundary                              # below the click decorators; adds -q, -v and --strict
def scan(output_format: str) -> None:
    result, notices = run_scan()
    if is_json(output_format):
        echo_json({"result": result, "notices": [n.to_dict() for n in notices]})
    else:
        click.echo(f"[SCAN: files={result.count}]")
        echo_notices(notices)
```

나머지는 경계(boundary)가 처리합니다.

- 명령이 발생시킨 `ERROR` 어드바이저리는 한 번 렌더링되고 종료 코드를 정합니다. JSON 모드에서는 stdout의
  `{"error": {...}}`가 되고 stderr에는 아무것도 출력되지 않습니다.
- 그 밖에 빠져나온 것(버그, `SystemExit`)은 종료 코드 `2`의 `UNEXPECTED_ERROR`가 되며, 트레이스백은 `-v`용으로
  로그에 남습니다.
- 플래그가 환경 변수보다 우선합니다. 변수는 정확히 `1`일 때만 켜진 것으로 보며, `-q`와 `-v`를 함께 쓰면
  `ARGUMENT_INVALID`입니다.
- 인자의 의미 검사에는 `devkit.advisory.ArgumentError`를 발생시킵니다.

그 밖의 보조 도구로는 `exit_on_warnings`(`--strict`에서 경고 뒤 종료 코드 `1`로 종료), 수집한 문제를 보고하는 명령을
위한 `exit_on_problems`와 `report_exit_code`, 하위 명령 모듈을 실행할 때만 임포트하는 `LazyGroup`, 그리고 테스트용
`devkit_cli.testing.invoke`와 `Outcome.json()`, `Outcome.codes()`가 있습니다.

`devkit` 자체도 이렇게 만들어졌습니다. `devkit_dist.adapters.cli`가 `Boundary("devkit")`(`DEVKIT_QUIET`,
`DEVKIT_VERBOSE`, `DEVKIT_STRICT`)를 연결하고, 루트 그룹은 `devkit.commands` 플러그인으로 확장된 `LazyGroup`입니다
(`ARCH-05-3-command-plugins`). `devkit spec`과 `devkit run`도 이 방식으로 붙습니다([하네스](harness.md)).

## 도구 구조를 건강하게 유지하기

`devkit add cli-tool`로 `cli-tool` 번들을 선택합니다. 기본 프리셋(preset)은 `cli-tool-structure` 지침과 다섯 개의
규칙을 배포하고, `guide` 프리셋은 지침만 배포합니다. 규칙이 검사하는 내용은 다음과 같습니다.

| 규칙 | 지키는 것 |
| --- | --- |
| `RULE-cli-tool-layout` | 모듈이 평평한 패키지가 아니라 기능 레이아웃(`features/<feature>/cli`, `usecases`, `services`, `repositories`, `models`, ...)에 놓입니다 |
| `RULE-cli-tool-layers` | CLI 모듈만 `click`이나 `devkit_cli`를 임포트하고, 기능 계층은 자기 순위 이하만 임포트하며, 루트 `cli`는 지연 로딩을 유지합니다 |
| `RULE-cli-tool-command-boundary` | 모든 click 명령에 경계 데코레이터가 붙습니다 |
| `RULE-cli-tool-library-output` | `print`가 없고, CLI 모듈 밖에는 `click.echo`나 `sys.stdout.write`가 없습니다 |
| `RULE-cli-tool-heavy-imports` | CLI 모듈이 임포트 시점에 무거운 모듈을 임포트하지 않습니다 |

각 규칙은 `include`와 `exclude` 패턴을 받으며, 다른 설정은 규칙 가이드에 문서화되어 있습니다
(`devkit rules explain RULE-cli-tool-layers`). 다른 규칙과 마찬가지로 `[rules]`에서 조정합니다
([거버넌스 규칙](governance.md)).

## 버전 관리

`devkit-cli`는 `click`과 `devkit-advisory`에만 의존하며, 임포트해도 다른 것을 로드하지 않습니다. 다른 저장소가 이미
사용하고 있으므로 이 패키지는 `devkit-dist`, `devkit-agt`, `devkit-advisory`와 함께 릴리스되는 semver 계약입니다.
`0.x` 안에서 공개 이름을 제거하거나 바꾸면 마이너 버전을 올립니다.

## 출처

- [CAP-CLI-agent-cli-toolkit](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md) (영어 원문):
  경계, 보조 도구, 테스트 보조 도구와 `cli-tool` 규칙.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md):
  도구 키트가 구현하는 출력 계약.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  도구 키트가 렌더링하는 어드바이저리.
- [ARCH-05-3-command-plugins](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-05-3-command-plugins.md):
  `devkit`이 명령 플러그인을 붙이는 방식.
