---
sources:
  CAP-DOCS-document-model: null
  CAP-GATE-commit-gates: null
  CAP-GOV-spec-rules: null
  CAP-TRACE-code-entrypoints: null
  UC-keep-the-living-spec-consistent: null
title: Living Spec 일관성 유지하기
translated_from: en/journeys/keep-the-living-spec-consistent.md@cac4759bde05e33d
---

# Living Spec 일관성 유지하기

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
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

`docs/` 아래의 Living Spec은 이후의 에이전트가 모든 것을 다시 읽지 않고도 믿을 수 있을 때에만 쓸모가 있습니다.
이 여정은 여러분(또는 에이전트)이 문서와 코드를 바꾸는 동안 devkit이 Living Spec의 구조적 건전성을 어떻게 지키는지
보여 줍니다. 깨진 참조, 한쪽에만 있는 링크, 잘못된 위치의 파일, 오래된 스펙 상태, 반영되지 않은 변경, 존재하지 않는
코드 진입점(entrypoint)은 각각 안정적인 규칙 ID와 함께 보고되며, 수정 방법이 명확한 경우에는 자동으로 고쳐집니다.

문서가 *올바른* 내용을 말하는지는 별개의 문제이며, [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)에서
다룹니다. 여기서 쓰는 용어(Living Spec, 규칙, 커밋 게이트(commit gate))는 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-keep-the-living-spec-consistent`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-keep-the-living-spec-consistent.md) (영어 원문).

## 시작하기 전에

- 프로젝트가 `spec` 번들을 선택했고, `devkit sync`가 그 규칙을 배포했습니다(규칙은 `core` 프리셋(preset)에 포함됩니다).
- 이 규칙들은 일반적인 devkit 규칙이므로 `.devkit/config.toml`의 `[rules]`에서 다루는 페이즈, 심각도, 조정에 관한
  내용이 모두 그대로 적용됩니다. [거버넌스 영역](../areas/governance.md)을 참고하십시오.

## 단계별 진행

1. **변경한 내용을 검사합니다.** 작업 공간 전체나 수정한 파일에 대해 스펙 규칙을 실행합니다.

   ```sh
   uv run devkit rules check                      # whole workspace
   uv run devkit rules check docs/usecases/x.md   # only these targets
   ```

   각 위반은 규칙(예: `RULE-traceability-link`), 그 위반이 `fixable`인지 `open`인지, 그리고 해야 할 조치를 알려
   줍니다. 위반은 실행 대상 파일에서만 보고되며, 완료된 스펙 번들은 이력으로 취급되어 이름을 직접 지정할 때에만
   검사됩니다.

2. **결정론적 수정을 적용합니다.**

   ```sh
   uv run devkit rules fix --dry-run   # preview
   uv run devkit rules fix
   ```

   수정은 대상이 된 현재 파일만, 그리고 그 수정이 소유한 바이트만 파일 고유의 스타일로 다시 씁니다. 파일을
   옮기거나 이름을 바꾸지 않고, 빠진 ID를 추측하지 않으며, 완료된 번들을 다시 쓰지 않습니다.

3. **다시 검사합니다.** `devkit rules check`를 다시 실행하면 아무것도 보고되지 않아야 합니다.

4. **커밋합니다.** 내장된 `rules-check` 게이트가 스테이징된 트리 그대로(`devkit rules check --staged`와 같은 방식)를
   평가하고 커밋을 받아들입니다. 스테이징되지 않은 수정은 판정에 영향을 주지 못합니다.

5. **풀 리퀘스트를 엽니다.** CI는 `devkit rules check --ci --base <ref>`를 실행해 브랜치 전체를 머지 베이스와 같은
   방식으로 비교해 판정합니다.

규칙이 무엇을 검사하고 직접 어떻게 고치는지 알고 싶다면 `uv run devkit rules explain <RULE-id>`를 실행하십시오.

## 규칙이 찾아내는 것

11개의 규칙은
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md) (영어 원문)에
정리되어 있습니다. 가장 자주 만나는 규칙은 다음과 같습니다.

| 규칙 | 보고되는 경우 | 수정 |
| --- | --- | --- |
| `RULE-document-reference` | ID가 해석되지 않거나, 참조가 대괄호 형식 또는 별칭(alias)을 사용함 | 일부 자동 수정 |
| `RULE-id-convention` | 파일 경로, `id`, `area`, 제목 토큰이 서로 맞지 않음 | 경로가 올바르면 자동 수정 |
| `RULE-traceability-link` | 유스케이스가 나열한 capability가 그 유스케이스를 역으로 나열하지 않음 | 역방향 ID 추가 |
| `RULE-spec-lifecycle` | `spec.md`, `tasks.md`, `reconcile.md`의 상태가 서로 다름 | `status: completed` 설정 |
| `RULE-reconcile-contract` | `resolved` 기록이 diff에서 바뀌지 않은 `modified` 대상을 주장함 | 직접 수정 |
| `RULE-code-entrypoints` | `entrypoints` 경로가 더 이상 존재하지 않음 | 직접 수정 |

문서가 ID를 얻는 방법과 참조가 해석되는 방식은 문서 모델인
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)이
정의합니다([문서 영역](../areas/documents.md) 참고).

## 문제가 생겼을 때

- **실행이 `SPEC_CONFIG_INVALID`(종료 코드 `2`)로 실패합니다.** `.devkit/config.toml`의 `[tool.spec]` 테이블이
  잘못되었습니다. 예를 들어 알 수 없는 키가 있는 경우입니다. 이는 위반이 아닙니다. 어떤 문서가 어떤 규약을
  따르는지 규칙이 알 수 없으므로 아무것도 판정하지 않습니다. 테이블을 고친 뒤 다시 실행하십시오.
- **`fix` 이후에도 위반이 `open`으로 남습니다.** 결정론적인 수정 방법이 없는 경우입니다. 어떤 문서도 선언하지 않은
  ID에 대한 참조, 존재하지 않는 진입점, 누락된 reconcile 증거 등이 그렇습니다. 수정은 의도적으로 이를 그대로
  둡니다. 안내된 조치를 직접 수행한 뒤 다시 검사하십시오.
- **건드리지 않은 capability 때문에 커밋이 거부됩니다.** 어떤 capability가 `entrypoints`에 선언한 코드를 삭제하거나
  옮겼기 때문이며, `RULE-code-entrypoints`는 삭제된 경로를 선언한 모든 문서를 보고합니다. 코드를 복원하거나,
  선언이 옮겨진 코드를 가리키도록 하거나, 선언을 제거한 뒤 다시 커밋하십시오. 경로 계약은
  [`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md) (영어 원문)입니다
  ([추적성 영역](../areas/traceability.md) 참고).
