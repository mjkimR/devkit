---
sources:
  ADR-viewer-planning-proposal-overlay: null
  ADR-viewer-working-tree: null
  CAP-COLL-shared-artifacts: null
  CAP-GEN-tracked-artifacts: null
  CAP-VIEW-repository-viewer: null
title: 뷰어
translated_from: en/areas/viewer.md@619b64f9c2a1c06b
---

# 뷰어

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
- [워크트리](worktree.md)
- [결정](../decisions.md)
- [변경 사항](../changes.md)
- [용어집](../glossary.md)
<!-- /handbook:generated -->

뷰어(viewer)는 에이전트가 `devkit spec`으로 읽는 문서, 즉 Living Spec, 제안, 스펙 번들, 마일스톤, 피드백을 하나 이상의
devkit 저장소에 걸쳐 보여 주는 로컬 읽기 전용 웹 페이지입니다(`CAP-VIEW-repository-viewer`). 선택형 `devkit-viewer`
패키지로 배포되며 `devkit viewer` 명령을 붙입니다. 보기 위한 곳이지 행동하는 곳이 아닙니다. 승인, 게이트 결정, 답변은
이곳에 기록되지 않습니다. 이 문서들이 무엇인지는 [개념](../concepts.md)을, 대신 명령줄에서 문서를 찾으려면
[알맞은 문서 찾기](../journeys/find-the-right-documents.md) 여정을 참고하세요.

## 시작하기

```sh
uv run devkit viewer serve                          # the devkit project you are in
uv run devkit viewer serve --repo ../a --repo ../b  # specific repositories (Git top levels)
uv run devkit viewer serve --scan repos/            # every direct child holding .devkit/config.toml
uv run devkit viewer serve --port 0                 # any free port (default 8765)
```

`[VIEWER: url=http://127.0.0.1:8765/ repos=3]` 한 줄을 출력하고, Ctrl-C로 멈출 때까지 포그라운드에서 서비스합니다.
데몬이 아닙니다. 각 저장소는 디렉터리 이름으로 식별되므로, 같은 이름의 디렉터리 두 개를 등록하면 거부됩니다
(`VIEWER_REPO_DUPLICATE`). Git 최상위가 아닌 `--repo`(`VIEWER_REPO_INVALID`), 서비스할 것이 없는 경우
(`VIEWER_NO_REPOSITORY`), 사용 중인 포트(`VIEWER_PORT_IN_USE`)도 거부됩니다. `-v`를 추가하면 요청마다 stderr에 요청
로그 한 줄이 출력됩니다.

## 보이는 것

페이지에는 저장소 선택기, 체크아웃된 브랜치 레이블, 그리고 다음 탭들이 있습니다(레이블은 UI에 표시되는 그대로입니다).

- **Dashboard**: 마일스톤, 제안, 피드백. 각 섹션은 따로 불러오며 Load more로 페이지를 넘깁니다.
- **문서 읽기**: `docs/` 아래의 Living Spec을 장별로 묶어 보여 주며, 문서 사이를 ID로 연결합니다.
- **Proposals**와 **Specs**: `docs/proposals/PROP-*/proposal.md`와 `specs/` 아래의 번들을 그 파일, 필터, 작업 진행
  상황과 함께 보여 줍니다.
- **로드맵**: `docs/roadmap/` 아래의 마일스톤을 active, planned 순으로 정렬하고 `depends_on`에서 준비 상태를 보여
  줍니다(`done`과 `dropped`는 기록 토글로 나타납니다).
- **파일 탐색**: 작업 트리를 보여 주며 Markdown, frontmatter, Mermaid를 렌더링합니다.

뷰어는 등록된 작업 트리에 저장된 파일을, 커밋되지 않은 파일과 추적되지 않는 파일까지 포함해 현재 체크아웃된 브랜치에서
보여 줍니다(`ADR-viewer-working-tree`). 브랜치를 바꾸는 일은 없습니다. 문서는 브라우저에서 파싱되므로 서로 다른
devkit-spec 버전을 고정한 저장소도 모두 렌더링되며, frontmatter가 잘못된 문서는 읽을 수 없음으로 표시되고 나머지는
그대로 보입니다.

### 최신 상태

결과는 저장소와 브랜치별로 30초 동안 캐시됩니다. 즉시 다시 불러오려면 대시보드의 Refresh 버튼을 쓰거나 브라우저
페이지를 새로 고치세요. 파일 감시는 없습니다.

