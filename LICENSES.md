# Licensing overview

The repository’s default license is **BSD 3-Clause** (see `LICENSE.md`).

## Upstream template (Greene Lab)

This repository is a derivative of the Greene Lab **Lab Website Template**. The template itself is BSD 3-Clause licensed; see `LICENSE.md`.

## Custom additions in this repo

In addition to the upstream template, this repository contains custom code and content added by **Michael A. David**. These additions are licensed under BSD 3-Clause (see `LICENSE.md`) unless explicitly stated otherwise in-file.

Custom helper scripts (added for this site):
- `_cite/wordclouds.py`: generate the publications word cloud
- `make_mad_icons.py`: generate static icons plus animated GIF variants
- `tools/gallery_from_csv.py`: CSV-first gallery pipeline (generate `_data/pictures.yaml` and `_data/art.yaml`)
- `tools/gallery_subtitles.py`: spreadsheet workflow for `subtitle` and `alt`
- `tools/generate_third_party_notices.py`: generate and update `THIRD_PARTY_NOTICES.md`
- `tools/make_network_background.py`: generate `images/background.jpg`
- `tools/make_share_image.py`: generate `images/share.jpg` (social previews)
- `tools/make_webp.py`: generate `.webp` variants
- `tools/pubmed_to_collaborators_map.py`: bootstrap collaborator map data from PubMed
- `tools/set_collaborators_active.py`: helper for collaborator statuses
- `tools/watermark_galleries.py`: build `images/wm/` from `images/originals/` (watermarks and conversions)

## What is covered by `LICENSE.md` (BSD 3-Clause)

- The website content, configuration, and code in this repo (including custom scripts under `tools/` and `_cite/`) are covered by `LICENSE.md` unless a file explicitly says otherwise.

## Third-party software (not covered by `LICENSE.md`)

This repository includes or loads third-party software with its own licenses/terms. See `THIRD_PARTY_NOTICES.md` for the authoritative list, including:
- Client-side libraries loaded via CDN (e.g., Plotly, Popper, Tippy, Mark.js, Font Awesome)
- Data source usage policies (e.g., NCBI E-utilities; optional OpenStreetMap Nominatim)
- Python packages used by helper scripts / citation tooling

## Images

Original photos and scientific images are retained privately and are not committed to this repository. The website serves published copies (including watermarked variants) from `images/wm/`.

Third-party libraries and tools used by this site are documented in `THIRD_PARTY_NOTICES.md`.
