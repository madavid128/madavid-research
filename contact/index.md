---
title: Contact
nav:
  order: 5
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

I welcome collaborations, questions, and opportunities to discuss research, analytics, or data-driven art!

{%
  include button.html
  type="email"
  text="michael.david@cuanschutz.edu"
  link="michael.david@cuanschutz.edu"
%}
{%
  include button.html
  type="phone"
  text="N/A"
  link="+1-111-111-1111"
%}
{%
  include button.html
  type="address"
  tooltip="My campus research location on Google Maps for easy navigation"
  link="https://www.google.com/maps/place/P18:+Research+Complex+1+-+North+(RC1-N)/@39.7454581,-104.8393807,17z/data=!3m1!4b1!4m6!3m5!1s0x876c634e7f1ea3f3:0x96535fe0772cff19!8m2!3d39.7454581!4d-104.8393807!16s%2Fg%2F11x9jgtm1?entry=ttu&g_ep=EgoyMDI1MTAyOS4yIKXMDSoASAFQAw%3D%3D"
%}

{% include section.html %}

{% capture col1 %}

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

{% capture col1 %}
Collaboration

{% endcapture %}

{% capture col2 %}
Curosity

{% endcapture %}

{% capture col3 %}
Courage

{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
