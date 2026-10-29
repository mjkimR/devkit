---
sources:
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
title: 어드바이저리
translated_from: en/areas/advisory.md@9d8ab7d2080bebb4
---

# 어드바이저리

<!-- handbook:provenance -->
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

`devkit` 명령어가 보고하는 모든 오류, 경고, 알림은 어드바이저리(advisory)입니다. 어드바이저리는 stderr에 출력되는 간결한
블록(또는 JSON 내의 동일한 엔벨로프)으로, 발생한 상황과 함께 에이전트가 다음에 수행해야 할 작업을 `[ACTION]` 줄로 명시합니다.
이는 에이전트에게 흔히 발생하는 두 가지 전형적인 실패 패턴, 즉 동일한 명령을 루프 돌며 재시도하는 문제와 임의로 `--force`를 꾸며내거나
검사를 통과하려고 규칙 자체를 수정해 버리는 파괴적인 임시방편을 방지하기 위함입니다. 이 프로토콜은 자체 개발 도구에서도 활용할 수 있도록
`devkit.advisory` 라이브러리로도 제공됩니다. devkit의 전체 출력 모델에서 어드바이저리의 역할과 위치는
[개념](../concepts.md) 및 `ARCH-08-1-agent-output`을 참고하십시오.

## 어드바이저리 읽기

```text
[ERROR]  (RULES_CONFIG_INVALID) config rules.phase_overrides.RULE-x: 'linter' is not 'hygiene'; set it to 'hygiene' or remove the entry to keep the rule's default phase
[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
         fail identically. Correct the flag, argument, or input file before rerunning.
[TARGET] .devkit/config.toml
[FIX]    Correct the [rules] table in .devkit/config.toml
```

- 헤드라인에는 심각도 레벨과 안정적인 `UPPER_SNAKE` 코드가 표시됩니다. 메시지 본문이 아니라 코드로 분기 처리를 수행하십시오.
- `[ACTION]`은 동작 모드와 해당 모드의 고정된 지시문을 나타냅니다.
- `[TARGET]`은 확인해야 할 대상 경로, `[FIX]`는 실행 가능한 정확한 명령어 또는 수정 조치, `[REPORT]`는 사용자에게 보고할 내용, `[DETAIL]`은
  진단 상세 정보입니다. 내용이 없는 필드 줄은 생략되며, 블록 내부에는 빈 줄이 포함되지 않고 색상 서식도 사용하지 않습니다.

## 명령이 실패했나요?

동작 모드와 관계없이 심각도 레벨이 이 질문에 답합니다.

| 레벨 | 헤드라인 | 의미 | 종료 코드 |
| --- | --- | --- | --- |
| `ERROR` | `[ERROR]` | 명령어가 목표 작업을 완수하지 못했거나, 검사에서 부정적인 결과를 발견했습니다 | `1` 또는 `2` |
| `WARNING` | `[WARN]` | 작업은 성공했으나, 사용자가 인지하거나 결정해야 할 사항이 있습니다 | 변경 없음(`--strict` 환경에서는 `0`이 `1`로 변경) |
| `NOTICE` | `[NOTICE]` | 작업은 성공했으며, 참고할 만한 유용한 정보가 있습니다 | 변경 없음 |

종료 코드 `1`은 부정적인 검사 결과(규칙 위반, 커밋 거부 등)를 의미하며, `2`는 명령어 자체를 실행할 수 없었음을 의미합니다. 거부 처리는
항상 오류(ERROR)이며 단순 경고로 낮추지 않습니다. 일반적인 진단 정보는 어드바이저리가 아니며, `-v` 옵션 지정 시에만 보이는
`[INFO]` 로그 라인으로 출력됩니다. `-q` 플래그는 알림(NOTICE)을 숨기지만 경고나 오류는 숨기지 않습니다.

## 상황별 대응 방식

오류가 발생했을 때 동작 모드는 에이전트가 취해야 할 다음 단계를 안내합니다.

| 모드 | 상황 | 에이전트의 동작 |
| --- | --- | --- |
| `INPUT_ERROR` | 플래그, 인자 또는 입력 파일이 잘못되었거나, 에이전트가 만든 내용에 대한 검사가 실패했습니다(커밋의 테스트 실패나 규칙 위반, 빈 커밋 메시지) | `[TARGET]`을 수정한 후 다시 실행합니다 |
| `AUTO` | 안전하고 결정적인 자동 해결책이 있습니다 | `[FIX]`를 1회 실행하고 1회 재시도한 뒤, 결과와 관계없이 멈춥니다 |
| `BLOCKED` | 명시적인 가드레일(보호 브랜치, 정책 게이트, 워크플로 규칙 등)이 정책에 따라 작업을 거부했습니다 | 상황을 보고하고 중단합니다. 규칙 변경 여부는 사용자의 판단에 맡깁니다 |
| `INTERACTION` | 사람의 의사결정이나 명시적 권한 승인이 필요합니다 | 사용자에게 확인을 요청합니다. `[FIX]`는 동의를 얻은 후에만 실행합니다 |
| `MAINTENANCE` | 코드베이스나 실행 도구 자체의 결함입니다 | 상황을 보고하고 중단합니다. 결함 수리는 별도의 작업 단위로 처리합니다 |
| `HALT` | 계속 진행할 경우 시스템 상태가 손상될 위험이 있습니다 | 미완료 상태로 남은 내역을 보고합니다. 임의로 재시도하거나 수동으로 마무리를 시도하지 않습니다 |
| `DEFER` | 결함이 아니며 일시적인 지연 상태입니다 | 지연 원인과 권장 재시도 시점을 보고합니다 |

