---
sources:
  CAP-DLV-incubation-sdd-baseline: null
  CAP-HARN-agent-guidance: null
  UC-adopt-sdd-from-incubation: null
title: 인큐베이션에서 SDD 도입하기
translated_from: en/journeys/adopt-sdd-from-incubation.md@a1f091a35577c575
---

# 인큐베이션에서 SDD 도입하기

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](incubate-an-idea.md)
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

인큐베이션한 제품은 쓸모가 있는 한 계속 인큐베이션 상태로 둘 수 있습니다. 남겨 둘 부분을 앞으로 스펙 주도 개발(SDD)로 바꾸기로 했다면, `sdd-baseline` 플레이북이 이를 정직하게 진행합니다. 에이전트는 유지할 제품을 구현, 현재 문서, 실제로 실행된 검사와 대조하고, 문서를 고친 뒤, 사용자가 정확한 효과를 승인한 후에만 개발 방식을 전환합니다. 지난 실험에 대한 소급 제안, 스펙 유닛, 결정은 만들어 내지 않습니다.

출처: [`UC-adopt-sdd-from-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-adopt-sdd-from-incubation.md) (영어 원문),
계약 [`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md) (영어 원문),
플레이북 [`sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md) (영어 원문).
인큐베이션을 쓴 적이 없는 저장소라면 [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)를 참고하십시오.

## 시작하기 전에

- 저장소의 개발 방식(development approach)이 `incubation`입니다([아이디어 인큐베이션하기](incubate-an-idea.md)). 이미 `sdd`라면 전환할 것이 없으며, 드리프트는 [Living Spec 드리프트 조정하기](reconcile-living-spec-drift.md)로 다룹니다.
- 유지할 동작, 흐름, 구조, 선택과 제외할 것을 말할 수 있어야 합니다.
- 에이전트가 저장소의 빌드, 린트, 테스트, 사용 점검을 실행할 수 있어야 합니다.
- 저절로 시작되는 것은 없습니다. 제품 크기, 경과 시간, 실험 횟수는 도입을 일으키지 않으며, 사용자가 플레이북을 호출하거나 제안될 때 확인해야 합니다.

## 단계별 진행

1. **전환 없이 시작.** 에이전트가 절차를 로드합니다(`uv run devkit playbook get spec/sdd-baseline` 또는 `/devkit-playbook`). 준비하는 동안 개발 방식은 계속 `incubation`입니다. `devkit-spec`이나 그 자산이 없으면 설치와 `uv run devkit add spec`의 효과를 제시합니다. 설치는 도입을 준비할 뿐, 활성화하거나 무언가를 입증하지 않습니다.
2. **범위 확정.** 저장소, 정확한 `HEAD`, 관련 수정 경로, `uv run devkit config show`에서 본 적용 중인 개발 방식을 기록하고, `.devkit/incubation.md`와 현재 문서를 입력으로 읽은 뒤, 유지할 항목과 제외할 항목을 사용자와 합의합니다.
3. **대조.** 유지할 항목마다 구현, 현재 문서(또는 없는 문서가 들어갈 곳), 증거를 연결하고 `verified`, `gap`, `excluded`로 표시합니다. 제외된 항목은 검증된 것으로 세지 않습니다. 범위가 필요로 하는 기능 명세, 유스케이스, 아키텍처, 결정 문서, 실행 지침만 쓰거나 고치며, 현재의 선택과 알려진 이유를 지난 대안을 지어내지 않고 적습니다.
4. **검사 실행.** 해당 프로젝트 명령을 실행하고 대표 사용자 흐름을 직접 실행하며, 명령, 소스 식별 정보, 환경, 결과를 기록합니다. 문서 형식 검사의 통과는 그것이 검사한 조건만 입증할 뿐, 제품이 준비되었다는 뜻이 아닙니다.
5. **준비 상태 제시.** 공백이 남지 않으면 보고서, 유지 범위, 검사 결과, 정확한 활성화 효과를 제시합니다: `.devkit/config.toml`의 `[development] approach = "sdd"`, 그리고 통합 provider가 없거나 `project`이면 이를 `spec`으로 설정하는 것. 다른 설정은 사용자가 변경을 승인하지 않는 한 유지됩니다.
6. **사용자 결정.** 사용자가 같은 소스와 범위에 대해 바로 그 효과를 승인하거나, 에이전트가 정확히 그 효과에 대해 이미 받은 명시적 결정을 재사용합니다.
7. **활성화와 확인.** 에이전트가 공유 설정을 편집하고 `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy`, `uv run devkit sync --check`를 실행해 관찰된 최종 상태를 기록합니다. 다음에 요청하는 변경은 [개발 요청 라우팅하기](route-development-intent.md)를 따르며, 기준선 자체는 유닛이나 엔벨로프를 남기지 않습니다.

보고서의 기본 위치는 `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`(또는 저장소의 일반 증거 위치)입니다. 워크플로 연결이나 상태가 없는 일반 자료입니다.

## 문제가 생겼을 때

- **요청한 적이 없는 경우:** 일반 인큐베이션이 계속되며, 이 여정은 시작되지 않습니다.
- **검사가 없거나 실패했거나 건너뛰었거나, 문서가 코드와 다른 경우:** 공백을 기록하고 사용자가 고릅니다: 문서 수정, 동작 수정의 별도 승인, 유지 범위 축소, 또는 도입을 미루고 인큐베이션에 머무르기. 필요한 항목을 면제해서 준비 상태로 만들지는 않습니다.
- **활성화 전에 소스가 바뀐 경우:** 영향받은 관찰을 무효로 하고 다시 확인합니다. 오래된 증거로 SDD를 활성화하지 않습니다.
- **필요한 provider 변경 같은 효과를 승인하지 않은 경우:** 도입은 활성화되지 않고 불일치가 보고됩니다.
- **설치, 정책 편집, 동기화가 중간에 실패한 경우:** 에이전트는 실제 부분 상태와 지원되는 복구 방법을 보고하며, 성공이나 롤백을 주장하지 않습니다. 완료는 재검증 후입니다.

## 최종 결과

유지할 제품에 사실에 맞는 현재 문서와 관찰된 증거가 갖춰지고, 개발 방식, 선택된 지침, 다음 변경의 라우팅이 모두 SDD로 일치합니다. 무관한 편집과 기존 SDD 이력은 남고, 해결되지 않은 공백은 계속 보입니다. 관련 영역: [전달](../areas/delivery.md).
