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

뷰어(viewer)는 에이전트가 `devkit spec` 명령으로 참조하는 문서들(Living Spec, 제안서, 스펙 번들, 마일스톤, 피드백)을
하나 이상의 devkit 저장소에 걸쳐 편리하게 열람할 수 있는 로컬 읽기 전용 웹 페이지입니다(`CAP-VIEW-repository-viewer`).
선택형 패키지인 `devkit-viewer`를 통해 제공되며, `devkit viewer` 명령으로 구동됩니다. 뷰어는 문서 열람을 위한 도구이며,
승인, 게이트 결정, 질문 답변 등 상태를 변경하는 작업은 여기서 수행되지 않습니다. 각 문서의 역할과 구조는 [개념](../concepts.md)을,
명령줄에서 직접 문서를 검색하는 방법은 [알맞은 문서 찾기](../journeys/find-the-right-documents.md) 여정을 참고하세요.

## 실행하기

```sh
uv run devkit viewer serve                          # 현재 위치한 devkit 프로젝트 대상 실행
uv run devkit viewer serve --repo ../a --repo ../b  # 지정한 특정 저장소들 (Git 최상위 디렉터리)
uv run devkit viewer serve --scan repos/            # .devkit/config.toml을 포함하는 모든 직계 하위 디렉터리
uv run devkit viewer serve --port 0                 # 사용 가능한 임의의 포트 (기본값: 8765)
```

실행하면 `[VIEWER: url=http://127.0.0.1:8765/ repos=3]` 한 줄이 출력되며, Ctrl-C로 중단할 때까지 포그라운드에서 서비스를
유지합니다. 백그라운드 데몬으로 실행되지 않습니다. 각 저장소는 디렉터리 이름으로 식별되므로, 등록된 디렉터리 중 이름이 중복되는 경우
실행이 거부됩니다(`VIEWER_REPO_DUPLICATE`). 또한 Git 최상위 디렉터리가 아닌 경로를 `--repo`로 지정하거나(`VIEWER_REPO_INVALID`),
서비스할 저장소가 없거나(`VIEWER_NO_REPOSITORY`), 지정한 포트가 이미 사용 중인 경우(`VIEWER_PORT_IN_USE`)에도 실행이 거부됩니다.
`-v` 옵션을 추가하면 요청마다 표준 에러(stderr)로 단일 행 요청 로그가 출력됩니다.

## 주요 화면 구성

웹 페이지에는 저장소 선택 메뉴, 현재 체크아웃된 브랜치 표시 레이블, 그리고 다음 탭들이 제공됩니다(탭 레이블은 UI에 표시되는 실제 명칭입니다).

- **Dashboard**: 마일스톤, 제안서, 피드백을 보여 줍니다. 각 섹션은 독립적으로 로드되며 Load more 버튼으로 페이징됩니다.
- **문서 읽기**: `docs/` 하위의 Living Spec을 장(chapter)별로 분류하여 보여 주며, 문서 간 링크를 ID 기반으로 연결합니다.
- **Proposals** 및 **Specs**: `docs/proposals/PROP-*/proposal.md` 파일과 `specs/` 하위의 스펙 번들 목록을 파일 구성, 필터링 옵션,
  작업 진행 상황과 함께 제공합니다.
- **로드맵**: `docs/roadmap/` 하위의 마일스톤을 active, planned 순서로 정렬하여 표시하며, `depends_on`을 바탕으로 준비 상태를 보여
  줍니다(`done` 및 `dropped` 상태는 히스토리 토글로 확인할 수 있습니다).
- **파일 탐색**: 작업 트리의 파일들을 표시하며, Markdown, frontmatter 메타데이터, Mermaid 다이어그램을 렌더링합니다.

뷰어는 현재 체크아웃된 브랜치를 기준으로, 커밋되지 않은 파일과 추적되지 않는 파일까지 포함하여 등록된 작업 트리의 저장된 파일들을
실시간으로 보여 줍니다(`ADR-viewer-working-tree`). 브랜치를 자동으로 전환하지는 않습니다. 문서는 브라우저에서 직접 파싱되므로,
고정된 devkit-spec 버전이 서로 다른 여러 저장소도 모두 정상 렌더링되며, frontmatter 형식이 잘못된 문서는 읽을 수 없음으로 표시되면서
다른 정상 문서는 계속 열람할 수 있습니다.

### 캐시 및 최신 상태

조회 결과는 저장소 및 브랜치별로 30초 동안 캐시됩니다. 즉시 최신 상태로 갱신하려면 대시보드의 Refresh 버튼을 누르거나 브라우저
페이지를 새로고침하세요. 별도의 파일 감시(file watching) 프로세스는 동작하지 않습니다.

## Planning 단계의 제안서 오버레이

