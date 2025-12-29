---
title: Projects
description: Software, datasets, and research outputs from Michael A. David, PhD.
nav:
  order: 2
  icon: fa-solid fa-wrench
  tooltip: Project areas and tools
---

# {% include icon.html icon="fa-solid fa-wrench" %}Projects

This page summarizes four major project areas, plus selected software and tools.

{%
  include alert.html
  type="info"
  content="New to the site? The FAQ has a short glossary (radiomics, multi-omics, etc.)."
%}

{%
  include button.html
  link="faq"
  text="FAQ / glossary"
  icon="fa-regular fa-circle-question"
  style="bare"
%}

Browse by methods:

{% include search-chips.html link="research" chips="\"tag: spatial histopathology\"|Spatial histopathology; \"tag: radiomics\"|Radiomics; \"tag: multi-omics\"|Multi-omics; \"tag: imaging\"|Imaging; \"tag: machine learning\"|Machine learning; \"tag: reproducible\"|Reproducible pipelines" %}

{% include section.html %}

## Project areas {#project-areas}

{% assign project_img_cartilage = site.data.project_area_images.cartilage | default: "images/projects-area-01.svg" %}
{% assign project_img_tendon = site.data.project_area_images.tendon | default: "images/projects-area-02.svg" %}
{% assign project_img_imaging = site.data.project_area_images["imaging-ml"] | default: "images/projects-area-03.svg" %}
{% assign project_img_other = site.data.project_area_images.other | default: "images/projects-area-04.svg" %}

{% capture text %}
Mechanisms of cartilage and synovium degeneration and repair in osteoarthritis and post-traumatic disease, linking tissue biology with translational outcomes.
{%
  include button.html
  link="research"
  text="Related publications"
  icon="fa-solid fa-book-open"
  style="bare"
  flip=true
%}
{%
  include button.html
  link="projects/cartilage"
  text="Learn more"
  icon="fa-solid fa-arrow-right"
  style="bare"
  flip=true
%}
{% endcapture %}
{%
  include feature.html
  image=project_img_cartilage
  title="Cartilage + Synovium Biology"
  text=text
%}

{% capture text %}
Tendon and peritendinous tissue injury, remodeling, and healing across scales, integrating biomechanics and molecular pathways to understand function and recovery.
{%
  include button.html
  link="research"
  text="Related publications"
  icon="fa-solid fa-book-open"
  style="bare"
  flip=true
%}
{%
  include button.html
  link="projects/tendon"
  text="Learn more"
  icon="fa-solid fa-arrow-right"
  style="bare"
  flip=true
%}
{% endcapture %}
{%
  include feature.html
  image=project_img_tendon
  title="Tendon + Peritendinous Tissue Biology"
  flip=true
  text=text
%}

{% capture text %}
Multimodal imaging (MRI/CT), radiomics, and machine learning to connect imaging signatures with tissue-level phenotypes and clinical outcomes.
{%
  include button.html
  link="research"
  text="Related publications"
  icon="fa-solid fa-book-open"
  style="bare"
  flip=true
%}
{%
  include button.html
  link="projects/imaging-ml"
  text="Learn more"
  icon="fa-solid fa-arrow-right"
  style="bare"
  flip=true
%}
{% endcapture %}
{%
  include feature.html
  image=project_img_imaging
  title="Imaging + Machine Learning"
  text=text
%}

{% capture text %}
Other musculoskeletal projects spanning joint injury and fibrosis, computational workflows, and cross-cutting translational collaborations.
{%
  include button.html
  link="research"
  text="Related publications"
  icon="fa-solid fa-book-open"
  style="bare"
  flip=true
%}
{%
  include button.html
  link="projects/other"
  text="Learn more"
  icon="fa-solid fa-arrow-right"
  style="bare"
  flip=true
%}
{% endcapture %}
{%
  include feature.html
  image=project_img_other
  title="Other"
  flip=true
  text=text
%}

{% include section.html %}

## Software & tools {#software-tools}

Selected repositories and automation scripts (maps, galleries, and publication updates).

{% include search-box.html %}
{% include search-info.html %}

{% include tags.html tags="software, tools, dataset, resource, website" %}

{% include list.html component="card" data="projects" filter="group == 'software-tools'" %}
