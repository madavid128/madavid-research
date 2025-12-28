![on-push](../../actions/workflows/on-push.yaml/badge.svg)
![on-pull-request](../../actions/workflows/on-pull-request.yaml/badge.svg)
![on-schedule](../../actions/workflows/on-schedule.yaml/badge.svg)

# Michael A. David — Research Portfolio

This repository powers my personal research website (Jekyll + Lab Website Template).

- Live site: https://michaeladavid.com
- Repo: `madavid128/madavid-research`

My research integrates spatial histopathology, transcriptomics, and medical imaging using machine learning to study post‑traumatic musculoskeletal conditions (contracture and osteoarthritis).

## Local preview (Docker)

1) Start the local site:
- `bash .docker/run.sh`

Tip:
- If you type `run.sh` and get `command not found`, that’s expected — the script is at `.docker/run.sh`.

2) View it:
- Open `http://localhost:4000`

3) Stop it:
- Press `Ctrl+C` in the terminal running Docker.

4) If it gets stuck, force restart:
- `docker rm -f lab-website-renderer`
- `bash .docker/run.sh`

Notes:
- Most edits (pages, `_data/*`, styles, scripts) are picked up automatically via hot reload.
- You only need to re-run Docker if the container is stopped or becomes unresponsive.
- Tip: on mobile, the nav closes automatically after you tap a link, and there’s a “back to top” button after scrolling.
- Tip: press `/` (or `Ctrl+K` / `⌘K`) on any page to open the global search overlay.
- Tip: global search covers pages, publications, news/blog, pictures/art, and people (collaborators + trainees).
- Tip: if search results seem outdated, hard refresh (⌘⇧R / Ctrl+Shift+R) or restart Docker to rebuild `search.json`.

## Common workflows (copy/paste)

### Start the site
- `bash .docker/run.sh`

### Update the galleries (CSV → YAML)
- `python tools/gallery_from_csv.py export --out tools/gallery_master.csv`
- `python tools/gallery_from_csv.py validate --csv tools/gallery_master.csv`
- `python tools/gallery_from_csv.py build --csv tools/gallery_master.csv`

This also generates:
- `_data/home_feature_images.yaml` (which images appear in Home highlights)
- `_data/project_area_images.yaml` (which images appear in Projects feature cards)
- `_data/header_backgrounds.yaml` (optional rotating home header backgrounds)
- `_data/page_share_images.yaml` (optional: social share previews picked from gallery images)

CSV columns used for these:
- `home_slot`: `publications`, `projects`, `team`, `art`, `pictures`
- `project_area`: `cartilage`, `tendon`, `imaging-ml`, `other`
- `project_area_rank`: optional integer (lower = higher priority) when multiple images are assigned to the same `project_area`
- `project_page_section`: `cartilage`, `tendon`, `imaging-ml`, `other` (adds images to project subpages without affecting the main Projects cards)
- `project_page_rank`: optional integer (lower shows earlier within the project subpage gallery)
- `header_background`: `true/false` (only applied on Home)
- `header_background_rank`: optional integer (lower shows earlier)
- `share_page`: `home`, `publications`, `projects`, `team`, `art`, `pictures`, `updates` (uses that image as the page’s `og:image`)
- `share_page_rank`: optional integer (lower wins) when multiple rows set the same `share_page`

Notes:
- `home_slot` is **not** a boolean. If you accidentally put `TRUE` in `home_slot`, `validate` will fail; `TRUE` belongs in `featured` (for gallery highlights) or `header_background` (for rotating home header images).
- `share_page` is optional. If you don’t set it, the site uses the default share card (`images/share.jpg`) or the per-section share cards (`images/share-<section>.jpg`).
- If your spreadsheet editor accidentally shifts columns, use the preview HTML to spot it quickly:
  - `python tools/gallery_from_csv.py preview --csv tools/gallery_master.csv`
  - Output: `tools/gallery_master_preview.html`

