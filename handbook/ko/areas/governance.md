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

devkit은 모호한 프롬프트 지침 대신 결정론적(deterministic) 규칙을 통해 저장소의 불변성(invariants)을 엄격하게
지켜냅니다. 규칙은 소스 및 문서 파일을 파싱하여 정책 위반 사항과 구체적인 해결 방안을 함께 보고하며, 사용자, AI 에이전트,
커밋 훅, CI 파이프라인 등 누가 실행하든 언제나 일관된 판정을 내립니다. `devkit rules`는 이를 실행하는 핵심 엔진이며, 규칙
자체는 대부분 번들 형태로 제공됩니다. 거버넌스 규칙(governance rule)이 번들, 게이트, Living Spec과 유기적으로 결합하는
방식은 [개념](../concepts.md)에서 자세히 설명합니다.

규칙 엔진 자체는 특정 문서 모델에 종속되지 않습니다. 내장 규칙은 어떤 저장소에서든 보편적으로 적용되는 항목(상대 Markdown
링크 유효성, 파일 길이 제한, 커밋된 시크릿/비밀 정보 방지, 정리되지 않은 빌드 산출물 방지 등)만을 검사합니다. 스펙, 유스케이스,
아키텍처 결정 등에 관한 도메인 규칙은 해당 문서를 정의하는 번들에서 `kind = "rule"` 에셋으로 제공됩니다. 아래에 소개하는
`spec` 번들의 11가지 거버넌스 규칙이 대표적인 예입니다.

## 작업 내용 검사하기

| 수행하려는 작업 | 실행 명령 |
| --- | --- |
| 작업 공간 전체 검사 | `devkit rules check` |
| 수정한 경로만 선별 검사 | `devkit rules check docs/a.md src/` |
| 장시간 소요되는 정리 검사(파일 길이, 방치된 브랜치 등) 포함 | `devkit rules check --phase hygiene` |
| 다음 커밋에 포함될 내용만 정확히 검사 | `devkit rules check --staged` |
| CI 파이프라인과 동일한 방식으로 브랜치 검사 | `devkit rules check --ci --base origin/main` |
| 자동 수정 사항을 미리 확인한 후 적용 | `devkit rules fix --dry-run` 실행 후 `devkit rules fix` |
| 특정 규칙의 상세 설명 및 가이드 확인 | `devkit rules explain RULE-markdown-link` |

각 위반 사항은 `[VIOLATION: <RULE-id> severity= file= line= status= message= remediation= guide=]` 형식의 한 줄로
출력됩니다. `status=fixable`은 `devkit rules fix` 명령으로 자동 해결할 수 있음을 나타내며, `guide=`는 `explain` 명령이
출력하는 배포된 가이드 문서 위치를 가리킵니다. error 심각도의 위반이 하나라도 있으면 명령 실행이 실패합니다. `--format json`
플래그를 사용하면 단일 JSON 객체 형태로 결과를 받아볼 수 있으며, `--summary-only`는 규칙별 위반 건수만 요약 출력합니다.

자동 수정(`fix`)은 1회의 수리 패스 후 1회의 재검사만 수행하며, 무한 루프를 돌지 않으므로 실행 비용이 매우 예측 가능합니다.
자동 수정기는 파일을 임의로 이동하지 않고, `.devkit/managed/`나 `.devkit/overrides/` 경로를 절대 건드리지 않으며, 올바른
UTF-8 인코딩이 아닌 파일은 수정 대상에서 제외합니다.

## 실제 검사 동작 방식

- **검사 대상(Targets)**: 인자로 명시한 파일은 Git이 무시(ignore)하는 파일이라도 지정된 그대로 검사합니다. 디렉터리를
  지정하면 Git이 무시하지 않는 파일들로 자동 확장됩니다. 검사 대상을 지정하지 않으면 작업 공간 전체를 검사합니다.
