---
layout: landing
title: Home
---

I am a quantitative researcher. This site collects condensed, public versions of my research projects. Each project page covers the question, the method, and what I found, with a link to the code. I evaluate every strategy against pre-registered pass rules and realistic costs, and I report the results whether or not they make money.

## Projects

{% include project-cards.html %}

## Blog

{% assign projects = site.projects | sort: "order" %}
{% for pr in projects %}
**{{ pr.title }}**
{% assign posts = site.posts | where: "project", pr.slug | sort: "series" %}
{% for po in posts %}
{{ po.series }}. [{{ po.title }}]({{ po.url | relative_url }})
{% endfor %}
{% endfor %}

All posts, with summaries, are on the [Blog]({{ '/blog/' | relative_url }}) page.

## Links

- [Stat arb code on GitHub](https://github.com/suhjy1/statarb-portfolio)
- [Crypto up/down code on GitHub](https://github.com/suhjy1/trading_crypto_showcase)
- [GitHub profile](https://github.com/suhjy1)
