---
sources:
  CAP-DOCS-document-model: null
  CAP-GATE-commit-gates: null
  CAP-GOV-spec-rules: null
  CAP-TRACE-code-entrypoints: null
  UC-keep-the-living-spec-consistent: null
title: Living Spec 일관성 유지하기
translated_from: en/journeys/keep-the-living-spec-consistent.md@de85e56bda890404
---

# Living Spec 일관성 유지하기

<!-- handbook:provenance -->
> 소스 커밋 `5e71d74c8e5a` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [주간 보고서 게시하기](publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](route-development-intent.md)
- [병렬 작업 안전하게 실행하기](run-parallel-work-safely.md)
- [어드바이저리](../areas/advisory.md)
- [에이전트 우선 CLI 도구 키트](../areas/cli.md)
- [협업](../areas/collaboration.md)
- [컴팩트 명령 출력](../areas/compact.md)
- [전달](../areas/delivery.md)
- [배포](../areas/distribution.md)
- [문서](../areas/documents.md)
- [커밋 게이트](../areas/gate.md)
- [생성 파일](../areas/generated.md)
- [거버넌스 규칙](../areas/governance.md)
- [하네스](../areas/harness.md)
- [호스트](../areas/host.md)
- [통합](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [검색](../areas/search.md)
- [추적성](../areas/traceability.md)
- [뷰어](../areas/viewer.md)
- [워크트리](../areas/worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

`docs/` 디렉터리에 위치한 Living Spec은 향후 투입될 에이전트가 매번 저장소 전체를 재독하지 않고도 그 내용을 온전히 신뢰할 수
있을 때에만 가치를 발휘합니다. 이 여정에서는 사용자나 에이전트가 문서와 코드를 수정하는 과정에서 devkit이 Living Spec의 구조적
정합성을 어떻게 견고하게 유지하는지 살펴봅니다. 깨진 문서 참조, 단방향 누락 링크, 배치 표준에 어긋난 파일, 오래된 스펙 상태값,
Living Spec에 미반영된 변경 내역, 유효하지 않은 코드 엔트리포인트 등은 모두 고유한 거버넌스 규칙 ID와 함께 감지되며, 수정 방법이
명확하고 결정론적인 경우 명령어 하나로 안전하게 자동 수정됩니다.

문서에 기술된 내용 자체가 실제 코드 동작과 *의미론적으로 일치하는가*는 구조적 정합성과는 다른 차원의 문제이며, 이는
[Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)에서 다룹니다. 본 문서에서 사용되는 핵심 개념(Living Spec,
거버넌스 규칙, 커밋 게이트(commit gate) 등)은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-keep-the-living-spec-consistent`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-keep-the-living-spec-consistent.md) (영어 원문).

## 시작하기 전에

- 프로젝트가 `docs` 번들을 선택했고, `devkit sync`가 문서 규칙을 이미 배포한 상태여야 합니다(규칙은 `core` 프리셋에 포함되어 배포됩니다).
  스펙 주도 전달을 사용하면 `spec` 번들이 기능 스펙과 제안의 수명 주기 규칙을 더합니다.
- 이 규칙들은 일반적인 devkit 거버넌스 규칙이므로 `.devkit/config.toml`의 `[rules]` 섹션에서 설정하는 페이즈(phase), 심각도(severity),
  예외 설정이 모두 동일하게 적용됩니다. 자세한 내용은 [거버넌스 규칙](../areas/governance.md) 영역 문서를 참고하십시오.

## 단계별 점검 및 유지 절차

1. **변경 사항 검사:** 작업 공간 전체 또는 수정한 파일들에 대해 규칙을 실행합니다.

   ```sh
   uv run devkit rules check                      # whole workspace
   uv run devkit rules check docs/usecases/x.md   # only these targets
   ```

   각 위반 사항은 관련 규칙 ID(예: `RULE-traceability-link`), 자동 수정 가능 여부(`fixable` 또는 `open`), 그리고 권장 해결 조치를
   함께 안내합니다. 위반 보고는 명령어 실행 대상 파일에 한해서만 출력되며, 완료된 스펙 번들은 과거 이력으로 취급되어 대상 경로를 직접
   명시했을 때에만 검사됩니다.

2. **결정론적 자동 수정 적용:**

   ```sh
   uv run devkit rules fix --dry-run   # preview
   uv run devkit rules fix
   ```

   자동 수정은 지정된 현재 파일 내에서 해당 규칙이 관할하는 바이트 영역만 파일 본래의 서식 스타일에 맞추어 안전하게 재작성합니다.
   임의로 파일을 이동하거나 이름을 변경하지 않으며, 누락된 ID를 임의로 추측하지 않고, 이미 완료된 스펙 번들은 절대 건드리지 않습니다.

3. **재검사:** `devkit rules check`를 다시 실행하여 위반 사항이 완전히 해소되었는지 확인합니다.

4. **커밋 생성:** 기본 내장된 `rules-check` 커밋 게이트가 Git 인덱스에 스테이징된 트리 상태(`devkit rules check --staged` 기준)를
   엄밀히 평가하여 커밋을 승인합니다. 작업 트리에 남아 있는 미스테이징 변경 사항은 게이트 판정에 일절 영향을 주지 않습니다.

5. **풀 리퀘스트 생성 및 원격 검증:** CI 파이프라인에서 `devkit rules check --ci --base <ref>` 명령을 실행하여, 머지 베이스(merge base)
   대비 브랜치의 모든 변경 사항을 동일한 규칙으로 철저히 검증합니다.

특정 규칙의 상세 검사 항목과 수동 수정 가이드를 확인하려면 `uv run devkit rules explain <RULE-id>`를 실행하십시오.

## 주요 스펙 규칙과 검사 항목

14가지 규칙(`docs`가 제공하는 문서 규칙 9개, `spec`이 제공하는 수명 주기 규칙 5개) 목록은
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-spec-rules.md) (영어 원문)에
정리되어 있습니다. 가장 자주 접하게 되는 규칙은 다음과 같습니다.

| 규칙 | 감지되는 위반 상황 | 자동 수정 지원 |
| --- | --- | --- |
| `RULE-document-reference` | 문서 ID가 해석되지 않거나, 참조가 대괄호 형식 또는 별칭(alias)을 사용함 | 부분 자동 수정 지원 |
| `RULE-id-convention` | 파일 경로, `id`, `area`, 제목 토큰이 서로 일치하지 않음 | 파일 경로가 올바르면 자동 수정 |
| `RULE-traceability-link` | 유스케이스가 참조하는 capability에서 해당 유스케이스를 역방향으로 참조하지 않음 | 역방향 참조 ID 자동 추가 |
| `RULE-spec-lifecycle` | `spec.md`, `tasks.md`, `reconcile.md`의 생명주기 상태가 서로 불일치함 | `status: completed`로 동기화 |
| `RULE-reconcile-contract` | `resolved` 기록에 명시된 `modified` 대상 문서가 실제 Git diff에서 변경되지 않음 | 수동 수정 필요 |
| `RULE-code-entrypoints` | `entrypoints`에 선언된 소스 코드 파일 경로가 존재하지 않음 | 수동 수정 필요 |
| `RULE-steering-documents` | `docs/steering/`의 파일에 `id`가 있거나 `title`·`summary`가 없거나, 디렉터리가 상한을 넘음 | 수동 수정 필요 |
| `RULE-ux-links` | UX 문서와 그 문서를 인용하는 유스케이스 단계가 서로 맞지 않음 | 수동 수정 필요 |

프로젝트의 개발 방식이 인큐베이션인 동안에도 문서 규칙은 평소와 같이 판정하지만, 수명 주기 규칙은 SDD 워크플로에 명시적으로 바인딩된
유닛에만 적용됩니다. 적용할 유닛이 없으면 검사 성공이 아니라 누락 증거로 `SDD_LIFECYCLE_INACTIVE`를 보고합니다.

문서가 ID를 부여받는 체계와 참조가 해석되는 원리는 문서 모델인
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)에
정의되어 있습니다([문서](../areas/documents.md) 영역 참고).

## 문제 해결

- **`DOCS_CONFIG_INVALID` 에러로 명령어 실행 실패 (종료 코드 `2`):** 문서 네임스페이스를 등록하는 `.devkit/config.toml`의
  `[tool.docs]` 테이블 설정에 알 수 없는 키가 포함되는 등 구문 오류가 있는 경우입니다. 이는 개별 문서의 규칙 위반이 아니라 설정 오류입니다. 규칙 엔진이 문서별 적용 규약을 판별할 수
  없으므로 아무런 검사도 진행되지 않습니다. 설정 테이블을 올바르게 수정한 후 다시 실행하십시오.
- **자동 수정(`fix`) 실행 후에도 위반 사항이 `open` 상태로 남아 있는 경우:** 모호함 없이 기계적으로 수정할 수 없는 위반 사항입니다. 예를 들어
  저장소 어디에도 선언되지 않은 미식별 ID 참조, 삭제된 코드 엔트리포인트, 필수 누락된 reconcile 증빙 등이 이에 해당합니다. 자동 수정 기능은
  위험한 임의 수정을 방지하기 위해 이러한 항목을 변경하지 않고 보존합니다. 안내된 조치 가이드를 참고하여 수동으로 수정한 뒤 다시 검사하십시오.
- **직접 수정하지 않은 capability 문서 때문에 커밋이 거부되는 경우:** 소스 코드 정리 중 특정 capability 문서의 `entrypoints`에 등록되어
  있던 코드를 삭제하거나 다른 위치로 이동했기 때문입니다. `RULE-code-entrypoints`는 유효하지 않은 경로를 선언하고 있는 모든 문서를 즉시
  감지합니다. 해당 코드를 복원하거나, 문서의 엔트리포인트 선언을 이동된 새 코드 경로로 갱신하거나, 불필요한 선언을 제거한 뒤 다시 커밋하십시오.
  코드 경로 추적성 계약에 대한 자세한 내용은
  [`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)에
  정의되어 있습니다([추적성](../areas/traceability.md) 영역 참고).
- **`reconcile.md` 관련 오류로 커밋이 거부되는 경우:** 이번 커밋에서 실제로 수정하지 않은 문서를 `modified` 대상으로 지정한 채 reconcile
  기록을 `resolved` 상태로 표시했기 때문입니다. Living Spec 문서의 실제 수정 내용을 해당 reconcile 기록과 반드시 함께 스테이징하여 커밋하십시오.
- **커밋 게이트가 `GATE_RULES_FAILED` 에러로 커밋을 거부하는 경우:** `[DETAIL]` 라인마다 위반된 규칙, 파일 경로, 줄 번호가 상세히 출력되며,
  자동 수정이 가능한 경우 `fix:` 힌트가 함께 제공됩니다. 만약 `RULES_RUN_FAILED`가 발생했다면 규칙 검사 엔진 자체가 정상 실행되지 못했음을
  의미합니다 (예: 새로운 작업 워크트리 환경에 관리 파일인 규칙 파일들이 아직 배포되지 않은 상태이며, 이 경우 `devkit sync`를 먼저 실행해야 합니다).
  커밋 게이트 메커니즘은
  [`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/gate/CAP-GATE-commit-gates.md) (영어 원문)
  ([커밋 게이트](../areas/gate.md) 영역 참고)에 정의되어 있습니다.

## 기대 효과 및 완료 상태

지정된 대상 파일과 커밋된 트리 전체가 모든 문서 규칙과 수명 주기 규칙을 완벽히 통과하며, 문서 간 링크와 생명주기 상태는 각 파일 고유의 서식
스타일에 맞추어 단정하게 정리됩니다. 이미 완료된 스펙 번들은 안전하게 보존됩니다. 규칙 검사에서 거부된 커밋은 Git 이력에 아예 생성되지
않으므로, 불완전하게 검증된 변경 사항이 저장소에 섞여 들어갈 위험이 사전에 완벽히 차단됩니다.
