---
title: Tags
description: Browse publications, projects, updates, pictures, and art by tag.
nav:
  order: 10
  icon: fa-solid fa-tags
  tooltip: Browse by tag
---

# {% include icon.html icon="fa-solid fa-tags" %}Tags

Browse the site by tag across pages, publications, projects, updates, pictures, and scientific art.

<div
  class="tags-index"
  data-tags-index
  data-search-url="{{ "/search.json" | relative_url }}{% if jekyll.environment == "development" %}?v={{ site.time | date: "%s" }}{% endif %}"
></div>