- **`reconcile.md` 때문에 커밋이 거부됩니다.** 이 커밋이 바꾸지 않는 `modified` 대상을 둔 채 기록을 `resolved`로
  표시했기 때문입니다. Living Spec 수정을 기록과 함께 스테이징하십시오.
- **게이트가 `GATE_RULES_FAILED`로 거부합니다.** 각 `[DETAIL]` 줄이 규칙, 파일, 줄 번호를 알려 주며, 규칙에
  수정 방법이 있으면 `fix:` 힌트도 함께 나옵니다. 반면 `RULES_RUN_FAILED`는 실행이 커밋을 전혀 판정하지 못했다는
  뜻입니다(예: 새 워크트리에 관리 파일(managed files)인 규칙 파일이 없는 경우이며, `devkit sync`를 실행하면 됩니다).
  게이트 동작은
  [`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md)
  ([게이트 영역](../areas/gate.md) 참고)에 정의되어 있습니다.

## 결과

대상 파일과 커밋된 트리가 모든 스펙 규칙을 통과하고, 링크와 상태는 각 파일 고유의 스타일로 작성되며, 완료된
번들은 손대지 않은 상태로 남습니다. 거부된 커밋은 커밋을 만들지 않으므로, 절반만 검사된 내용이 반영되는 일은
없습니다.
