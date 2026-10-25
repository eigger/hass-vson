# Scoped adoption verification

Date: 2026-10-23 (Asia/Seoul).

Scope: BLE session migration, diagnostic entities and shared test/validation infrastructure; see [STANDARDS.md](STANDARDS.md). Base commit: `a095f96d18863c76e02f7b5c195fff66ce6987f9`; results below apply to this task's uncommitted working-tree implementation, not the original base commit or future changes.

The plan was to preserve WP6003 frames/timing, existing measurement and diagnostic identities and minimum HA support; replace handwritten BLE connection/notification/error mechanics with public blesession APIs; publish retained failure reports; verify actual HA loading, recovery and cleanup; and share CI instead of duplicating it. This scope is implemented.

| Check | Result |
| --- | --- |
| Actual HA 2025.1.0 / Python 3.13.14 / pytest-homeassistant-custom-component 0.13.201 | PASS: 36 tests |
| Actual HA 2026.10.2 / Python 3.14.5 / pytest-homeassistant-custom-component 0.13.373 | PASS: 36 tests |
| blesession exact declared version | 0.9.0 installed in both environments; exact pin is both minimum and selected version |
| Bluetooth sensor data dependency | 1.7.1 installed in both environments; compatible with minimum HA's component pins |
| Dependency consistency | PASS: `uv pip check` in both environments |
| Ruff 0.17.2 lint and formatting | PASS |
| Whitespace diff check | PASS |
| Reusable workflow YAML and full-SHA references | PASS: YAML parsed and references inspected |
| DOC-07 bilingual structure/link/table check | PASS using central `scripts/bluetooth_documents.py` from local standards checkout `0ec31111a81b0ee5702f1d8a17f03616a10a5db6` |
| Independent review | PASS: separate `review` subagent inspected lifecycle, protocol, availability, failure retention, shared workflows and bilingual docs; incorrect documented notification/write UUIDs corrected; final follow-up reported no remaining findings |
| Remote HACS/Hassfest/GitHub Actions and actionlint | Not run locally; reusable CI configured, no push or workflow dispatch performed |
| Physical WP6003, firmware, local adapter and proxy routes | Not verified; automated tests simulate BLE transport only |

Commands: `.venv/bin/python -m pytest -q`, `/tmp/hass-vson-current/bin/python -m pytest -q`, `.venv/bin/python -m ruff check .`, `.venv/bin/python -m ruff format --check .`, `uv pip check --python .venv/bin/python`, `uv pip check --python /tmp/hass-vson-current/bin/python`, and `git diff --check`. Both environments resolve the actual HA Bluetooth/USB manifest requirements alongside test and integration requirements, without `--no-deps`.

Coverage includes actual entry/platform setup and one shared device, user config flow, duplicate/unsupported discovery, options validation and reload, measurement availability and recovery, failed first poll, retained last failure/count, active-poll unload/cancellation, connect failure, missing GATT, invalid packets, missing notifications, dropped links, whole-attempt timeout, cleanup warnings, report fallback and Bleak's native write-response selection. External transport tests use the official `blesession.testing.FakeClient`; Home Assistant itself is real.

Compatibility findings fixed during verification: the old code used a nonexistent active-update method on the passive processor coordinator, imported unit enums absent from HA 2025.1.0, and relied on undeclared parser dependencies. Latest bluetooth-sensor-state-data 1.9.0 is incompatible with the minimum HA Bluetooth pins, so the compatible 1.7.1 is declared rather than raising minimum HA support. Initial environment resolver failures were corrected with the matching HA/plugin pair and actual component requirements; they are not counted as passing runs.

Remaining full-adoption work is listed in STANDARDS.md. No support-minimum increase, release, commit, push, other-repository edit or branch-protection change was performed.

## Earlier ZIP packaging verification (historical)

# Scoped adoption checklist


## 2026-10-23 HACS ZIP and Downloads (scoped)

