# Standards reference

Reviewed standards SHA: `4fa557eaa7142b87a6cae8b09c249cf50c3865c6`

Source: [eigger/hass-repo-standards](https://github.com/eigger/hass-repo-standards/tree/4fa557eaa7142b87a6cae8b09c249cf50c3865c6).

This is a targeted application for blesession, diagnostic entities, shared HA test infrastructure, reusable test/validation workflows, and bilingual Bluetooth guidance. It is not a claim of full repository standards adoption. Existing HA minimum `2025.1.0`, sensor unique IDs are preserved; the release version is 1.4.0. No exceptions have been approved or invented.

The implementation reuses blesession `0.9.0` for connection ownership, notifications, bounded writes/disconnects, attempt serialization, trace vocabulary, radio facts and retained session reports. WP6003 commands, packet parsing, timing policy and HA entities remain integration responsibilities. No new cross-repository library abstraction or edits to other integrations are needed for this change.

Both reusable workflows are pinned to the reviewed standards SHA. The root HA test fixture and domain fixture guidance come from the central templates. Existing parser, sensor, import and config/options regressions were retained or converted to actual HA tests under `tests/components/vson/`; the fake `homeassistant.*` modules were removed.

See [verification evidence](ADOPTION_CHECKLIST.md). Full metadata/category review, managed README/badge adoption, automated dependency maintenance, central adoption-status updates, remote CI and physical hardware validation are not claimed by this scoped change. The central status table was not modified because this task's changes are confined to hass-vson.

## Earlier ZIP packaging adoption

The previously adopted release workflow and its reviewed SHA remain unchanged. Historical record follows.

# Scoped standards adoption

- Reviewed standards SHA: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`
- Standard: https://github.com/eigger/hass-repo-standards/tree/fd4162c0b93fbe8e109f99c787773ae09ba157e1

Only HACS ZIP release packaging and README badges are adopted in this change. Existing code, support minimum, dependencies, documentation body and CI are preserved. Full standards adoption and real HA verification remain outside this change.


## 2026-10-23 ZIP release and Downloads update

Base commit: `a095f96d18863c76e02f7b5c195fff66ce6987f9`. HACS remains Custom. `hacs.json` now selects `vson.zip`; publishing the next release builds and attaches that integration ZIP through the pinned central action. Analytics Usage is replaced by Downloads. The archive contains tracked integration files at its root. No existing release/tag/assets are modified.

Implementation and review: root; generated release caller reuses the independently reviewed central ZIP contract. Support minimum, manifest, code, dependencies, README body and prior adoption exceptions are preserved. Verification evidence is recorded in ADOPTION_CHECKLIST.md; this scoped update does not establish full standards compliance.
