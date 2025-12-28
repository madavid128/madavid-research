---
title: Imaging + Machine Learning
description: Multimodal imaging, radiomics, and interpretable ML for translational orthopedics.
---

# Imaging + Machine Learning

Multimodal imaging (MRI/CT), radiomics, and machine learning to connect imaging signatures with tissue‑level phenotypes and clinical outcomes.

**Key methods:** {% include search-chips.html link="research" chips="radiomics; imaging; \"machine learning\"|Machine learning; \"interpretable machine learning\"|Interpretable ML" %}
{% include glossary-links.html items="glossary-radiomics|Radiomics; glossary-interpretable-ml|Interpretable ML; glossary-multi-omics|Multi-omics" %}

{% include section.html %}

## Key outputs
- **Dataset/tool**: Selected code + tools live on my GitHub (`https://github.com/{{ site.links.github }}`) and on the Projects page under [Software & tools](projects#software-tools).
- **Paper**: Search the Publications page for imaging/ML/radiomics work: {% include search-chips.html link="research" chips="\"machine learning\"|Machine learning; radiomics; imaging" %}
- **Figure**: Representative images appear in [Images](#images).

{% include section.html %}

## What I work on
- Imaging-derived biomarkers and radiomics features
- Interpretable models that link imaging to biology
- Reproducible pipelines for translational deployment

{% include section.html %}

## Key questions
- What imaging signatures track tissue‑level phenotypes and outcomes?
- How can models stay interpretable enough for translational decision‑making?
- Which workflows generalize across datasets and sites?

## Methods I use
- Radiomics ([glossary](faq#glossary-radiomics)) and multimodal imaging feature extraction (MRI/CT where available)
- Interpretable machine learning ([glossary](faq#glossary-interpretable-ml)) and careful validation
- Reproducible pipelines (versioned code, containers, and traceable metadata)

{% include section.html %}

## Related publications
{% include search-chips.html link="research" chips="machine learning|Machine learning; radiomics; imaging" %}

{% include section.html %}

## Images

{% assign filter_primary = "project_page_section == 'imaging-ml'" %}
{% assign filter_fallback = "project_area == 'imaging-ml'" %}
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
    content="To add images to this project page, set `project_page_section=imaging-ml` for one or more rows in `tools/gallery_master.csv`, then run the gallery build + watermark commands. (`project_area` is reserved for the main Projects page cards.)"
  %}
{% endunless %}
