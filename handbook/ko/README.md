---
sources:
  ARCH-01-introduction-and-goals: null
  ARCH-03-context: null
  ARCH-05-1-containers: null
  CAP-DIST-content-packages: null
  CAP-DLV-release-handbook: null
title: devkit 핸드북
translated_from: en/README.md@4ce38c78b6c2318e
---

# devkit 핸드북

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

devkit은 AI 코딩 에이전트(Codex, Claude Code, Antigravity)가 주도적으로 개발 작업을 수행하는 저장소를 위한 개발자 도구 모음입니다.
저장소 내 모든 에이전트에게 동일한 지침, 동일한 결정적(deterministic) 검사, 일관된 전달 절차를 제공하며, 에이전트가 임의로 추측하지 않고 즉시 조치할 수 있는 명확한 형태로 응답합니다.

이 핸드북은 devkit을 구축하고 일상적으로 활용하는 개발자를 위해 작성되었습니다. `docs/` 아래의 Living Spec을 기반으로 생성된 릴리스 스냅샷이며, 형식적인 명세 단위가 아니라 개발자가 달성하려는 작업 목적을 중심으로 재구성했습니다. 각 페이지는 기반이 된 원본 명세 문서로 연결되며, 핸드북 내용과 Living Spec이 서로 다를 때는 항상 Living Spec이 우선합니다(`CAP-DLV-release-handbook`).

## devkit이 제공하는 것

devkit은 단일 CLI 명령인 `devkit`으로 제공되며, 동일한 버전으로 함께 릴리스되는 Python 휠 패키지로 배포됩니다
([`ARCH-05-1-containers`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-05-1-containers.md) (영어 원문)):

- **배포**(`devkit-dist`): 에이전트 자산을 번들 단위로 패키징하고, 프로젝트에서 선택한 번들을 `devkit sync`로 배포합니다. 스킬과 서브에이전트를 각 에이전트의 네이티브 디렉터리에 프로젝션하며, 필요한 시점에 지침 컨텍스트를 로드합니다. 공유 에이전트 자산만 필요한 저장소라면 이 패키지만 단독으로 설치하면 됩니다.
- **하네스**(`devkit-agt`): 저장소 거버넌스 규칙(`devkit rules`), 데이터 기반 전달 워크플로(`devkit workflow`), 커밋 게이트(`devkit gate`), 작업 워크트리(`devkit worktree`), 추적 관리되는 기계 생성 파일, 사람의 승인을 거치는 통합(`devkit integration`), 출력이 제한된 컴팩트 명령 실행(`devkit run`)을 제공합니다.
- **스펙 주도 전달**(`devkit-spec`): Living Spec 문서 모델, 제안 및 스펙 번들(`devkit spec`), 스킬과 역할 계약을 담은 `spec` 번들, 그리고 문서의 일관성을 검증하는 규칙을 제공합니다.
- **다른 저장소용 라이브러리**: `devkit-advisory`(Python 표준 라이브러리만 사용하는 독립적인 `devkit.advisory` 에이전트 어드바이저리 프로토콜)와 `devkit-cli`(click 기반 CLI 도구를 위한 에이전트 우선 출력 계약)를 제공합니다.
- **선택 구성 요소**: `devkit-mcp`(선택적 MCP 런타임), `devkit-viewer`(로컬 읽기 전용 저장소 뷰어), `devkit-catalog`(옵트인 번들 카탈로그), 그리고 고밀도(dense) 및 하이브리드 문서 검색을 위한 `search` extra를 지원합니다.

이러한 구성 요소들이 추구하는 설계 목표인 결정적 결과, 트랜잭션 방식의 동기화, 엄격한 계층 분리, POSIX 전용 동작 원칙은
[`ARCH-01-introduction-and-goals`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-01-introduction-and-goals.md) (영어 원문)에
정리되어 있습니다.

## 전체 모델

devkit은 세 주체(사용자, 에이전트, 저장소) 사이에서 동작합니다
([`ARCH-03-context`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-03-context.md) (영어 원문)):

- **사용자**는 `.devkit/config.toml`에서 프로젝트 정책을 구성하고, 에이전트의 제안을 검토 및 확정하며, 최종 통합 승인처럼 devkit이 사람의 몫으로 남겨둔 중요 결정을 내립니다.
- **에이전트**는 `devkit` 명령을 실행하고, stdout의 한 줄짜리 `[KIND: ...]` 결과 센티널과 stderr의 에이전트 어드바이저리를 읽으며, 워크플로 엔진이 안내하는 단계에 따라 작업을 진행합니다.
- **Git과 로컬 워크스페이스**는 영속적으로 보존되어야 하는 모든 데이터를 관리합니다. 배포된 자산과 설치 기록(receipt), Living Spec, 작업 유닛(Unit), 엔벨로프(envelope), 훅, 작업 워크트리가 여기에 보관됩니다. devkit은 자체 백그라운드 데몬을 실행하지 않으며, LLM API를 직접 호출하지도 않습니다.

