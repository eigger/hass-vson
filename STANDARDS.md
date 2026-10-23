# Scoped standards adoption

- Reviewed standards SHA: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`
- Standard: https://github.com/eigger/hass-repo-standards/tree/fd4162c0b93fbe8e109f99c787773ae09ba157e1

Only HACS ZIP release packaging and README badges are adopted in this change. Existing code, support minimum, dependencies, documentation body and CI are preserved. Full standards adoption and real HA verification remain outside this change.


## 2026-10-23 ZIP release and Downloads update

Base commit: `a095f96d18863c76e02f7b5c195fff66ce6987f9`. HACS remains Custom. `hacs.json` now selects `vson.zip`; publishing the next release builds and attaches that integration ZIP through the pinned central action. Analytics Usage is replaced by Downloads. The archive contains tracked integration files at its root. No existing release/tag/assets are modified.

Implementation and review: root; generated release caller reuses the independently reviewed central ZIP contract. Support minimum, manifest, code, dependencies, README body and prior adoption exceptions are preserved. Verification evidence is recorded in ADOPTION_CHECKLIST.md; this scoped update does not establish full standards compliance.
