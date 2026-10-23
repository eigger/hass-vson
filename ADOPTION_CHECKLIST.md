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
