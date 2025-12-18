---
title: Team
description: Collaborators, mentees, and research partnerships.
nav:
  order: 3
  icon: fa-solid fa-users
  tooltip: About our team
share: images/background.jpg
---

# {% include icon.html icon="fa-solid fa-users" %}Team

I collaborate with clinicians, engineers, and scientists across imaging, computation, and musculoskeletal biology. I’m always excited to work with curious, kind, and rigorous people.

{% include section.html %}

## Principal investigator
{% include list.html data="members" component="portrait" filter="role == 'principal-investigator'" %}

{% include section.html %}

## Collaboration & mentorship

{% capture col1 %}
### Collaboration

I partner on projects involving:
- spatial histopathology + AI
- medical imaging (MRI/CT) + radiomics
- transcriptomics/multi‑omics integration
- reproducible analysis pipelines
{% endcapture %}

{% capture col2 %}
### Mentorship

If you’re interested in collaborating or mentoring opportunities, I’m happy to chat and help define a project with clear scope and measurable deliverables.

{%
  include button.html
  link="contact"
  text="Contact"
  icon="fa-regular fa-envelope"
  style="solid"
%}
{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html %}

## Collaborators

{% include collaborator-map.html %}

{%
  include button.html
  link="collaborators"
  text="Full collaborator directory"
  icon="fa-solid fa-globe"
  style="bare"
%}

{% include section.html %}

## Current collaborations

Add and manage your current collaborators in `_data/current_collaborations.yaml`.

<div class="grid">
  {% assign emptyarray = "" | split: "," %}
  {% assign collabs = site.data.current_collaborations | default: emptyarray %}
  {% for c in collabs %}
    {%
      include card.html
      title=c.name
      subtitle=c.subtitle
      description=c.description
      link=c.link
      image=c.image
      tags=c.tags
      style="small"
    %}
  {% endfor %}
</div>

{% include section.html %}

## Trainees

Trainee locations are grouped by institution (current vs past).

{% include trainee-map.html %}

{% include trainees.html %}

{% include section.html %}

## Mentorship & joining

I enjoy mentoring trainees and collaborating across disciplines. If you’re interested in working together, please reach out with a short note about your background, your interests, and what you’d like to learn or build.

**Good fits**
- Biomedical engineering, orthopedics, biomechanics, imaging, and computational biology
- Machine learning (especially interpretable ML) applied to real translational questions
- People who value rigor, reproducibility, and supportive collaboration

{%
  include button.html
  link="about"
  text="About me"
  icon="fa-regular fa-user"
  style="solid"
%}
{%
  include button.html
  link="contact"
  text="Contact"
  icon="fa-regular fa-envelope"
  style="solid"
%}

{% include section.html %}
