---
sources:
  CAP-DIST-sync-and-transactions: null
  CAP-DLV-idea-incubation: null
  CAP-HARN-agent-guidance: null
  UC-incubate-an-idea: null
title: 아이디어 인큐베이션하기
translated_from: en/journeys/incubate-an-idea.md@43f2e69636fe1f88
---

# 아이디어 인큐베이션하기

<!-- handbook:provenance -->
> 소스 커밋 `18b834c35c0c` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)
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
- [선택한 느린 작업 빠르게 하기](speed-up-selected-slow-operations.md)
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

모든 아이디어가 확정된 계약에서 시작하지는 않습니다. 제품이 무엇이어야 하는지 아직 알아가는 중이라면, 스펙 주도 개발(SDD)은 작업이 활용할 수 있는 것보다 많은 기록을 요구합니다. 인큐베이션(incubation)은 더 가벼운 대안입니다. 에이전트가 다음으로 유용한 제품 작업(질문, 범위가 정해진 실험, 대표 흐름 구현, 사용 점검) 하나를 진행하고, 실제로 실행한 것을 검증하며, 다음 세션이 이어받을 수 있도록 현재 사실을 짧은 파일에 남깁니다. 변경마다 유닛, 승인, 엔벨로프를 만들지 않으며, 작은 앱은 계속 인큐베이션 상태로 유지해도 됩니다.

