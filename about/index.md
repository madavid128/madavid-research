---
title: About
description: Background, values, and personal interests.
nav:
  order: 7
  icon: fa-regular fa-user
  tooltip: About me
share: images/background.jpg
---

# {% include icon.html icon="fa-regular fa-user" %}About

## Work
I’m a biomedical engineer focused on translational orthopedics, combining bioinformatics, machine learning, and multimodal imaging to understand and predict musculoskeletal disease.

{% include section.html %}

## Mentorship and collaboration
I enjoy collaborating across disciplines and mentoring trainees with diverse backgrounds and interests.

{%
  include button.html
  link="team"
  text="Team and collaborators"
  icon="fa-solid fa-users"
  style="solid"
%}
{%
  include button.html
  link="contact"
  text="Contact"
  icon="fa-regular fa-envelope"
  style="bare"
%}

{% include section.html %}

## CV
Instructor, Department of Orthopedics, University of Colorado Anschutz Medical Campus (Colorado Program for Musculoskeletal Research).

Research focus: translational orthopedics using multimodal imaging, bioinformatics, and machine learning to study post‑traumatic joint conditions (contracture and osteoarthritis).

{%
  include button.html
  type="google-scholar"
  text="Google Scholar"
  link=site.links.google-scholar
  style="solid"
%}
{%
  include button.html
  type="orcid"
  text="ORCID"
  link=site.links.orcid
  style="solid"
%}
{%
  include button.html
  type="pubmed"
  text="PubMed"
  link=site.links.pubmed
  style="solid"
%}

{% if site.links.cv and site.links.cv != "" %}
  {%
    include button.html
    link=site.links.cv
    text="Download full CV (PDF)"
    icon="fa-solid fa-download"
    style="bare"
  %}
{% endif %}

{% include section.html %}

## Beyond the lab
Outside of research, I enjoy sports, creative work, and spending time outdoors (including nature photography).

<figure style="margin: 18px 0;">
  <img
    src="{{ 'images/mad-animated.gif' | relative_url }}"
    alt="Animated MAD logo"
    width="192"
    height="192"
    loading="lazy"
    style="display:block; margin: 0 auto; border-radius: 16px; box-shadow: var(--shadow);"
  >
  <figcaption style="text-align:center; color: var(--dark-gray); margin-top: 10px;">
    A little “electric sign” version of my logo.
  </figcaption>
</figure>

{%
  include button.html
  link="pictures?search=&quot;tag: nature&quot;"
  text="Nature pictures"
  icon="fa-regular fa-images"
  style="solid"
%}
{%
  include button.html
  link="pictures?search=&quot;tag: sports&quot;"
  text="Sports"
  icon="fa-solid fa-person-running"
  style="solid"
%}
{%
  include button.html
  link="art"
  text="Scientific art"
  icon="fa-solid fa-palette"
  style="bare"
%}
