# Vson brand assets

The integration bundles its brand images in `custom_components/vson/brand/`,
next to `manifest.json`, so they are included in the HACS release ZIP.

- `icon.png`: 256 × 256 pixels.
- `icon@2x.png`: 512 × 512 pixels, resized from `icon.png` with Lanczos resampling.
- `logo.png`: 512 × 128 pixels.

The icon and logo are copied from the existing
[Home Assistant Vson brand assets](https://github.com/home-assistant/brands/tree/master/custom_integrations/vson).
Their upstream Git blob hashes are `07c2c7fc2da1013884dbe33452616e7f358c56ef`
(`icon.png`) and `4f61a5c4299b38d147b71503d35be4649e55185d` (`logo.png`).
The same images work on light and dark themes because they include their own
red background; separate dark variants are not needed.