### Project pages: per-area image galleries (optional)

Each project subpage (`projects/cartilage/`, `projects/tendon/`, etc.) can show an **Images** gallery.
To add images:
- In `tools/gallery_master.csv`, set `project_page_section` to `cartilage` / `tendon` / `imaging-ml` / `other` on one or more rows.
- Use `project_area` / `project_area_rank` only when you want to change the **main Projects page** feature-card images.
- Rebuild YAML: `python tools/gallery_from_csv.py build --csv tools/gallery_master.csv`
- If needed, regenerate published images: `python tools/watermark_galleries.py`

### Home header background rotation (optional)

The rotating header is enabled automatically when:
- `header_background=true` is set on **2+** CSV rows, and
- you rebuild YAML (`python tools/gallery_from_csv.py build ...`) which writes `_data/header_backgrounds.yaml`.

Timing:
- Default is `interval_ms: 14000` (~14 seconds) in `_data/header_backgrounds.yaml`.
- To change it, edit `_data/header_backgrounds.yaml` `interval_ms` (or tell me and I can make it configurable via CSV).

Behavior notes:
- Rotation is enabled **only on the Home page** (`/`). Other pages always use their static header (`page.header` or `site.header`).
- The Home page starts on the default header image (`site.header`) and then begins rotating after ~`interval_ms`.
- While the page is open, it does not automatically “return” to the default image; it keeps cycling through the list. Reloading the page starts at the default again.

### Preview the CSV with thumbnails (helps avoid mistakes)
- `python tools/gallery_from_csv.py preview --csv tools/gallery_master.csv`
- Open `tools/gallery_master_preview.html` in your browser.

### Create a starter gallery CSV from images (directory → CSV)

If you’re starting fresh (or you added a batch of new files under `images/originals/`), you can generate a starter `tools/gallery_master.csv` by scanning a directory:

- `python tools/gallery_from_csv.py scan --dir images/originals --out tools/gallery_master.csv`

Then edit titles/tags/years in the CSV and run the normal build steps:

- `python tools/gallery_from_csv.py validate --csv tools/gallery_master.csv`
- `python tools/gallery_from_csv.py build --csv tools/gallery_master.csv`

### Regenerate watermarked images (originals → images/wm/)
- `python -m pip install -r tools/requirements-watermark.txt`
- `python tools/watermark_galleries.py --force`

### Quick site checks (before pushing)
- `python -m pip install -r tools/requirements-site-check.txt`
- `python tools/site_health_check.py`

## Global search (header magnifying glass)

This site has a built-in search overlay (no Google dependency):
- Open it: click the magnifying glass, press `/`, or press `Ctrl+K` / `⌘K`
- It searches across: nav pages + subpages, projects, publications, news/blog items, pictures, and scientific art
- It’s powered by a build-time JSON index at `search.json` → served at `/search.json`

If you update `_data/citations.yaml`, `_data/news.yaml`, `_data/projects.yaml`, or add new pages, and search results don’t change:
- Restart the local Docker site (it rebuilds the Jekyll output)
- Or hard refresh your browser to bypass cached `/search.json`

## Social sharing preview (OpenGraph / iMessage / Slack)

Social previews use the OpenGraph image (`og:image` / `twitter:image`). This site is configured to use `images/share.jpg`.

