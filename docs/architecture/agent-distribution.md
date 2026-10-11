# Agent 자산 통합 배포 체계

상태: uv 프로젝트 의존성 기반 구현. CLI는 `devkit`, 소비 경로는 `.devkit/`이다.

## 채택한 배포 방식

소비 프로젝트의 dev 의존성으로 배포 CLI와 콘텐츠 패키지를 함께 설치한다.
Python 코드가 없는 콘텐츠도 manifest와 리소스를 담은 wheel로 배포한다.

```bash
uv add --dev devkit-distribution package-a-rules package-b-playbooks
uv run devkit sync
```

uv는 패키지 획득·버전·Python 의존성·환경을 관리하고 `uv.lock`으로 고정한다.
`devkit sync`는 같은 환경의 콘텐츠 패키지를 발견해 리소스를 프로젝트에 배치한다.
업데이트는 uv에서 의존성을 갱신한 다음 sync하며, 새 checkout은 uv 환경 복원과
sync로 재생성한다. 별도 ZIP 배포·다운로드 cache·release resolver는 기본 흐름에 없다.
기존 ZIP build는 로컬 export 보조 명령으로 유지한다.

전역 `uv tool install` 환경은 프로젝트 dev 의존성을 발견하지 못할 수 있으므로
프로젝트에서는 `uv run devkit`을 사용한다. 실제 배포 패키지 이름은
`devkit-distribution`이며 실행 명령은 `devkit`이다.

## 패키지 계약

콘텐츠 패키지는 `devkit_distribution.bundles` entry point group에 리소스 모듈을
등록한다. entry point 값은 callable이 아닌 import 가능한 module 이름이다.
그 모듈 아래 `bundle/`에 `bundle.toml`과 모든 선언 리소스를 wheel에 포함한다.
module 초기화에는 부작용을 두지 않는다. sync는 rule 구현을 import하지 않는다.

```toml
[project.entry-points."devkit_distribution.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

`bundle.toml` schema 1은 name·version·assets·presets를 선언한다. asset 종류는
skill·subagent·instruction·playbook·rule이다. source 또는 agent별 variants를
선언하며 native 파일의 본문·설정 키는 변환하지 않는다. skill은 references,
scripts 등 전체 디렉터리를 포함한다. 상대 경로 탈출·symlink·특수 파일은 거부한다.
정확한 schema와 예제는 [패키지 README](../../packages/devkit-distribution/README.md)에 있다.

bundle name은 환경 전체에서 유일해야 한다. 서로 다른 패키지가 같은 bundle을
제공하면 오류다. Python dependency 해결은 uv에 맡기며 bundle 버전 solver나
별도 다운로드 메커니즘을 만들지 않는다. receipt는 package 버전과 bundle 버전을
함께 기록한다. 배포 여부는 entry point 등록으로 명시하며 일반 설치 패키지는 무시한다.

## 설치 및 소유권

```text
.devkit/
  installation.json       # 배포 package·선택·파일 해시/mode·asset 경로: Git 보존
  managed/<bundle>/       # wheel에서 복원하는 리소스: Git 제외
  transient/              # 중단 복구 journal: Git 제외
<agent native paths>      # 선택 agent의 skill/subagent 배포 사본
```

기본 sync는 발견한 모든 bundle의 모든 asset을 managed에 배포한다.
`--preset bundle:name`으로 특정 bundle의 asset 선택을 제한한다. 설정을 생략한
재실행은 기존 선택을 유지하고 `--all-assets`로 preset 제한을 해제한다.
선택한 agent는 `--agent`로 지정하고 이후 receipt에서 유지한다.
`--no-agents`로 native 배포 선택을 해제할 수 있다.

instructions·playbooks·rule은 managed의 원래 상대 경로를 보존한다. receipt의
asset 목록에 실제 배포 경로를 제공하고 `devkit list`로 발견한다. Python rule의
dependency는 해당 wheel의 dependency로 선언한다. rule 실행·plugin API 연결은
별도 후속 작업이며 파일 설치만으로 rule이 자동 실행되지는 않는다.

Codex와 Claude Code의 파일 배치 adapter는 skill 전체 트리와 agent별 native
subagent 변형을 복사한다. 선택 agent의 subagent 변형이 없으면 실패한다.
공통 subagent를 임의로 변환하지 않는다. native 파일 생성과 실제 agent 로딩은
별도다. trust·전역 설정·공유 config 및 AGENTS/CLAUDE 지침 진입점은 자동 수정하지
않는다. agent별 실제 세션 발견·실행과 버전 호환성은 아직 검증하지 않았다.

배포 도구는 기록에 있는 파일만 관리한다. 다른 도구의 파일은 보존하며 기존
동일 내용 파일도 기록 없는 상태에서는 충돌이다. 기존 내용·mode가 배포 기록과
다르면 사용자 편집으로 보고 전체 sync를 중단한다. 패키지 제거·preset 해제로
제외된 파일은 기록된 상태와 같은 경우에만 삭제한다. 편집된 파일은 삭제하지 않는다.
사용자 local/override 합성 및 원본 변경 review 계약은 아직 구현하지 않았다.

sync는 설치 전 전체 충돌 검사 후 lock·durable journal·atomic replacement로
파일과 receipt를 적용한다. 중단 journal이 있으면 다음 sync를 막는다.
`devkit recover`는 기록된 before/after와 같은 파일만 이전 상태로 복원한다.
`--dry-run`은 변경 목록을 출력하고 프로젝트에는 쓰지 않는다. `--check`는 변경이
필요하면 실패 상태를 반환한다. `.gitignore`나 Git index는 자동 수정하지 않는다.
managed/transient 및 생성 native 파일의 ignore 정책은 소비 프로젝트에서 설정한다.

## specrig와의 관계

조사한 원본은 `/home/mj/projects/workbench/repos/specrig` 로컬 checkout이다.
`cli/internal/scaffold/{layers,manifest,transaction}.go`의 소유권·해시 기반
충돌 검사·복구 구조와 `cli/internal/harness/assets.go`의 공통 resolver를 참고했다.
원격 릴리즈나 실제 agent 실행은 이번 조사에서 검증하지 않았다.

specrig 콘텐츠는 얇은 Python 리소스 패키지로 포장할 수 있다. 생산자의 기존
디렉터리는 빌드 설정으로 wheel 리소스 경로에 포함하며 원본을 재작성할 필요가 없다.
specrig Go 실행파일은 기존 릴리즈 수명주기를 유지한다. 동일 native 파일을
specrig와 devkit이 동시에 소유하지 않도록 기존 배포 경로는 충돌로 처리한다.

## 검증 및 후속 범위

검증은 `just lint`, `just check`, `just test`, `just rules-check`로 수행한다.
wheel 빌드·설치 후 실제 entry point 발견과 프로젝트 동기화를 별도로 확인한다.
테스트는 패키지 발견·중복 bundle·preset 선택·native bytes·실행 mode·재실행,
업데이트·제거·사용자 편집·symlink·dry-run·transaction rollback·recover를 다룬다.

후속 범위는 local/override, agent별 지침 진입점과 config 등록, rule plugin 실행,
agent 버전 호환성 및 실제 세션 검증이다. 개인 전역 설치는 초기 범위에 없다.
