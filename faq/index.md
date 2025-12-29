---
title: FAQ
description: Quick answers and a short glossary for new visitors.
nav:
  order: 9
  icon: fa-regular fa-circle-question
  tooltip: FAQ / glossary
---

# {% include icon.html icon="fa-regular fa-circle-question" %}FAQ

Quick answers for new visitors, plus a short glossary of terms that show up across my projects and publications.

{% assign jumps = "" | split: "," %}
{% assign jumps = jumps | push: "new-here|New here?" | push: "glossary|Glossary" | push: "contact|Contact" %}
{% include page-jumps.html items=jumps %}

{% include section.html %}

## New here? {#new-here}

<div class="start-here" aria-label="Start here">
  <div class="start-here-title">Start here</div>
  <div class="start-here-items">
    <div class="start-here-item">
      {%
        include button.html
        link="research"
        text="Publications"
        icon="fa-solid fa-book-open"
        style="solid"
      %}
      <div class="start-here-desc">Highlighted papers + a full searchable list.</div>
    </div>
    <div class="start-here-item">
      {%
        include button.html
        link="projects"
        text="Projects"
        icon="fa-solid fa-wrench"
        style="solid"
      %}
      <div class="start-here-desc">Four project areas, key questions, and methods.</div>
    </div>
    <div class="start-here-item">
      {%
        include button.html
        link="team"
        text="Team"
        icon="fa-solid fa-users"
        style="solid"
      %}
      <div class="start-here-desc">Collaborators, trainees, and how to get involved.</div>
    </div>
  </div>
</div>

**Where should I start?**  
Start with [Publications](research) (highlighted + full list), then [Projects](projects) (four research areas), then [Team](team) (collaborators + trainees).

**How can I find a specific paper quickly?**  
Use the search icon in the header (or press `/` or `Ctrl/⌘+K`) and type a keyword, author, or year.

**Can I collaborate or propose a project?**  
Yes; I’m happy to talk through ideas and help scope a project with clear deliverables. The fastest way is email.

{% include section.html %}

## Glossary {#glossary}

<p class="small">
  Jump to:
  <a href="#glossary-transcriptomics">Transcriptomics</a>,
  <a href="#glossary-radiomics">Radiomics</a>,
  <a href="#glossary-spatial-histopathology">Spatial histopathology</a>,
  <a href="#glossary-multi-omics">Multi-omics</a>,
  <a href="#glossary-interpretable-ml">Interpretable machine learning</a>,
  <a href="#glossary-ptoa">Post-traumatic osteoarthritis (PTOA)</a>,
  <a href="#glossary-contracture">Contracture</a>.
</p>

<div class="directory-controls" data-details-controls role="group" aria-label="Glossary controls">
  <button type="button" class="button" data-style="bare" data-details-action="expand">Expand all</button>
  <button type="button" class="button" data-style="bare" data-details-action="collapse">Collapse all</button>
</div>

<details id="glossary-transcriptomics">
  <summary><strong>Transcriptomics</strong></summary>
  <p>Measuring gene expression (RNA) to understand which biological programs are active in a tissue or cell population.</p>
</details>

<details id="glossary-radiomics">
  <summary><strong>Radiomics</strong></summary>
  <p>Quantitative features extracted from medical images (e.g., MRI/CT) that can be linked to tissue-level phenotypes or outcomes.</p>
</details>

<details id="glossary-spatial-histopathology">
  <summary><strong>Spatial histopathology</strong></summary>
  <p>Digitized tissue sections with spatial context, enabling measurement of structure, composition, and cell/tissue phenotypes across a slide.</p>
</details>

<details id="glossary-multi-omics">
  <summary><strong>Multi-omics</strong></summary>
  <p>Integrating multiple biological data types (e.g., transcriptomics, proteomics) to understand disease mechanisms and heterogeneity.</p>
</details>

<details id="glossary-interpretable-ml">
  <summary><strong>Interpretable machine learning</strong></summary>
  <p>Models and analyses designed to make the “why” behind predictions understandable (e.g., key features, regions, pathways).</p>
</details>

<details id="glossary-ptoa">
  <summary><strong>Post-traumatic osteoarthritis (PTOA)</strong></summary>
  <p>Osteoarthritis that develops after joint injury, often with early inflammatory and structural changes that can be studied in preclinical and clinical cohorts.</p>
</details>

<details id="glossary-contracture">
  <summary><strong>Contracture</strong></summary>
  <p>Loss of joint range of motion due to fibrosis/stiffening of periarticular tissues after injury or inflammation.</p>
</details>

{% include section.html %}

## Contact {#contact}

If you’d like to collaborate, chat about mentoring, or ask a question about a paper/tool, please reach out via the [Contact](contact) page.
