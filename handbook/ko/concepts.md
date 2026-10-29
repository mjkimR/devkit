---
sources:
  ADR-delivery-classification: null
  ARCH-08-1-agent-output: null
  ARCH-08-2-resource-taxonomy: null
  ARCH-08-cross-cutting: null
  CAP-ADV-agent-advisory-protocol: null
  CAP-COLL-work-scope-registry: null
  CAP-DIST-agent-projections: null
  CAP-DIST-context-and-playbooks: null
  CAP-DIST-manifest-spec: null
  CAP-DIST-sync-and-transactions: null
  CAP-DIST-workspace-ownership: null
  CAP-DLV-delivery-workflows: null
  CAP-DLV-human-interaction: null
  CAP-DLV-idea-incubation: null
  CAP-DLV-project-policy: null
  CAP-DLV-proposal-incubation: null
  CAP-DLV-spec-bundles: null
  CAP-DLV-workflow-envelopes: null
  CAP-DLV-workflow-orchestration: null
  CAP-DOCS-document-model: null
  CAP-GATE-commit-gates: null
  CAP-GOV-rules-engine: null
  CAP-HARN-agent-guidance: null
  CAP-INT-mcp-services: null
  CAP-WT-task-worktrees: null
title: 개념
translated_from: en/concepts.md@b9ef31d3b59f06a9
---

# 개념

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](README.md)
- [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](journeys/adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](journeys/handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](journeys/incubate-an-idea.md)
- [제안 숙성 후 넘기기](journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](journeys/run-parallel-work-safely.md)
- [선택한 느린 작업 빠르게 하기](journeys/speed-up-selected-slow-operations.md)
- [어드바이저리](areas/advisory.md)
- [에이전트 우선 CLI 도구 키트](areas/cli.md)
- [협업](areas/collaboration.md)
- [컴팩트 명령 출력](areas/compact.md)
- [전달](areas/delivery.md)
- [배포](areas/distribution.md)
- [문서](areas/documents.md)
- [커밋 게이트](areas/gate.md)
- [생성 파일](areas/generated.md)
- [거버넌스 규칙](areas/governance.md)
- [하네스](areas/harness.md)
- [호스트](areas/host.md)
- [통합](areas/integration.md)
- [MCP](areas/mcp.md)
- [검색](areas/search.md)
- [추적성](areas/traceability.md)
- [뷰어](areas/viewer.md)
- [워크트리](areas/worktree.md)
- [결정](decisions.md)
- [변경 사항](changes.md)
- [용어집](glossary.md)
<!-- /handbook:generated -->

이 페이지에서는 핸드북의 다른 문서들을 이해하는 데 필요한 핵심 개념을 실제 접하게 되는 순서대로 소개합니다. 먼저 지침이 에이전트에게 전달되는 방식을 살펴보고, 작업이 어떻게 구조화되고 검증되는지, 그리고 완료된 작업이 어떻게 최종 반영되는지 차례대로 알아봅니다. 각 절은 해당 개념을 정의하는 공식 계약 문서로 연결되며, 간략한 정의는 [용어집](glossary.md)에서 확인할 수 있습니다.

## 번들: 배포 단위

**devkit 번들**(bundle)은 `bundle.toml`에 선언된 이름 있는 에이전트 자산 묶음입니다. 지침 조각, 지시문(instruction), 플레이북, 규칙, 워크플로, 스킬, 서브에이전트 역할, 커밋 게이트, 호스트 훅 등이 여기에 포함됩니다. 번들은 Python 휠(콘텐츠 패키지)에 포함되어 배포되거나 프로젝트 저장소 내에 직접 둘 수 있습니다. **프리셋**(preset)은 `core`나 `default`처럼 번들 자산의 일부를 목적에 맞게 선별하여 이름을 부여한 구성 단위입니다
([`CAP-DIST-manifest-spec`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-manifest-spec.md) (영어 원문)).

