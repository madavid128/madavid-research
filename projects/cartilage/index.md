---
title: Cartilage + Synovium Biology
description: Mechanisms of cartilage and synovium degeneration and repair in osteoarthritis and post-traumatic disease.
---

# Cartilage + Synovium Biology

Mechanisms of cartilage and synovium degeneration and repair in osteoarthritis and post-traumatic disease, linking tissue biology with translational outcomes.

**Key methods:** {% include search-chips.html link="research" chips="\"spatial histopathology\"|Spatial histopathology; transcriptomics; multi-omics; machine learning" %}
{% include glossary-links.html items="glossary-spatial-histopathology|Spatial histopathology; glossary-transcriptomics|Transcriptomics; glossary-multi-omics|Multi-omics; glossary-interpretable-ml|Interpretable ML" %}

{% include section.html %}

## Key outputs
- **Dataset/tool**: Selected code + tools live on my GitHub (`https://github.com/{{ site.links.github }}`) and on the Projects page under [Software & tools](projects#software-tools).
- **Paper**: Search the Publications page for cartilage/synovium work: {% include search-chips.html link="research" chips="cartilage; synovium" %}
- **Figure**: Representative images appear in [Images](#images).

{% include section.html %}

## What I work on
- Early tissue and cellular changes that precede gross degeneration
- Quantitative phenotyping across histology and imaging
- Translational models that connect biology to clinically relevant outcomes

{% include section.html %}

## Key questions
- What early cartilage and synovium changes predict later degeneration?
- How do cartilage and synovium interactions shape inflammation and repair?
- Which pathways are most actionable for translational intervention?

## Methods I use
- Histology + spatial histopathology ([glossary](faq#glossary-spatial-histopathology)) with quantitative image analysis
- Multimodal imaging (microscopy, MRI/CT where appropriate) and reproducible pipelines
- Machine learning and multi-omics ([glossary](faq#glossary-multi-omics)) integration for interpretable insights

{% include section.html %}

## Related publications
{% include search-chips.html link="research" chips="cartilage; synovium; osteoarthritis" %}

{% include section.html %}

## Images

{% assign filter_primary = "project_page_section == 'cartilage'" %}
{% assign filter_fallback = "project_area == 'cartilage'" %}
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
    content="To add images to this project page, set `project_page_section=cartilage` for one or more rows in `tools/gallery_master.csv`, then run the gallery build + watermark commands. (`project_area` is reserved for the main Projects page cards.)"
  %}
{% endunless %}
