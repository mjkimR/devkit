---
sources:
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
title: 어드바이저리
translated_from: en/areas/advisory.md@bf6f81319d7030ba
---

# 어드바이저리

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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
- [MCP](mcp.md)
- [검색](search.md)
- [추적성](traceability.md)
- [뷰어](viewer.md)
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

`devkit` 명령이 보고하는 모든 오류, 경고, 알림은 어드바이저리(advisory)입니다. 어드바이저리는 stderr에 출력되는 짧은
블록(또는 JSON 안의 같은 엔벨로프)으로, 무슨 일이 일어났는지와 에이전트가 다음에 할 일을 `[ACTION]` 줄에 담아
알려 줍니다. 목적은 에이전트의 전형적인 두 가지 실패, 즉 같은 명령을 반복해서 재시도하는 것과 `--force`를 지어내거나
규칙이 통과할 때까지 규칙을 고치는 식의 파괴적인 우회책을 즉흥적으로 만드는 것을 막는 데 있습니다. 이 프로토콜은
여러분의 도구에서 쓸 수 있도록 `devkit.advisory` 라이브러리로도 제공됩니다. devkit의 전체 출력 모델에서 어드바이저리가
차지하는 위치는 [개념](../concepts.md)과 `ARCH-08-1-agent-output`을 참고하세요.

## 어드바이저리 읽기

```text
[ERROR]  (RULES_CONFIG_INVALID) .devkit/config.toml: [rules] phase override for RULE-x must be a string
[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
         fail identically. Correct the flag, argument, or input file before rerunning.
[TARGET] .devkit/config.toml
[FIX]    Set [rules.phases] RULE-x = "linter"
```

- 헤드라인에는 레벨과 안정적인 `UPPER_SNAKE` 코드가 담깁니다. 메시지가 아니라 코드로 분기하세요.
- `[ACTION]`은 모드와 그 모드의 고정된 지시문을 나타냅니다.
- `[TARGET]`은 열어 볼 대상, `[FIX]`는 정확한 명령이나 편집, `[REPORT]`는 사용자에게 전할 내용, `[DETAIL]`은 진단
  정보입니다. 빈 줄은 생략되며, 블록에는 빈 줄이 들어가지 않고 색상도 쓰지 않습니다.

## 명령이 실패했나요?

모드와 별개로 레벨이 이 질문에 답합니다.

| 레벨 | 헤드라인 | 의미 | 종료 코드 |
| --- | --- | --- | --- |
| `ERROR` | `[ERROR]` | 명령이 할 일을 하지 못했거나, 검사가 부정적인 결과를 찾았습니다 | `1` 또는 `2` |
| `WARNING` | `[WARN]` | 성공했지만 사용자가 알아야 하거나 결정해야 할 것이 있습니다 | 변경 없음(`--strict`에서는 `0`이 `1`이 됨) |
| `NOTICE` | `[NOTICE]` | 성공했으며 알아 둘 만한 것이 있습니다 | 변경 없음 |

종료 코드 `1`은 부정적인 결과(위반, 거부된 커밋), `2`는 명령을 실행할 수 없었다는 뜻입니다. 거부는 항상 오류이며 결코
경고가 아닙니다. 일반 진단 정보는 어드바이저리가 아니라 `-v`에서 보이는 `[INFO]` 로그 줄입니다. `-q`는 알림을
숨기지만 경고나 오류는 결코 숨기지 않습니다.

## 어떻게 대응할까

오류의 경우 모드가 에이전트의 다음 단계를 알려 줍니다.

| 모드 | 상황 | 에이전트가 하는 일 |
| --- | --- | --- |
| `INPUT_ERROR` | 플래그, 인자 또는 입력 파일이 잘못되었습니다 | `[TARGET]`을 고치고 다시 실행합니다 |
| `AUTO` | 안전하고 결정적인 수정이 있습니다 | `[FIX]`를 한 번 실행하고 한 번 재시도한 뒤, 결과와 관계없이 멈춥니다 |
| `BLOCKED` | 의도된 가드레일(커밋 게이트, 워크플로 규칙)이 거부했습니다 | 보고하고 멈춥니다. 규칙을 바꾸는 것은 사용자의 결정입니다 |
| `INTERACTION` | 사람의 결정이나 권한이 필요합니다 | 사용자에게 묻습니다. `[FIX]`는 동의를 받은 뒤에 씁니다 |
| `MAINTENANCE` | 코드나 도구의 결함입니다 | 보고하고 멈춥니다. 수리는 별도의 작업입니다 |
| `HALT` | 계속하면 상태가 손상될 수 있습니다 | 반쯤 끝난 채로 남은 것을 보고합니다. 재시도하거나 손으로 마무리하지 않습니다 |
| `DEFER` | 망가진 것은 없으며 나중에 시도하면 됩니다 | 원인과 재시도 시점을 보고합니다 |

