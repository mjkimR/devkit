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
translated_from: en/concepts.md@d1525518c84e5a1a
---

# 개념

<!-- handbook:provenance -->
> 소스 커밋 `3da97383dc87` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](README.md)
- [기존 저장소에 devkit 도입하기](journeys/adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](journeys/drive-development-to-integration.md)
- [알맞은 문서 찾기](journeys/find-the-right-documents.md)
- [전달 문제와 예외 처리하기](journeys/handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](journeys/incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](journeys/inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](journeys/keep-the-living-spec-consistent.md)
- [주간 보고서 게시하기](journeys/publish-a-weekly-report.md)
- [Living Spec 드리프트 조정하기](journeys/reconcile-living-spec-drift.md)
- [오래된 활동 브랜치 정리하기](journeys/resolve-stale-activity-branches.md)
- [누적된 군더더기 검토와 리팩터링](journeys/review-and-refactor-accumulated-slop.md)
- [개발 요청 라우팅하기](journeys/route-development-intent.md)
- [병렬 작업 안전하게 실행하기](journeys/run-parallel-work-safely.md)
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

이 페이지는 핸드북의 나머지 부분이 기대는 개념을 만나는 순서대로 소개합니다. 먼저 지침이 에이전트에게 어떻게
전달되는지, 다음으로 작업이 어떻게 조직되고 검사되는지, 마지막으로 작업이 어떻게 반영되는지를 다룹니다. 각 절은 그
개념을 정의하는 계약으로 링크하며, 짧은 정의는 [용어집](glossary.md)에 있습니다.

## 번들: 배포 단위

**번들**(bundle)은 `bundle.toml`에 선언된 이름 있는 에이전트 자산 묶음입니다. 지시문(instruction), 플레이북,
규칙, 워크플로, 스킬, 서브에이전트 역할, 커밋 게이트, 호스트 훅, 지침 조각이 여기에 들어갑니다. 번들은 Python
휠(콘텐츠 패키지) 안에 담겨 배포되거나 여러분의 저장소 안에 있습니다. **프리셋**(preset)은 `core`나 `default`처럼
번들 자산 가운데 일부를 고른 이름 있는 선택입니다
([`CAP-DIST-manifest-spec`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-manifest-spec.md) (영어 원문)).

휠을 설치하면 그 번들을 쓸 수 있게 될 뿐입니다. 무엇을 배포할지는 프로젝트가 `.devkit/config.toml`에서
고릅니다. 일부 번들(`devkit`, `advisory`, `harness`)은 스스로 선택되고, 나머지는 `devkit add <bundle>`로 추가하고
`devkit remove <bundle>`로 뺍니다. 설치되고 선택된 번들은 `devkit list`로 확인합니다.

자산은 세 계층으로 나뉩니다
([`ARCH-08-2-resource-taxonomy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-2-resource-taxonomy.md) (영어 원문)).
자연어 지침(`AGENTS.md` 블록, 지시문, 플레이북, 워크플로), 기계화된 실행(규칙, 스킬, 서브에이전트, 커밋 게이트,
호스트 훅), 그리고 번들, 프리셋, 프로젝트 설정으로 이루어진 패키징 계층입니다.

## 동기화, 설치 기록, 그리고 편집해도 되는 것

`devkit sync`는 선택된 번들을 하나의 트랜잭션으로 배포합니다. 모두 쓰거나 모두 되돌립니다
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)).
결과물은 세 종류입니다.

- **관리 파일**(managed files): `.devkit/managed/<bundle>/` 아래의 원본 사본으로, 손으로 편집하지 않습니다.
- **프로젝션**(projections): 스킬과 서브에이전트 역할을 각 에이전트 고유 디렉터리에 둔 네이티브 사본입니다.
  `.agents/skills/`, `.claude/skills/`, `.codex/skills/` 등이 있습니다
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-agent-projections.md) (영어 원문)).
- **설치 기록**(receipt), `.devkit/installation.json`: 배포된 모든 파일과 그 체크섬, 소속 번들을 기록해 커밋하는
  파일입니다. `devkit sync --check`와 `devkit status`가 작업 공간을 이 기록과 비교합니다.

업스트림 자산을 고치고 싶을 때는 관리 사본이나 프로젝션을 편집하지 않습니다. 대신 `devkit override`로
**프로젝트 오버라이드**(project override)를 만듭니다. 오버라이드는 `.devkit/overrides/` 아래에 있고 기반이 된
업스트림 버전과 함께 추적되므로, 업스트림이 바뀌면 드리프트로 드러납니다
([`CAP-DIST-workspace-ownership`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md) (영어 원문)).

## 필요할 때 불러오는 지침

시작 파일에 있는 텍스트는 매 턴마다 토큰을 소비하므로, devkit은 지침을 단계적으로 불러옵니다
([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md) (영어 원문)).

- 루트 `AGENTS.md`의 관리 블록에는 방향 안내만 담깁니다.
- `devkit get-context <bundle>`은 번들의 헌장(constitution)과 지시문 헤더를 돌려주며, 각 헤더에는 에이전트가
  본문을 읽어야 하는 조건이 붙어 있습니다.
- **플레이북**(playbook)은 가끔 쓰는 절차로, 디스크에 남아 있습니다. 에이전트는 `devkit playbook search`로 찾고
  `devkit playbook get <bundle>/<id>`로 정확히 하나를 가져오며, 여러분이 호출하거나 확인했을 때만 실행합니다.
- **스킬**(skill)은 `/spec`, `/spec-next`처럼 에이전트 호스트가 호출하는 진입점이고, **서브에이전트**(subagent)는
  호스트별로 투영되는 역할 계약(코드 리뷰어, 조정 리뷰어, 워커)입니다.

## Living Spec

**Living Spec**은 `docs/` 아래에 있는, 시스템에 대한 지속되는 설명입니다. 이것이 진실의 원천이며 코드, 지침, 이
핸드북은 모두 이를 따릅니다. 각 문서는 프런트매터에 ID를 가집니다
([`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md) (영어 원문)).

