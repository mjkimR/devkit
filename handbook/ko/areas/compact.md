---
sources:
  ARCH-08-1-agent-output: null
  CAP-ADV-agent-advisory-protocol: null
  CAP-CMP-bounded-execution: null
title: 컴팩트 명령 출력
translated_from: en/areas/compact.md@bfb23f21015952de
---

# 컴팩트 명령 출력

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

테스트 러너, 린터, 타입 체커와 같은 개발 도구들은 사람 개발자를 염두에 두고 결과를 출력합니다. 진행 표시 점(dot), 통과한 테스트 목록,
소요 시간 표, 터미널 색상 등이 대표적입니다. AI 에이전트가 이러한 도구를 직접 실행하면 방대한 출력 전체를 그대로 수신하게 되며,
출력량이 많을 경우 에이전트 호스트 환경이 임의의 지점에서 출력을 잘라내어 정작 중요한 실패 원인을 유실하기 쉽습니다.
`devkit run`은 이 문제를 근본적으로 해결합니다. 대상 명령어를 실행하여 전체 출력은 별도의 로그 파일에 안전하게 보존하고, 에이전트에게는
핵심 정보만 엄선된 분량으로 요약하여 보여주는 컴팩트 출력(compact output)을 제공합니다. devkit이 에이전트의 컨텍스트 예산을 이처럼
신중하게 관리하는 이유는 [개념](../concepts.md)을 참고하십시오.

## `devkit run`으로 명령 실행하기

```sh
devkit run -- just test
devkit run -- uv run pytest tests/unit/test_scan.py -k timeout
devkit run --format json -- npm run lint
```

실행기 옵션은 실행할 명령어 앞에 지정하며, 명령어 구분자(`--`) 이후의 모든 인자는 대상 프로그램에 그대로 전달됩니다.
대상 명령어는 현재 작업 디렉터리에서 표준 입력(stdin)이 닫힌 상태로 실행되므로, 예기치 않게 사용자 입력을 기다리느라 에이전트 세션이
무한정 멈추는(hang) 현상을 방지합니다. 여러 명령어를 연속해서 실행해야 할 때는 이를 조합한 작업 레시피를 실행기에 전달하십시오
(`devkit run -- just lint`). `devkit run`은 개별 명령 실행을 래핑할 뿐, 다중 명령의 실행 순서를 자체적으로 계획하지 않습니다.

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

- `[RUN]`은 실행 결과, 대상 명령어 자체의 종료 코드, 전체 로그 파일 경로를 표시합니다.
- `[RUN_SUMMARY]` 줄은 도구가 자체 출력한 최종 요약 내용입니다(pytest, ruff, mypy, Pyright, tsc, Jest, Vitest,
  Playwright, cargo, ESLint, Prettier, 커버리지 총계 및 `devkit rules` 요약 형식을 자동 인식합니다). 별도의 요약 형식이
  인식되지 않는 명령어가 성공적으로 완료된 경우에는 표준 출력의 마지막 줄들을 대신 표시합니다(`[RUN_LAST_LINE]`).
- 명령어가 실패한 경우에 한해, 발췌문에서 생략된 실패 테스트 항목을 `[RUN_FAILURE]`로 표시하여 해당 노드 ID로 즉시 재실행할 수 있도록
  지원합니다. 발췌문은 진행 표시나 불필요한 노이즈를 필터링한 후 출력의 시작과 끝부분만을 균형 있게 보여줍니다.
- `[RUN_OMITTED]`는 예산 초과로 화면에 표시되지 못한 항목 수를 집계합니다. 어떤 내용도 조용히 누락되지 않습니다. 발췌문 내의 모든
  생략 마커에는 해당 마커가 대체하는 로그 파일의 라인 번호 범위가 명시되므로, `sed -n 'A,Bp' <log>` 명령어로 생략된 부분을 정확하게
  확인할 수 있습니다.

실행 중인 하위 `devkit` 명령어가 출력한 어드바이저리 블록은 원형 그대로 추출되어 stderr로 전달되며, 가장 중요한 오류 블록이 맨 마지막에
위치합니다. 이를 통해 주변 로그 출력이 잘려 나가더라도 에이전트가 다음 행동을 결정하는 핵심 지시문인 `[ACTION]`을 온전히 확인할 수
있습니다([어드바이저리](advisory.md)).

## 종료 코드

