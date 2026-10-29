---
sources:
  CAP-DLV-weekly-report: null
  UC-inspect-weekly-repository-progress: null
  UC-publish-a-weekly-report: null
title: 주간 보고서 게시하기
translated_from: en/journeys/publish-a-weekly-report.md@08e4e68031de0e4e
---

# 주간 보고서 게시하기

<!-- handbook:provenance -->
> 소스 커밋 `022b9f03bbd2` 기준 devkit `v0.1.5` 스냅숏이며 2026-10-29에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [인큐베이션에서 SDD 도입하기](adopt-sdd-from-incubation.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [아이디어 인큐베이션하기](incubate-an-idea.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
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

이미 검증을 마친 주간 보고서를 동료들이 읽을 수 있는 위키 페이지, 채널, 문서 저장소 등에 게시하려는 상황을 다룹니다. 이 여정에서는 에이전트가 다른 사람의 콘텐츠를 덮어쓰거나 중복 전송하지 않고, 보고서가 온전하게 전달되었는지 확인할 수 있도록 안전하게 게시하는 절차를 안내합니다.

보고서 생성은 별도의 단계(`UC-inspect-weekly-repository-progress`)에서 진행됩니다. 두 작업 모두 선택형 `maintenance` 카탈로그 번들의 `weekly-report` 플레이북에 포함되어 있습니다. 자세한 내용은 [전달 영역](../areas/delivery.md)을 참고하고, 플레이북 전반에 관한 내용은 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/governance/UC-publish-a-weekly-report.md) (영어 원문),
계약 [`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-weekly-report.md).

## 시작하기 전에

- `maintenance` 번들을 추가(`uv run devkit add maintenance`, 또는 이 플레이북만 사용하려면 `maintenance:reporting`)하고 동기화했습니다.
- 보고서가 생성 및 검증을 마친 상태입니다. 보고서 파일 곁에 SHA-256 다이제스트와 동반 결과 기록(companion outcome record)이 함께 존재합니다. 보고서 원본 자체는 불변이며, 게시에 관한 모든 세부 사항은 이 동반 기록에 작성됩니다.
- 대상 목적지에 도달할 수 있는 승인된 수단(에이전트가 이미 갖춘 커넥터나 명령)이 준비되어 있습니다. devkit은 자체 게시 도구를 제공하지 않습니다.

플레이북 실행이나 통합 정책만으로는 게시 권한이 자동으로 부여되지 않습니다. 게시를 진행하려면 직접 지정한 대상 목적지에 대해 명시적인 승인 권한을 부여해야 합니다.

## 단계별 진행

1. **목적지 선택 및 권한 부여.** 플레이북을 명시적으로 호출하고(`/devkit-playbook` 또는 `uv run devkit playbook get maintenance/weekly-report`), 게시 대상 위치와 함께 게시 승인을 에이전트에 전달합니다.
2. **에이전트 준비.** 에이전트가 동반 기록을 읽고 대상 목적지에 접속할 커넥터나 명령을 확인합니다.
3. **충돌 확인.** 목적지의 대상 위치에 기존 콘텐츠가 이미 있는지 확인합니다.
4. **다이제스트 검증.** 로컬 보고서의 SHA-256을 다시 계산하여 기록된 다이제스트와 일치하는지 대조합니다.
5. **전송.** 보고서의 원본 바이트를 실행 ID와 함께 전송하고 시도 이력, 목적지, 부여된 권한을 동반 기록에 남깁니다.
6. **검증.** 목적지의 수신 확인(영수증) 또는 링크를 다시 읽어 콘텐츠, 실행 ID, 다이제스트가 일치하는지 확인합니다.
7. **결과 보고.** 동반 기록이 수신 증거와 함께 `published` 상태로 갱신되며, 에이전트가 최종 목적지와 결과를 보고합니다. 보고서 원본 파일은 변경되지 않습니다.

## 게시 상태

| 상태 | 의미 |
| --- | --- |
| `pending` | 목적지, 권한, 게시 수단 또는 허가가 아직 지정되지 않음 |
| `published` | 검증된 수신 확인이 콘텐츠, 실행 ID, 다이제스트와 일치함 |
| `failed` | 커넥터 또는 명령 실행 실패가 확인됨 |
| `unknown` | 응답이 유실되었거나 목적지를 검증할 수 없음 |

## 문제가 생겼을 때

- **동반 기록이 없거나 완료된 생성 기록이 없는 경우:** 게시가 차단되고 아무것도 전송되지 않습니다. 이미 검증된 보고서는 그대로 유지되므로, 새 기록이 필요하면 보고서를 다시 생성하십시오.
- **승인된 커넥터가 없거나 권한이 누락된 경우:** 게시는 `pending` 상태로 유지됩니다. 에이전트는 로컬 산출물을 보존한 채 누락된 항목을 안내합니다.
- **목적지에 이미 콘텐츠가 존재하는 경우:** 부여된 권한에 해당 대상을 덮어쓰도록 명시된 경우에만 에이전트가 이를 교체합니다. 그렇지 않으면 아무것도 전송하지 않습니다.
- **로컬 다이제스트가 더 이상 일치하지 않는 경우:** 아무것도 전송되지 않습니다. 내용이 변경되었다면 별도의 생성 단계를 거쳐 새로운 실행으로 다시 만들어야 합니다.
- **커넥터가 실패를 보고하는 경우:** 동반 기록에 오류 세부 사항과 함께 `failed`가 기록됩니다. 이후 재시도할 때는 동일한 실행 ID와 원본 바이트를 그대로 재전송합니다.
- **응답이 유실된 경우:** 동반 기록에 `unknown`이 기록되며, 에이전트는 재시도에 앞서 목적지의 상태를 먼저 점검합니다. 일치하는 수신 확인이 발견되면 재전송 없이 `published`로 처리되고, 콘텐츠가 없음을 확인하면 부여된 권한 범위 내에서 재시도할 수 있습니다. 상태를 확인할 수 없는 목적지는 `unknown` 상태로 유지되며 에이전트가 후속 조치를 사용자에게 문의합니다.
- **목적지에 다른 콘텐츠(다른 실행 ID 또는 다이제스트)가 있는 경우:** 위의 경우와 마찬가지로 충돌로 처리됩니다.
- **리허설(모의 테스트)인 경우:** 통제된 연습 환경에서는 에이전트가 권한과 수신 확인을 모의(`simulated`)로 표시하며, 실제로 외부에 게시되었다고 간주하지 않습니다.

## 최종 결과

수신 확인을 직접 점검할 수 있는 `published` 기록을 얻거나, 모든 시도 이력이 보존된 명확한 `pending`, `failed`, `unknown` 상태를 얻게 됩니다. 보고서 바이트와 생성 결과는 결코 임의로 변경되지 않으며, 권한에 명시되지 않은 기존 콘텐츠는 덮어쓰지 않습니다. 또한 `unknown` 상태의 게시는 사전 확인 없이 맹목적으로 재시도되지 않습니다.
