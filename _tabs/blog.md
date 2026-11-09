---
layout: page
icon: fas fa-pen-nib
order: 2
---

Research notes from my projects. Each one covers a single question in more depth than the project pages: the method, the evidence, and what I concluded.
{: .projects-intro }

{% assign projects = site.projects | sort: "order" %}
{% for pr in projects %}
## {{ pr.title }}

[Project overview]({{ pr.url | relative_url }}) · [Code]({{ pr.repo }})

{% include post-cards.html project=pr.slug %}
{% endfor %}