To regenerate the share image from your MAD icon:
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png`

### Per-page share images (optional)

Any page can override the social preview image by setting `share:` in its front matter, for example:
- `share: images/share-projects.jpg`

This repo includes a few per-page share images already:
- `images/share-home.jpg`
- `images/share-projects.jpg`
- `images/share-publications.jpg`
- `images/share-art.jpg`
- `images/share-pictures.jpg`
- `images/share-team.jpg`
- `images/share-updates.jpg`

To regenerate them:
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-home.jpg --subtitle "Translational Orthopedics | Machine Learning | Multimodal Imaging | Scientific Art"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-projects.jpg --subtitle "Projects | Translational Orthopedics | Machine Learning | Multimodal Imaging | Scientific Art"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-publications.jpg --subtitle "Publications | Translational Orthopedics | Machine Learning | Multimodal Imaging | Scientific Art"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-art.jpg --subtitle "Scientific Art | Translational Orthopedics | Machine Learning | Multimodal Imaging"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-pictures.jpg --subtitle "Pictures | Translational Orthopedics | Machine Learning | Multimodal Imaging | Scientific Art"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-team.jpg --subtitle "Team | Collaborators | Trainees | Mentorship"`
- `python tools/make_share_image.py --icon web-app-manifest-512x512.png --out images/share-updates.jpg --subtitle "News/Blog | Translational Orthopedics | Machine Learning | Multimodal Imaging | Scientific Art"`

Notes:
- If you change `_config.yaml` `url`/`baseurl`, the absolute `og:image` URL will change.
- Sharing apps often cache previews. If the image doesn’t update right away after a deploy, try sharing a different URL (e.g., add `?v=2`) or wait for the cache to expire.

## Sitemap / robots (SEO basics)

This site includes:
- `robots.txt` (tells crawlers they can index the site and where the sitemap is)
- `/sitemap.xml` (auto-generated list of pages for search engines)

You usually don’t “use” the sitemap directly; it exists so Google/Bing can discover new pages reliably.

SEO note:
- SEO = “search engine optimization” (how easily search engines and social apps can understand/preview your site).
- For this repo, SEO is mostly: good page descriptions, OpenGraph image (`images/share.jpg`), and the sitemap/robots files.

## Analytics (optional)

This site currently loads:
- **Rybbit** (existing): included via `_includes/analytics.html`.

Optional additional analytics:
- **GoatCounter** (privacy-friendly; no cookies by default).

To enable GoatCounter:
1) Create a GoatCounter site (https://www.goatcounter.com/)
2) Set `_config.yaml`:
   - `analytics.goatcounter.endpoint: "https://YOURCODE.goatcounter.com/count"`

Notes:
- GoatCounter is injected only in **production** (not local Docker), so local development stays clean.
- Sharing previews and SEO are unrelated to analytics.

## Blog posts

Blog posts live in `_posts/` and render under the **News/Blog** tab.

- Create a new post: `_posts/YYYY-MM-DD-title.md`
- Recommended front matter:
  - `title: ...`
  - `author: michael-david` (matches `_members/michael-david.md`)
  - `tags: [tag1, tag2]`
  - optional: `image: images/background.jpg`

## Publications + word cloud

The Publications page displays:
- the full publications list (`_data/citations.yaml`)
- a word cloud (`images/publications-wordcloud.png`)
- clickable “top terms” (`_data/publications_terms.yaml`)
- a “Download all (BibTeX)” file (`downloads/publications.bib`)

These are generated by the citation pipeline (`python _cite/cite.py`) and by the GitHub Actions workflow `.github/workflows/update-citations.yaml`.

If you run the pipeline locally, set an email for NCBI requests:
- `export NCBI_EMAIL="you@domain.edu"`

The single-file BibTeX download is generated automatically by the citation pipeline.
To regenerate it manually:
- `python tools/export_citations_bibtex.py`

## Collaborator map

The interactive collaborator map (on `team/` and `collaborators/`) is driven by `_data/collaborators_map.csv`.
Add one row per person/institution and include `lat`/`lon` (decimal degrees) for the marker to appear.

Recommended columns:
- `name` (required)
- `status` (`current` or `past`)
- `department`, `institution`, `city`, `region`, `country`
- `first_year`, `last_year` (enables the time slider)
- `lat`, `lon`
- `link` (absolute URL or site‑relative path like `contact`)
- `tags` (separate with `;`, e.g. `collaborator;institution`)
- optional: `papers`, `affiliation`, `institutions` (semicolon list)

