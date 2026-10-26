---
sources:
  CAP-GOV-evaluation-lifecycle: null
  CAP-GOV-rule-authoring: null
  CAP-GOV-rules-engine: null
  CAP-GOV-spec-rules: null
  UC-adopt-in-an-existing-repository: null
  UC-keep-the-living-spec-consistent: null
  UC-resolve-stale-activity-branches: null
title: 거버넌스 규칙
translated_from: en/areas/governance.md@b915c87b97b2ca2f
---

# 거버넌스 규칙

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

devkit은 프롬프트 지침 대신 결정적인 규칙으로 저장소의 불변 조건을 지킵니다. 규칙은 파일을 파싱해 위반 사항을 해결
방법과 함께 보고하며, 사용자, 에이전트, 커밋 훅, CI 중 누가 물어도 같은 판정이 나옵니다. `devkit rules`는 엔진이고,
규칙 자체는 대부분 번들로 들어옵니다. 거버넌스 규칙(governance rule)이 번들, 게이트, Living Spec과 어떻게 맞물리는지는
[개념](../concepts.md)을 참고하십시오.

엔진은 문서 모델을 모릅니다. 내장 규칙은 어느 저장소에서나 성립하는 것(상대 Markdown 링크, 파일 길이, 커밋된 비밀,
떠도는 산출물)만 다룹니다. 스펙, 유스케이스, 결정에 관한 모든 것은 그 문서를 정의하는 번들의 `kind = "rule"` 자산으로
배포됩니다. 아래에 나오는 `spec` 번들의 열한 개 규칙이 그 예입니다.

## 작업 검사하기

| 하고 싶은 일 | 실행 |
| --- | --- |
| 작업 공간 전체 검사 | `devkit rules check` |
| 건드린 부분만 검사 | `devkit rules check docs/a.md src/` |
| 느린 경고(파일 길이, 오래된 브랜치) 포함 | `devkit rules check --phase hygiene` |
| 다음 커밋에 들어갈 내용 그대로 검사 | `devkit rules check --staged` |
| CI처럼 브랜치 검사 | `devkit rules check --ci --base origin/main` |
| 수정 미리 보기 후 적용 | `devkit rules fix --dry-run`, 그다음 `devkit rules fix` |
| 규칙 하나 이해하기 | `devkit rules explain RULE-markdown-link` |

각 발견 사항은 `[VIOLATION: <RULE-id> severity= file= line= status= message= remediation= guide=]` 한 줄입니다.
`status=fixable`은 `devkit rules fix`가 고칠 수 있다는 뜻이고, `guide=`는 `explain`이 출력하는 배치된 가이드를
가리킵니다. error 심각도의 위반은 명령을 실패시킵니다. `--format json`은 대신 객체 하나를 내고, `--summary-only`는
규칙별 개수만 남깁니다.

수정 실행은 한 번의 수리 패스와 한 번의 재검사로 이루어지며 반복하지 않으므로 비용을 예측할 수 있습니다. 수정기는 파일을
옮기지 않고, `.devkit/managed/`나 `.devkit/overrides/`를 건드리지 않으며, 올바른 UTF-8이 아닌 파일은 그대로 둡니다.

## 실행이 실제로 검사하는 것

- **대상**: 지정한 파일은 Git이 무시하더라도 그대로 검사합니다. 디렉터리는 Git이 무시하지 않는 파일로 펼쳐집니다.
  대상을 주지 않으면 작업 공간 전체를 다룹니다.
- **대상 범위 지정**: 대상 밖의 파일을 읽는 규칙은 `inputs` 패턴을 선언합니다. 대상을 지정한 실행에서 일치하는 대상이
  없으면 그 규칙은 건너뛰므로, 문서만 검사할 때 아키텍처 규칙의 비용을 치르지 않습니다. 작업 공간 전체 실행과 CI는 여전히
  모두 평가하므로 놓치는 것은 없습니다.
