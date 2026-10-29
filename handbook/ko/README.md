---
sources:
  ARCH-01-introduction-and-goals: null
  ARCH-03-context: null
  ARCH-05-1-containers: null
  CAP-DIST-content-packages: null
  CAP-DIST-sync-and-transactions: null
  CAP-DLV-idea-incubation: null
  CAP-DLV-incubation-sdd-baseline: null
  CAP-DLV-release-handbook: null
title: devkit 핸드북
translated_from: en/README.md@d634c3ad9ce32a16
---

# devkit 핸드북

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

devkit은 AI 코딩 에이전트(Codex, Claude Code, Antigravity)가 주도적으로 개발 작업을 수행하는 저장소를 위한 개발자 도구 모음입니다.
저장소 내 모든 에이전트에게 동일한 지침, 동일한 결정적(deterministic) 검사, 일관된 전달 절차를 제공하며, 에이전트가 임의로 추측하지 않고 즉시 조치할 수 있는 명확한 형태로 응답합니다.

이 핸드북은 devkit을 구축하고 일상적으로 활용하는 개발자를 위해 작성되었습니다. `docs/` 아래의 Living Spec을 기반으로 생성된 릴리스 스냅샷이며, 형식적인 명세 단위가 아니라 개발자가 달성하려는 작업 목적을 중심으로 재구성했습니다. 각 페이지는 기반이 된 원본 명세 문서로 연결되며, 핸드북 내용과 Living Spec이 서로 다를 때는 항상 Living Spec이 우선합니다(`CAP-DLV-release-handbook`).

## devkit이 제공하는 것

devkit은 단일 CLI 명령인 `devkit`으로 제공되며, 동일한 버전으로 함께 릴리스되는 Python 휠 패키지로 배포됩니다
([`ARCH-05-1-containers`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-05-1-containers.md) (영어 원문)):

- **배포**(`devkit-dist`): 에이전트 자산을 번들 단위로 패키징하고, 프로젝트에서 선택한 번들을 `devkit sync`로 배포합니다. 스킬과 서브에이전트를 각 에이전트의 네이티브 디렉터리에 프로젝션하며, 필요한 시점에 지침 컨텍스트를 로드합니다. 공유 에이전트 자산만 필요한 저장소라면 이 패키지만 단독으로 설치하면 됩니다.
- **하네스**(`devkit-agt`): 저장소 거버넌스 규칙(`devkit rules`), 데이터 기반 전달 워크플로(`devkit workflow`), 커밋 게이트(`devkit gate`), 작업 워크트리(`devkit worktree`), 추적 관리되는 기계 생성 파일, 사람의 승인을 거치는 통합(`devkit integration`), 출력이 제한된 컴팩트 명령 실행(`devkit run`)을 제공합니다.
- **문서**(`devkit-docs`): Living Spec의 문서 모델, 문서 간 ID 해석·목록·검색·참조 추적을 담당하는 `devkit docs` 명령, 문서 규칙, 그리고 공통 형식과 작성 지침을 담은 자동 선택 `docs` 번들을 제공합니다. 특정 전달 절차에 대해서는 알지 못합니다.
- **스펙 주도 전달**(`devkit-spec`): 제안 및 스펙 번들(`devkit spec`), 전달 정책, 워커 결과 점검, 스킬·워크플로·역할 계약을 담은 `spec` 번들, 그리고 문서의 일관성을 지키는 수명 주기 규칙을 제공합니다. `devkit-docs`를 기반으로 동작합니다.
- **다른 저장소용 라이브러리**: `devkit-advisory`(Python 표준 라이브러리만 사용하는 독립적인 `devkit.advisory` 에이전트 어드바이저리 프로토콜)와 `devkit-cli`(click 기반 CLI 도구를 위한 에이전트 우선 출력 계약)를 제공합니다.
- **선택 구성 요소**: `devkit-mcp`(선택적 MCP 런타임), `devkit-viewer`(로컬 읽기 전용 저장소 뷰어), `devkit-catalog`(`incubation`, `maintenance`, `response-style` 같은 옵트인 번들 카탈로그), 그리고 고밀도(dense) 및 하이브리드 문서 검색을 위한 `search` extra를 지원합니다.

이러한 구성 요소들이 추구하는 설계 목표인 결정적 결과, 트랜잭션 방식의 동기화, 엄격한 계층 분리, POSIX 전용 동작 원칙은
[`ARCH-01-introduction-and-goals`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-01-introduction-and-goals.md) (영어 원문)에
정리되어 있습니다.

## 전체 모델

devkit은 세 주체(사용자, 에이전트, 저장소) 사이에서 동작합니다
([`ARCH-03-context`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-03-context.md) (영어 원문)):

