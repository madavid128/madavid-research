---
title: Home
description: Biomedical engineer advancing bioinformatics, machine learning, and multimodal imaging for translational orthopedics.
share: images/background.jpg
---

# Michael A. David, PhD

Biomedical engineer advancing bioinformatics, machine learning, and multimodal imaging for translational orthopedics, while collaborating with and mentoring diverse colleagues and trainees.

<div class="home-cta">
  {%
    include button.html
    link="research"
    text="Publications"
    icon="fa-solid fa-book-open"
    style="solid"
  %}
  {%
    include button.html
    link="projects"
    text="Projects"
    icon="fa-solid fa-wrench"
    style="solid"
  %}
  {%
    include button.html
    link="contact"
    text="Contact"
    icon="fa-regular fa-envelope"
    style="bare"
  %}
</div>

I’m an Instructor in Orthopedics at the University of Colorado Anschutz Medical Campus. I build end‑to‑end machine learning workflows for spatial histopathology, transcriptomics/multi‑omics, and medical imaging to study post‑traumatic joint conditions (contracture and osteoarthritis).

{% include section.html %}

## Highlights

{% capture text %}

My research integrates digital histopathology, MRI/CT radiomics, and multi‑omics to study musculoskeletal health and disease, with an emphasis on reproducible, open data analytical workflows.

{%
  include button.html
  link="research"
  text="See publications"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/MichaelDavid_headshot.jpeg"
  link="research"
  title="Publications"
  text=text
%}

{% capture text %}

Four major project areas spanning imaging, spatial biology, multimodal analytics, and translational orthopedics.

{%
  include button.html
  link="projects"
  text="Explore project areas"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/website_icon3.png"
  link="projects"
  title="Projects"
  flip=true
  style="bare"
  text=text
%}

{% capture text %}

My research allows me to work with wonderful students, colleagues, mentees, and mentors. Together, we bridge engineering, imaging, and data science to tackle the complexities of musculoskeletal health.

{%
  include button.html
  link="team"
  text="Meet my research team and collaborations"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/background.jpg"
  link="team"
  title="My Research Team and Collaborations"
  text=text
%}

{% capture text %}

Scientific visualization and data‑driven art — including Art in Science programs I founded and run.

{%
  include button.html
  link="art"
  text="Explore scientific art"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image="images/art-in-science-01.svg"
  link="art"
  title="Scientific Art"
  flip=true
  text=text
%}

{% include section.html %}

{%
  include button.html
  link="contact"
  text="Get in touch"
  icon="fa-regular fa-envelope"
  style="solid"
%}

{% include section.html %}

## News

{% include news-list.html data="news" limit=3 %}

{%
  include button.html
  link="updates"
  text="See News/Blog"
  icon="fa-regular fa-newspaper"
  style="bare"
%}