- **제외**: `[rules]`의 `exclude`는 모든 대상 집합에서 경로를 빼지만, 링크 수리에는 계속 보입니다.
- **스냅샷**: `--staged`는 Git 인덱스를, `--ci`는 `HEAD`를 병합 기준점과 비교해 평가하므로, 스테이징하지 않은 수정이나
  무시된 로컬 파일이 판정을 바꿀 수 없습니다. 이것이 스냅샷 실행(snapshot run)입니다. 작업 트리가 스테이징한 내용과 이미
  같으면 스테이징 검사는 그 자리에서 실행되고, 비용은 저장소 크기가 아니라 커밋 크기를 따릅니다. `.devkit/config.toml`의
  정책 변경은 스테이징된 뒤에야 스냅샷에 반영됩니다.

이것이 `rules-check` 커밋 게이트가 매 커밋마다 실행하는 검사입니다. [커밋 게이트](gate.md)를 참고하십시오.

## 프로젝트에 맞게 정책 조정하기

프로젝트는 배포된 규칙 파일을 절대 수정하지 않습니다. 관리 사본은 로드될 때마다 설치 기록과 해시로 대조됩니다. 모든
조정은 `.devkit/config.toml`의 `[rules]`에 둡니다.

```toml
[rules]
exclude = ["docs/materials/**"]

[rules.phase_overrides]          # park a linter rule in hygiene while you clear existing debt
RULE-document-summary = "hygiene"

[rules.severity_overrides]
RULE-file-length = "error"

[rules.settings.RULE-file-length]
max_lines = 300

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

`linter` 페이즈는 커밋과 CI가 강제하는 단계이고, `hygiene`는 더 넓은 주기적 점검입니다(규칙 페이즈, rule phase).
옮겨 둔 규칙은 작업 공간 전체 hygiene 실행에서 남은 개수를 출력하며(`[PHASE_OVERRIDE: ... remaining=3]`), 0이 되면
`RULES_PROMOTION_READY` 알림이 오버라이드를 지우라고 알려 줍니다. 새 규칙은 `promote_to`로 자기 쪽에서 같은 일을 할
수 있습니다. `devkit rules phases`는 아무것도 평가하지 않고 기본 페이즈와 실제 적용 페이즈를 나열합니다.

작업 공간 전체 hygiene 실행은 설치된 hygiene 확장도 호출합니다. 이 확장은 오래된 `plan-*`, `dev-*` 브랜치처럼 파일
규칙이 아닌 저장소 상태를 보고하며
([오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md) 참고), 실행을 실패시키지 않습니다.

## spec 거버넌스 규칙

`spec` 번들의 `core` 프리셋은 Living Spec과 기능 스펙의 일관성을 지키는 열한 개의 `linter` 규칙을 배치합니다.
`RULE-spec-progress`와 `RULE-proposal-boundaries`만 경고이고 나머지는 모두 오류입니다.

| 규칙 | 지키는 것 | 수정 |
| --- | --- | --- |
| `RULE-document-reference` | 참조가 코드 스팬 형식의 정확하고 해석 가능한 전체 ID이며, ID나 별칭이 중복되지 않음 | 대괄호 형식, 별칭, 이관된 제안 ID |
| `RULE-id-convention` | 경로, ID, `area`, H1 토큰이 일치하고 날짜나 숫자 ID가 없음 | `id`, `area`, H1 정렬 |
| `RULE-spec-format` | 기능, 유스케이스, 제안, 마일스톤의 필수 프런트매터 | 누락 필드 채움 |
| `RULE-traceability-link` | 유스케이스와 기능 링크가 양쪽에 모두 존재 | 역방향 ID 추가 |
| `RULE-task-coverage` | 모든 수락 기준에 작업이 있고 모든 작업 참조가 존재 | 직접 |
| `RULE-spec-lifecycle` | 스펙 상태, 작업 체크리스트, 조정 상태가 일치 | `completed` 설정 |
| `RULE-spec-progress` | 체크된 작업이 있는 스펙은 `in-progress` | `in-progress` 설정 |
| `RULE-reconcile-contract` | `reconcile.md`의 형식이 올바르고 수정 대상이 실제로 바뀜 | 직접 |
| `RULE-code-entrypoints` | 기능과 유스케이스의 엔트리포인트가 존재 | 직접 |
| `RULE-proposal-boundaries` | 제안이 소유한 경로가 존재 | 직접 |
| `RULE-document-summary` | 검색 대상 문서에 짧은 영어 `summary`가 있음 | 직접 |

완료된 스펙 번들은 이력입니다. 직접 지정할 때만 검사되고 수정으로 다시 쓰이지 않습니다. 자유 형식의 `materials/`
디렉터리는 예외입니다. 이 규칙들과 함께하는 일상적인 흐름은
[Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)를 따르십시오. 레거시 문서가 가득한
저장소에 devkit을 도입할 때는 [기존 저장소에 도입하기](../journeys/adopt-in-an-existing-repository.md)에서 설명하듯
시끄러운 규칙을 `hygiene`로 옮겨 둡니다.

## 직접 규칙 작성하기

규칙은 플러그인 패키지 디렉터리입니다. `BaseRule` 하위 클래스를 담은 `rule.py`, 상대 경로로 import하는 보조 모듈, 옆에
놓인 `guide.md`, 함께 움직이는 `tests/`로 구성됩니다.

```text
rules/doc_heading/
  rule.py        # class DocHeadingRule(BaseRule): id, phase, severity, guide="guide.md", check(ctx)
  headings.py
  guide.md       # Overview, Cause of Violation, Remediation, Configuration, Exceptions
  tests/test_rule.py