| 종류 | ID | 설명하는 것 |
| --- | --- | --- |
| 아키텍처(Architecture) | `ARCH-...` | 시스템 구조, 런타임 흐름, 횡단 관심사 |
| 역량(Capability) | `CAP-<AREA>-<slug>` | 영역별로 묶인, 하나의 동작에 대한 계약 |
| 유스케이스(Use case) | `UC-<slug>` | 행위자가 여러 역량을 거쳐 목표에 이르는 방법 |
| 결정(Decision) | `ADR-<slug>` | 구조적 선택을 한 이유 |
| 제안(Proposal) | `PROP-<slug>` | 스펙이 되기 전에 다듬는 중인 아이디어 |
| 마일스톤(Milestone) | `MS-<slug>` | 종료 조건이 있는 로드맵 주제 |

역량과 유스케이스는 프런트매터에서 서로를 참조합니다. 진행 중인 작업은 이와 별도로 `specs/` 아래에 있습니다. 스펙은
하나의 변경을 설명하고, 변경이 끝나면 그 효과를 `docs/`에 다시 반영합니다(**조정**, reconcile).
`devkit spec resolve`, `devkit spec refs`, `devkit spec list`, `devkit spec search`는 각각 ID, 참조, 종류, 의미로
문서를 찾습니다.

## 작업 분류

모든 개발 요청은 작업을 시작하기 전에 세 축으로 분류됩니다
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md) (영어 원문),
[`ADR-delivery-classification`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261022-delivery-classification.md)).

- **`task-kind`**: `feature`, `bugfix`, `overall-refactor` 가운데 하나입니다.
- **`planning-depth`**: 변경의 크기가 아니라, 구현 전에 무엇을 정해 두어야 하는지를 나타냅니다.
  - `session`: 정할 것이 없어 작업 유닛 없이 바로 작업합니다.
  - `spec`: 계약이 바뀌므로 먼저 스펙 번들에 요구 사항, 계획, 작업을 기록합니다.
  - `proposal`: 방향 자체가 열려 있으므로 스펙을 만들기 전에 제안을 다듬고 수락합니다.
- **`activity-effort`**: `low`, `medium`, `high` 가운데 하나로, 리뷰와 검증을 얼마나 철저히 할지 정합니다.

분류는 에이전트가 제안하고 여러분이 확정합니다. 이 조합은 정확히 하나의 워크플로
`sdd-<planning-depth>[-<task-kind>]`(예: `sdd-spec-feature`)를 가리킵니다. 깊이는 작업 중에 올라가기만 하며, 예외는
제안의 인계나 여러분이 결정한 재분류뿐입니다.

작업은 세 **활동**(activity)을 거칩니다. **Backlog**는 지금 시작하지 않는 요청을 초안 제안으로 보관하고 다음에
맡을 일의 순위를 매깁니다. **Planning**은 `plan-<slug>` 브랜치에서 제안을 다듬습니다. **Development**는
`dev-<slug>` 브랜치에서 구현합니다. 각 활동은 하나의 모드로 실행됩니다. 기본값은 `direct`이고, 에이전트가 각자의
워크트리에 있는 워커에게 위임하도록 요청하면 `local-orchestrated`가 됩니다.

## 유닛, 스펙, 제안

**유닛**(Unit)은 워크플로가 이끄는 디렉터리로, 앵커 파일로 식별됩니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
유닛에는 두 종류가 있습니다.

