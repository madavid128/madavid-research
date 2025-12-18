---
title: Collaborators Map
description: A global view of collaborators and trainees.
---

# {% include icon.html icon="fa-solid fa-globe" %}Collaborators Map

Provide collaborator entries (name + location) and this page plots them on a world map with connection lines to my home base.

{% include section.html %}

{% include collaborator-map.html %}

{% include section.html %}

## Directory

{% include search-box.html %}
{% include search-info.html %}

{% include tags.html tags="collaborator, trainee, institution" %}

<div class="grid">
  {% assign people = site.data.collaborators | sort: "name" %}
  {% if site.data.collaborators_map and site.data.collaborators_map.size > 0 %}
    {% assign people = site.data.collaborators_map | sort: "name" %}
  {% endif %}
  {% for p in people %}
    {% capture subtitle %}{{ p.institution }} — {{ p.city }}{% if p.region and p.region != "" %}, {{ p.region }}{% endif %}, {{ p.country }}{% endcapture %}
    {%
      include card.html
      title=p.name
      subtitle=subtitle
      description=p.description
      link=p.link
      image="images/news-placeholder.svg"
      tags=p.tags
      style="small"
    %}
  {% endfor %}
</div>
