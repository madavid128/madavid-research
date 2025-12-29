---
title: Home
description: Biomedical engineer advancing bioinformatics, machine learning, and multimodal imaging for translational orthopedics.
page_jumps: "off"
---

# Michael A. David, PhD

{% capture intro_left %}
I’m a biomedical engineer with a PhD and an Instructor in the Department of Orthopedics at the University of Colorado Anschutz Medical Campus.

My work focuses on:
- End-to-end machine learning workflows across spatial histopathology, transcriptomics and multi-omics, and medical imaging
- Clinical and preclinical datasets to study post-traumatic and idiopathic musculoskeletal disease (e.g., contracture and osteoarthritis) in the ankle, knee, hip, elbow, and spine
- Collaboration and mentorship with diverse colleagues and trainees

Outside the lab, I enjoy connecting with nature, music, and good people.
{% endcapture %}

{% capture intro_right %}
<figure class="home-intro-portrait">
  <img
    src="{{ 'images/MichaelDavid_headshot.jpeg' | relative_url }}"
    alt="Michael A. David headshot"
    loading="eager"
  >
</figure>
{% endcapture %}

{% include cols.html col1=intro_left col2=intro_right %}

{% include section.html %}

<div class="home-welcome" aria-label="Welcome">
  <div class="home-welcome-title">Welcome; thanks for visiting.</div>
  <div class="home-welcome-text">
    Browse papers and project areas, or reach out if you’d like to collaborate, invite a talk, or discuss scientific art.
  </div>
  <div class="home-welcome-buttons">
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
      style="solid"
    %}
  </div>
  <div class="home-welcome-small">
    New here? {% include button.html link="faq" text="FAQ / glossary" icon="fa-regular fa-circle-question" style="bare" %}
  </div>
</div>

<div class="home-welcome-small">
  Quick links:
  {% include button.html type="pubmed" text="PubMed" link=site.links.pubmed style="bare" %}
  {% capture scholar_url %}https://scholar.google.com/citations?user={{ site.links.google-scholar }}{% endcapture %}
  {% include button.html type="google-scholar" text="Scholar" link=scholar_url style="bare" %}
  {% include button.html type="orcid" text="ORCID" link=site.links.orcid style="bare" %}
  {% include button.html type="email" text="Contact" link="contact" style="bare" %}
</div>

## Highlights

{% assign home_img_publications = site.data.home_feature_images.publications | default: "images/publications-wordcloud.png" %}
{% assign home_img_projects = site.data.home_feature_images.projects | default: "images/science_20.jpeg" %}
{% assign home_img_team = site.data.home_feature_images.team | default: "images/team_1-2025.jpeg" %}
{% assign home_img_art = site.data.home_feature_images.art | default: "images/science_0.png" %}
{% assign home_img_pictures = site.data.home_feature_images.pictures | default: "images/nature_anschutz-day-2025.jpeg" %}

{% capture text %}

My research integrates digital histopathology, MRI/CT radiomics, and multi-omics to study musculoskeletal health and disease, with an emphasis on reproducible, open data analytical workflows.

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
  image=home_img_publications
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
  image=home_img_projects
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
  image=home_img_team
  link="team"
  title="My Research Team and Collaborations"
  text=text
%}

{% capture text %}

Scientific visualization and data-driven art; including Art in Science programs I founded and run.

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
  image=home_img_art
  link="art"
  title="Scientific Art"
  flip=true
  text=text
%}

{% capture text %}

Photos from lab life, conferences, outreach, and beyond the lab; with watermarked originals in the gallery lightbox.

{%
  include button.html
  link="pictures"
  text="Browse pictures"
  icon="fa-solid fa-arrow-right"
  flip=true
  style="bare"
%}

{% endcapture %}

{%
  include feature.html
  image=home_img_pictures
  link="pictures"
  title="Pictures"
  text=text
%}

{% include section.html %}

## Featured talks

{% assign media = site.data.media | sort: "date" | reverse %}
{% assign featured_media = media | slice: 0, 2 %}
<div class="grid media-grid">
  {% for item in featured_media %}
    {% assign year = item.date | date: "%Y" %}
    {% capture subtitle_with_year %}{{ item.subtitle }} · {{ year }}{% endcapture %}
    {%
      include card.html
      title=item.title
      subtitle=subtitle_with_year
      description=item.description
      link="updates#media"
      image=item.image
      tags=item.tags
      style="small"
    %}
  {% endfor %}
</div>

{%
  include button.html
  link="updates#media"
  text="More talks and media"
  icon="fa-solid fa-arrow-right"
  style="bare"
  flip=true
%}