출처: [`UC-incubate-an-idea`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-incubate-an-idea.md) (영어 원문),
계약 [`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md) (영어 원문),
진입 스킬 [`incubate`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-catalog/src/devkit_catalog/incubation/bundle/skills/incubate/SKILL.md) (영어 원문).
SDD의 제안 숙성과는 별개이며, 그쪽은 [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)입니다.

## 시작하기 전에

- `devkit-docs`와 `devkit-catalog`를 설치한 뒤 선택형 번들을 선택합니다: `uv run devkit add incubation`(프리셋 `core`). `devkit-spec`은 필요하지 않습니다. 번들은 `/incubate`, 지침 포인터, 선택적 지원 역할 세 개, 현재 컨텍스트 템플릿을 배포하며, 선택만으로 제품 파일이 생기지는 않습니다.
- `.devkit/config.toml`에서 공유 개발 방식(development approach)을 설정합니다.

  ```toml
  [development]
  approach = "incubation"
  ```

  기본값은 `sdd`입니다. 번들 선택은 개발 방식을 바꾸지 않으며, 이 설정만이 바꿉니다
  ([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md) (영어 원문)).
- 저장소의 일반 실행 환경(빌드, 테스트, 실행 명령)을 사용할 수 있어야 합니다.

## 단계별 진행

1. **호출.** 원하는 작업과 함께 `/incubate`를 실행하거나 아이디어를 이어서 진행하라고 요청합니다. 에이전트는 에이전트 컨텍스트마다 한 번 `uv run devkit get-context incubation`을, 문서 작업 전에는 `get-context docs`를 읽습니다.
2. **개발 방식 확인.** 에이전트가 `uv run devkit config show`를 실행하고 `configuration.development.approach`를 읽습니다. 제품 작업은 `incubation`일 때만 시작합니다.
3. **현재 사실 복구.** `.devkit/incubation.md`가 있으면 읽고, 실행 지침과 구현을 살펴 현재 목표, 사용자, 제약, 사용자가 내린 결정, 가정, 마지막으로 관찰된 증거를 파악합니다. 버려진 이력은 재구성하지 않습니다.
4. **다음 작업 선택.** 아직 정해지지 않았거나 입증되지 않은 것에서 유용한 단계 하나를 고릅니다. 그 단계에 사용자가 아직 내리지 않은 제품 결정이 필요하면, 그 질문 하나만 추천안과 함께 묻습니다.
5. **실행.** 합의된 목표 안에서 범위가 정해진 작업을 수행합니다. 조사와 실험은 관찰과 가정을 구분하고, 실험은 쓰기 범위와 중단 조건을 밝힙니다. 목표가 유지되는 동안 남겨 둘 코드, 테스트, 문서는 자유롭게 다시 만들 수 있습니다.
6. **검증.** 대표 흐름을 실제로 실행하고 해당 프로젝트 검사를 돌려, 어떤 소스에서 무엇이 실제로 실행되었는지 보고합니다. 건너뛰었거나, 사용할 수 없었거나, 결론이 나지 않은 검사는 미검증으로 남습니다.
7. **컨텍스트 남기기.** `.devkit/incubation.md`를 갱신하고 결과, 한계, 다음 작업을 보고합니다.

## 선택적 지원 역할

에이전트는 분리 가능한 질문을 위임할 수 있으며, 모든 역할이 매번 필요하지는 않습니다. 각 역할에는 목표 하나, 명시적 경계, 소스 식별 정보, 기대 출력이 주어지며, 에이전트는 실제 반환 결과(와 diff)를 확인한 후에만 사용합니다.

| 역할 | 반환 | 경계 |
| --- | --- | --- |
| `product-clarifier` | 후보 사용자와 문제, 대안, 빠진 질문. 결정을 지어내지 않음 | 읽기 전용 |
| `incubation-researcher` | 결정 하나를 위한 증거, 또는 경로·명령·한계를 밝힌 범위가 정해진 실험 | 기본은 읽기 전용, 할당된 프로토타입만 쓰기, 커밋 없음 |
| `usage-reviewer` | 대표 흐름의 기대 사용과 관찰된 사용 비교, 실패 조건 | 제품 소스는 읽기 전용, 할당된 테스트 데이터만, 커밋 없음 |

## 현재 컨텍스트 파일

인큐베이션 현재 컨텍스트(incubation current context)인 `.devkit/incubation.md`는 에이전트가 최신 상태로 유지하는 프로젝트 소유의 일반 Markdown입니다. 목표, 사용자, 제약, 흐름; 구현 선택이나 가정과 구분된 사용자의 결정; 실행·검사 명령과 그것이 어떤 소스에서 낸 증거; 남은 한계와 질문; 다음으로 유용한 작업을 담습니다. ID, 상태, 스키마가 없고, 대체된 실험은 기록으로 남기지 않고 지우며, 동기화가 이 파일을 덮어쓰지 않습니다. 역할은 증거를 반환할 뿐 이 파일을 편집하지 않습니다. 이후 세션은 오래된 항목을 그대로 믿지 않고 의존하는 내용을 다시 확인합니다.

## 문제가 생겼을 때

- **개발 방식이 `sdd`인 경우:** 에이전트는 제품 작업을 멈추고 파일과 컨텍스트를 그대로 둔 채 바꿔야 할 설정을 알려 줍니다. 개발 방식을 스스로 바꾸지 않습니다.
- **`DEVELOPMENT_CONFIG_INVALID`:** `[development]` 테이블이 잘못되어 `devkit config show`가 종료 코드 `2`로 끝납니다. 에이전트는 오류를 보고하고, 고쳐질 때까지 제품 작업을 하지 않습니다.
- **컨텍스트가 없거나 오래된 경우:** 전체 백로그나 이력을 요구하지 않고, 구현, 실행 지침, 사용자의 답으로 현재 사실을 다시 세웁니다.
- **목표나 제약이 바뀌는 경우:** 그에 의존하는 작업은 사용자의 방향을 기다립니다.
- **역할이 실패하거나 범위를 벗어난 경우:** 에이전트가 실제 부분 상태를 보고하고, 그 반환을 증거로 쓰지 않으며, 다른 사람의 작업은 버리지 않습니다.
- **의도한 동작이 실패한 경우:** 목표 안에서 고치고 영향받은 검사를 다시 실행합니다.
- **증거가 없는 경우:** 검사를 미검증으로 보고하고 공백을 다음 작업에 넣으며, 통과했다고 주장하지 않습니다.
- **SDD 도입을 요청하는 경우:** 인큐베이션을 유지한 채 스펙 자산을 준비할 수 있다고 설명하고, 별도의 기준선 절차인 [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)로 안내합니다. 이 여정이 SDD를 활성화하지는 않습니다.

## 최종 결과

작업의 관찰된 결과, 이어서 진행하는 데 필요한 현재 사실과 지침, 명시적인 한계와 다음 단계가 남습니다. 개발 방식 전환, 지어낸 제품 결정, 건너뛴 검사의 통과를 주장하는 일은 없으며, 무관한 편집과 기존 SDD 이력은 그대로 유지됩니다. 관련 영역: [전달](../areas/delivery.md).