- Target base: `a095f96d18863c76e02f7b5c195fff66ce6987f9`; reviewed release central: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`.
- Scope: HACS-04/CI-11 release ZIP and DOC-03/05 Downloads replacing Analytics Usage. No release is created during this update.
- Local scoped validation: PASS — canonical badge check, no Analytics Usage, release metadata/caller contract, actionlint 1.7.12, native git diff --check, unchanged tracked integration/manifest/dependencies/tests.
- Actual archive build: PASS at `e9a5520df3b4cef5fd7a2c78bdc8c388fe32da5b`; `vson.zip`, 19 files, SHA256 `a5b52c5dada67686bceb771ad23da3a5d563185dbc679abdc53ba3e4c2c35318`. All archive members matched checkout bytes; manifest.json and __init__.py are at ZIP root. Final documentation-only follow-up preserves this integration tree. Windows Python 3.14.6; validation WSL Python 3.14.4/PyYAML 6.0.3/packaging 26.0.
- Full central integration checker: FAIL (pre-existing or unadopted contracts outside this scoped update; not treated as PASS). Findings:

```text
DOC-01 .hass-standards.json: readmes must be [README.md, README.ko.md]
HA-02 custom_components/vson/manifest.json: categories requires 1–3 actual product categories (HA-02 project policy)
TEST-08 tests/components/vson/test_init.py: Required contract file is missing
TEST-08 tests/components/vson/test_config_flow.py: Required contract file is missing
TEST-08 tests/components/vson/test_binary_sensor.py: Required contract file is missing
TEST-08 tests/components/vson/test_sensor.py: Required contract file is missing
TEST-08 tests/components/vson/test_coordinator.py: Required contract file is missing
HA-13 custom_components/__init__.py: Required contract file is missing
HA-11 custom_components/vson/translations/ko.json: Unresolved Core translation reference
HA-11 custom_components/vson/translations/en.json: English deployment translations must match strings.json source
TEST-08 tests/__init__.py: must exist and be empty
TEST-08 tests/components/__init__.py: must exist and be empty
TEST-08 tests/components/vson/__init__.py: must exist and be empty
TEST-03 tests/conftest.py: must match the central template exactly
TEST-08 tests/components/vson/conftest.py: [Errno 2] No such file or directory: '/mnt/d/Source/Github/.hacs-custom-zip/hass-vson/tests/components/vson/conftest.py'
TEST-08 tests/components/vson/test_init.py: real HA lifecycle tests are required
CI-02 .github/workflows/tests.yml: name and events must match the central template (actual default branch)
CI-01 .github/workflows/tests.yml: central reusable workflow pinned to reviewed full SHA required
CI-02 .github/workflows/validate.yml: name and events must match the central template (actual default branch)
CI-01 .github/workflows/validate.yml: central reusable workflow pinned to reviewed full SHA required
CI-01 .github/workflows/validate.yml: central standards composite action pinned to full SHA required
```

- Existing CI workflows are preserved, except hass-kocom-smarthome where matching reviewed central references are synchronized. Existing support minimum and prior exceptions remain.
- Independent review and remote CI: tracked in this branch's pull request; merge requires resolved actionable findings and successful applicable checks. No real release upload, device or new real HA runtime validation is claimed by these local packaging checks.

## Release 1.4.0 preparation

Rebased on `069078005fdae393a03a28d351bd22625c8bf8d9`, preserving the 1.3.0 ZIP workflow, HACS ZIP selection, Downloads badges and historical adoption records. The user authorized PR creation, squash merge and a release with GitHub-generated notes. Both local HA environments passed all 36 tests again after rebase. PR #10 remote validation identified `iot_class: local_poll` as invalid; corrected to `local_polling` and reran CI before merge. Final remote results are available on [PR #10](https://github.com/eigger/hass-vson/pull/10).


## 2026-10-25 중앙 검사기 부분 갱신 검증

- 검토한 중앙 SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`; 적용 시작 커밋: `9ed5c63609b5ed72f9af1c0c82991d1529375ef1`.
- 범위: 중앙 pin·standards-ref·검토 기준 기록 정합화 및 누락 standards job 추가. HA 구현·요구 버전은 유지합니다.
- 로컬: Python 3.14.5 / PyYAML 6.0.3, `python scripts/check_integration.py <target>` (검토한 중앙 source에서 실행): FAIL — 아래 미충족 항목을 확인했으며 성공으로 표시하지 않음.
- actionlint: PASS. PR CI·독립 리뷰 결과는 PR 링크와 check 결과를 확인합니다. 이 로컬 결과만으로 전체 채택 완료를 주장하지 않습니다.
- 수정 전에도 최신 검사기로 검사 시 10개 진단이 있었습니다. 이번 검사기가 드러내는 잔여 항목은 다음과 같습니다. 승인 예외나 실패 무시를 추가하지 않았습니다.

```text
DOC-01 .hass-standards.json: readmes must be [README.md, README.ko.md]
HA-02 custom_components/vson/manifest.json: categories requires 1–3 actual product categories (HA-02 project policy)
TEST-08 tests/components/vson/test_binary_sensor.py: Required contract file is missing
HA-13 custom_components/__init__.py: Required contract file is missing
HA-11 custom_components/vson/translations/ko.json: Unresolved Core translation reference
HA-11 custom_components/vson/translations/en.json: English deployment translations must match strings.json source
```
- 독립 리뷰: 별도 review_checker_rollout 담당자가 19개 리포의 workflow 69개·기존 job 100개를 구조 비교했습니다. 새 CI 회귀 지적 없음. 기존 job ID·입력·권한·지원 최소와 통합 코드 보존 및 새 standards job의 중앙 템플릿 일치 확인. 실행 변경 없는 이 기록 추가 전 작업 트리를 검토했습니다.


## 2026-10-25 CI 실패 보완 검증

