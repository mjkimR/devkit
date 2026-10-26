---
sources:
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
  CAP-CMP-bounded-execution: null
title: 컴팩트 명령 출력
translated_from: en/areas/compact.md@6d0e5dc3adbc6a01
---

# 컴팩트 명령 출력

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
- [어드바이저리](advisory.md)
- [에이전트 우선 CLI 도구 키트](cli.md)
- [협업](collaboration.md)
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

테스트 실행기, 린터, 타입 검사기는 사람을 위해 출력합니다. 진행 점, 통과한 테스트 이름, 소요 시간 표, 색상 같은
것들입니다. 이런 도구를 직접 실행한 에이전트는 이 모든 출력을 받으며, 출력이 길면 에이전트 호스트가 임의의 지점에서
잘라 버려 실패 내용을 놓치는 일이 잦습니다. `devkit run`은 이 문제를 해결합니다. 명령 하나를 실행해 전체 출력은 로그
파일에 남기고, 중요한 부분만 제한된 분량으로 보여 주는 컴팩트 출력(compact output)을 출력합니다. devkit이 에이전트의
컨텍스트를 이렇게 신중하게 아끼는 이유는 [개념](../concepts.md)을 참고하세요.

## 명령을 통해 실행하기

```sh
devkit run -- just test
devkit run -- uv run pytest tests/unit/test_scan.py -k timeout
devkit run --format json -- npm run lint
```

옵션은 명령 앞에 둡니다. 명령부터 뒤의 모든 것은 그대로 전달됩니다. 명령은 현재 디렉터리에서 stdin이 닫힌 채로
실행되므로, 입력을 기다리는 명령은 에이전트를 멈춰 세우지 않고 종료됩니다. 여러 명령을 실행하려면 이를 연결한
레시피를 감싸세요(`devkit run -- just lint`). 실행기는 감쌀 뿐 계획하지 않습니다.

## 결과 읽기

```text
[RUN: "just test" outcome=failed exit=1 log=/tmp/devkit-run-501/<project>/20261026-101500-just-ab12.log]
[RUN_SUMMARY: "3 failed, 412 passed in 21.4s"]
[RUN_FAILURE: "tests/unit/test_x.py::test_y" kind=failed message=-]
[RUN_WARNING: "DeprecationWarning: ..." location=tests/test_x.py:12]
[RUN_OMITTED: summaries=0 failures=0 warnings=2 advisories=0 output=0]
[RUN_OUTPUT: shown=8000 omitted=31250 filtered=840]
<excerpt>
```

- `[RUN]`은 결과, 명령 자체의 종료 코드, 로그 경로를 알려 줍니다.
- `[RUN_SUMMARY]` 줄은 도구가 출력한 결과 줄입니다(pytest, ruff, mypy, Pyright, tsc, Jest, Vitest, Playwright,
  cargo, ESLint, Prettier, 커버리지 합계, `devkit rules` 요약을 인식합니다). 인식된 요약 없이 통과한 명령은 대신
  마지막 줄들을 보여 줍니다(`[RUN_LAST_LINE]`).
- 실패한 경우에만 `[RUN_FAILURE]`가 발췌에서 잘린 실패 pytest 테스트의 이름을 알려 주므로 노드 ID로 다시 실행할 수
  있으며, 발췌는 진행 표시와 잡음을 걸러 낸 출력의 앞부분과 뒷부분을 보여 줍니다.
- `[RUN_OMITTED]`는 들어가지 못한 것을 셉니다. 조용히 버려지는 것은 없습니다. 발췌 안의 모든 생략 표시는 자신이
  대신하는 로그 줄 범위를 알려 주므로, `sed -n 'A,Bp' <log>`로 빠진 부분을 정확히 볼 수 있습니다.

중첩된 `devkit` 명령이 출력한 어드바이저리 블록은 통째로 추출되어 stderr로 전달되며 오류가 맨 뒤에 옵니다. 그래서
주변 출력이 잘려도 결정적인 `[ACTION]`은 살아남습니다([어드바이저리](advisory.md)).

## 종료 코드

실행기는 명령이 통과하면 `0`, 실패하면 `1`로 종료합니다. 명령 자체의 코드는 `exit=`에 있으므로 도구의 `2`가 실행기의
`2`로 오해되는 일은 없습니다. 실행기는 명령을 시작할 수 없거나(`RUN_COMMAND_NOT_STARTED`), 로그를 쓸 수 없거나
(`RUN_LOG_DIR_INVALID`), 자신의 인자를 파싱할 수 없을 때만 `2`로 종료합니다.

실행을 중단하면(Ctrl-C 또는 에이전트 호스트의 타임아웃 시그널) 명령의 프로세스 그룹 전체가 멈추고,
`outcome=interrupted`가 담긴 `[RUN]` 줄만 출력한 뒤 `128 + N`으로 종료합니다. 실행이 끝난 뒤까지 살아남는 테스트나
빌드 프로세스는 없습니다.

## 로그

로그는 작업 트리 밖, 시스템 임시 디렉터리 안의 사용자별·프로젝트별 디렉터리(`0700`으로 생성)에 저장됩니다. 실행마다
파일 하나를 쓰며, 프로젝트별로 최신 20개를 보관합니다. 로그가 전체 기록이므로, 보이는 출력만으로 부족하면 `rg`나
`sed`로 읽으세요.

## 출력을 더 작게 만들기

실패에서 남는 가장 큰 부분은 대개 도구 자체의 보고서이며, 이를 안정적으로 줄일 수 있는 것은 도구뿐입니다. 레시피에서
`pytest --tb=short`와 `ruff check --output-format=concise`를 쓰세요. `devkit-run` 지침도 둘 다 권장합니다.
`--slow-after`초(기본값 `60`, `0`이면 끔)보다 오래 실행된 명령에는 더 좁은 실행을 제안하는 `RUN_SLOW_COMMAND` 알림이
붙습니다.

## 에이전트가 이를 배우는 곳

`devkit run`은 `devkit-agt`와 함께 배포됩니다. 자동 선택되는 `harness` 번들의 `devkit-run` 지침이 에이전트에게 이를
사용하고 검증 레시피 안에 넣도록 가르칩니다. 에이전트가 레시피 밖에서 범위를 좁힌 명령을 자주 실행한다면
`devkit add harness:run`으로 선택형 프리셋(preset)을 선택하세요. 실행기를 가리키는 짧은 `AGENTS.md` 한 줄이 추가됩니다.

게이트와 워크플로 검사도 같은 실행기를 재사용합니다. `verify-commands` 커밋 게이트는 모든 명령을 이 실행기로 실행하고,
거부 메시지에는 제한된 출력만 담습니다([커밋 게이트](gate.md)). 라이브러리 호출자는
`devkit_agt.features.compact.run_command`를 사용하며, 이 함수는 아무것도 출력하지 않고 `CommandRun`을 반환합니다.

## 출처

- [CAP-CMP-bounded-execution](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/compact/CAP-CMP-bounded-execution.md) (영어 원문):
  실행, 로그, 제한된 출력과 그 한도, 출력 형식과 라이브러리.
- [Compact reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/compact.md): 사용법,
  오류 코드와 모듈 지도.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md):
  `devkit run`이 모든 명령과 공유하는 출력 계약.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  실행기가 인식하는 어드바이저리 문법.