경고는 항상 `CONTINUE`, 알림은 `NOTE`를 담습니다. 작업은 이미 성공했으므로 에이전트는 사용자에게 알리고, 요청받았을
때만 `[FIX]`를 실행합니다. 재시도를 허용하는 모드는 `AUTO`뿐입니다.

사람인 여러분이 어드바이저리에 직접 대응하는 일은 드물며, 대개 에이전트가 전달하는 형태로 보게 됩니다. 에이전트가
무언가를 묻는다면 보통 `INTERACTION` 오류의 `[REPORT]` 질문이거나, 사용자가 알아야 하는 `CONTINUE` 경고입니다.

## 기계용 채널

- `--format json`은 stdout에 객체 하나를 출력합니다. 실패는 `{"error": {...}}`이며 `code`, `level`, `message`,
  `exit_code`와, 모드·지시문 텍스트·비어 있지 않은 모든 필드를 담은 `advisory` 객체를 포함합니다. 성공한 결과의
  경고와 알림은 `notices` 아래에 들어갑니다. stderr에는 아무것도 출력되지 않으므로, 두 채널을 합치는 에이전트
  호스트도 어드바이저리를 두 번 읽지 않습니다.
- MCP 도구는 렌더링된 블록을 오류 텍스트로 반환하거나, 결과 뒤에 경고와 알림 블록을 덧붙입니다.
- HTTP 서비스는 RFC 7807 problem 문서 안에서 같은 엔벨로프를 쓸 수 있습니다.

어떤 전송 계층이나 소비자도 에이전트를 대신해 `[FIX]`를 실행하지 않습니다.

## 직접 만든 도구에서 어드바이저리 작성하기

`devkit.advisory`(`devkit-advisory` 패키지로, 다른 저장소가 이미 의존하는 semver 계약입니다)를 사용합니다.

1. 먼저 레벨을 고릅니다. 실패하거나 거부했다면 `ERROR`, 성공했지만 알아야 할 것이 있으면 `WARNING`, 성공했고 알아
   둘 만한 것이 있으면 `NOTICE`, 대응할 것이 없으면 로그 줄입니다.
2. 오류라면 필드(`actor`, `retry`, `guardrail`, `input_error`)를 설정하고, 도출된 모드가 원하는 지시문인지
   확인합니다. 모드는 직접 설정하지 않습니다. `AUTO`에는 `fix`가 필요합니다.
3. `[TARGET]`은 파일, 플래그 또는 `path:line:col`로, `[FIX]`는 자리 표시자 없이 바로 실행할 수 있는 정확한 명령으로
   만들고, 모든 문구를 결정적으로 씁니다. "likely"나 "might" 같은 표현은 쓰지 않습니다.
4. 경고와 알림은 발생시키지 말고 결과와 함께 반환하며, 조건 하나당 어드바이저리 하나를 보고합니다.

`advisory` 번들은 이 계약의 소비자용 미러인 `agent-advisory`와 `agent-advisory-python` 지침, 그리고 서로 관계없는 두
Python 클래스가 같은 코드를 선언하면 거부하는 `RULE-advisory-unique-code`를 제공합니다. click 도구에 이 출력 계약을
그대로 적용하려면 [에이전트 우선 CLI 도구 키트](cli.md)를 참고하세요.

## 출처

- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md) (영어 원문):
  레벨, 블록 형식, 필드, 모드 도출, 표준 지시문 텍스트와 작성 점검표.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md):
  명령의 stdout, stderr, 종료 코드 사이에서 어드바이저리가 차지하는 위치.
- [Advisory reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/advisory.md):
  `devkit.advisory` Python API.
