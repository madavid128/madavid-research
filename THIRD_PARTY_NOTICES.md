# Third-party notices

This repository and website use third-party software.

## Website template

- Lab Website Template (Greene Lab) — BSD 3‑Clause License (see `LICENSE.md`)

## Client-side libraries (loaded via CDN)

- Plotly.js — MIT License: https://github.com/plotly/plotly.js/blob/master/LICENSE
- Popper.js — MIT License: https://github.com/floating-ui/floating-ui/blob/master/LICENSE
- Tippy.js — MIT License: https://github.com/atomiks/tippyjs/blob/master/LICENSE
- Mark.js — MIT License: https://github.com/julmot/mark.js/blob/master/LICENSE
- Font Awesome Free — License: https://fontawesome.com/license/free

## Data sources and usage policies

- NCBI E‑utilities (PubMed): https://www.ncbi.nlm.nih.gov/books/NBK25500/
- OpenStreetMap Nominatim (optional geocoding): https://operations.osmfoundation.org/policies/nominatim/

## Citation tooling

The citation pipeline under `_cite/` installs Python packages listed in `_cite/requirements.txt`, each with its own license.

Additional packages used by the citation pipeline:
- wordcloud — MIT License: https://github.com/amueller/word_cloud/blob/main/LICENSE

## Optional tooling (local scripts)

- `tools/pubmed_to_collaborators_map.py` uses NCBI E‑utilities (PubMed) and optionally OpenStreetMap Nominatim for geocoding; both are subject to their respective usage policies.