- **대상 범위 축소(Target scoping)**: 검사 대상 외의 다른 파일까지 함께 참조해야 하는 규칙은 `inputs` 패턴을 선언합니다.
  대상 경로를 지정하여 실행할 때 매칭되는 대상이 없으면 해당 규칙은 평가를 건너뛰므로, 문서만 검사할 때 불필요하게
  아키텍처 규칙까지 실행되는 비용을 아낄 수 있습니다. 단, 작업 공간 전체 검사나 CI 검사에서는 모든 규칙을 온전히 평가하므로
  검증 누락이 발생하지 않습니다.
- **제외 경로(Exclusions)**: `[rules]`의 `exclude` 설정에 등록된 경로는 모든 검사 대상 집합에서 제외됩니다. 단, 상대
  링크 자동 수리 과정에서는 참조 대상으로서 계속 인식됩니다.
- **스냅샷 검사(Snapshots)**: `--staged`는 Git 인덱스를 검사하고, `--ci`는 `HEAD`를 병합 기준점(merge base)과 비교하여
  평가하므로, 스테이징되지 않은 로컬 수정이나 무시된 로컬 파일이 검증 결과에 영향을 주지 않습니다. 이것이 스냅샷
  실행(snapshot run)입니다. 작업 트리의 내용이 이미 스테이징된 내용과 동일하다면 스테이징 검사는 워크트리에서 직접 실행되므로,
  검사 비용이 저장소 전체 크기가 아니라 커밋 크기에만 비례합니다. `.devkit/config.toml`의 정책 변경 사항은 스테이징된 이후에야
  스냅샷 검사에 반영됩니다.

이 스냅샷 검사가 바로 `rules-check` 커밋 게이트가 매 커밋마다 실행하는 검사입니다. 자세한 내용은
[커밋 게이트](gate.md)를 참고하십시오.

## 프로젝트 환경에 맞춘 정책 조정

프로젝트에서는 배포된 규칙 파일을 직접 수정하지 않습니다. 관리 대상 사본 파일들은 로드될 때마다 설치 기록의 체크섬 해시와
일치하는지 항상 검증됩니다. 모든 정책 조정은 `.devkit/config.toml`의 `[rules]` 테이블에서 관리합니다.

