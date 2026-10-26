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

코드와 `docs/` 디렉터리의 Markdown 문서, 어쩌면 자체 작성한 에이전트 지침까지 포함된 기존 저장소가 있습니다.
기존의 모든 레거시 문서를 당장 처음부터 다시 작성하지 않고도, 오늘 시작하는 신규 작업부터 스펙 주도 전달(spec-driven delivery)
프로세스를 적용하고자 합니다. 이 여정에서는 설치 단계부터 `devkit rules check`를 통과하는 상태까지 안내하며, 기존 레거시 문서는
향후 관련 작업을 진행할 때 점진적으로 이관하도록 남겨 둡니다.

이 페이지의 바탕이 되는 유스케이스는
[`UC-adopt-in-an-existing-repository`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/harness/UC-adopt-in-an-existing-repository.md) (영어 원문)입니다.
번들, 동기화(sync), Living Spec 같은 핵심 개념은 [개념](../concepts.md)을 참고하십시오.

## 시작하기 전에

- 저장소가 `uv`로 관리되고 있어야 합니다.
- 현재 작업 트리의 변경 사항이 모두 커밋되어 있어야 합니다. 격리 단계에서 파일을 이동하므로, 깨끗한 커밋 상태가 롤백 기준점이 됩니다.

## 1. 패키지 설치와 동기화

```bash
uv add --dev devkit devkit-spec
uv run devkit sync
```

devkit-spec은 자체 실행 파일을 따로 제공하지 않습니다. 엔트리 포인트를 통해 `spec` 번들과 `devkit spec` 명령어 그룹을 등록하므로,
모든 작업은 프로젝트 환경에 설치된 단일 `devkit` 실행 파일 하나로 실행됩니다
([`CAP-HARN-command-mount`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-command-mount.md) (영어 원문)).

이어서 `devkit sync`를 실행하면 다음 세 가지 작업이 진행됩니다
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문)):

- 번들의 `core` 프리셋을 `.devkit/managed/spec/` 디렉터리로 복사합니다.
- 스킬과 역할 계약을 지원 대상 에이전트 호스트 디렉터리로 프로젝션합니다.
- 루트 `AGENTS.md`의 관리 블록에 안내 포인터 라인을 추가합니다.

`docs/`나 `specs/` 디렉터리 아래에는 아무런 파일도 생성하거나 수정하지 않으므로, 기존 문서는 온전히 유지됩니다.

## 2. 명령어 동작 확인

```bash
uv run devkit spec --version
```

`[VERSION: devkit-spec <version>]` 형태로 출력됩니다. 참고로 `devkit --version`은 spec 패키지가 아니라 devkit 자체의 버전을
출력한다는 점에 유의하십시오.

## 3. 베이스라인 점검

```bash
uv run devkit rules check
```

이제 스펙 거버넌스 규칙이 `docs/` 및 `specs/` 디렉터리에 이미 존재하는 Markdown 문서들을 검사합니다. 기존 저장소(brownfield)에서는
대개 위반 사항이 보고됩니다. 예를 들어 ADR-0001과 같은 번호 기반 ID, 필수 프론트매터 누락, Living Spec 레이아웃 표준과 맞지 않는 경로
등이 감지됩니다. 검사 결과는 위반 규칙, 대상 파일, 해결 조치 사항을 담은 `[VIOLATION: ...]` 형태로 출력됩니다. 11가지 규칙 목록은
[`CAP-GOV-spec-rules`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md) (영어 원문)에
있으며, `uv run devkit rules explain <RULE-id>`로 개별 규칙의 가이드를 확인할 수 있습니다.

## 4. 에이전트를 통한 레거시 문서 격리

에이전트에게 `brownfield-adoption` 플레이북 실행을 요청하거나, 저장소에 devkit을 도입해 달라고 요청했을 때 `spec`
스킬이 제안하는 한 줄 제안을 수락하십시오. 사용자의 명시적 요청이나 확인이 있어야 에이전트가 파일을 이동할 수 있는 권한을 얻습니다.

에이전트는 플레이북 절차에 따라 다음을 수행합니다.

