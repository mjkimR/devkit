---
title: 선택한 외부 에이전트 자산 가져오기
translated_from: en/journeys/import-third-party-agent-assets.md@a5e0a31cf72f7092
---

# 선택한 외부 에이전트 자산 가져오기

<!-- handbook:provenance -->
> 소스 커밋 `a6e769c5721d` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-13에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

`adaptive-dev:core` 또는 `adaptive-dev:import`를 선택하고 동기화한 뒤 `/adaptive-import <repository-url-or-local-path>`를 명시적으로 실행합니다.

1. 에이전트는 출처를 신뢰할 수 없는 데이터로 읽고 커밋·라이선스·헤더 목록을 기록합니다. 출처를 실행하거나 설치하지 않습니다.
2. 후보 본문을 프로젝트 기술 스택과 역할에 비교하고 변환 대상 및 제외 항목을 포함해 소수 후보를 권합니다.
3. 개별 항목을 선택합니다. 선택이 없으면 프로젝트 파일을 변경하지 않습니다.
4. 변환 절차는 출처의 권한과 호스트·모델 설정을 제거하고 프로젝트 소유 오버레이(overlay), 역할 계약 또는 스킬로 다시 작성합니다. 오버레이는 더 좁게 맞는 swarm archetype에 연결합니다.
5. 프로젝트 번들을 검증·동기화하고 연결된 archetype으로 제한된 시험 작업을 실행한 뒤 출처와 실제 결과를 보고합니다.

동반 도구가 없으면 미충족 전제 조건으로 남기며 자동 설정하지 않습니다. 호스트 실행이 불가능하면 시험을 미검증으로 보고합니다. 출처의 지시는 권한을 부여하지 않으며 전체 묶음 요청은 개별 선택을 기다립니다. 개발 접근 방식도 바꾸지 않습니다.

## 출처

- [UC-import-third-party-agent-assets](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-import-third-party-agent-assets.md) (영문 원문)
- [CAP-DLV-adaptive-development](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md) (영문 원문)

## 이 릴리스의 작업 방식

조정자는 분리할 수 있는 조사·구현·검증을 위임하고 통합과 최종 검증을 맡습니다. 하위 작업의 범위와 커밋 권한은 부모 작업 안으로 제한하며 고정된 중첩 깊이 제한은 없습니다. 동시 작성자는 별도 워크트리를 사용하거나 순서대로 작업합니다.