휠 패키지를 설치하면 해당 번들을 사용할 수 있는 준비가 될 뿐입니다. 실제로 어떤 번들을 배포할지는 프로젝트의 `.devkit/config.toml`에서 결정합니다. 일부 번들은 패키지가 설치되면 자동으로 선택되며(`devkit`, `advisory`, `harness`, 그리고 각 패키지가 설치된 경우의 `docs`와 `spec`), 그 외의 번들은 `devkit add <bundle>`로 추가하거나 `devkit remove <bundle>`로 제외할 수 있습니다. 현재 설치되어 선택된 번들 목록은 `devkit list`로 확인합니다.

자산은 세 가지 계층으로 나뉩니다
([`ARCH-08-2-resource-taxonomy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-2-resource-taxonomy.md) (영어 원문)).
자연어 지침(`AGENTS.md` 블록, 지시문, 플레이북, 워크플로), 기계적인 실행(규칙, 스킬, 서브에이전트, 커밋 게이트, 호스트 훅), 그리고 번들과 프리셋, 프로젝트 설정으로 이루어진 패키징 계층입니다.

## 동기화, 설치 기록, 그리고 직접 수정할 수 있는 대상

`devkit sync`는 선택된 번들을 단일 트랜잭션으로 배포합니다. 모든 파일이 온전히 기록되거나, 오류 시 전체가 롤백됩니다
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)).
동기화가 생성하는 산출물은 세 가지입니다.

- **관리 파일**(managed files): `.devkit/managed/<bundle>/` 아래에 위치하는 원본 사본으로, 직접 손으로 편집해서는 안 됩니다.
- **프로젝션**(projections): 스킬과 서브에이전트 역할을 각 에이전트 도구의 고유 디렉터리에 배치한 네이티브 사본입니다.
  예를 들어 `.agents/skills/`, `.claude/skills/`, `.codex/skills/` 등이 있습니다
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md) (영어 원문)).
- **설치 기록**(receipt), `.devkit/installation.json`: 배포된 모든 파일과 체크섬, 소속 번들을 빠짐없이 기록하여 Git에 커밋하는
  파일입니다. `devkit sync --check`와 `devkit status`는 현재 워크스페이스 상태를 이 설치 기록과 대조해 검증합니다.

업스트림 자산을 프로젝트 요구사항에 맞게 변경해야 할 때는 관리 파일이나 프로젝션을 직접 수정하지 않습니다. 대신 `devkit override`를
실행하여 **프로젝트 오버라이드**(project override)를 생성해야 합니다. 오버라이드는 `.devkit/overrides/` 아래에 저장되며, 기반이 된
업스트림 버전과 함께 추적 관리되므로 업스트림에 변경이 발생하면 차이(drift)로 명확하게 드러납니다
([`CAP-DIST-workspace-ownership`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md) (영어 원문)).

## 필요할 때 불러오는 지침

에이전트 시작 파일(startup files)에 담긴 텍스트는 매 대화 턴마다 컨텍스트 토큰을 소모하므로, devkit은 지침을 상황에 맞춰 단계적으로 로드합니다
([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).

- 루트 `AGENTS.md`의 관리 블록에는 전체적인 방향을 잡기 위한 최소한의 안내만 담깁니다.
- `devkit get-context <bundle>`은 번들의 핵심 원칙(constitution), 지시문(instruction) 헤더, 그리고 번들이 선언한 디렉터리에 있는
  프로젝트 문서의 제목과 요약을 반환합니다(`spec` 번들은 `docs/steering/` 아래의 스티어링 문서를 나열합니다). 각 헤더에는 에이전트가
  어떤 조건에서 본문을 읽어야 하는지가 명시되어 있습니다.
- **플레이북**(playbook)은 비정기적으로 쓰이는 작업 절차로, 평소에는 디스크에만 보관됩니다. 에이전트는 `devkit playbook search`로 필요한 절차를 찾고
  `devkit playbook get <bundle>/<id>`로 정확한 내용을 가져오며, 사용자가 직접 호출하거나 승인했을 때만 실행합니다.
- **스킬**(skill)은 `/spec`, `/spec-next`, `/incubate`처럼 에이전트 호스트가 호출하는 진입점 명령이며, **서브에이전트**(subagent)는
  각 호스트에 프로젝션되는 역할 계약(코드 리뷰어, 조정 리뷰어, 워커 등)입니다. 대부분의 역할은 세션의 모델을 그대로 이어받으며,
  프로젝트는 `[subagents]` 테이블에서 역할별 모델 수준을 지정할 수 있습니다
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md) (영어 원문)).

## Living Spec

**Living Spec**은 `docs/` 디렉터리에 보관되는 영속적인 시스템 명세입니다. 이것이 프로젝트의 단일 진실 공급원(Single Source of Truth)이며 소스 코드와 에이전트 지침, 그리고 이
핸드북 모두가 Living Spec을 따릅니다. 각 문서는 프런트매터에 고유 ID를 가집니다
([`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)).

