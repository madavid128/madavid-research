---
title: Pictures
description: Photos from research, outreach, conferences, and scientific art.
nav:
  order: 5
  icon: fa-regular fa-images
  tooltip: Photos and galleries
---

# {% include icon.html icon="fa-regular fa-images" %}Pictures

How to browse: use the tag chips to filter, click any image to open it, and expand/collapse Nature, Music, and Sports under **Beyond the lab**.

{% include section.html %}

{% include search-box.html %}
{% include search-info.html %}

{% assign picture_tags = "" | split: "," %}
{% for item in site.data.pictures %}
  {% assign picture_tags = picture_tags | concat: item.tags %}
{% endfor %}
{% include tags.html tags=picture_tags %}

{% include section.html %}

## Prints & permissions

{% include prints-permissions.html %}

## Highlights

{% include gallery-highlights.html data="pictures" limit=4 watermark="true" %}

{% include section.html %}


## Lab & mentors

Lab life is where curiosity becomes a shared pursuit; mentors, collaborators, and trainees make the work feel supported and worthwhile.

{% include gallery.html data="pictures" filter="tags && (tags.include?('team') or tags.include?('group') or tags.include?('mentors'))" watermark="true" %}

{% include section.html %}

## Milestones

Moments along the way that shaped my training and career.

{% include gallery.html data="pictures" filter="tags && (tags.include?('milestone') or tags.include?('phd') or tags.include?('portrait'))" watermark="true" %}

{% include section.html %}

## Conferences & talks

Snapshots from posters, presentations, and community events where ideas get tested and new collaborations start.

{% include gallery.html data="pictures" filter="tags && (tags.include?('conference') or tags.include?('poster') or tags.include?('talk') or tags.include?('news') or tags.include?('media'))" watermark="true" %}

{% include section.html %}

## Beyond the lab

Art and nature across the globe; from sea to mountains and our sun; captured in moments that help me reset and stay inspired.

{% assign emptyarray = "" | split: "," %}
{% assign pictures_data = site.data.pictures | default: emptyarray %}

{% assign beyond_nature = pictures_data | data_filter: "tags && tags.include?('nature')" %}
{% assign beyond_music  = pictures_data | data_filter: "tags && tags.include?('music')" %}
{% assign beyond_sports = pictures_data | data_filter: "tags && tags.include?('sports')" %}

<div data-directory-pane="beyond-the-lab">
  <div class="directory-controls" data-details-controls role="group" aria-label="Beyond the lab controls">
    <button type="button" class="button" data-style="bare" data-details-action="expand">Expand all</button>
    <button type="button" class="button" data-style="bare" data-details-action="collapse">Collapse all</button>
  </div>

  <details class="gallery-group">
    <summary>Nature ({{ beyond_nature.size }})</summary>
    {% include gallery.html data="pictures" filter="tags && tags.include?('nature')" watermark="true" %}
  </details>

  <details class="gallery-group">
    <summary>Music ({{ beyond_music.size }})</summary>
    {% include gallery.html data="pictures" filter="tags && tags.include?('music')" watermark="true" %}
  </details>

  <details class="gallery-group">
    <summary>Sports ({{ beyond_sports.size }})</summary>
    {% include gallery.html data="pictures" filter="tags && tags.include?('sports')" watermark="true" %}
  </details>
</div>
