---
title: 격리된 명령 실행하기
translated_from: en/journeys/execute-an-isolated-command.md@97c03ee086ef45a1
---

# 격리된 명령 실행하기

<!-- handbook:provenance -->
> 소스 커밋 `f115e96c8059` 기준 devkit `v0.1.6` 스냅숏이며 2026-11-11에 생성되었습니다. 내용이 다르면 `docs/`의 Living Spec이 우선하며, 이 페이지는 다음 갱신 전까지 바뀌지 않습니다.
<!-- /handbook:provenance -->

고정된 로컬 커밋에서 기본 명령을 실행하면서 독립 작업을 계속하려면 `devkit exec`를 사용합니다. 임시 데이터·격리 서비스·임시 포트를 준비합니다. 체크아웃 격리는 OS 샌드박스가 아닙니다.

```sh
uv run devkit exec start --ref HEAD -- just lint-check
uv run devkit exec list
uv run devkit exec wait <run-id> --clean
```

시작 명령은 대기 중인 실행 ID를 반환합니다. 캡처된 감독 프로세스(supervisor)가 분리 체크아웃을 준비하고 설정과 해당 프로젝트의 locked sync를 마친 뒤 명령을 실행합니다. `status <run-id>`와 `logs <run-id>`로 확인하며 전체 로그와 결과는 공통 Git 디렉터리에 남습니다.

대기 시간 초과나 관찰자 중단은 실행을 취소하지 않습니다. `cancel <run-id>`는 관리 대상의 종료를 확인하고 체크아웃을 보존합니다. 명시적인 `clean <run-id>`는 종료 결과, 프로세스 정지 증명, 소유권과 깨끗한 파일 상태가 확인된 체크아웃만 제거합니다. 소유권 불명이나 예상 밖 파일이 있으면 보존하며 정리 결과와 명령 결과는 별도로 보고합니다.

통과 증거는 기록된 커밋과 범위에만 적용합니다. `devkit run`은 동기식 컴팩트 출력 명령으로 유지됩니다.

## 출처

- [UC-execute-an-isolated-command](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/harness/UC-execute-an-isolated-command.md) (영문 원문)
- [CAP-HARN-isolated-execution](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-isolated-execution.md) (영문 원문)
