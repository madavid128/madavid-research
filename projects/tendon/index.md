---
title: Tendon + Peritendinous Tissue Biology
description: Tendon and peritendinous tissue injury, remodeling, and healing across scales.
---

# Tendon + Peritendinous Tissue Biology

Tendon and peritendinous tissue injury, remodeling, and healing across scales, integrating biomechanics and molecular pathways to understand function and recovery.

**Key methods:** {% include search-chips.html link="research" chips="histology; biomechanics; repair; \"type 2 diabetes\"|Type 2 diabetes" %}
{% include glossary-links.html items="glossary-multi-omics|Multi-omics; glossary-interpretable-ml|Interpretable ML" %}

{% include section.html %}

## Key outputs
- **Dataset/tool**: Selected code + tools live on my GitHub (`https://github.com/{{ site.links.github }}`) and on the Projects page under [Software & tools](projects#software-tools).
- **Paper**: Search the Publications page for tendon/repair work: {% include search-chips.html link="research" chips="tendon; repair" %}
- **Figure**: Representative images appear in [Images](#images).

{% include section.html %}

## What I work on
- Quantitative measures of tendon structure, cellularity, and mechanics
- Interactions between systemic factors (e.g., metabolic health) and repair
- Translational models that connect biology to functional outcomes

{% include section.html %}

## Key questions
- How do tendon and peritendinous tissues remodel after injury and repair?
- Which systemic factors (e.g., metabolic health) most strongly shape healing?
- What measurements best connect tissue biology to function?

## Methods I use
- Histology and quantitative image analysis (including immunostaining where relevant)
- Preclinical models and functional/biomechanical readouts
- Reproducible analysis pipelines and statistics (with ML when useful)

{% include section.html %}

## Related publications
{% include search-chips.html link="research" chips="tendon; repair; type 2 diabetes|Type 2 diabetes" %}

{% include section.html %}

## Images

{% assign filter_primary = "project_page_section == 'tendon'" %}
{% assign filter_fallback = "project_area == 'tendon'" %}
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
    content="To add images to this project page, set `project_page_section=tendon` for one or more rows in `tools/gallery_master.csv`, then run the gallery build + watermark commands. (`project_area` is reserved for the main Projects page cards.)"
  %}
{% endunless %}
