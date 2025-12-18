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

**Where should I start?**  
Start with [Publications](research) (highlighted + full list), then [Projects](projects) (four research areas), then [Team](team) (collaborators + trainees).

**How can I find a specific paper quickly?**  
Use the search icon in the header (or press `/` or `Ctrl/⌘+K`) and type a keyword, author, or year.

**Can I collaborate or propose a project?**  
Yes — I’m happy to talk through ideas and help scope a project with clear deliverables. The fastest way is email.

{% include section.html %}

## Glossary {#glossary}

<details>
  <summary><strong>Radiomics</strong></summary>
  <p>Quantitative features extracted from medical images (e.g., MRI/CT) that can be linked to tissue-level phenotypes or outcomes.</p>
</details>

<details>
  <summary><strong>Spatial histopathology</strong></summary>
  <p>Digitized tissue sections with spatial context, enabling measurement of structure, composition, and cell/tissue phenotypes across a slide.</p>
</details>

<details>
  <summary><strong>Multi-omics</strong></summary>
  <p>Integrating multiple biological data types (e.g., transcriptomics, proteomics) to understand disease mechanisms and heterogeneity.</p>
</details>

<details>
  <summary><strong>Interpretable machine learning</strong></summary>
  <p>Models and analyses designed to make the “why” behind predictions understandable (e.g., key features, regions, pathways).</p>
</details>

{% include section.html %}

## Contact {#contact}

If you’d like to collaborate, chat about mentoring, or ask a question about a paper/tool, please reach out via the [Contact](contact) page.
