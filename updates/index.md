---
title: News/Blog
description: News, announcements, and blog posts.
nav:
  order: 6
  icon: fa-regular fa-newspaper
  tooltip: News and blog
---

# {% include icon.html icon="fa-regular fa-newspaper" %}News/Blog

Short updates, announcements, and occasional longer-form posts; plus a running list of talks, interviews, and press.

{% include section.html %}

## News {#news}

{% include search-box.html %}
{% include search-info.html %}

{% include tags.html tags="update, award, collaboration, outreach, art, software, publication" %}

{% include news-list.html data="news" %}

{% include section.html %}

## Blog {#blog}

{% include search-box.html %}
{% include tags.html tags=site.tags %}
{% include search-info.html %}

{% include list.html data="posts" component="post-excerpt" %}

{% include section.html %}

## Media {#media}

Talks, interviews, press, and other public-facing updates. I add items here as they happen (typically a few times per year).

{% include search-box.html %}
{% include search-info.html %}

{% include tags.html tags="talk, interview, press, update, outreach" %}

{% assign media = site.data.media | sort: "date" | reverse %}
<div class="grid media-grid">
  {% for item in media %}
    {% assign year = item.date | date: "%Y" %}
    {% capture subtitle_with_year %}{{ item.subtitle }} · {{ year }}{% endcapture %}
    {%
      include card.html
      title=item.title
      subtitle=subtitle_with_year
      description=item.description
      link=item.link
      image=item.image
      tags=item.tags
      style="small"
    %}
  {% endfor %}
</div>