```

- 파일은 `ctx.cache`(캐시된 텍스트, 프런트매터, 링크, 공유되는 파싱된 Python 트리 하나)로 읽고, `ctx.is_file_targeted`가
  받아들이는 파일만 보고합니다.
- 타입이 있는 `settings`(frozen dataclass), 대상 밖의 파일을 읽는다면 `inputs`, 규칙의 근거가 되는 지침이나 플레이북을
  가리키는 `related`, `hygiene`에서 시작하는 규칙이라면 `promote_to`를 선언합니다.
- `fix`는 쓴 경로를 반환하도록 구현하며, 쓰기는 `ctx.cache.write_text`로만 합니다.
- `devkit rules check --rules-dir rules`로 시험하고, `devkit rules test RULE-doc-heading --rules-dir rules`로
  테스트합니다. 이 명령은 `devkit_agt.features.rules.services.testing`의 `load_rule`과 `check`를 사용합니다.

배포하려면 이 디렉터리를 프로젝트 번들의 `kind = "rule"` 자산으로 선언하고 `devkit sync`를 실행합니다. `spec-rule`
스킬이 에이전트에게 전체 절차를 안내합니다.

## 실행이 실패했을 때

| 코드 | 할 일 |
| --- | --- |
| `RULES_LOAD_FAILED` | 관리 규칙 파일이 없거나 드리프트됨: `devkit sync`를 실행하거나, 의도한 수정은 `devkit override create <bundle>:<asset>`으로 유지 |
| `RULES_SETTINGS_INVALID`, `RULES_CONFIG_INVALID` | 메시지가 가리키는 `[rules]` 테이블 수정 |
| `RULES_TARGET_INVALID` | 관리 사본 밖, 작업 공간 안의 파일이나 디렉터리 지정 |
| `SPEC_CONFIG_INVALID` | 형식이 잘못된 `[tool.spec]` 테이블 수정 |

파일별 Python 팩트를 가져오는 규칙은 `.devkit/transient/` 아래의 로컬 메모에서 실행 간에 그 팩트를 재사용합니다(파일별
규칙 팩트, per-file rule facts). 파생 상태이므로 메모가 없거나 손상되어도 시간만 더 들 뿐 결과는 바뀌지 않습니다.

## 출처

- [CAP-GOV-rules-engine](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-rules-engine.md) (영어 원문):
  엔진, 규칙 출처, 파일별 팩트.
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md):
  대상, 범위 지정, 페이즈, 정책, 스냅샷 게이트.
- [CAP-GOV-rule-authoring](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-rule-authoring.md):
  규칙 프로토콜, 작업 공간 캐시 API, 규칙 테스트.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  열한 개 spec 규칙 전체.
- [규칙 레퍼런스](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/rules.md): 명령, 출력, 종료
  코드, 내장 규칙 카탈로그.