```toml
[rules]
exclude = ["docs/materials/**"]

[rules.phase_overrides]          # 기존 기술 부채를 정리하는 동안 linter 규칙을 hygiene 페이즈로 임시 유예
RULE-document-summary = "hygiene"

[rules.severity_overrides]
RULE-file-length = "error"

[rules.settings.RULE-file-length]
max_lines = 300

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

`linter` 페이즈는 커밋 및 CI 단계에서 필수로 강제되는 규칙들이며, `hygiene`는 정기적으로 수행하는 광범위한 위생 점검
페이즈입니다(규칙 페이즈, rule phase). 임시로 유예(`phase_overrides`)해 둔 규칙은 작업 공간 전체 hygiene 검사 시 남은
위반 건수를 출력하며(`[PHASE_OVERRIDE: ... remaining=3]`), 위반 건수가 0이 되면 `RULES_PROMOTION_READY` 안내가 출력되어
해당 오버라이드 설정을 제거할 수 있음을 알려줍니다. 새로 도입하는 규칙의 경우 작성 시 `promote_to`를 선언하여 동일한 유예 방식을
자체 지원할 수도 있습니다. `devkit rules phases` 명령을 사용하면 실제 검사를 실행하지 않고도 각 규칙의 기본 페이즈와 현재
적용 중인 실효 페이즈 목록을 확인할 수 있습니다.

작업 공간 전체 hygiene 검사는 설치된 위생 점검 확장(hygiene extensions)들도 함께 호출합니다. 이 확장들은 파일 규칙 범주에
들지 않는 저장소 전반의 상태, 예를 들어 방치된 `plan-*`, `dev-*` 브랜치 등을 탐지하여 보고하며
([오래된 활동 브랜치 정리하기](../journeys/resolve-stale-activity-branches.md) 참고), 검사 실행 자체를 실패시키지는 않습니다.

## spec 거버넌스 규칙

`spec` 번들의 `core` 프리셋은 Living Spec과 기능 스펙의 일관성을 엄격하게 유지하는 11가지 `linter` 규칙을 제공합니다.
`RULE-spec-progress`와 `RULE-proposal-boundaries`만 경고(warning) 수준이고 나머지는 모두 오류(error) 수준입니다.

| 규칙 | 보장하는 조건 | 자동 수정(`fix`) 지원 |
| --- | --- | --- |
| `RULE-document-reference` | 모든 참조가 코드 스팬 형태의 정확하고 해석 가능한 전체 ID여야 하며, 중복 ID나 중복 별칭이 없어야 함 | 대괄호 표기, 별칭, 이관 완료된 제안 ID 자동 변환 |
| `RULE-id-convention` | 파일 경로, 문서 ID, `area` 속성 및 H1 제목 토큰이 상호 일치해야 하며, 날짜나 숫자 기반 임의 ID를 허용하지 않음 | `id`, `area`, H1 일치 정렬 |
| `RULE-spec-format` | 기능, 유스케이스, 제안, 마일스톤 문서의 필수 프런트매터 필드 누락 방지 | 누락된 기본 필드 자동 채움 |
| `RULE-traceability-link` | 유스케이스와 기능 간의 양방향 추적성 링크가 상호 누락 없이 존재해야 함 | 누락된 역방향 ID 자동 추가 |
| `RULE-task-coverage` | 모든 수락 기준에 대응하는 구현 작업이 존재해야 하며, 작업에 명시된 참조가 유효해야 함 | 수동 조치 |
| `RULE-spec-lifecycle` | 스펙 상태, 작업 체크리스트 완료 여부, 리콘사일(reconcile) 상태가 상호 일치해야 함 | `completed` 상태 자동 설정 |
| `RULE-spec-progress` | 완료 체크된 작업이 하나라도 있는 스펙은 반드시 `in-progress` 상태여야 함 | `in-progress` 상태 자동 설정 |
| `RULE-reconcile-contract` | `reconcile.md`의 형식이 올바르고, 수정 대상 문서들이 실제로 변경되어야 함 | 수동 조치 |
| `RULE-code-entrypoints` | 기능 및 유스케이스에 선언된 코드 엔트리포인트가 실제 코드에 존재해야 함 | 수동 조치 |
| `RULE-proposal-boundaries` | 제안 문서에 명시된 소유 대상 경로들이 실제로 존재해야 함 | 수동 조치 |
| `RULE-document-summary` | 검색 대상 문서에 간결한 영문 `summary`가 작성되어 있어야 함 | 수동 조치 |

완료된 스펙 번들은 과거 이력으로 취급됩니다. 사용자가 경로를 직접 지정할 때만 검사 대상이 되며, 자동 수정(`fix`)으로 내용을
임의 덮어쓰지 않습니다. 자유로운 형식의 `materials/` 디렉터리는 규칙 적용에서 제외됩니다. 이 규칙들을 활용한 일상적인
개발 루프는 [Living Spec 일관성 유지하기](../journeys/keep-the-living-spec-consistent.md)를 참고하십시오. 레거시 문서가 많은
기존 저장소에 devkit을 처음 도입할 때는 [기존 저장소에 devkit 도입하기](../journeys/adopt-in-an-existing-repository.md)에서 안내하는
대로 위반 사항이 많은 규칙을 `hygiene` 페이즈로 임시 유예해 두는 것이 효과적입니다.

## 사용자 정의 규칙 작성하기

규칙은 독립된 플러그인 패키지 디렉터리로 구성됩니다. `BaseRule` 서브클래스가 정의된 `rule.py`, 상대 경로로 임포트되는 보조 모듈,
같은 위치의 안내 문서 `guide.md`, 그리고 함께 관리되는 테스트 코드 `tests/`로 이루어집니다.

```text
rules/doc_heading/
  rule.py        # class DocHeadingRule(BaseRule): id, phase, severity, guide="guide.md", check(ctx)
  headings.py
  guide.md       # Overview, Cause of Violation, Remediation, Configuration, Exceptions
  tests/test_rule.py