## 아직 Planning 중인 제안

Planning 중인 제안은 자신의 `plan-<slug>` 브랜치에서 편집되므로, 베이스 체크아웃에는 이전 사본이 있을 수 있습니다.
Dashboard의 제안 섹션과 Proposals 탭은 로컬 출처에서만 읽은 Planning 버전을 다음 순서로 덧씌웁니다
(`ADR-viewer-planning-proposal-overlay`).

1. `plan-<slug>`를 체크아웃한 다른 워크트리(그 워크트리에 저장된 파일)
2. 로컬 브랜치 `plan-<slug>`
3. 마지막으로 fetch한 시점 기준의 원격 추적 브랜치 `<remote>/plan-<slug>`

이미 `HEAD`에 병합된 브랜치는 건너뛰며, 현재 있는 브랜치에 대해서는 아무것도 보여 주지 않습니다. 덧씌워진 카드에는 출처
배지가 붙습니다. 뷰어는 fetch하거나 GitHub를 호출하지 않으므로, 동료의 원격 Planning 브랜치를 보려면 먼저 fetch하세요.
덧씌우기가 실패하면 체크아웃의 카드가 짧은 안내와 함께 그대로 남습니다. 덧씌우기는 제안에만 적용됩니다. 스펙,
마일스톤, 피드백, Living Spec, 파일 탐색은 항상 등록된 작업 트리를 읽습니다.

## 공유된 제안 리뷰 읽기

`/review/<repository-id>/<generation-id>`는 해당 저장소의 로컬 저장소에 있는 정확히 하나의 `proposal-review` 공유
아티팩트(shared artifact)를 보여 줍니다(`CAP-COLL-shared-artifacts`, [협업](collaboration.md) 참고). 페이지는 그
출처 커밋, 언어, 만료 시점을 눈에 띄게 보여 주며, Markdown을 이스케이프된 텍스트로 표시하므로 그 안의 어떤 것도 실행될
수 없습니다. 만료된 보고서는 `410`, 없는 보고서는 `404`로 응답합니다. Host에게 새 보고서를 게시해 달라고 요청하세요.
뷰어는 보고서를 다시 생성하지 않습니다.

## 안전

- `127.0.0.1`에만 바인딩하며, `Host` 헤더가 해당 포트의 `127.0.0.1`이나 `localhost`가 아닌 요청은 거부합니다
  (`VIEWER_HOST_REFUSED`). 이로써 DNS 리바인딩 페이지가 차단됩니다. CORS 헤더는 보내지 않습니다.
- `GET`에만 응답하며, 쓰기, 커밋, fetch를 결코 하지 않습니다.
- `..`, `.git` 세그먼트, 백슬래시, 맨 앞의 `/`가 있는 경로는 거부되며, 심볼릭 링크는 나열하지도 읽지도 않습니다.
- 렌더링된 Markdown과 SVG는 DOMPurify를 거칩니다.

## 뷰어 수정하기

`packages/devkit-viewer/frontend/` 아래의 프런트엔드는 하나의 Svelte 소스에서 두 가지 결과물을 만듭니다.

- 페이지: `src/devkit_viewer/static/`에 빌드되며, 추적되는 생성 아티팩트 `viewer-assets`로 커밋됩니다
  (`CAP-GEN-tracked-artifacts`). 따라서 devkit을 설치할 때는 Node가 필요 없고, 프런트엔드를 바꿀 때만 필요합니다.
  바꾼 뒤에는 `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`를 실행하고,
  `devkit generated check viewer-assets`로 커밋된 빌드를 확인합니다.
- 컴포넌트 라이브러리 `devkit-viewer`: autohub가 벤더링하는 tarball로 묶입니다. 호스트는 자체
  `RepositoryDataSource`를 제공하고 인증은 자기 쪽에서 처리합니다. 레지스트리에 게시되는 것은 없습니다.

## 출처

- [CAP-VIEW-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/viewer/CAP-VIEW-repository-viewer.md) (영어 원문):
  서비스, 엔드포인트, Planning 출처, 페이지 동작, 로드맵, 라이브러리와 리뷰 페이지.
- [Viewer quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/viewer.md).
- [ADR-viewer-working-tree](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261024-viewer-working-tree.md),
  [ADR-viewer-planning-proposal-overlay](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261026-viewer-planning-proposal-overlay.md).