- **스펙 번들**(spec bundle): `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`이며 `spec.md`를 앵커로 하고, 옆에 `plan.md`와
  `tasks.md`가 있습니다. `devkit spec new`가 이를 만들고 워크플로에 묶습니다
  ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md) (영어 원문)).
- **제안 번들**(proposal bundle): `docs/proposals/PROP-<slug>/` 아래에 있으며 `proposal.md`를 앵커로 하고
  `sdd-proposal`에 묶입니다. 자료와 예비 결정(PADR)을 모읍니다. 수락되면 `devkit spec proposal handoff`가 본문,
  결정, 자료를 그대로 가져가 스펙 번들로 바꿉니다
  ([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).

`session` 작업에는 유닛이 없습니다. 스펙도, 엔벨로프도, 조정 기록도 없고 커밋만 남습니다.

## 워크플로, 단계, 게이트

**워크플로**(workflow)는 데이터로 선언된 전달 절차입니다. 프런트매터에 순서 있는 **단계**(stage)를 나열한 Markdown
파일이며, 각 단계에는 진입 검사와 종료 검사가 있습니다
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md) (영어 원문)).
에이전트는 현재 단계를 스스로 판단하지 않습니다. `devkit workflow next --unit <dir>`을 실행하면 유닛의 파일에 대해
검사를 평가해, 충족되지 않은 첫 단계와 빠진 것, 따라야 할 스킬을 출력합니다. `devkit workflow show <id>`는 정의
전체를 출력합니다. 유닛은 워크플로 ID만 저장하므로, 정의가 바뀌면 이미 진행 중인 작업에도 적용됩니다.

**게이트**(gate)는 결정을 기다리는 단계입니다. `spec` 워크플로는 세 게이트를 씁니다
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md) (영어 원문)).

- `plan-intent`: 작업이 무엇인지 합의합니다.
- `plan-accept`: 제안의 방향을 수락합니다.
- `dev-integration`: 끝난 작업의 반영을 승인합니다.

각 게이트는 `ask`(사람을 기다림) 또는 `auto`(프로젝트 정책에 위임)입니다. 위임은 정책으로 보고될 뿐, 결코 여러분의
동의로 보고되지 않습니다. 합의한 대로 계속할 수 없는 작업은 별도의 `exception` 단계가 처리합니다. 실제 적용되는
설정은 `devkit spec policy`로 보고
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md) (영어 원문)),
결정은 `devkit workflow answer`로 기록합니다
([`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-human-interaction.md)).

## 엔벨로프

**엔벨로프**(envelope)는 `<unit>/envelopes/<kind>-<NN>.yaml`에 있는 작은 YAML 파일로, 한 단계나 위임된 역할이 만든
결과를 기록합니다. 리뷰 결과, 조정 검사, 최종 변경 보고서, 워커의 실행 기록 등이 여기에 해당합니다
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md) (영어 원문)).
엔벨로프는 덮어쓰지 않습니다. 새 엔벨로프는 다음 번호를 받고, 워크플로 검사는 가장 최근 것을 읽습니다.

`worker` 엔벨로프는 여러분에게 묻는 **질문**(한 라운드로 모음)이나 실행을 멈춘 **문제**(problem)를 담을 수 있습니다.
이들은 별도의 엔벨로프로 닫힙니다. `answer`는 여러분의 결정을, `resolution`은 문제를 어떻게 고쳤는지를 기록합니다.
질문은 답해야 하고 문제는 해결해야 하며, 어느 쪽도 추정으로 대신하지 않습니다. 엔벨로프는
`devkit workflow envelope`으로 씁니다.

## 규칙과 커밋 게이트

**거버넌스 규칙**(governance rule)은 에이전트의 기억에 맡기지 않고 파싱으로 검사하는 결정적 불변 조건입니다
([`CAP-GOV-rules-engine`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-rules-engine.md) (영어 원문)).
`devkit rules check`는 위반을 안정적인 규칙 ID와 함께 보고하고, `devkit rules fix`는 안전한 수정을 한 번에 적용한 뒤
한 번 다시 검사합니다. 엔진 자체는 스펙이나 유스케이스를 모르며, 그런 규칙은 `devkit-spec`의 스펙 규칙처럼 번들로
들어옵니다. 작업 트리, 스테이징된 트리(`--staged`), 또는 기준 커밋과의 비교(`--ci --base <ref>`)를 검사할 수
있습니다.

**커밋 게이트**(commit gate)는 Git의 커밋 훅에서 정책을 실행합니다
([`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md) (영어 원문)).
`devkit gate install`이 래퍼를 설치하고, `rules-check`, `verify-commands` 같은 게이트 자체는 번들에서 옵니다.
커밋이 만들어지기 전에는 게이트가 커밋을 거부할 수 있지만, 커밋 후에는 경고만 합니다.