- 이전 부분 갱신의 실패 진단을 실제 수정했습니다. 표준 README 관리 영역과 실제 설치 앵커를 중앙 렌더러로 적용하고, 제품 기능에 근거한 manifest categories 및 검토 근거를 기록했습니다. 기존 제품별 사용 설명·지원 최소·회귀 테스트를 보존합니다.
- 범위: custom_components namespace 파일, 정확한 중앙 루트 테스트 설정·빈 package 파일, domain fixture 관리 영역을 보완했습니다. 기존 HA fixture와 통신 mock은 유지합니다.
- 실제 배포용 영어 문자열과 strings.json을 정합화했습니다. 한국어 번역 키·placeholder를 유지합니다.
- 기존 실제 HA 연결·실패 복구·진행 중 poll 취소 회귀를 test_binary_sensor.py로 옮겨 연결/문제 엔티티 검증을 올바른 플랫폼 파일에 배치했습니다. 기존 단위·회귀 테스트를 삭제하지 않았습니다.
- 원격 Hassfest는 categories를 지원하는 검토 Core `ec18d8b25d1ee39aa8b85a72a170e42bee33228c`의 공식 validator 경로를 사용합니다. 통합 지원 최소를 올리지 않습니다.
- 현재 환경 실제 버전: `{"python": "3.14.5", "homeassistant": "2026.10.2", "pytest-homeassistant-custom-component": "0.13.373"}`. 각 리포 별도 격리 환경에서 의존성을 설치하고 pip check PASS.
- `python -m pytest tests/components/vson/ -q`: **36 passed**, skip 없음. 최신 중앙 검사기·actionlint·Ruff lint/format·git diff --check PASS.
- 최소 HA 조합과 최종 head 원격 CI는 이 PR의 갱신된 checks 결과로 확인합니다. 실물 기기·실제 외부 API/서버 검증은 수행하지 않았습니다.
- 독립 리뷰: 주 담당 root가 해당 작업 트리를 검토했습니다. 제품 분류의 실제 기능 근거, 기존 테스트 보존·의미 있는 파일 이동, fixture 역할 alias, 번역 및 README 관리 영역을 확인했으며 manifest 키 순서 지적 수정 후 추가 회귀 지적 없음.


### 2026-10-25 Standards workflow 분리 검증

- 분리 시작 커밋: `0b4f45eafdcb3272c0416d87181584b878855879`; 검토 중앙 소스 `ca740d88b32fa5dcbc94c41fce2908450c76ed50` (중앙 PR #24). Validate는 HACS/Hassfest job을 그대로 유지하며 중앙 job만 standards.yml로 이동하고 표시 이름을 Standards로 변경합니다.
- 독립 리뷰: root 구현의 19개 리포에 대해 별도 fix_scale_atflee_ci 담당자가 Validate job 19개와 이동 job 19개의 YAML 정의를 비교했습니다. 파일 이동·표시 이름 외 실제 검사 단계·이벤트·권한·timeout·입력 변경 없음. 중앙 위치 인식 변경은 root가 별도 독립 리뷰했습니다.
- 로컬: 새 중앙 검사기·actionlint·diff 검사 PASS. 중앙 전체232개·관련38개 회귀 테스트와 양 배치19개 동등성 검사 PASS. 모든 대상 기본 브랜치의 branch protection·rulesets 조회에서 필수 검사 이름 설정이 없어 이름 변경으로 인한 대기 충돌 없음. 원격 CI는 이 PR의 최신 head에서 확인합니다.
- 검사 기준을 추가하거나 완화하지 않았으며 기존 inline 배치도 같은 기준으로 지원합니다. 실제 runtime·지원 최소·의존성은 이 파일 분리에서 변경하지 않습니다.

## 2026-10-25 중앙 immutable release 참조 전환

- 요청/범위: 사용자 요청으로 `hass-vson`의 중앙 workflow/action 참조를 `v1.0.0`으로, `standards-ref`를 `44349ee5621eea5d80e5c427f7a2435d2c2491bb`으로 전환. manifest·hacs·requirements·통합 코드·테스트·지원 최소 및 caller-owned CI 설정은 변경하지 않음.
- 기준 대상: 기본 브랜치 base `eb247f689bba34371f641907a2453255cc16be56`. 중앙 release는 `manage_integration.py verify-release`로 published/non-prerelease/immutable 및 peeled SHA 일치를 원격 확인.
- 실제 검증: Python 3.14 중앙 `check_integration.py` 변경 전/후, changed workflow actionlint, `git diff --check`, reference-only 범위 assert를 실행. 이번 refs-only 변경에서는 HA/device 테스트를 재실행하지 않았고 PR CI/병합은 대기.
- 리뷰: 중앙 generated reference-only 결과로 GOV-05 자체 검토; 별도 교차 검토는 조율자가 수행 예정. 기존 실패·미검증은 PASS로 재분류하지 않음.
