---
sources:
  CAP-DLV-weekly-report: null
  UC-inspect-weekly-repository-progress: null
  UC-publish-a-weekly-report: null
title: 주간 보고서 게시하기
translated_from: en/journeys/publish-a-weekly-report.md@d707a4ae7471c38f
---

# 주간 보고서 게시하기

<!-- handbook:provenance -->
> 소스 커밋 `ae01161143be` 기준 devkit `v0.1.4` 스냅숏이며 2026-10-26에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit 핸드북](../README.md)
- [개념](../concepts.md)
- [기존 저장소에 devkit 도입하기](adopt-in-an-existing-repository.md)
- [개발부터 통합까지 진행하기](drive-development-to-integration.md)
- [알맞은 문서 찾기](find-the-right-documents.md)
- [전달 문제와 예외 처리하기](handle-delivery-problems-and-exceptions.md)
- [제안 숙성 후 넘기기](incubate-and-hand-off-a-proposal.md)
- [주간 저장소 진행 상황 점검하기](inspect-weekly-repository-progress.md)
- [Living Spec 일관성 유지하기](keep-the-living-spec-consistent.md)
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

검증을 마친 주간 보고서가 이미 있고, 이를 다른 사람들이 읽는 곳(위키 페이지, 채널, 문서 저장소)에 올리고 싶은
상황입니다. 이 여정은 에이전트가 보고서를 게시하는 방법을 보여 줍니다. 보고서가 손상 없이 도착했는지 알 수 있고,
다른 사람의 콘텐츠를 덮어쓰지 않으며, 두 번 보내지도 않습니다.

보고서 생성은 별도의 단계(`UC-inspect-weekly-repository-progress`)입니다. 두 단계 모두 선택형 `maintenance` 카탈로그
번들의 `weekly-report` 플레이북(playbook)에 들어 있습니다. [전달 영역](../areas/delivery.md)을 참고하고, 플레이북
전반에 대해서는 [개념](../concepts.md)을 참고하십시오.

출처: [`UC-publish-a-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/governance/UC-publish-a-weekly-report.md) (영어 원문),
계약 [`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md).

## 시작하기 전에

- `maintenance` 번들이 선택되어(`uv run devkit add maintenance`, 또는 이 플레이북만 쓰려면 `maintenance:reporting`)
  동기화되어 있습니다.
- 보고서가 생성되고 검증되었습니다. 즉 SHA-256 다이제스트와 함께 그 옆에 동반 결과 기록(companion outcome record)이
  있습니다. 보고서 자체는 변경되지 않으며, 게시에 관한 모든 내용은 동반 기록에 기록됩니다.
- 목적지에 도달할 수 있는, 이미 승인된 수단이 있습니다. 즉 에이전트가 이미 가진 커넥터나 명령입니다. devkit에는
  자체 게시 도구가 포함되어 있지 않습니다.

플레이북을 실행했다고 해서 게시가 승인되는 것은 아니며, 어떤 통합 정책도 게시를 승인하지 않습니다. 게시하려면
여러분이 고른 목적지에 대해 여러분이 명시적으로 권한을 주어야 합니다.

## 단계별 진행

1. **목적지를 고르고 권한을 줍니다.** 플레이북을 명시적으로 호출하고(`/devkit-playbook` 또는
   `uv run devkit playbook get maintenance/weekly-report`), 어디에 게시할지와 게시해도 된다는 점을 에이전트에게
   알려 줍니다.
2. **에이전트가 준비합니다.** 동반 기록을 읽고, 목적지에 도달하는 커넥터나 명령을 찾습니다.
3. **충돌 확인.** 목적지의 대상 위치에 기존 콘텐츠가 있는지 살펴봅니다.
4. **다이제스트 확인.** 로컬 보고서의 SHA-256을 다시 계산해 기록된 값과 비교합니다.
5. **전송.** 보고서의 바이트를 그대로 실행 ID와 함께 보내고, 시도, 목적지, 권한을 동반 기록에 남깁니다.
6. **검증.** 목적지의 수신 확인이나 링크를 다시 읽어 콘텐츠, 실행 ID, 다이제스트가 일치하는지 확인합니다.
7. **결과 보고.** 이제 동반 기록은 수신 증거와 함께 `published` 상태가 되고, 에이전트는 목적지와 결과를 알려
   줍니다. 보고서 파일은 바뀌지 않습니다.

## 게시 상태

| 상태 | 의미 |
| --- | --- |
| `pending` | 아직 목적지, 권한, 게시 수단 또는 허가가 없음 |
| `published` | 검증된 수신 확인이 콘텐츠, 실행, 다이제스트와 일치함 |
| `failed` | 커넥터나 명령이 실패를 확인함 |
| `unknown` | 응답이 유실되었거나 목적지를 검증할 수 없음 |

## 문제가 생겼을 때

- **동반 기록이 없거나, 완료된 생성 기록이 없습니다.** 게시가 차단되고 아무것도 전송되지 않습니다. 검증된 보고서는
  그대로 남습니다. 새 기록이 필요하면 다시 생성하십시오.
- **승인된 커넥터가 없거나 허가가 없습니다.** 게시는 `pending`으로 남습니다. 에이전트는 로컬 산출물을 보존하고
  무엇이 빠졌는지 알려 줍니다.
- **목적지의 그 위치에 이미 콘텐츠가 있습니다.** 여러분의 권한이 그 대상을 지정한 경우에만 에이전트가 이를
  대체합니다. 그렇지 않으면 아무것도 전송되지 않습니다.
- **로컬 다이제스트가 더 이상 일치하지 않습니다.** 아무것도 전송되지 않습니다. 바뀐 콘텐츠는 새로운 실행이며,
  생성 단계에서 만들어야 합니다.
- **커넥터가 실패를 보고합니다.** 동반 기록에 오류와 함께 `failed`가 기록됩니다. 이후 재시도는 같은 실행 ID와 같은
  바이트를 다시 보냅니다.
- **응답이 유실되었습니다.** 동반 기록에 `unknown`이 기록되고, 에이전트는 재시도하기 전에 목적지를 살펴봅니다.
  일치하는 수신 확인이 있으면 재전송 없이 `published`로 정리되고, 없음이 확인되면 여러분의 권한 범위 안에서
  재시도할 수 있으며, 검증할 수 없는 목적지는 `unknown`으로 남고 에이전트가 어떻게 할지 묻습니다.
- **목적지에 다른 콘텐츠(다른 실행 또는 다이제스트)가 있습니다.** 위와 같이 충돌로 취급됩니다.
- **리허설일 뿐입니다.** 통제된 연습에서는 에이전트가 권한과 수신 확인을 모의(simulated)로 표시하고, 외부에
  게시했다고 주장하지 않습니다.

## 결과

수신 확인을 직접 점검할 수 있는 `published` 기록이거나, 모든 시도가 보존된 분명한 `pending`, `failed`, `unknown`
상태 중 하나를 얻습니다. 보고서 바이트와 생성 결과는 결코 바뀌지 않고, 권한이 지정하지 않은 콘텐츠는 대체되지
않으며, `unknown` 상태의 게시는 확인 없이 재시도되지 않습니다.