| 종류 | ID | 설명하는 것 |
| --- | --- | --- |
| 아키텍처(Architecture) | `ARCH-...` | 시스템 구조, 런타임 흐름, 횡단 관심사 |
| 역량(Capability) | `CAP-<AREA>-<slug>` | 영역별로 묶인, 하나의 동작에 대한 계약 |
| 유스케이스(Use case) | `UC-<slug>` | 행위자가 여러 역량을 거쳐 목표에 이르는 방법 |
| 결정(Decision) | `ADR-<slug>` | 구조적 선택을 한 이유 |
| 제안(Proposal) | `PROP-<slug>` | 스펙이 되기 전에 다듬는 중인 아이디어 |
| 마일스톤(Milestone) | `MS-<slug>` | 종료 조건이 있는 로드맵 주제 |

역량과 유스케이스는 프런트매터에서 서로를 상호 참조합니다. 현재 진행 중인 작업은 이와 분리되어 `specs/` 아래에서 관리됩니다. 스펙은
개별 변경 사항을 정의하며, 구현이 완료되면 그 변경 내용이 `docs/`의 Living Spec에 다시 반영됩니다(**조정**, reconcile).
문서 모델은 `devkit-docs` 패키지가 담당하며, `devkit docs resolve`, `devkit docs refs`, `devkit docs list`, `devkit docs search`
명령을 통해 문서 ID, 상호 참조, 종류, 의미적 검색 등으로 원하는 문서를 신속하게 찾을 수 있습니다.

## 개발 방식: SDD 또는 인큐베이션

프로젝트는 두 가지 **개발 방식**(development approach) 중 하나로 작업하며, 이는 `.devkit/config.toml`에 기록되는 공유 설정입니다.

```toml
[development]
approach = "incubation"   # absent means "sdd"
```

`uv run devkit config show`는 실제 적용되는 방식과 그 출처를 보여 주며, `uv run devkit spec policy`도 첫 줄에 같은 정보를 출력합니다.
패키지를 설치하거나 번들을 선택하거나 스킬을 호출해도 방식은 바뀌지 않으며, 체크아웃 로컬 설정으로 덮어쓸 수도 없습니다
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)).

- **SDD**는 이 페이지의 나머지 부분이 설명하는 방식입니다. 작업 분류, 유닛, 워크플로, 게이트, 엔벨로프, 조정이 모두 여기에 속합니다.
- **인큐베이션**(incubation)은 아직 제품의 모습을 찾아가는 단계에 적합합니다. 옵트인 `incubation` 번들(`devkit add incubation`,
  `devkit-spec` 불필요)이 `/incubate`를 제공하며, 이 진입점은 한 번에 하나씩 유용한 제품 작업을 진행하고
  `.devkit/incubation.md`에 **인큐베이션 현재 컨텍스트**(incubation current context)를 유지합니다. 현재 목표, 사용자가 내린 선택과
  가정의 구분, 제품을 실행하고 확인하는 방법, 실제로 관찰한 결과, 다음 작업이 여기에 담깁니다. 변경마다 스펙 번들, 엔벨로프, 승인을
  만들지 않으며, 인큐베이션이 활성화된 동안에는 `devkit spec new` 같은 SDD 수명 주기 명령이 `SPEC_LIFECYCLE_INACTIVE`로 거부됩니다
  ([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md) (영어 원문)).