경고는 항상 `CONTINUE`, 알림은 항상 `NOTE` 모드를 갖습니다. 기본 작업 자체는 이미 성공한 상태이므로, 에이전트는 해당 내용을 사용자에게
안내하고 사용자의 명시적 요청이 있을 때만 `[FIX]`를 실행합니다. 재시도를 자동으로 수행할 수 있는 권한을 부여하는 모드는 `AUTO`뿐입니다.

`INPUT_ERROR`와 `BLOCKED`를 가르는 기준은 누가 조치해야 하느냐입니다. 테스트가 실패하거나 문서가 규칙을 위반해 거부된 커밋은
`INPUT_ERROR`입니다. 에이전트가 자신의 변경을 고친 뒤 다시 커밋하면 됩니다. `BLOCKED`는 에이전트가 우회해서는 안 되는 정책에만 쓰입니다.

개발자(사용자)가 어드바이저리를 직접 마주하는 일은 드물며, 대부분 에이전트가 전달해 주는 내용을 확인하게 됩니다. 에이전트가 사용자에게
확인을 요청한다면 보통 `INTERACTION` 오류의 `[REPORT]` 질문이거나, 사용자가 알아두어야 할 `CONTINUE` 경고입니다.

## 머신 연동 채널

- `--format json` 옵션을 지정하면 stdout에 압축된(들여쓰기 없는) 단일 JSON 객체를 출력합니다. 모든 바이트가 에이전트의
  컨텍스트로 들어가기 때문입니다. JSON만 출력하는 명령어도 `--format json`을 받으므로, 에이전트는 모든 명령어에 이 옵션을 붙여도
  됩니다. 작업 실패 시 `{"error": {...}}` 구조로 반환되며, `code`,
  `level`, `message`, `exit_code` 및 모드·지시문 텍스트·비어 있지 않은 모든 필드를 담은 `advisory` 객체를 포함합니다. 성공한 작업의
  경고 및 알림은 `notices` 필드 아래에 포함됩니다. 이때 stderr에는 아무것도 출력되지 않으므로, 두 스트림을 통합하여 수집하는 에이전트
  호스트에서도 동일한 어드바이저리가 중복 전달되지 않습니다.
- MCP 도구는 서식화된 블록을 오류 텍스트로 직접 반환하거나, 작업 결과 뒤에 경고 및 알림 블록을 덧붙여 전달합니다.
- HTTP 서비스에서는 RFC 7807 problem 문서 형식 내에서 동일한 엔벨로프 구조를 재활용할 수 있습니다.

어떤 전송 계층이나 소비자 도구도 에이전트를 대신하여 `[FIX]` 명령어를 임의로 실행하지 않습니다.

## 독자적인 도구에서 어드바이저리 작성하기

`devkit.advisory`(`devkit-advisory` 패키지이며, 다른 여러 저장소에서 런타임에 활용 중인 semver 계약입니다)를 사용하십시오.

1. 먼저 레벨을 결정합니다. 작업이 실패했거나 가드레일이 거부한 경우 `ERROR`, 성공했으나 확인해야 할 사항이 있는 경우 `WARNING`, 성공했고
   참고할 정보가 있는 경우 `NOTICE`를 선택하며, 즉각적인 조치가 필요 없는 단순 참고 정보는 로그 라인으로 남깁니다.
2. 오류인 경우 관련 필드(`actor`, `retry`, `guardrail`, `input_error`)를 설정하고, 자동으로 도출되는 모드가 의도한 지시문과 일치하는지
   확인합니다. 모드는 직접 지정하지 않습니다. `AUTO` 모드가 되려면 반드시 `fix` 필드가 제공되어야 합니다.
3. `[TARGET]`은 파일 경로, 플래그 또는 `path:line:col` 형식으로 지정하고, `[FIX]`는 자리 표시자(placeholder) 없이 즉시 실행 가능한
   정확한 명령어로 구성하며, "likely"나 "might" 같은 모호한 표현 없이 명확하고 결정적인 문체로 작성합니다.
4. 경고와 알림은 예외로 발생시키지(raise) 말고 결과 객체와 함께 반환하며, 보고 조건 하나당 단일 어드바이저리를 생성합니다.

`advisory` 번들은 이 프로토콜 규격의 지침 문서인 `agent-advisory` 및 `agent-advisory-python`, 그리고 서로 무관한 두 Python 클래스가
동일한 코드를 중복 선언하지 못하도록 검증하는 `RULE-advisory-unique-code`를 제공합니다. click 기반 도구에 이러한 출력 규격을 손쉽게
적용하는 방법은 [에이전트 우선 CLI 도구 키트](cli.md)를 참고하십시오.

## 출처

- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md) (영어 원문):
  심각도 레벨, 블록 형식, 필드 구성, 모드 도출 규칙, 표준 지시문 텍스트 및 작성자 점검표.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md):
  명령어의 stdout, stderr 및 종료 코드 체계 내에서 어드바이저리가 차지하는 역할과 구조.
- [Advisory reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/advisory.md):
  `devkit.advisory` Python API 레퍼런스.
