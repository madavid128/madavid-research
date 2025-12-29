---
title: Other Projects
description: Cross-cutting translational collaborations and musculoskeletal projects.
---

# Other Projects

Other musculoskeletal projects spanning joint injury and fibrosis, computational workflows, and cross-cutting translational collaborations.

**Key methods:** {% include search-chips.html link="research" chips="contracture; fibrosis; reproducible; pipelines" %}
{% include glossary-links.html items="glossary-contracture|Contracture; glossary-ptoa|PTOA; glossary-multi-omics|Multi-omics; glossary-interpretable-ml|Interpretable ML" %}

{% include section.html %}

## Key outputs
- **Dataset/tool**: Selected code + tools live on my GitHub (`https://github.com/{{ site.links.github }}`) and on the Projects page under [Software & tools](projects#software-tools).
- **Paper**: Browse related publications: {% include search-chips.html link="research" chips="contracture; fibrosis; osteoarthritis" %}
- **Figure**: Representative images appear in [Images](#images).

{% include section.html %}

## What I work on
- Collaborative projects across institutions and disciplines
- Methods development to support translational pipelines
- New directions and exploratory analyses

{% include section.html %}

## Key questions
- What new collaborations can unlock the next set of translational questions?
- Which analyses or measurements are missing from current workflows?
- Where can a computational approach reduce friction and improve reproducibility?

## Methods I use
- Cross-disciplinary collaboration and project scoping
- Reproducible analysis pipelines and lightweight tooling
- Rapid prototyping (then hardening) for shared use

{% include section.html %}

## Related publications
{% include search-chips.html link="research" chips="contracture; fibrosis; osteoarthritis" %}

{% include section.html %}

## Images

{% assign filter_primary = "project_page_section == 'other'" %}
{% assign filter_fallback = "project_area == 'other'" %}
{% assign filter_active = filter_primary %}

{% assign project_art = site.data.art | data_filter: filter_primary %}
{% assign project_pictures = site.data.pictures | data_filter: filter_primary %}

{% assign needs_fallback = false %}
{% if project_art == nil or project_art.size == 0 %}
  {% if project_pictures == nil or project_pictures.size == 0 %}
    {% assign needs_fallback = true %}
  {% endif %}
{% endif %}

{% if needs_fallback %}
  {% assign project_art = site.data.art | data_filter: filter_fallback %}
  {% assign project_pictures = site.data.pictures | data_filter: filter_fallback %}
  {% assign filter_active = filter_fallback %}
{% endif %}

{% if project_art and project_art.size > 0 %}
  {% include gallery.html data="art" filter=filter_active watermark="true" %}
{% endif %}

{% if project_pictures and project_pictures.size > 0 %}
  {% include gallery.html data="pictures" filter=filter_active watermark="true" %}
{% endif %}

{% assign has_any = false %}
{% if project_art and project_art.size > 0 %}
  {% assign has_any = true %}
{% endif %}
{% if project_pictures and project_pictures.size > 0 %}
  {% assign has_any = true %}
{% endif %}

{% unless has_any %}
  {%
    include alert.html
    type="info"
    content="To add images to this project page, set `project_page_section=other` for one or more rows in `tools/gallery_master.csv`, then run the gallery build + watermark commands. (`project_area` is reserved for the main Projects page cards.)"
  %}
{% endunless %}