문서 검사와 프로젝트 자체 검사는 두 방식 모두에 적용되며, 이미 존재하는 SDD 기록도 기존 검사를 그대로 유지합니다. 인큐베이션에서
SDD로 옮겨 가는 것은 `sdd-baseline` 플레이북을 통한 의도적인 단계이며, [전달](areas/delivery.md#incubation)에서 설명합니다.

## 작업 분류

SDD에서는 모든 개발 요청이 작업을 시작하기 전에 세 가지 축을 기준으로 분류됩니다
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문),
[`ADR-delivery-classification`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261022-delivery-classification.md)).

- **`task-kind`**: 작업 유형을 나타내며 `feature`, `bugfix`, `overall-refactor` 중 하나입니다.
- **`planning-depth`**: 변경 규모가 아니라 구현에 앞서 사전에 확정해야 할 기획 범위를 나타냅니다.
  - `session`: 사전에 확정할 사항이 없으므로 작업 유닛 없이 즉시 구현합니다.
  - `spec`: 계약이나 사양이 변경되므로, 먼저 스펙 번들을 만들어 요구사항, 구현 계획, 세부 작업을 체계적으로 기록합니다.
  - `proposal`: 기능 방향 자체가 열려 있으므로, 스펙을 작성하기 전에 제안을 구체화하고 승인을 먼저 받습니다.
- **`activity-effort`**: 작업 노력 수준(`low`, `medium`, `high`)으로, 코드 리뷰와 검증을 얼마나 철저히 진행할지 결정합니다.

작업 분류는 에이전트가 제안하고 사용자가 최종 확정합니다. 이 세 축의 조합에 따라 `sdd-<planning-depth>[-<task-kind>]`(예: `sdd-spec-feature`)라는 단 하나의 워크플로가 지정됩니다. 작업 진행 도중 기획 깊이(`planning-depth`)는 상향 조정만 가능하며, 제안 인계(handoff)를 거치거나 사용자가 직접 재분류(session reclassification)를 결정한 경우에만 예외가 인정됩니다.

작업은 세 가지 **활동**(activity)을 거칩니다. **Backlog**는 당장 착수하지 않는 요청을 제안 초안 형태로 보관하며 우선순위를 관리합니다. **Planning**은 `plan-<slug>` 브랜치에서 제안을 구체화합니다. **Development**는 `dev-<slug>` 브랜치에서 실제 기능을 구현합니다. 각 활동은 하나의 모드로 실행됩니다. 기본 모드는 `direct`이며, 사용자의 요청에 따라 에이전트가 독립된 워크트리의 워커들에게 작업을 위임하는 경우에는 `local-orchestrated` 모드가 적용됩니다.

## 유닛, 스펙, 제안

**유닛**(Unit)은 워크플로 엔진이 진행을 제어하는 기본 작업 디렉터리이며, 앵커(anchor) 파일의 존재로 식별됩니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
유닛에는 두 가지 종류가 있습니다.

- **스펙 번들**(spec bundle): `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` 경로에 위치하며 `spec.md`를 앵커 파일로 두고, 그 곁에 `plan.md`와
  `tasks.md`가 함께 구성됩니다. `devkit spec new` 명령으로 생성하며 해당 워크플로와 자동으로 연결됩니다
  ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)).
