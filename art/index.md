---
title: Scientific Art
description: Scientific visualization and data-driven art, including programs I founded and run.
nav:
  order: 4
  icon: fa-solid fa-palette
  tooltip: Scientific art
---

# {% include icon.html icon="fa-solid fa-palette" %}Scientific Art

{% assign jumps = "" | split: "," %}
{% assign jumps = jumps | push: "programs|Programs" | push: "prints-permissions|Prints & permissions" | push: "gallery|Gallery" %}
{% include page-jumps.html items=jumps %}

I create and curate scientific visualization and data-driven artwork. I also founded and run the following Art in Science programs:

{% include section.html %}

## Programs {#programs}

These programs are part of how I share science more broadly; building community around the idea that research can be rigorous and beautiful at the same time.

{%
  include alert.html
  type="info"
  content="I founded and run Art in Science programs at the University of Delaware, CU Orthopedics, and the Orthopaedic Research Society (ORS)."
%}

{% include section.html %}

{% capture col1 %}
### Art in Science (University of Delaware)
I started and ran the Art in Science program at UDel (2014 to 2018).

{%
  include button.html
  link="https://sites.udel.edu/art-in-science/"
  text="Art in Science at UDel"
  icon="fa-solid fa-palette"
  style="solid"
%}
{% endcapture %}

{% capture col2 %}
### Art in Science Showcase (CU Orthopedics)
I started and run the Art in Science showcase at CU Orthopedics (2023 to present).

{%
  include button.html
  link="https://medschool.cuanschutz.edu/orthopedics/research/events/research-symposium/abstract-submission/art-in-science-award"
  text="Art in Science Showcase at CU Ortho"
  icon="fa-solid fa-award"
  style="solid"
%}
{% endcapture %}

{% capture col3 %}
### ORS Art x Science
I started and run ORS Art x Science (2024 to present).

{%
  include button.html
  link="https://www.ors.org/artxscience/"
  text="ORS Art x Science"
  icon="fa-solid fa-atom"
  style="solid"
%}
{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}

{% include section.html %}

## Prints & permissions {#prints-permissions}

{% include prints-permissions.html %}

These are scientific images I’ve collected across my career; spanning projects, datasets, and imaging modalities. I hope they convey the beauty of nature in the scientific realm and offer a small glimpse into the kinds of patterns and moments that keep me curious.

{% include section.html %}

## Gallery highlights {#gallery}

{%
  include alert.html
  type="info"
  content="Tip: click any image to view it larger."
%}

{% include gallery-highlights.html data="art" limit=4 watermark="true" %}

{% include section.html %}

{% include search-box.html %}
{% include search-info.html %}
{% assign art_tags = "" | split: "," %}
{% for item in site.data.art %}
  {% assign art_tags = art_tags | concat: item.tags %}
{% endfor %}
{% include tags.html tags=art_tags %}

{% include gallery.html data="art" watermark="true" %}
