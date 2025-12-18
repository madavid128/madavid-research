---
title: Scientific Art
description: Scientific visualization and data-driven art, including programs I founded and run.
nav:
  order: 4
  icon: fa-solid fa-palette
  tooltip: Scientific art
share: images/background.jpg
---

# {% include icon.html icon="fa-solid fa-palette" %}Scientific Art

I create and curate scientific visualization and data‑driven artwork. I also founded and run the following Art in Science programs:

{% include section.html %}

{%
  include alert.html
  type="info"
  content="I founded and run Art in Science programs at the University of Delaware, CU Orthopedics, and the Orthopaedic Research Society (ORS)."
%}

{% include section.html %}

{% capture col1 %}
### Art in Science (University of Delaware)
I started and run the Art in Science program at UDel.

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
I started and run the Art in Science showcase at CU Orthopedics.

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
I started and run ORS Art x Science.

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

## Gallery

{% include search-box.html %}
{% include search-info.html %}
{% include tags.html tags="art, visualization, imaging, multiomics, outreach, award" %}

{% include gallery.html data="art" %}