- **제안 번들**(proposal bundle): `docs/proposals/PROP-<slug>/` 경로에 위치하며 `proposal.md`를 앵커 파일로 두고
  `sdd-proposal` 워크플로에 연결됩니다. 조사 자료와 예비 아키텍처 결정(PADR)을 모읍니다. 제안이 정식 수락되면 `devkit spec proposal handoff` 명령을 통해 본문,
  결정 사항, 참고 자료를 온전히 보존한 채 스펙 번들로 전환됩니다
  ([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).

`session` 작업에는 유닛이 생성되지 않습니다. 스펙, 엔벨로프, 조정 기록 없이 일반적인 Git 커밋만 남깁니다.

## 워크플로, 단계, 게이트

**워크플로**(workflow)는 데이터 형태로 선언된 전달 절차입니다. 프런트매터에 순서대로 정렬된 **단계**(stage) 목록이 정의된 Markdown
파일이며, 각 단계마다 명확한 진입 검사(entry check)와 종료 검사(exit check)가 설정되어 있습니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
에이전트가 다음 단계를 임의로 판단하지 않습니다. 에이전트는 `devkit workflow next --unit <dir>`을 실행하여 유닛 내 파일들을 기준으로
검사 조건을 평가하고, 아직 충족되지 않은 첫 번째 단계와 누락된 조건, 그리고 다음에 따라야 할 스킬을 정확히 안내받습니다. 전체 워크플로 정의는 `devkit workflow show <id>`로
확인할 수 있습니다. 유닛은 워크플로의 ID만 저장하므로, 워크플로 정의가 변경되면 이미 진행 중인 작업에도 즉시 새 정의가 적용됩니다.

**게이트**(gate)는 사용자의 명시적인 결정을 기다리는 단계입니다. `spec` 워크플로는 다음 세 게이트를 사용합니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)):

- `plan-intent`: 진행할 작업 내용에 합의합니다.
- `plan-accept`: 제안이 제시한 방향을 공식 수락합니다.
- `dev-integration`: 구현이 완료된 작업의 최종 반영을 승인합니다.

각 게이트는 사람의 결정을 기다리는 `ask` 또는 프로젝트 정책에 따라 자동 위임되는 `auto` 모드로 동작합니다. 정책에 의해 자동 위임된 경우 정책에 따른 결정임이 기록되며, 결코 사용자가 직접
동의한 것으로 처리되지 않습니다. 사전에 합의된 범위를 벗어나 정상 진행이 불가능한 작업은 별도의 `exception` 단계로 전환되어 처리됩니다. 현재 적용 중인 정책
설정은 `devkit spec policy`로 확인하며
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)),
사용자의 결정은 `devkit workflow answer` 명령으로 기록합니다
([`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-human-interaction.md)).

## 엔벨로프

**엔벨로프**(envelope)는 `<unit>/envelopes/<kind>-<NN>.yaml` 경로에 저장되는 작은 YAML 파일로, 특정 단계나 위임된 역할이 생성한
결과물을 보존합니다. 코드 리뷰 결과, Living Spec 조정 검증, 최종 변경 보고서, 워커의 실행 결과 등이 여기에 기록됩니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).
기존 엔벨로프를 절대 덮어쓰지 않으며, 새 엔벨로프가 작성될 때마다 다음 일련번호를 부여받습니다. 워크플로 검사는 해당 종류의 가장 최신 엔벨로프를 기준으로 평가합니다.

`worker` 엔벨로프에는 사용자에게 확인해야 할 **질문**(한 번의 라운드로 취합)이나 실행을 중단시킨 **문제**(problem)가 포함될 수 있습니다.
이러한 항목은 별도의 대응 엔벨로프가 작성되어야 종결됩니다. `answer` 엔벨로프는 사용자의 답변과 결정을 기록하고, `resolution` 엔벨로프는 문제를 해결한 방식을 기록합니다.
질문에는 명확한 답변이 필요하고 문제는 확실히 해결되어야 하며, 어느 쪽도 임의로 추정하여 넘길 수 없습니다. 엔벨로프를 작성할 때는
`devkit workflow envelope` 명령을 사용합니다.

## 규칙과 커밋 게이트

**거버넌스 규칙**(governance rule)은 에이전트의 기억에 의존하는 대신 정적 파싱을 통해 기계적으로 검증하는 결정적 불변 조건(invariant)입니다
([`CAP-GOV-rules-engine`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-rules-engine.md) (영어 원문)).
`devkit rules check`는 발견된 위반 사항을 식별 가능한 고유 규칙 ID와 함께 보고하며, `devkit rules fix`는 안전한 자동 수정을 일괄 적용한 후
1회 재검증을 수행합니다. 규칙 엔진 자체는 스펙이나 유스케이스의 세부 도메인을 알지 못하며, 이러한 규칙은 `devkit-spec`의 스펙 규칙처럼 개별 번들을 통해
주입됩니다. 현재 워킹 트리, 스테이징된 파일(`--staged`), 기준 커밋과의 차이점(`--ci --base <ref>`)을 지정하여 유연하게 검사할 수
있습니다.

**커밋 게이트**(commit gate)는 Git 커밋 훅 시점에 정책을 실행합니다
([`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/gate/CAP-GATE-commit-gates.md) (영어 원문)).
`devkit gate install` 명령으로 훅 래퍼를 설치하며, `rules-check`나 `verify-commands` 같은 실제 게이트 정책은 번들에서 제공됩니다.
커밋이 생성되기 전(pre-commit)에는 게이트가 위반 사항을 감지해 커밋 생성을 차단할 수 있지만, 커밋이 완료된 후(post-commit)에는 경고만 출력합니다.

