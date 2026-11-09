# Prompts for generating blog posts as HTML

Paste one of these into Claude (or any LLM) along with your notes, code, or results.
Save the output as a `.html` file in `inbox/`, then run:

```bash
python tools/new_post.py inbox/my-post.html --project <slug> --categories "Research, Prediction Markets" --tags "copulas, pricing" --move
```

---

## A. Article post (uses the site's look)

> Write a blog post as an **HTML fragment** (no `<html>`, `<head>`, or `<body>` tags, and no inline CSS) for my Jekyll site.
>
> - First line: `<h1>Title</h1>`, then `<p>` one-sentence summary `</p>`. Both are pulled out automatically.
> - Use only semantic tags: `<h2>`, `<h3>`, `<p>`, `<ul>/<ol>`, `<blockquote>`, `<table>`, `<figure><img><figcaption>`, `<pre><code class="language-python">`.
> - Math (MathJax): inline `\( ... \)`, display `\[ ... \]`.
> - Callouts: `<blockquote class="prompt-tip"><p>…</p></blockquote>` (also `prompt-info`, `prompt-warning`, `prompt-danger`).
> - Images: `<img src="fig1.png" alt="…">` with the file saved next to the HTML.
> - Escape `<`, `>`, `&` inside `<pre><code>`.
> - Tone: precise, first person, written for quant researchers. No marketing language.
> - Topic / material: …

## B. Interactive post (its own page)

> Build a **single self-contained HTML document** (`<!doctype html>` … `</html>`) for a blog post.
>
> - Put a `<title>` (used as the post title) and `<meta name="description" content="…">` (used as the summary) in `<head>`.
> - Inline all CSS and JS. External scripts only from `cdn.jsdelivr.net` (e.g. KaTeX, Plotly, D3, Chart.js).
> - Match the site (Chirpy theme): light background `#ffffff`, text `#34343c`, links `#0056b2`; dark mode background `#1b1b1e`, text `#afb0b1`, links `#8ab4f8`. System sans-serif fonts, body column max width ~50rem.
> - Support dark mode via `prefers-color-scheme`.
> - Leave the bottom-left corner clear: the site adds a small "← back" link there.
> - No secrets, internal data, or employer-proprietary numbers.
> - Topic / material: …

---

**Tips**
- Local images referenced by relative path (e.g. `<img src="fig1.png">`) are copied into `assets/img/posts/<slug>/` automatically. Keep them next to the HTML file in `inbox/`.
- Jupyter: `jupyter nbconvert --to html notebook.ipynb` gives a full document, so it becomes an interactive post. Add `--mode site` to put just its contents inside the site layout instead.
- Override anything: `--title`, `--summary`, `--date 2026-11-10`, `--slug`, `--image cover.png`, `--force`.
- No `--image`? A post linked with `--project` reuses that project's cover.