### Update collaborators (manual CSV)

1) Edit `_data/collaborators_map.csv`
2) Ensure each row you want on the map has `lat` and `lon`
3) Refresh your local site (hot reload should pick it up; otherwise restart Docker)

### Bootstrap collaborators from PubMed (optional)

This writes `_data/collaborators_map.csv` (it does not change the Jekyll build logic).

1) Create a venv:
- `python3 -m venv .venv`
- `source .venv/bin/activate`

2) Install deps:
- `python -m pip install -r tools/requirements-collaborators.txt`

3) Build collaborator CSV from PubMed:
- `python tools/pubmed_to_collaborators_map.py --email you@domain.edu`

Notes:
- Rerunning preserves curated fields (status/tags/links/lat/lon) by default.
- To disable merging, pass `--no-merge-existing`.

4) Optional: geocode to fill `lat/lon` (rate limited / sometimes unavailable):
- `python tools/pubmed_to_collaborators_map.py --email you@domain.edu --geocode`

If geocoding fails with `HTTP Error 503`, retry later or increase retries:
- `python tools/pubmed_to_collaborators_map.py --email you@domain.edu --geocode --geocode-retries 10`

## Trainees map

The trainees map uses:
- `_data/trainees.yaml` (trainee entries with `start`/`end`, e.g. `April 2021`, `Present`)
- `_data/trainee_institutions.yaml` (institution → location + lat/lon)

The map UI includes a year slider and play button:
- **Active**: shows trainees active in that year
- **To date**: shows trainees who have started by that year (ended trainees display as “Past”)

On `collaborators/` and `team/`, directories also have a **Table** view (sortable) for fast scanning.

## Galleries (Pictures / Scientific Art)

`pictures/` and `art/` use a lightweight gallery + lightbox:
- Data: `_data/pictures.yaml`, `_data/art.yaml`
- Rendering: `_includes/gallery.html`
- Shared “Prints & permissions” copy: `_includes/prints-permissions.html`
- JS: `_scripts/gallery.js`
- Styles: `_styles/gallery.scss`

Replace placeholder SVGs under `images/` with real images (JPG/PNG/WebP) and update the corresponding `_data/*.yaml` entries.

### Watermarked images (discourage casual reuse)

The site uses **gallery images** from `images/wm/`. These files are **committed** to the repo. Originals are kept **out of the repo** under `images/originals/` (ignored by git), so only processed copies are published.

By default, the watermark script applies watermarks only to filenames starting with:
- `nature`
- `science`
- `music`
- `sports`
All other gallery images are copied into `images/wm/` without a watermark.

Workflow:

1) Place originals in `images/originals/` using the same filenames as referenced in `_data/pictures.yaml` and `_data/art.yaml`.
2) Generate watermarked copies into `images/wm/` (commit these files):
    - `python -m pip install -r tools/requirements-watermark.txt`
    - `python tools/watermark_galleries.py`

Supported formats:
- For best portability, gallery YAML uses web-friendly formats: `.jpg` / `.jpeg` / `.png` (the script also generates `.webp`).
- If your CSV/YAML row lists a source as `.heic/.heif` or `.tif/.tiff`, the CSV build step normalizes the `image:` value to the web output (`.jpg` or `.png`) and the watermark script will find the original by stem and convert as needed.
- HEIC/HEIF originals (`.heic` / `.heif`) are supported when `pillow-heif` is installed (included in `tools/requirements-watermark.txt`).

Notes:
- Keep `_data/pictures.yaml` / `_data/art.yaml` pointing at `images/...` (not `images/wm/...`). The site **renders from** `images/wm/` automatically when watermarking is enabled in `_config.yaml`.
- If you rename originals to include a year suffix (example: `group_photo-2021.jpeg`), the watermark script can still find them even if YAML references `group_photo.jpeg` (and vice-versa). If you want the year to display on the card, use the `-YYYY` filename suffix in the YAML `image:` path.
- The script also generates smaller thumbnails in `images/wm/thumb/`. Gallery grids load thumbnails for speed, and the full-resolution image loads when you click.

