#!/usr/bin/env python3
"""
Turn any HTML file into a blog post.

    python tools/new_post.py path/to/post.html                 # auto-detect
    python tools/new_post.py inbox/*.html                      # several at once
    python tools/new_post.py file.html --project copula-parlay-engine --date 2026-11-10 \
        --categories "Research, Prediction Markets" --tags "copulas, pricing" --image cover.png

Two modes (auto-detected, override with --mode):
  standalone  A full HTML document (<!doctype>/<html>/<body>). Saved as-is to
              assets/posts/<slug>/ and shown inline in the site page (sidebar visible), inside a
              shadow DOM so its styles stay separate. Needs tinycss2 (pip install tinycss2). Add `series: N` to set its order within a project.
  site        An HTML fragment (no <html>/<body>). Wrapped in the Chirpy post layout (sidebar,
              TOC, MathJax, tags), like a Markdown post. Use --mode site on a full document to pull out
              just its <body> (plus any <style>/<script> from <head>) and wrap it in the site.

Title / summary are taken from <title>, <h1>, <meta name="description">, or the first <p>,
unless given with --title / --summary. Local images next to the HTML file are copied into
assets/img/posts/<slug>/ and their paths rewritten. Standard library only, no installs.
"""
import argparse, datetime as dt, html, json, re, shutil, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"


def baseurl() -> str:
    m = re.search(r'^baseurl:\s*["\']?([^"\'\n#]*)', (ROOT / "_config.yml").read_text(encoding="utf-8"), re.M)
    return (m.group(1).strip() if m else "").rstrip("/")


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70] or "post"


def first(pattern: str, s: str, flags=re.I | re.S):
    m = re.search(pattern, s, flags)
    return m.group(1) if m else None


def meta_description(src: str) -> str:
    for tag in re.findall(r"<meta\b[^>]*>", src, re.I):
        if re.search(r"""name\s*=\s*["']description["']""", tag, re.I):
            m = re.search(r"""content\s*=\s*(?:"([^"]*)"|'([^']*)')""", tag, re.I)
            if m:
                return m.group(1) if m.group(1) is not None else m.group(2)
    return ""