1. 기존 레거시 Markdown 목록을 취합하고, 파일이 많거나 여러 성격이 혼재된 경우 사용자와 함께 검토합니다.
2. 레거시 파일들을 `docs/materials/_legacy/<원래 경로>` 위치로 이동합니다. 자료(`materials/`) 디렉터리는 자유 형식
   디렉터리이므로 스펙 거버넌스 규칙 검사 대상에서 제외됩니다.
3. 저장소 내 다른 파일에서 이동된 경로를 참조하던 링크를 일괄 갱신합니다.
4. 본격적인 내용 이관에 앞서 파일 이동만을 별도의 단일 커밋으로 제안하므로, 파일 이동 내역과 향후 내용 수정을 명확히 분리하여 검토할 수 있습니다.

검사를 억지로 통과시키기 위해 규칙 자체를 왜곡하여 수정하는 일은 없습니다.

## 5. 규칙 재검사

```bash
uv run devkit rules check
uv run devkit gate status
```

두 명령어 모두 종료 코드 `0`을 반환합니다. 이제부터 신규 작업은 `spec` 스킬을 통해 진행하며
([개발 요청 라우팅하기](route-development-intent.md) 참고), 격리해 둔 레거시 문서는 해당 영역의 작업을 다룰 때마다 Living Spec으로
자연스럽게 이관하면 됩니다.

## 추가 선택 옵션

- **문서 기본 골격 구성:** `uv run devkit add spec:docs-skeleton` 명령어는 아직 존재하지 않는 골격 파일만 안전하게 생성합니다.
  예를 들어 기존의 `docs/README.md` 같은 파일은 덮어쓰지 않고 유지됩니다.
- **명령어만 사용하고 번들 배포 건너뛰기:** `.devkit/config.toml`에 `[presets] spec = false`를 설정하고
  `uv run devkit sync`를 실행합니다. 관리 파일이나 프로젝션 파일은 배포되지 않지만 `devkit spec` 명령어는 계속
  사용할 수 있습니다.
- **정책 검토:** `uv run devkit spec policy` 명령어로 현재 설정된 승인 게이트 목록을 확인합니다. 확정된 결정 사항은
  `.devkit/config.toml`에 기록하십시오. 자세한 내용은 [전달](../areas/delivery.md) 문서를 참고하십시오.

## 문제 해결

| 보이는 상황 | 해야 할 일 |
| --- | --- |
| 외부 도구가 특정 경로의 파일을 직접 읽어야 해서 이동할 수 없는 경우 | 해당 파일을 그대로 유지하기로 결정합니다. 에이전트는 이를 `.devkit/config.toml`의 `[rules] exclude` 등에 예외로 기록하며, 바로 윗줄 주석에 명확한 사유를 기재합니다. |
| 특정 규칙의 위반 사항을 영역별로 기존 위치에서 점진적으로 해결하고 싶은 경우 | `[rules.phase_overrides]`를 통해 해당 규칙을 `hygiene` 페이즈로 조정하기로 결정합니다. 에이전트가 사유와 함께 설정에 반영합니다. |
| 이동한 파일의 상대 경로 링크가 깨진 경우 | `_legacy/` 경로 기준으로 올바르게 참조되도록 링크에 접두사를 추가하거나, `docs/materials/_legacy/**` 경로를 규칙 검사에서 제외하도록 설정합니다. |
| 오류 수준의 위반 사항이 있는 파일을 수정한 커밋을 커밋 게이트가 거부하는 경우 | 위반 사항을 즉시 수정하거나, 해당 파일을 격리 폴더로 이동하거나, 규칙 페이즈를 완화하거나 비활성화하기로 결정합니다. 이러한 설정 변경 시에는 반드시 사유를 주석으로 명시해야 합니다. |

이 여정 전반에서 보장되는 원칙은 분명합니다. `devkit sync`는 `docs/`나 `specs/` 디렉터리의 기존 파일을 무단으로 변경하지 않으며,
검사 통과만을 목적으로 규칙 자체를 훼손하지 않고, 모든 예외와 유예 설정은 사용자가 직접 결정한 위치에만 사유와 함께 기록됩니다.

## 관련 페이지

- [하네스](../areas/harness.md) 및 [거버넌스 규칙](../areas/governance.md) 영역 문서.
- Living Spec 문서가 늘어나기 시작하면 [알맞은 문서 찾기](find-the-right-documents.md)를 참고하십시오.