실행기는 실행한 대상 명령어가 성공하면 `0`, 실패하면 `1`로 종료합니다. 대상 명령어 자체의 실제 종료 코드는 `exit=` 속성에 명시되므로,
대상 도구가 반환한 `2`와 실행기 자체의 오류 코드 `2`가 혼동될 염려가 없습니다. 실행기는 프로세스를 시작조차 할 수 없거나
(`RUN_COMMAND_NOT_STARTED`), 로그 파일을 쓸 수 없거나(`RUN_LOG_DIR_INVALID`), 실행기 자체의 인자 파싱에 실패한 경우에만
종료 코드 `2`를 반환합니다.

실행 도중 중단 신호(Ctrl-C 또는 에이전트 호스트의 타임아웃 시그널)가 발생하면 명령어의 프로세스 그룹 전체를 즉각 중지하고,
`outcome=interrupted`를 포함한 `[RUN]` 한 줄만 출력한 뒤 `128 + N` 코드로 종료합니다. 실행이 중단된 후 백그라운드에 좀비 프로세스로
남는 테스트나 빌드 작업은 발생하지 않습니다.

## 로그

로그는 워크트리 외부에 위치한 시스템 임시 디렉터리 내에 사용자별·프로젝트별 디렉터리(권한 `0700`)로 분리되어 안전하게 보관됩니다.
매 실행마다 단일 로그 파일이 생성되며, 프로젝트당 최신 20개까지만 보존됩니다. 전체 실행 기록이 온전히 보존되므로, 요약된 발췌 뷰만으로
원인을 파악하기 부족하다면 `rg`나 `sed` 명령어로 전체 로그를 직접 검토하십시오.

## 출력을 더 작게 만들기

명령어 실패 시 가장 많은 분량을 차지하는 것은 도구 자체의 오류 보고서이며, 이를 가장 확실하게 줄이는 방법은 도구 고유의 간소화 옵션을
활용하는 것입니다. 검증 레시피에 `pytest --tb=short`나 `ruff check --output-format=concise`와 같은 옵션을 적용하십시오
(`devkit-run` 지침에서도 이를 권장합니다). 지정한 임계값(`--slow-after`, 기본값 60초, `0` 지정 시 비활성화)보다 오래 걸리는 명령어에는
더 세부적인 타깃 실행을 권고하는 `RUN_SLOW_COMMAND` 알림이 추가됩니다.

## 에이전트가 이를 학습하는 방식

`devkit run`은 `devkit-agt` 패키지와 함께 배포됩니다. 자동 선택되는 `harness` 번들의 `devkit-run` 지침을 통해 에이전트가 이 실행기를
사용하고 검증 레시피에 적용하도록 안내합니다. 만약 에이전트가 레시피 외부에서 특정 테스트나 검사 명령어를 직접 실행하는 빈도가 높다면,
`devkit add harness:run`을 실행하여 선택형 프리셋을 추가하십시오. `AGENTS.md`에 실행기 사용을 권고하는 간결한 지침 한 줄이 등록됩니다.

커밋 게이트와 워크플로 검사에서도 동일한 실행기를 재사용합니다. 예를 들어 `verify-commands` 커밋 게이트는 모든 검증 명령어를 이 실행기를
통해 실행하며, 거부 메시지에는 제한된 컴팩트 뷰만 포함합니다([커밋 게이트](gate.md)). `devkit generated`도 실패한 재생성 명령을
같은 방식으로 보고합니다([생성 파일](generated.md)). 파이썬 라이브러리 레벨의 호출자는
`devkit_agt.features.compact.run_command`를 활용할 수 있으며, 이 함수는 표준 출력에 아무것도 직접 출력하지 않고
`CommandRun` 객체를 반환합니다. 이 객체의 `failure_details`가 두 곳에서 함께 쓰는 어드바이저리 상세 줄입니다.

## 출처

- [CAP-CMP-bounded-execution](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/compact/CAP-CMP-bounded-execution.md) (영어 원문):
  명령 실행 제어, 로그 관리 정책, 제한된 발췌 뷰 및 예산 계산 로직, 출력 형식과 라이브러리 API.
- [Compact reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/compact.md):
  명령어 사용법, 에러 코드 목록 및 모듈 맵.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md):
  `devkit run`이 모든 하위 명령어와 공유하는 출력 계약 규격.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  실행기가 인식하고 보존하는 어드바이저리 문법 구조.