Planning을 진행 중인 제안서는 전용 `plan-<slug>` 브랜치에서 편집되므로, 베이스 체크아웃에는 이전 버전의 파일이 남아 있을 수 있습니다.
Dashboard의 제안 섹션과 Proposals 탭은 로컬 저장소 소스만을 참조하여, 다음 우선순위에 따라 Planning 버전의 제안서를 최신 내용으로
덧씌워(overlay) 표시합니다(`ADR-viewer-planning-proposal-overlay`).

1. `plan-<slug>` 브랜치를 체크아웃한 다른 워크트리 (디스크에 저장된 최신 파일)
2. 로컬의 `plan-<slug>` 브랜치
3. 마지막으로 fetch한 시점의 원격 추적 브랜치 `<remote>/plan-<slug>`

현재 작업 중인 `HEAD`에 이미 병합된 브랜치는 건너뛰며, 현재 위치한 브랜치에 대해서는 오버레이를 적용하지 않습니다. 오버레이된 카드에는
출처를 나타내는 배지가 부착됩니다. 뷰어는 백그라운드에서 fetch하거나 GitHub API를 호출하지 않으므로, 동료의 원격 Planning 브랜치
내용을 확인하려면 먼저 git fetch를 실행하세요. 오버레이 처리에 실패하면 베이스 체크아웃의 카드가 간단한 안내 문구와 함께 유지됩니다.
이러한 오버레이는 제안서에만 적용되며, 스펙, 마일스톤, 피드백, Living Spec, 파일 탐색 탭은 항상 등록된 작업 트리의 파일을 직접 읽습니다.

## 공유 제안서 리뷰 열람

`/review/<repository-id>/<generation-id>` 경로는 해당 저장소의 로컬 저장소에 보관된 특정 `proposal-review` 공유
아티팩트(shared artifact)를 표시합니다(`CAP-COLL-shared-artifacts`, [협업](collaboration.md) 참고). 페이지 상단에는 원본 커밋,
작성 언어, 만료 시점이 눈에 띄게 표시되며, Markdown 본문은 임의의 코드가 실행되지 않도록 이스케이프된 텍스트로 안전하게 렌더링됩니다.
만료된 보고서는 `410`, 존재하지 않는 보고서는 `404` 상태 코드로 응답합니다. 보고서가 만료되었거나 없는 경우 Host에게 새 보고서 게시를
요청하세요. 뷰어가 보고서를 자체적으로 재생성하지는 않습니다.

## 보안 원칙

- `127.0.0.1`에만 바인딩하며, `Host` 헤더가 해당 포트의 `127.0.0.1` 또는 `localhost`가 아닌 요청은 거부합니다
  (`VIEWER_HOST_REFUSED`). 이를 통해 외부 웹페이지를 통한 DNS 리바인딩 공격을 원천 차단합니다. CORS 헤더는 일체 전송하지 않습니다.
- `GET` 요청에만 응답하며, 파일 쓰기나 커밋, fetch 등의 변경 작업을 절대 수행하지 않습니다.
- 경로에 `..`, `.git` 세그먼트, 역슬래시(`\`), 또는 시작 부분의 `/`가 포함된 요청은 즉시 거부하며, 심볼릭 링크 파일은 목록에
  표시하거나 읽지 않습니다.
- 렌더링되는 Markdown 및 SVG 콘텐츠는 DOMPurify를 통해 안전하게 정제됩니다.

## 뷰어 수정 및 빌드

`packages/devkit-viewer/frontend/` 디렉터리의 프런트엔드는 하나의 Svelte 소스로부터 다음 두 가지 결과물을 빌드합니다.

- 웹 페이지: `src/devkit_viewer/static/` 경로로 빌드되며, 추적 대상 생성 아티팩트인 `viewer-assets`로 커밋됩니다
  (`CAP-GEN-tracked-artifacts`). 따라서 일반적인 devkit 사용 및 설치 시에는 Node.js가 필요하지 않으며, 뷰어 프런트엔드 코드를
  수정할 때만 Node.js가 필요합니다. 코드를 수정한 후에는 `just viewer lint`, `just viewer check`, `just viewer test`,
  `just viewer build`를 차례로 실행하고, `devkit generated check viewer-assets` 명령으로 커밋된 빌드 산출물의 정합성을 확인합니다.
- 컴포넌트 라이브러리 `devkit-viewer`: autohub가 벤더링하여 사용하는 tarball 아카이브 형태로 패키징됩니다. 호스트 애플리케이션은 자체
  `RepositoryDataSource`를 구현하여 연동하고 인증 처리를 자체적으로 담당합니다. 공개 패키지 레지스트리에 별도로 배포되지는 않습니다.

## 출처

- [CAP-VIEW-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/viewer/CAP-VIEW-repository-viewer.md) (영어 원문):
  서비스, 엔드포인트, Planning 출처, 페이지 동작, 로드맵, 라이브러리와 리뷰 페이지.
- [Viewer quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/viewer.md).
- [ADR-viewer-working-tree](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261024-viewer-working-tree.md),
  [ADR-viewer-planning-proposal-overlay](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261026-viewer-planning-proposal-overlay.md).