Keeping originals:
- If you only want to keep originals for watermarked categories (e.g., `nature`, `science`, `music`), you can delete other originals after `images/wm/` is generated. The script will skip entries whose originals are missing as long as the corresponding file already exists in `images/wm/`.

Note:
- The home page highlights reference images like `images/science_0.png`. Those files are served from `images/wm/` too, so keep highlight images listed in `_data/pictures.yaml` or `_data/art.yaml` so the watermark script will generate/copy them.

Make it lighter/darker:
- `python tools/watermark_galleries.py --force --opacity 0.12` (lighter)
- `python tools/watermark_galleries.py --force --opacity 0.25` (darker)

Notes:
- Watermarks are a deterrent; screenshots are always possible.
- WebP encoding can be slow for very large images. To speed it up:
  - Use a faster method: `python tools/watermark_galleries.py --force --webp-method 2`
  - Or skip WebP generation entirely: `python tools/watermark_galleries.py --force --no-webp`
- If your committed `images/wm/` files feel too large, you can downscale during watermark generation:
  - `--max-edge 2400` (default) limits the long edge for the full-size file
  - `--thumb-edge 640` (default) controls gallery thumbnails
- If you removed/renamed images, you can delete unreferenced outputs in `images/wm/`:
  - `python tools/watermark_galleries.py --force --clean`
- The script writes `_data/watermark_build.yaml` to force Jekyll to rebuild and refresh browser caches for updated images (helpful on Docker-mounted volumes).
- If you want to override the output folder, pass `--out-dir ...`.
- Change which files get watermarks with `--watermark-prefixes nature,science,music`.
- If you change prefixes/opacity/angle and existing images don’t update, rerun with `--force`.
- TIFF originals (`.tif` / `.tiff`) are converted to PNG for the site. If YAML references `images/foo.png` but your original is `images/originals/foo.tiff`, the script will still find it (stem match).

### Years + descriptions (optional)

You can add a one-sentence description to any gallery card using `subtitle:` in `_data/pictures.yaml` / `_data/art.yaml` (leave it blank for now and fill later).

You can also add `alt:` for better accessibility (a short, literal description of what’s in the image). If omitted, the site falls back to the displayed title.

If your filename ends with `-YYYY` (example: `nature_42-2021.jpeg`), the gallery will automatically display the year badge. You can also set an explicit `year:` field per item.

Galleries are sorted by `year` / `-YYYY` when available (most recent first). Items without a year suffix sort after the year-tagged items; within a year (or among unknown-year items), `date:` is used as a secondary tiebreaker.

### Tag vocabulary (recommended)

Keeping tags consistent makes filtering and search feel “complete”.

Suggested tag sets:
- Pictures (professional): `team`, `group`, `mentors`, `milestone`, `phd`, `portrait`, `poster`, `talk`, `conference`, `news`, `media`
- Pictures (personal): `nature`, `music`, `sports`, `beyond the lab`, `outdoors`
- Scientific art: `art`, `scientific art`, plus any domain tags you want (example: `imaging`)

Notes:
- Prefer singular nouns and consistent casing (`machine learning` not `machine-learning`).
- Avoid creating near-duplicates (example: pick one of `talk` vs `speaking`; you can always add `speaking` later if you want it).

### CSV workflow for subtitles (recommended)

If you prefer editing in a spreadsheet, use `tools/gallery_subtitles.py` to export and merge subtitles/alts.

Export templates:
- `python tools/gallery_subtitles.py export --data _data/pictures.yaml --out tools/subtitles_pictures.csv`
- `python tools/gallery_subtitles.py export --data _data/art.yaml --out tools/subtitles_art.csv`

