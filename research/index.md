---
title: Research
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Research

My research integrates spatial histopathology, transcriptomics, and medical imaging using machine learning (ML) to study and diagnose post-traumatic joint conditions of contracture and osteoarthritis. I develop ML models end-to-end to identify tissue and cellular subtypes, phenotypes, and predictive relationships. My ML models are built upon preclinical and clinical datasets involving the ankle, elbow, and knee. 

Topic areas: Machine Learning, Deep Learning, Post-Traumatic Osteoarthritis, Musculoskeletal Biology, Biomedical Engineering, Multi-omics, Medical Imaging, Spatial histopathology.

{% comment %} === PUBMED & SCHOLAR BUTTONS === {% endcomment %}
{% capture scholar_url %}https://scholar.google.com/citations?user={{ site.links.google-scholar }}{% endcapture %}
{% assign orcid = site.links.orcid %}
{% capture pubmed_url %}https://pubmed.ncbi.nlm.nih.gov/?term={{ orcid | uri_escape }}%5Bauid%5D{% endcapture %}
<div class="mb-6 flex flex-wrap gap-3">
  {% include button.html link=pubmed_url text="More on PubMed" icon="fa-solid fa-book" style="solid" %}
  {% include button.html link=scholar_url text="More on Google Scholar" icon="fa-brands fa-google" style="solid" %}
</div>

{% include section.html %}

## Highlighted
{% include citation.html lookup="Open collaborative writing with Manubot" style="rich" %}

{% include section.html %}

## All
{% include search-box.html %}
{% include search-info.html %}
{% include list.html data="citations" component="citation" style="rich" %}
