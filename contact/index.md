---
title: Contact
description: Email and location for collaborations and opportunities.
nav:
  order: 8
  icon: fa-regular fa-envelope
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

I welcome collaborations, questions, and opportunities related to research, analytics, or data‑driven art.

<div class="contact-mailto" data-contact-mailto data-email="michael.david@cuanschutz.edu">
  <div class="contact-mailto-title">Contact me about…</div>
  <div class="contact-mailto-grid">
    <label class="contact-mailto-field">
      <span>Topic</span>
      <select data-contact-topic>
        <option value="Collaboration">Collaboration</option>
        <option value="Mentoring">Mentoring</option>
        <option value="Speaking invitation">Speaking invitation</option>
        <option value="Scientific art / outreach">Scientific art / outreach</option>
        <option value="Other">Other</option>
      </select>
    </label>

    <label class="contact-mailto-field">
      <span>Your name (optional)</span>
      <input type="text" inputmode="text" autocomplete="name" data-contact-name placeholder="Name">
    </label>

    <label class="contact-mailto-field contact-mailto-field--full">
      <span>Message (optional)</span>
      <textarea rows="4" data-contact-message placeholder="A few details to help me respond quickly…"></textarea>
    </label>
  </div>

  <button type="button" class="button" data-style="solid" data-contact-send>
    {% include icon.html icon="fa-regular fa-envelope" %}
    <span>Open email draft</span>
  </button>
  <div class="contact-mailto-note">Opens your email client; nothing is submitted.</div>
</div>

## Collaboration & mentorship

**Best topics to email about**
- Research collaborations (especially imaging + machine learning + spatial biology)
- Speaking invitations and seminars
- Mentorship opportunities (students/trainees)
- Scientific art / outreach partnerships

**Collaboration** — I partner on projects involving:
- Spatial histopathology + AI
- Medical imaging (MRI/CT) + radiomics
- Transcriptomics/multi‑omics integration
- Reproducible analysis pipelines

**Mentorship** — If you’re interested in collaborating or mentoring opportunities, I’m happy to chat and help define a project with clear scope and measurable deliverables.

**Response** — I do my best to reply within a few business days.

{%
  include button.html
  type="email"
  text="michael.david@cuanschutz.edu"
  link="michael.david@cuanschutz.edu"
%}
{%
  include button.html
  type="linkedin"
  text="LinkedIn"
  link=site.links.linkedin
  style="bare"
%}
{%
  include button.html
  type="github"
  text="GitHub"
  link=site.links.github
  style="bare"
%}
{%
  include button.html
  type="address"
  tooltip="My campus research location on Google Maps for easy navigation"
  link="https://www.google.com/maps/place/P18:+Research+Complex+1+-+North+(RC1-N)/@39.7454581,-104.8393807,17z/data=!3m1!4b1!4m6!3m5!1s0x876c634e7f1ea3f3:0x96535fe0772cff19!8m2!3d39.7454581!4d-104.8393807!16s%2Fg%2F11x9jgtm1?entry=ttu&g_ep=EgoyMDI1MTAyOS4yIKXMDSoASAFQAw%3D%3D"
%}

{% include section.html %}

## Quick links

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

{% capture col1 %}

{%
  include figure.html
  image="images/MichaelDavid_headshot.jpeg"
  caption="Email is the best way to reach me."
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/background.jpg"
  caption="Based at the University of Colorado Anschutz Medical Campus."
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}
