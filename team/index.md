---
title: Team
description: Collaborators, mentees, and research partnerships.
nav:
  order: 3
  icon: fa-solid fa-users
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Team

{% assign jumps = "" | split: "," %}
{% assign jumps = jumps | push: "principal-investigator|Principal investigator" | push: "collaboration-mentorship|Collaboration & mentorship" | push: "collaborators|Collaborators" | push: "trainees|Trainees" | push: "joining|Get involved" %}
{% include page-jumps.html items=jumps %}

I collaborate with clinicians, engineers, and scientists across imaging, computation, and musculoskeletal biology. I’m always excited to work with curious, kind, and rigorous people.

{%
  include alert.html
  type="info"
  content="Want to connect? I’m happy to chat about collaboration ideas, mentoring opportunities, or project scoping; the fastest way is via email on the Contact page."
%}

{% include section.html %}

## Principal investigator {#principal-investigator}
{% include list.html data="members" component="portrait" filter="role == 'principal-investigator'" %}

{% include section.html %}

## Collaboration & mentorship {#collaboration-mentorship}

{% capture col1 %}
### Collaboration

I partner on projects involving:
- spatial histopathology + AI
- medical imaging (MRI/CT) + radiomics
- transcriptomics and multi-omics integration
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

## Collaborators {#collaborators}

{% include collaborator-map.html %}

{%
  include button.html
  link="collaborators"
  text="Full collaborator directory"
  icon="fa-solid fa-globe"
  style="bare"
%}

{% include section.html %}

<h2 id="current-collaborations" data-jump-ignore>Current collaborations</h2>

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

## Trainees {#trainees}

Trainee locations are grouped by institution (current vs past).

{% include trainee-map.html %}

<div data-directory data-directory-key="trainees-directory" data-directory-default="details">
  <div class="directory-controls" role="group" aria-label="Trainee directory view">
    <button type="button" class="button" data-style="bare" data-directory-view="details" aria-pressed="true">Details</button>
    <button type="button" class="button" data-style="bare" data-directory-view="table" aria-pressed="false">Table</button>
  </div>

  <div data-directory-pane="details">
    <div class="directory-controls" data-details-controls role="group" aria-label="Trainee list controls">
      <button type="button" class="button" data-style="bare" data-details-action="expand">Expand all</button>
      <button type="button" class="button" data-style="bare" data-details-action="collapse">Collapse all</button>
    </div>
    {% include trainees.html %}
  </div>

  <div data-directory-pane="table" hidden>
    {% include search-box.html %}
    {% include search-info.html %}
    {% include trainees-table.html %}
  </div>
</div>

{% include section.html %}

## Get involved {#joining}

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