def split_front_matter(src: str):
    """Allow the input to already carry simple `key: value` front matter."""
    if not src.startswith("---"):
        return {}, src
    end = src.find("\n---", 3)
    if end == -1:
        return {}, src
    fm = {}
    for line in src[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, src[end + 4:].lstrip("\n")


def convert(path: Path, a) -> Path:
    fm, src = split_front_matter(path.read_text(encoding="utf-8"))
    is_full = bool(re.search(r"<!doctype|<html[\s>]|<body[\s>]", src, re.I))
    mode = a.mode if a.mode != "auto" else ("standalone" if is_full else "site")

    title = a.title or fm.get("title") or text_of(first(r"<title[^>]*>(.*?)</title>", src) or "") \
        or text_of(first(r"<h1[^>]*>(.*?)</h1>", src) or "") or path.stem.replace("-", " ").title()
    summary = a.summary or fm.get("summary") \
        or html.unescape(meta_description(src)) \
        or text_of(first(r"<p[^>]*>(.*?)</p>", src) or "")
    if len(summary) > 200:
        summary = summary[:197].rsplit(" ", 1)[0] + "…"
    date = a.date or fm.get("date", "")[:10] or dt.date.today().isoformat()
    slug = a.slug or fm.get("slug") or slugify(title)
    project = a.project or fm.get("project")
    split = lambda v: [x.strip() for x in (v or "").strip("[]").split(",") if x.strip()]
    categories = split(a.categories or fm.get("categories")) or ["Research"]
    tags = split(a.tags or fm.get("tags"))
    image = a.image or fm.get("image")
    if image and not re.match(r"^(https?:|/)", image):  # local cover file → copy into assets
        f = (path.parent / image).resolve()
        if f.is_file():
            dest = ROOT / "assets" / "img" / "posts" / slugify(a.slug or fm.get("slug") or title)
            dest.mkdir(parents=True, exist_ok=True); shutil.copy2(f, dest / f.name)
            image = f"/assets/img/posts/{dest.name}/{f.name}"
        else:
            print(f"  ! cover image {image} not found; skipping"); image = None
    if not image and project:  # fall back to the linked project's cover
        pf = ROOT / "_projects" / f"{project}.md"
        if pf.is_file():
            image = first(r"^image:\s*(\S+)", pf.read_text(encoding="utf-8"), re.M)

    body = src
    if mode == "site":
        if is_full:  # keep head <style>/<script>, take <body> contents
            head = first(r"<head[^>]*>(.*?)</head>", src) or ""
            keep = "\n".join(re.findall(r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>", head, re.I | re.S))
            body = keep + "\n" + (first(r"<body[^>]*>(.*)</body>", src) or src)
        # the layout prints the title, so drop a leading <h1> that repeats it
        body = re.sub(r"^\s*<h1[^>]*>.*?</h1>", "", body.strip(), count=1, flags=re.I | re.S)
        # ...and a leading <p> that is the summary (the layout shows it as the lede)
        m = re.match(r"\s*<p[^>]*>(.*?)</p>", body, re.I | re.S)
        if m and text_of(m.group(1)) and summary.rstrip("…") and text_of(m.group(1)).startswith(summary.rstrip("…")):
            body = body[m.end():]

    # copy local images / assets and rewrite their paths
    dest_dir = ROOT / "assets" / "img" / "posts" / slug
    def relink(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if re.match(r"^(https?:|data:|//|/|#|mailto:)", url):
            return m.group(0)
        f = (path.parent / url).resolve()
        if not f.is_file():
            print(f"  ! missing asset {url} (left as-is)")
            return m.group(0)
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest_dir / f.name)
        return f'{attr}={q}{baseurl()}/assets/img/posts/{slug}/{f.name}{q}'
    body = re.sub(r'\b(src|href)=(["\'])([^"\']+\.(?:png|jpe?g|gif|svg|webp|csv|json|pdf|mp4))\2', relink, body, flags=re.I)

    if "{% endraw %}" in body:
        print("  ! file contains '{% endraw %}' — Liquid may break; remove it from the source")

    front = {"title": title, "description": summary, "categories": categories, "tags": tags}
    if mode == "standalone":
        front["layout"] = "post"  # shown inside the site page; the document itself is served from assets/posts/<slug>/
    if project:
        front["project"] = project
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in front.items()]
    lines.insert(3, f"date: {date} 09:00:00")  # local time per `timezone` in _config.yml
    if image:
        lines += ["image:", f"  path: {json.dumps(image)}", f"  alt: {json.dumps(title, ensure_ascii=False)}"]
    # Keep Jekyll from splitting the excerpt inside the {% raw %} block.
    if mode == "standalone":
        # Serve the full document as a static file and embed it, so the site sidebar stays visible.
        doc = ROOT / "assets" / "posts" / slug / "index.html"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(body.strip() + "\n", encoding="utf-8")
        try:  # split into content.html + fonts.css for inline display (see tools/build_embeds.py)
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import build_embeds
            build_embeds.build(doc)
        except ImportError:
            print("  ! run `pip install tinycss2` then `python tools/build_embeds.py` before pushing")
        lines += [f"embed: /assets/posts/{slug}/", "---"]
        out_text = "\n".join(lines) + "\n"
    else:
        lines += ['excerpt_separator: "<!--jekyll-no-excerpt-->"', "---"]
        out_text = "\n".join(lines) + "\n{% raw %}\n" + body.strip() + "\n{% endraw %}\n"

    out = POSTS / f"{date}-{slug}.html"
    if out.exists() and not a.force:
        sys.exit(f"  ✗ {out.relative_to(ROOT)} already exists (use --force to overwrite)")
    out.write_text(out_text, encoding="utf-8")
    print(f"  ✓ {path.name} → {out.relative_to(ROOT)}  [{mode}]")
    print(f"    title:   {title}\n    url:     {baseurl()}/posts/{slug}/")
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--mode", choices=["auto", "standalone", "site"], default="auto")
    ap.add_argument("--title"); ap.add_argument("--summary"); ap.add_argument("--slug")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--project", help="project slug to link this post to")
    ap.add_argument("--categories", help='comma list, max 2 levels, e.g. "Research, Prediction Markets"')
    ap.add_argument("--tags", help='comma list, e.g. "copulas, pricing"')
    ap.add_argument("--image", help="cover image (path or URL); defaults to the project's cover")
    ap.add_argument("--force", action="store_true", help="overwrite an existing post")
    ap.add_argument("--move", action="store_true", help="delete the source file after converting")
    a = ap.parse_args()
    if len(a.files) > 1 and (a.title or a.slug):
        sys.exit("--title/--slug only make sense with a single file")
    for f in a.files:
        convert(f, a)
        if a.move:
            f.unlink()


if __name__ == "__main__":
    main()
