---
sources:
  CAP-GOV-spec-rules: null
  CAP-HARN-agent-guidance: null
  CAP-HARN-command-mount: null
  UC-adopt-in-an-existing-repository: null
title: 기존 저장소에 devkit 도입하기
translated_from: en/journeys/adopt-in-an-existing-repository.md@67c0dd2b17682b6d
---

# 기존 저장소에 devkit 도입하기

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
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

코드와 `docs/` 아래의 Markdown, 어쩌면 자체 에이전트 지침까지 갖춘 저장소가 있다고 합시다. 기존 레거시 문서를
먼저 모두 고쳐 쓰지 않고도, 오늘부터 새 작업은 스펙 기반 전달(spec-driven delivery)을 따르게 하고 싶습니다. 이
여정은 설치부터 `devkit rules check` 통과까지 안내하고, 레거시 콘텐츠는 작업이 닿을 때마다 옮기도록 남겨 둡니다.

이 페이지의 바탕이 되는 유스케이스는
[`UC-adopt-in-an-existing-repository`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/harness/UC-adopt-in-an-existing-repository.md) (영어 원문)입니다.
번들, 동기화(sync), Living Spec 같은 용어는 [개념](../concepts.md)을 참고하십시오.

## 시작하기 전에

- 저장소는 `uv`로 관리됩니다.
- 현재 상태가 커밋되어 있습니다. 격리 단계에서 파일을 옮기므로, 깨끗한 커밋이 되돌릴 지점이 됩니다.

## 1. 패키지 설치와 동기화

```bash
uv add --dev devkit devkit-spec
uv run devkit sync
```

devkit-spec에는 자체 실행 파일이 없습니다. 엔트리 포인트로 `spec` 번들과 `devkit spec` 명령 그룹을 등록하므로,
모든 명령은 프로젝트 환경의 단일 `devkit` 실행 파일을 거쳐 실행됩니다
([`CAP-HARN-command-mount`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-command-mount.md) (영어 원문)).

이어서 `devkit sync`는 세 가지 일을 합니다
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)).

- 번들의 `core` 프리셋(preset)을 `.devkit/managed/spec/`에 복사합니다.
- 스킬과 역할 계약을 각 에이전트 호스트의 디렉터리에 프로젝션(projection)합니다.
- 루트 `AGENTS.md`의 관리 블록에 지침 포인터 한 줄을 추가합니다.

`docs/`나 `specs/` 아래에는 아무것도 쓰지 않습니다. 기존 문서는 그대로 남습니다.

## 2. 명령이 응답하는지 확인

```bash
uv run devkit spec --version
```

`[VERSION: devkit-spec <version>]`이 출력됩니다. `devkit --version`은 spec 패키지가 아니라 devkit 자체의 버전을
보고한다는 점에 유의하십시오.

## 3. 기준선 확인

```bash
uv run devkit rules check
```

이제 스펙 규칙이 `docs/`와 `specs/` 아래에 이미 있는 Markdown을 읽습니다. 브라운필드(brownfield) 저장소에서는
보통 위반이 보고됩니다. ADR-0001 같은 번호 기반 ID, 누락된 프론트매터, Living Spec 레이아웃과 맞지 않는 경로
등입니다. 각 결과는 규칙, 파일, 해결 방법을 담은 `[VIOLATION: ...]` 한 줄입니다. 열한 가지 규칙의 목록은
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md) (영어 원문)에
있으며, `uv run devkit rules explain <RULE-id>`로 규칙 하나의 가이드를 출력할 수 있습니다.

## 4. 에이전트에게 레거시 문서 격리 맡기기

에이전트에게 `brownfield-adoption` 플레이북을 요청하거나, 이 저장소에 devkit을 도입해 달라고 했을 때 `spec`
스킬이 내놓는 한 줄 제안을 확인하십시오. 여러분의 요청이나 확인이 에이전트가 파일을 옮길 수 있는 권한이 됩니다.

에이전트는 플레이북을 다음과 같이 따릅니다.

1. 레거시 Markdown 목록을 만들고, 길거나 성격이 섞인 묶음은 여러분과 함께 검토합니다.
2. 레거시 파일을 `docs/materials/_legacy/<original path>` 아래로 옮깁니다. 자료(material) 디렉터리는 형식이
   자유로우며 어떤 스펙 규칙도 검사하지 않습니다.
3. 저장소의 다른 곳에서 옮겨진 경로를 가리키는 참조를 갱신합니다.
4. 마이그레이션 전에 격리 작업을 하나의 커밋으로 제안하므로, 파일 이동과 내용 수정을 따로 검토할 수 있습니다.

검사를 통과시키려고 규칙을 수정하는 일은 없습니다.

## 5. 규칙 다시 실행

```bash
uv run devkit rules check
uv run devkit gate status
```

두 명령 모두 `0`으로 종료합니다. 이제부터 새 작업은 `spec` 스킬을 거치며
([개발 의도 라우팅하기](route-development-intent.md) 참고), 레거시 콘텐츠는 작업이 닿을 때마다 Living Spec으로
옮겨집니다.

## 진행 중 선택할 수 있는 옵션

- **문서 골격 생성.** `uv run devkit add spec:docs-skeleton`은 아직 없는 골격 파일만 씁니다. 예를 들어 기존
  `docs/README.md`는 바뀌지 않습니다.
- **명령은 유지하고 번들은 건너뛰기.** `.devkit/config.toml`에 `[presets] spec = false`를 설정하고
  `uv run devkit sync`를 실행합니다. 관리 파일(managed files)이나 프로젝션은 배포되지 않지만 `devkit spec`은 계속
  사용할 수 있습니다.
- **정책 검토.** `uv run devkit spec policy`는 어떤 승인 게이트(gate)가 여러분을 기다리는지 보여 줍니다. 결정한
  내용은 `.devkit/config.toml`에 기록하십시오. [Delivery](../areas/delivery.md)를 참고하십시오.

## 문제가 생겼을 때

| 보이는 상황 | 해야 할 일 |
| --- | --- |
| 어떤 도구가 그 경로에서 읽기 때문에 파일이 그 자리에 있어야 함 | 유지하기로 결정합니다. 에이전트는 이 유예를 `[rules] exclude` 같은 `.devkit/config.toml` 항목으로 기록하고, 바로 위 주석에 이유를 남깁니다. |
| 한 규칙의 부채를 영역별로 제자리에서 고치고 싶음 | 그 규칙을 `[rules.phase_overrides]`로 `hygiene` 페이즈로 옮기기로 결정합니다. 에이전트가 이유와 함께 기록합니다. |
| 옮긴 파일의 상대 링크가 깨짐 | `_legacy/`에서도 해석되도록 링크에 접두어를 붙이거나, `docs/materials/_legacy/**`를 제외하기로 결정합니다. |
| 오류 결과가 있는 파일을 건드린 커밋을 커밋 게이트(commit gate)가 거부함 | 결과를 고치거나, 파일을 격리하거나, 규칙을 낮추거나 끄기로 결정합니다. 이런 항목에는 모두 이유가 붙습니다. |

전 과정에서 보장되는 것은 다음과 같습니다. `devkit sync`는 `docs/`나 `specs/` 아래의 기존 파일을 바꾸지 않고,
통과를 위해 규칙을 수정하지 않으며, 유예는 여러분이 결정한 곳에만 존재합니다.

## 관련 페이지

- [하네스](../areas/harness.md) 영역과 [Governance](../areas/governance.md) 영역.
- Living Spec이 커지기 시작하면 [알맞은 문서 찾기](find-the-right-documents.md).
