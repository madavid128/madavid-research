---
title: Projects
description: Software, datasets, and research outputs from Michael A. David, PhD.
nav:
  order: 2
  icon: fa-solid fa-wrench
  tooltip: Project areas and tools
share: images/background.jpg
---

# {% include icon.html icon="fa-solid fa-wrench" %}Projects

This page summarizes four major project areas, plus selected software and tools.

{% include section.html %}

## Project areas

{% capture text %}
Mechanisms of cartilage and synovium degeneration and repair in osteoarthritis and post‑traumatic disease, linking tissue biology with translational outcomes.
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
  image="images/projects-area-01.svg"
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
  image="images/projects-area-02.svg"
  title="Tendon + Peritendinous Tissue Biology"
  flip=true
  text=text
%}

{% capture text %}
Multimodal imaging (MRI/CT), radiomics, and machine learning to connect imaging signatures with tissue‑level phenotypes and clinical outcomes.
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
  image="images/projects-area-03.svg"
  title="Imaging + Machine Learning"
  text=text
%}

{% capture text %}
Other musculoskeletal projects spanning joint injury and fibrosis, computational workflows, and cross‑cutting translational collaborations.
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
  image="images/projects-area-04.svg"
  title="Other"
  flip=true
  text=text
%}

{% include section.html %}

## Software & tools

{% include search-box.html %}
{% include search-info.html %}

{% include tags.html tags="software, tools, dataset, resource, website" %}

### Featured

{% include list.html component="card" data="projects" filter="group == 'featured'" %}

{% include section.html %}

### More

{% include list.html component="card" data="projects" filter="!group" style="small" %}

{% include section.html %}

{%
  include button.html
  link="art"
  text="Explore Scientific Art"
  icon="fa-solid fa-palette"
  style="solid"
%}

{% include section.html %}

{% capture gh_url %}https://github.com/{{ site.links.github }}{% endcapture %}
{%
  include button.html
  link=gh_url
  text="More on GitHub"
  icon="fa-brands fa-github"
  style="bare"
%}
