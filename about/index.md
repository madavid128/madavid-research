---
title: About
description: Background, values, and personal interests.
nav:
  order: 7
  icon: fa-regular fa-user
  tooltip: About me
---

# {% include icon.html icon="fa-regular fa-user" %}About

{% assign jumps = "" | split: "," %}
{% assign jumps = jumps | push: "education|Education" | push: "appointments|Academic appointments" | push: "skills|Research skills" | push: "mentorship|Mentorship and collaboration" | push: "cv|CV" | push: "beyond|Beyond the lab" %}
{% include page-jumps.html items=jumps %}

A quick overview of my research focus, how I like to collaborate and mentor, and a few things I enjoy outside the lab.

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

## Education {#education}

**Doctor of Philosophy (PhD) in Biomedical Engineering**  
*University of Delaware* — Newark, DE (August 2013 – May 2019)
- Dissertation: *Local, Intra-Articular Delivery of Zoledronic Acid as a Disease-Modifying Therapeutic for Post-Traumatic Osteoarthritis*
- Advisor: Christopher Price, PhD
- Committee: Dawn M. Elliott, PhD; Randall L. Duncan, PhD; Jason P. Gleghorn, PhD

**Bachelor of Science (BS) in Biomedical Engineering**  
*University of Rochester* — Rochester, NY (August 2009 – June 2013)
- Concentration: Cell and Tissue Engineering
- Minor: Chemical Engineering

{% include section.html %}

## Academic appointments {#appointments}

<div class="directory-table-wrap" aria-label="Academic appointments">
  <table class="directory-table" style="min-width: 0;">
    <thead>
      <tr>
        <th>Position</th>
        <th>Institution</th>
        <th>Dates</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Instructor</strong><br>Colorado Program for Musculoskeletal Research, Department of Orthopedics</td>
        <td>University of Colorado Anschutz Medical Campus<br>Aurora, CO</td>
        <td>May 2025 – Present</td>
      </tr>
      <tr>
        <td><strong>Research Instructor</strong><br>Colorado Program for Musculoskeletal Research, Department of Orthopedics</td>
        <td>University of Colorado Anschutz Medical Campus<br>Aurora, CO</td>
        <td>March 2022 – April 2025</td>
      </tr>
      <tr>
        <td><strong>Postdoctoral Research Associate</strong><br>Musculoskeletal Soft Tissue Laboratory, Department of Mechanical Engineering &amp; Materials Science</td>
        <td>Washington University in St. Louis<br>St. Louis, MO</td>
        <td>May 2019 – February 2022</td>
      </tr>
      <tr>
        <td><strong>Graduate Research Assistant</strong><br>Mechanotransduction and Mechanobiology Laboratory, Department of Biomedical Engineering</td>
        <td>University of Delaware<br>Newark, DE</td>
        <td>October 2013 – April 2019</td>
      </tr>
      <tr>
        <td><strong>Research Assistant</strong><br>Cartilage Bioengineering Laboratory, Department of Mechanical Engineering</td>
        <td>University of Delaware<br>Newark, DE</td>
        <td>July 2013 – September 2013</td>
      </tr>
      <tr>
        <td><strong>Undergraduate Research Assistant</strong><br>Center for Musculoskeletal Research</td>
        <td>University of Rochester<br>Rochester, NY</td>
        <td>May 2011 – June 2013</td>
      </tr>
    </tbody>
  </table>
</div>

{% include section.html %}

## Research skills {#skills}
I’m a biomedical engineer focused on translational orthopedics, combining bioinformatics, machine learning, and multimodal imaging to understand and predict musculoskeletal disease.

Comprehensive training in imaging, computational analysis, histology, and preclinical musculoskeletal models.

<div class="directory-table-wrap" aria-label="Research skills">
  <table class="directory-table" style="min-width: 0;">
    <thead>
      <tr>
        <th>Area</th>
        <th>Highlights</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Laboratory instruments</strong></td>
        <td>
          MRI (11.74T Agilent; 9.4T Bruker BioSpec 94/20); microscopy (epifluorescence, confocal, multiphoton, polarized light, spectrophotometer);
          biomechanical testing (Instron) and microCT (Scanco); live animal imaging (IVIS/UVP);
          histology processing (processor, embedder, microtome; manual/auto staining + imaging);
          nanoparticle characterization (Litesizer/Zetasizer); flow cytometry (Novocyte).
        </td>
      </tr>
      <tr>
        <td><strong>Laboratory techniques</strong></td>
        <td>
          2D/3D cell culture (agarose/collagen hydrogels); primary cell isolation (chondrocyte, synoviocyte, tenocyte across multiple species);
          tissue explant/co-culture (cartilage + synovium); preclinical joint injury models (mouse knee DMM; rat elbow trauma);
          nanoparticle/liposome drug delivery; histology + IHC, semi-quantitative scoring, digital histopathology;
          spatial transcriptomics; machine learning + bioinformatics.
        </td>
      </tr>
      <tr>
        <td><strong>Computing &amp; analysis</strong></td>
        <td>
          Python, R, MATLAB, Java/Groovy; Docker, CLI, cloud computing.
          Histology/IHC: CT-Fire, NDPI-Nanozoomer, OsteoMeasure, QuPath.
          CT/MRI: CTan, BoneJ, Dragonfly, ITK-SNAP, Seg3D2.4, 3D Slicer.
          Flow/cell cycle: CellProfiler, FCSExpress, NovoExpress.
        </td>
      </tr>
    </tbody>
  </table>
</div>

{% include section.html %}

## Mentorship and collaboration {#mentorship}
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

## CV {#cv}
Download my CV and find my publications/profiles below.

{% assign cv_pdf = "downloads/cv.pdf" | file_exists %}
{% if cv_pdf %}
  {%
    include button.html
    link="downloads/cv.pdf"
    text="Download CV (PDF)"
    icon="fa-solid fa-download"
    style="solid"
  %}
{% endif %}

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

## Beyond the lab {#beyond}
Outside of research, I enjoy music, creative work, and spending time outdoors (including nature photography).

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
  link="pictures?search=&quot;tag: music&quot;"
  text="Music"
  icon="fa-solid fa-music"
  style="solid"
%}
{%
  include button.html
  link="art"
  text="Scientific art"
  icon="fa-solid fa-palette"
  style="bare"
  %}

{% include section.html %}