## 에이전트 어드바이저리와 출력 계약

devkit의 최우선 사용자는 에이전트이므로, 모든 CLI 명령은 일관된 형식으로 응답합니다
([`ARCH-08-cross-cutting`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-cross-cutting.md) (영어 원문),
[`ARCH-08-1-agent-output`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md)).

- **stdout은 실행 결과 전용입니다**: 한 줄짜리 `[KIND: ...]` 센티널이 출력되거나, `--format json` 옵션을 사용했을 때는 단 하나의 JSON 객체만 반환됩니다.
- **stderr는 에이전트 어드바이저리를 전달합니다**: `[ERROR]`, `[WARN]`, `[NOTICE]` 블록으로 구성되며, 각 블록은 식별 가능한 `UPPER_SNAKE`
  코드와 다음 단계를 명시하는 `[ACTION]` 지시문을 포함합니다
  ([`CAP-ADV-agent-advisory-protocol`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md) (영어 원문)).
- **종료 코드**: `0`은 성공, `1`은 부정적 결과(규칙 위반, 드리프트 감지, 커밋 거부 등), `2`는 명령 실행 실패(실행 자체를 완료할 수 없음)를
  뜻합니다. 경고나 알림은 `--strict` 옵션을 지정하지 않는 한 종료 코드를 바꾸지 않습니다.

조건 분기는 임의의 메시지 문구가 아니라 코드와 센티널을 기준으로 처리하십시오. `devkit run <command>` 역시 동일한 원칙에 따라 긴 도구
출력을 제어합니다. 전체 상세 로그는 디스크에 온전히 기록하고, stdout에는 길이가 제한된 컴팩트 요약만 전달합니다.

## 워크트리와 병렬 작업

**활동 브랜치**(activity branch)는 `plan-<slug>` 또는 `dev-<slug>` 형식의 이름을 갖습니다. **작업 워크트리**(task worktree)는
해당 브랜치를 저장소 상위 디렉터리 옆의 고정된 경로(`<parent>/<repo>-wt-<branch>`)에 별도로 체크아웃한 독립 작업 공간으로, 여러 작업이 서로의
파일을 간섭하지 않고 동시에 병렬로 진행될 수 있도록 지원합니다
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
`devkit worktree start <branch>`로 워크트리를 생성하고, `devkit worktree status`로 현재 활성 목록을 확인하며, 기본 체크아웃에서
실행하는 `devkit worktree finish`로 브랜치를 통합하고 해당 워크트리를 정리합니다. 워크트리를 필요할 때만 선별적으로 사용할지 항상 사용할지는
프로젝트 정책에 따라 결정됩니다.