## 어드바이저리와 출력 계약

devkit의 첫 번째 독자는 에이전트이므로, 모든 명령은 같은 방식으로 응답합니다
([`ARCH-08-cross-cutting`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-cross-cutting.md) (영어 원문),
[`ARCH-08-1-agent-output`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md)).

- **stdout은 결과입니다**: 한 줄짜리 `[KIND: ...]` 센티널, 또는 `--format json`에서는 JSON 객체 하나입니다.
- **stderr는 어드바이저리를 전달합니다**: `[ERROR]`, `[WARN]`, `[NOTICE]` 블록이며, 각각 안정적인 `UPPER_SNAKE`
  코드와 다음 단계를 지시하는 `[ACTION]` 줄을 가집니다
  ([`CAP-ADV-agent-advisory-protocol`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md) (영어 원문)).
- **종료 코드**: `0`은 성공, `1`은 부정적 결과(위반, 드리프트, 거부된 커밋), `2`는 명령을 실행할 수 없었음을
  뜻합니다. 경고와 알림은 `--strict`를 주지 않는 한 종료 코드를 바꾸지 않습니다.

분기는 메시지 문구가 아니라 코드와 센티널로 하십시오. `devkit run <command>`는 같은 생각을 긴 도구 출력에
적용합니다. 전체 로그는 디스크에 남기고, 길이가 제한된 요약만 stdout으로 보냅니다.

## 워크트리와 병렬 작업

**활동 브랜치**(activity branch)의 이름은 `plan-<slug>` 또는 `dev-<slug>`입니다. **작업 워크트리**(task worktree)는
그 브랜치를 저장소 옆의 고정된 경로 `<parent>/<repo>-wt-<branch>`에 따로 체크아웃한 것으로, 여러 작업이 서로의
파일을 건드리지 않고 동시에 진행될 수 있게 합니다
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md) (영어 원문)).
`devkit worktree start <branch>`가 워크트리를 만들고, `devkit worktree status`가 목록을 보여 주며, 기준 체크아웃에서
실행하는 `devkit worktree finish`가 브랜치를 통합하고 워크트리를 제거합니다. 워크트리를 필요할 때만 쓸지 항상 쓸지는
프로젝트 정책이 정합니다.

작업이 병렬로 진행되면 `devkit spec scope`가 각 작업이 선언한 문서와 코드 경로를, 모든 워크트리가 공유하는
레지스트리에서 비교합니다. 겹침은 일정과 통합 순서를 정하는 데 참고될 뿐, 쓰기를 막지는 않습니다
([`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md) (영어 원문)).

## Host와 통합

**Host**는 여러분이 대화하는 에이전트 세션입니다. 요청을 라우팅하고, 요청하면 워커에게 위임하며, 여러분의 승인을
CLI에 전달하는 주체입니다. 통합(integration)은 두 단계로 이루어집니다
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md) (영어 원문)).

1. `devkit integration prepare <branch> ...`는 커밋된 작업, 정책, 준비 상태 검사, 그리고 수행할 정리 작업을 정확히
   검증하고 다이제스트를 돌려줍니다. 아무것도 바꾸지 않습니다.
2. 제시된 내용을 여러분이 승인하면, `devkit integration integrate <branch> ... --expected-digest <digest>`가 모든
   검사를 다시 수행하고 로컬 fast-forward 또는 풀 리퀘스트로 작업을 반영합니다. 준비 이후 무엇이든 바뀌었다면
   거부합니다.

다이제스트는 그 사이에 아무것도 움직이지 않았다는 것만 증명합니다. 승인을 전달하는 것은 Host입니다.

## 전체가 맞물리는 방식

스펙 깊이의 전형적인 변경은 다음과 같이 진행됩니다.

1. `devkit sync`가 `spec` 번들을 배포해 두었고, 에이전트는 `devkit get-context spec`으로 이를 불러옵니다.
2. 여러분이 `/spec <intent>`로 의도를 밝힙니다. 에이전트는 `devkit spec policy`를 읽고 분류를 제안하며, 여러분이
   확정하면 `dev-<slug>` 브랜치와 스펙 번들을 만들고 `plan-intent`를 기록합니다.
3. 에이전트는 `devkit workflow next`를 따라 스펙, 계획, 작업, 구현, 리뷰 엔벨로프, Living Spec 조정, 최종 변경
   보고서까지 진행합니다.
4. 그 과정에서 규칙과 커밋 게이트가 모든 커밋을 검사합니다.
5. 에이전트가 통합을 준비해 결과를 제시하고, 여러분이 승인하면 통합과 정리를 수행합니다.

[여정](README.md#journeys)에서 각 경로를 따라가 보고, [영역](README.md#areas)에서 각 역량 그룹을 살펴보십시오.