Edit the CSV columns:
- `subtitle`: shown **only** in the lightbox when an image is clicked
- `alt`: accessibility text for the image (recommended)

Merge back into YAML (won’t overwrite existing values unless `--overwrite`):
- `python tools/gallery_subtitles.py merge --data _data/pictures.yaml --csv tools/subtitles_pictures.csv`
- `python tools/gallery_subtitles.py merge --data _data/art.yaml --csv tools/subtitles_art.csv`

Note:
- If you use the CSV-first pipeline (`tools/gallery_master.csv`), you can edit `subtitle` and `alt` there instead and skip this separate subtitle CSV workflow.

### CSV-first gallery pipeline (non-coder friendly)

If you want **one spreadsheet to control everything** (image, title, tags, year, subtitles, alt text), use `tools/gallery_from_csv.py`.

This makes `tools/gallery_master.csv` the source of truth and (re)generates:
- `_data/pictures.yaml`
- `_data/art.yaml`

1) Install the tiny dependency (PyYAML):
- `python -m pip install -r tools/requirements-gallery-csv.txt`

2) Export your current YAML into a starter master CSV (only needed once):
- `python tools/gallery_from_csv.py export --out tools/gallery_master.csv`

3) Edit the CSV in Excel / Google Sheets (then save as CSV).

4) Build YAML from the CSV:
- `python tools/gallery_from_csv.py build --csv tools/gallery_master.csv`

Optional: validate before building
- `python tools/gallery_from_csv.py validate --csv tools/gallery_master.csv`

Optional: highlights
- To add a **Highlights** strip (top 4) on Pictures and Scientific Art, set:
  - `featured=true`
  - optional `featured_rank=1..4` (controls ordering)
  - Then rebuild and preview as usual.

Optional: wire images into the Home + Projects pages
- In `tools/gallery_master.csv`, you can also select images for:
  - Home page Highlights: set `home_slot` to one of `publications`, `projects`, `team`, `art`
  - Project area cards: set `project_area` to one of `cartilage`, `tendon`, `imaging-ml`, `other`
- Then rebuild YAML:
  - `python tools/gallery_from_csv.py build --csv tools/gallery_master.csv`

Optional: thumbnail preview (recommended)
- CSV files can’t reliably embed image thumbnails (CSV is plain text), but you can generate a local HTML preview:
  - `python tools/gallery_from_csv.py preview --csv tools/gallery_master.csv`
  - Open `tools/gallery_master_preview.html` in your browser.

5) If you’re using watermarked images, regenerate `images/wm/` after YAML changes:
- `python tools/watermark_galleries.py`

Bootstrap from a folder (optional):
- If you want to generate a starter `tools/gallery_master.csv` from a directory listing (no YAML required), run:
  - `python tools/gallery_from_csv.py scan --dir images/originals --out tools/gallery_master.csv`
  - This guesses `collection`, `title`, `tags`, and `year` from filenames. Review/edit afterwards.

Notes:
- The CSV uses `tags` separated by `;` (example: `nature; outdoors; beyond the lab`).
- Keep `image` values as `images/<filename>` (NOT `images/wm/<filename>`). The site can map to `images/wm/` automatically at render time.
- In the CSV, `image` can be either `my_photo.jpg` or `images/my_photo.jpg` (both are accepted). The build script normalizes to `images/...`.
- The CSV `image` should include the extension (recommended). If you forget it (e.g., `nature_42`), the build script will try to infer the correct filename by searching `images/originals/`, then `images/wm/`, then `images/`. If multiple extensions exist for the same stem, it will ask you to specify the exact filename.
- Originals can be `.heic/.heif` or `.tif/.tiff`. The CSV/YAML should still use web-friendly extensions (`.jpg`/`.png`); the watermark script will find the original by stem and convert as needed.
- `subtitle` is shown only when an image is clicked (lightbox), not on the gallery cards.
- `date` should be `YYYY-MM-DD` (recommended). The build script also accepts `M/D/YY` from spreadsheets and converts it automatically.