실제 작업 흐름은 다음과 같습니다. 먼저 `devkit sync`가 에이전트 지침을 배포하면, 에이전트는 `devkit get-context <bundle>`을 통해 필요한 지침을 확인합니다. 개발 요청은 유형별로 분류되어 하나의 워크플로에 연결되고, 에이전트는 `devkit workflow next` 안내에 맞춰 단계별로 작업을 진행하며 리뷰나 질문을 엔벨로프에 기록합니다. 거버넌스 규칙과 커밋 게이트가 저장소의 일관성을 상시 유지하고, 완료된 작업은 사람이 검토 후 승인하면 `devkit integration`을 통해 기준 브랜치에 안전하게 통합됩니다. 각 구성 요소와 상호작용 방식은 [개념](concepts.md)에서 자세히 다룹니다.

## 시작하기

1. 핸드북 전반에서 사용되는 핵심 개념과 어휘를 파악하려면 [개념](concepts.md)을 먼저 살펴보십시오.
2. devkit을 설치합니다. 에이전트에게 설치 가이드를 제공해 계획을 세우게 하거나, 릴리스 휠을 직접 설치한 뒤 `uv run devkit sync`를 실행하십시오
   (어떤 휠이 어떤 번들을 포함하는지는
   [`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)에
   자세히 설명되어 있습니다).
3. 저장소에 이미 기존 코드와 문서가 있다면 [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)를 참고하고, 그렇지 않다면 아래의 여정 목록에서 원하는 작업을 선택하십시오.

<a id="journeys"></a>

## 여정

방향 잡기:
- [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)
- [알맞은 문서 찾기](journeys/find-the-right-documents.md)

작업 전달:
- [개발 요청 라우팅하기](journeys/route-development-intent.md)
- [제안 숙성 후 넘기기](journeys/incubate-and-hand-off-a-proposal.md)
- [개발부터 통합까지 진행하기](journeys/drive-development-to-integration.md)
- [전달 문제와 예외 처리하기](journeys/handle-delivery-problems-and-exceptions.md)
- [병렬 작업 안전하게 실행하기](journeys/run-parallel-work-safely.md)
- [오래된 활동 브랜치 정리하기](journeys/resolve-stale-activity-branches.md)

Living Spec 건강하게 유지하기:
- [Living Spec 일관성 유지하기](journeys/keep-the-living-spec-consistent.md)
- [Living Spec 드리프트 조정하기](journeys/reconcile-living-spec-drift.md)
- [누적된 군더더기 검토와 리팩터링](journeys/review-and-refactor-accumulated-slop.md)

진행 상황 보고:
- [주간 저장소 진행 상황 점검하기](journeys/inspect-weekly-repository-progress.md)
- [주간 보고서 게시하기](journeys/publish-a-weekly-report.md)

<a id="areas"></a>

## 영역

| 영역 | 다루는 내용 |
| --- | --- |
| [advisory](areas/advisory.md) | 코드와 지시문을 갖춘 구조화된 오류, 경고, 알림 |
| [cli](areas/cli.md) | click 도구를 위한 에이전트 우선 출력 계약 |
| [collaboration](areas/collaboration.md) | 공유 보고서 아티팩트와 작업 범위 레지스트리 |
| [compact](areas/compact.md) | 전체 로그는 디스크에 남기는 길이 제한 명령 출력 |
| [delivery](areas/delivery.md) | 워크플로, 제안, 스펙 번들, 엔벨로프, 정책, 보고서 |
| [distribution](areas/distribution.md) | 번들, 동기화, 설치 기록, 프로젝션, 컨텍스트, 플레이북 |
| [documents](areas/documents.md) | 문서 모델, 조회, 검색, 네임스페이스 |
| [gate](areas/gate.md) | 커밋 훅과 계층형 게이트 정책 |
| [generated](areas/generated.md) | 추적되는 기계 생성 파일 |
| [governance](areas/governance.md) | 규칙 엔진, 규칙 작성, 스펙 규칙 |
| [harness](areas/harness.md) | `devkit spec` 명령 마운트와 에이전트 지침 |
| [host](areas/host.md) | 호스트 수명 주기 훅과 프로젝트 MCP 등록 |
| [integration](areas/integration.md) | 커밋된 작업의 준비와 통합 |
| [mcp](areas/mcp.md) | 선택형 MCP 런타임 |
| [search](areas/search.md) | 어휘, 밀집, 하이브리드 순위 매기기 |
| [traceability](areas/traceability.md) | 역량과 유스케이스의 코드 진입점 |
| [viewer](areas/viewer.md) | 로컬 읽기 전용 저장소 뷰어 |
| [worktree](areas/worktree.md) | 활동 브랜치와 작업 워크트리 |

## 참고 페이지

[결정](decisions.md)에서는 정식 채택된 아키텍처 결정을, [변경 사항](changes.md)에서는 이번 스냅샷의 새로운 변경점을,
[용어집](glossary.md)에서는 devkit 전반에서 널리 쓰이는 핵심 도메인 용어를 확인할 수 있습니다.