```

- 파일 검사는 `ctx.cache`(캐시된 텍스트, 프런트매터, 링크, 공유 파싱된 단일 Python AST 트리 제공)를 통해 수행하며,
  `ctx.is_file_targeted`가 허용하는 파일에 대해서만 위반 사항을 보고합니다.
- 타입 어노테이션이 적용된 `settings`(frozen dataclass), 대상 파일 외의 파일도 읽어야 하는 경우 `inputs`, 규칙의 근거가 되는
  지침이나 플레이북을 가리키는 `related`, `hygiene` 페이즈에서 시작하는 규칙인 경우 `promote_to`를 선언합니다.
- `fix` 메서드는 수정한 파일 경로 목록을 반환하도록 구현하며, 파일 쓰기는 반드시 `ctx.cache.write_text`를 통해서만 수행해야 합니다.
- `devkit rules check --rules-dir rules`로 즉시 검사해 볼 수 있으며,
  `devkit rules test RULE-doc-heading --rules-dir rules`를 통해 단위 테스트를 실행할 수 있습니다(내부적으로
  `devkit_agt.features.rules.services.testing`의 `load_rule`과 `check`를 사용).

작성한 규칙을 배포하려면 프로젝트 번들의 `kind = "rule"` 에셋으로 해당 디렉터리를 선언한 후 `devkit sync`를 실행하십시오.
`spec-rule` 스킬을 활용하면 에이전트가 전체 작성 및 등록 절차를 단계별로 안내합니다.

## 규칙 실행 실패 시 대처 방법

| 오류 코드 | 조치 방법 |
| --- | --- |
| `RULES_LOAD_FAILED` | 관리 규칙 파일이 누락되었거나 임의 변경(드리프트)됨: `devkit sync`를 실행해 복원하거나, 의도적인 수정인 경우 `devkit override create <bundle>:<asset>`으로 오버라이드 유지 |
| `RULES_SETTINGS_INVALID`, `RULES_CONFIG_INVALID` | 오류 메시지에 안내된 `[rules]` 테이블 설정 수정 |
| `RULES_TARGET_INVALID` | 관리 사본 디렉터리가 아닌, 작업 공간 내부의 유효한 파일이나 디렉터리를 지정 |
| `SPEC_CONFIG_INVALID` | 잘못 작성된 `[tool.spec]` 테이블 설정 수정 |

파일별 Python 팩트를 추출하는 규칙은 `.devkit/transient/` 디렉터리 내의 로컬 메모(memo) 캐시를 활용하여 여러 실행에 걸쳐
분석 결과를 재사용합니다(파일별 규칙 팩트, per-file rule facts). 이 캐시는 파생 상태(derived state)이므로 메모 파일이 없거나
손상되어도 분석 시간이 약간 더 걸릴 뿐 판정 결과 자체는 달라지지 않습니다.

## 관련 자료

- [CAP-GOV-rules-engine](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-rules-engine.md) (영어 원문):
  규칙 엔진 아키텍처, 규칙 소스 및 파일별 팩트.
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md):
  검사 대상 선정, 스코핑, 규칙 페이즈, 정책 계층 및 스냅샷 게이트.
- [CAP-GOV-rule-authoring](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-rule-authoring.md):
  규칙 프로토콜 규약, 워크스페이스 캐시 API, 규칙 단위 테스트 작성법.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  11개 spec 거버넌스 규칙 상세 명세.
- [규칙 레퍼런스](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/rules.md): 명령어, 출력 형식, 종료
  코드, 내장 규칙 카탈로그.