### Verify originals vs gallery lists

If you add/remove originals, use this quick check to ensure every file in `images/originals/` is referenced by `_data/pictures.yaml` or `_data/art.yaml`, and vice‑versa:

```bash
python - <<'PY'
import yaml
from pathlib import Path

root = Path('.').resolve()
orig_dir = root / 'images' / 'originals'
exts = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.tif', '.tiff', '.JPG', '.heic', '.heif'}
actual = {p.name for p in orig_dir.iterdir() if p.is_file() and p.suffix in exts}

ref = set()
for data_file in [root/'_data'/'pictures.yaml', root/'_data'/'art.yaml']:
    data = yaml.safe_load(data_file.read_text()) or []
    for item in data:
        if isinstance(item, dict):
            img = item.get('image')
            if isinstance(img, str) and img.startswith('images/'):
                ref.add(Path(img).name)

print("Missing:", sorted(ref - actual))
print("Extra:", sorted(actual - ref))
PY
```

Interpretation:
- `Missing`: remove those entries from YAML **or** add the originals to `images/originals/`.
- `Extra`: remove those originals **or** add them to the appropriate YAML file.

Licensing note:
- This repository uses the BSD 3‑Clause license (`LICENSE.md`). Helper scripts in `tools/` follow the same license unless explicitly stated otherwise.

### Optional: generate WebP variants

If you add JPG/PNG photos, you can optionally generate `.webp` variants (served automatically when present):

- Install Pillow: `python -m pip install Pillow`
- Run: `python tools/make_webp.py images`

## Manual publications (e.g., dissertation)

If an item is not on PubMed, add it to `_data/sources.yaml`. The cite pipeline will include it alongside automated sources without affecting PubMed/ORCID ingestion.

## Icons

The site uses Font Awesome classes for most icons (see `_data/types.yaml` and per‑page `nav.icon` front matter).

### Generate a full icon set (static PNG/ICO/SVG + animated GIFs)

`make_mad_icons.py` reads `web-app-manifest-512x512.png` and generates:
- PNGs: `apple-touch-icon.png`, `favicon-96x96.png`, `web-app-manifest-192x192.png`, `web-app-manifest-512x512.png`
- `favicon.ico` (16/32/48/64)
- `favicon.svg` (wrapper pointing at `web-app-manifest-512x512.png`)
- Animated GIFs (electric‑sign effect) at multiple sizes
- A zip bundle `MAD_icons.zip` (generated; ignored by git)

1) Create a venv (if you don’t already have one):
- `python3 -m venv .venv`
- `source .venv/bin/activate`

2) Install Pillow:
- `python -m pip install Pillow`

3) Run:
- `python make_mad_icons.py`

Outputs:
- `dist_icons/` (generated files; ignored by git)
- `MAD_icons.zip` (generated; ignored by git)

To apply the **static** icons to the website, copy these from `dist_icons/` to the repo root (overwrite existing):
- `apple-touch-icon.png`
- `favicon-96x96.png`
- `favicon.ico`
- `favicon.svg`
- `web-app-manifest-192x192.png`
- `web-app-manifest-512x512.png`

Animated favicon support varies by browser. The GIFs will always work as normal images on pages, but may not animate in the browser tab.

## Background image (network style)

To generate a dark abstract “network” header background (teal/green nodes + lines):
- `python tools/make_network_background.py`

Default output:
- `images/background.jpg` (2400×1350)

Useful options:
- `python tools/make_network_background.py --width 1920 --height 1080`
- `python tools/make_network_background.py --seed 128` (deterministic)

## Licensing notes

The repository’s default license is `LICENSE.md` (BSD 3‑Clause).

_Built with [Lab Website Template](https://greene-lab.gitbook.io/lab-website-template-docs)._
