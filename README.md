# Jung Yong Suh — research portfolio & blog

Built on the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) Jekyll theme (v7.6, from `chirpy-starter`), with two additions:
a **Projects** tab and a **plug-and-play HTML post** pipeline.

## Publish (one time)

1. Create a **public** repo named `suhjy1.github.io` and push this folder to `main`.
2. Find-and-replace `suhjy1` and  everywhere (`_config.yml`, `_data/contact.yml`, `_projects/*.md`, `_tabs/about.md`).
3. Add a square photo at `assets/img/avatar.png` (or clear `avatar:` in `_config.yml`).
4. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
   (Chirpy needs Actions; the "Deploy from a branch" option will not work.)
5. Each push runs `.github/workflows/pages-deploy.yml`. The site is live in about 2 minutes.

## Write a Markdown post

`_posts/YYYY-MM-DD-slug.md`:

```yaml
---
title: "Post title"
description: One-line summary (shown under the title and on the home page).
date: 2026-11-12 09:00:00
categories: [Research, Prediction Markets]   # max two levels
tags: [copulas, pricing]                    # lowercase
project: copula-parlay-engine               # optional: lists the post on that project page
image:
  path: /assets/img/covers/parlay.png       # optional cover
  alt: Caption
pin: true                                   # optional: stick to top of home
---
```

- Math (MathJax, on for every post): `$$x^2$$` inline, or `$$` on its own lines with blank lines around it for display.
- Callouts: a blockquote followed by `{: .prompt-tip }` (or `.prompt-info`, `.prompt-warning`, `.prompt-danger`).
- Full writing guide: <https://chirpy.cotes.page/posts/write-a-new-post/>

## Plug-and-play HTML posts

Generate a post as HTML (with Claude, a notebook export, anything), drop it in `inbox/`, then:

```bash
python tools/new_post.py inbox/my-post.html \
  --project copula-parlay-engine \
  --categories "Research, Prediction Markets" --tags "copulas, pricing" --move
```

| Input | Result |
|---|---|
| Full document (`<!doctype html>…`) | Served as-is with its own CSS/JS (`layout: standalone`), plus a small "← back" link. Still listed on the home page, in archives, categories and tags. |
| Fragment (`<h1>…<p>…<h2>…`) | Rendered inside the normal Chirpy post: sidebar, table of contents, MathJax, tags. |
| Full document + `--mode site` | Takes the `<body>` only and renders it as a normal post. |

- Title, description, cover, and date are inferred; override them with `--title --summary --image --date --slug`.
- Relative images next to the file are copied to `assets/img/posts/<slug>/`.
- Content is wrapped in `{% raw %}`, so `{{ }}` in JS is safe.
- Prompts for generating either kind of post: **`tools/POST_PROMPT.md`**.
- `inbox/` and `tools/` are never published.

## Add a project

`_projects/slug.md`, with front matter `title, slug, summary, status, year, order, tags, stack, image, repo` (optional `demo`).
It appears on the Projects tab, sorted by `order`. Posts with `project: slug` are listed on its page automatically.

## Preview locally (optional)

```bash
bundle install
bash tools/run.sh        # http://127.0.0.1:4000
```

## Before making anything public

Strip employer-proprietary code, data, parameters, and client names from the condensed repos and posts.
