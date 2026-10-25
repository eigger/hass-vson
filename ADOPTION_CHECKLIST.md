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