작업이 병렬로 진행될 때는 `devkit spec scope` 명령이 각 작업에서 선언한 문서와 코드 경로를 모든 워크트리가 공유하는
작업 범위 레지스트리에서 상호 비교합니다. 경로 중복은 일정 조정과 통합 순서를 정하는 데 참고 자료로 쓰일 뿐, 파일 쓰기 자체를 인위적으로 차단하지는 않습니다
([`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md) (영어 원문)).

## Host와 통합

**Host**는 사용자가 직접 대화하는 에이전트 세션입니다. 사용자의 요청을 라우팅하고, 요청에 따라 전용 워커에게 작업을 위임하며, 사용자의 최종 승인을
CLI에 전달하는 핵심 주체입니다. 통합(integration)은 다음 두 단계로 엄격하게 진행됩니다
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)):

1. `devkit integration prepare <branch> ...`는 커밋된 작업 내역, 프로젝트 정책, 통합 준비 상태 검사를 수행하고 향후 수행할 정리 작업을 정확히
   검증한 뒤 다이제스트(digest)를 반환합니다. 이 단계에서는 저장소 상태를 전혀 변경하지 않습니다.
2. 제시된 준비 결과를 사용자가 검토하고 승인하면, `devkit integration integrate <branch> ... --expected-digest <digest>`가 모든
   검증을 다시 수행한 뒤 로컬 fast-forward 병합 또는 풀 리퀘스트를 통해 작업을 기준 브랜치에 안전하게 반영합니다. 준비 시점 이후 무엇이든 변경되었다면
   통합 실행을 거부합니다.

다이제스트는 준비와 실제 통합 사이에 아무런 임의 변경이 발생하지 않았음을 증명할 뿐이며, 실제 반영 권한은 Host가 전달하는 사용자의 승인에서 나옵니다.
인큐베이션에서도 같은 두 단계로 `session` 변경을 통합하며, 이때 준비 상태는 스펙 번들이 아니라 사용자에게 보고된 리뷰, 테스트, 린트
결과와 저장소 규칙을 기준으로 판단합니다.

## 전체 동작 흐름

`spec` 기획 깊이를 갖는 일반적인 기능 변경 작업은 다음과 같은 순서로 진행됩니다.

1. `devkit sync`로 배포된 `spec` 번들의 컨텍스트를 에이전트가 `devkit get-context spec`으로 로드합니다.
2. 사용자가 `/spec <intent>` 명령으로 개발 의도를 전달하면, 에이전트는 `devkit spec policy`를 확인하여 작업 분류를 제안합니다. 사용자가
   이를 확정하면 `dev-<slug>` 브랜치와 스펙 번들을 생성하고 `plan-intent` 통과를 기록합니다.
3. 에이전트는 `devkit workflow next`의 안내에 따라 스펙 작성, 구현 계획 수립, 작업 목록 분할, 실제 구현, 리뷰 엔벨로프 작성, Living Spec 조정(reconcile), 최종 변경
   보고서 작성 단계를 순서대로 완수합니다.
4. 그 과정에서 거버넌스 규칙과 커밋 게이트가 매 커밋마다 엄격하게 무결성을 검사합니다.
5. 에이전트가 통합을 준비해 결과를 보고하고, 사용자가 승인하면 최종 통합과 워크스페이스 정리를 수행합니다.

인큐베이션에서는 흐름이 더 짧습니다. 사용자가 아이디어와 함께 `/incubate`를 실행하거나 이어서 진행해 달라고 요청하면, 에이전트는
`.devkit/incubation.md`를 읽고 다음으로 유용한 작업을 골라 수행한 뒤, 실제로 실행하고 관찰한 내용을 보고하고 현재 컨텍스트를 갱신합니다.

[여정](README.md#journeys)에서 각 경로를 따라가 보고, [영역](README.md#areas)에서 각 역량 그룹을 살펴보십시오.