- **사용자**는 `.devkit/config.toml`에서 프로젝트 정책을 구성하고, 에이전트의 제안을 검토 및 확정하며, 최종 통합 승인처럼 devkit이 사람의 몫으로 남겨둔 중요 결정을 내립니다.
- **에이전트**는 `devkit` 명령을 실행하고, stdout의 한 줄짜리 `[KIND: ...]` 결과 센티널과 stderr의 에이전트 어드바이저리를 읽으며, 프로젝트의 개발 방식이 정한 지침에 따라 작업을 진행합니다. SDD에서는 워크플로 엔진이 안내하는 단계를 따릅니다.
- **Git과 로컬 워크스페이스**는 영속적으로 보존되어야 하는 모든 데이터를 관리합니다. 배포된 자산과 설치 기록(receipt), Living Spec, 작업 유닛(Unit), 엔벨로프(envelope), 훅, 작업 워크트리가 여기에 보관됩니다. devkit은 자체 백그라운드 데몬을 실행하지 않으며, LLM API를 직접 호출하지도 않습니다.

### 두 가지 개발 방식

모든 프로젝트는 **개발 방식**(development approach)을 하나 공유하며, `sdd`(기본값)와 `incubation` 중에서 고릅니다. 이 선택은
`.devkit/config.toml`의 `[development] approach`에 기록됩니다. `uv run devkit config show`는 실제 적용되는 값과 그 출처를 보여 줍니다.
패키지를 설치하거나 번들을 선택해도 방식은 바뀌지 않으며, 사용자가 동의한 명시적인 수정만이 이를 바꿉니다
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)).

- **SDD**(스펙 주도 개발)는 완전한 전달 절차입니다. 먼저 `devkit sync`가 에이전트 지침을 배포하면, 에이전트는 `devkit get-context <bundle>`로 필요한 지침을 읽습니다. 개발 요청은 분류되어 하나의 워크플로에 연결되고, 에이전트는 `devkit workflow next` 안내에 맞춰 단계별로 작업하며 리뷰와 질문을 엔벨로프에 기록합니다. 거버넌스 규칙과 커밋 게이트가 저장소의 일관성을 유지하고, 완료된 작업은 사용자가 승인하면 `devkit integration`을 통해 기준 브랜치에 통합됩니다.
- **인큐베이션**(incubation)은 아직 제품의 모습을 찾아가는 아이디어를 위한 방식입니다. 옵트인 `incubation` 번들의 `/incubate` 진입점이 다음으로 유용한 제품 작업(질문, 범위가 정해진 실험, 구현, 사용 확인)을 진행하고, 이어서 작업하는 데 필요한 현재 사실만 `.devkit/incubation.md`에 남깁니다. 변경마다 스펙 번들, 엔벨로프, 승인을 만들지 않으며, 문서 검사와 프로젝트 자체 검사는 그대로 적용됩니다
  ([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md) (영어 원문)).
  작은 앱이라면 계속 인큐베이션에 머물러도 됩니다. 이후 변경을 SDD로 진행하고 싶다면 `sdd-baseline` 플레이북이 유지할 제품을 검증하고, 사용자의 결정이 있을 때만 방식을 전환합니다
  ([`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md) (영어 원문)).

각 구성 요소와 상호작용 방식은 [개념](concepts.md)에서 자세히 다룹니다.

## 시작하기

1. 핸드북 전반에서 사용되는 핵심 개념과 어휘를 파악하려면 [개념](concepts.md)을 먼저 살펴보십시오.
2. devkit을 설치합니다. 에이전트에게 설치 가이드를 제공해 계획을 세우게 하거나, 릴리스 휠을 직접 설치한 뒤 `uv run devkit sync`를 실행하십시오
   (어떤 휠이 어떤 번들을 포함하는지는
   [`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md) (영어 원문)에
   자세히 설명되어 있습니다).
3. 출발점을 고르십시오.
   - 이미 코드와 문서가 있는 저장소: [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)
   - 스펙을 쓰기 전에 먼저 탐색해 보고 싶은 새 아이디어: [아이디어 인큐베이션하기](journeys/incubate-an-idea.md), 그리고 원한다면 이후에 [인큐베이션에서 SDD 도입하기](journeys/adopt-sdd-from-incubation.md)
   - 그 밖의 경우: 아래 SDD 여정, 먼저 [개발 요청 라우팅하기](journeys/route-development-intent.md)부터

<a id="journeys"></a>

## 여정

방향 잡기:
- [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)
- [알맞은 문서 찾기](journeys/find-the-right-documents.md)

아이디어 탐색:
- [아이디어 인큐베이션하기](journeys/incubate-an-idea.md)
- [인큐베이션에서 SDD 도입하기](journeys/adopt-sdd-from-incubation.md)

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
- [선택한 느린 작업 빠르게 하기](journeys/speed-up-selected-slow-operations.md)

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
| [delivery](areas/delivery.md) | 개발 방식, 인큐베이션, 워크플로, 제안, 스펙 번들, 엔벨로프, 정책, 유지 관리 플레이북 |
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
