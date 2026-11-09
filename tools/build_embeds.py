#!/usr/bin/env python3
"""
Prepare self-contained HTML posts for inline display on the site (no iframe).

For every assets/posts/<slug>/index.html this writes, next to it:
  content.html  the post's <style> (rewritten so html/:root/body rules target the
                shadow-DOM host and a .post-body wrapper), the <body> markup, and the
                post's scripts as <script type="text/x-post"> (run later by the loader)
  fonts.css     the post's @font-face rules (fonts must be declared at document level)

The post page (_layouts/post-embed.html) fetches content.html into a shadow root, so the
post keeps its own design, the site's styles don't leak in, and the page scrolls normally.
Run after adding or editing a post:  python tools/build_embeds.py
Needs: pip install tinycss2
"""
import re, sys
from pathlib import Path
import tinycss2

ROOT = Path(__file__).resolve().parent.parent
HOSTSEL = re.compile(r'(?<![\w-])(?::root|html)(?![\w-])')
BODYSEL = re.compile(r'(?<![\w.#-])body(?![\w-])')
HOSTCOMPOUND = re.compile(r':host((?:\[[^\]]*\]|:not\([^)]*\)|\.[\w-]+)+)')


def rewrite_selector(sel: str) -> str:
    sel = HOSTSEL.sub(':host', sel)
    sel = BODYSEL.sub('.post-body', sel)
    sel = HOSTCOMPOUND.sub(r':host(\1)', sel)
    sel = sel.replace(':host .post-body', ':host .post-body')
    return sel


def process(rules, fonts):
    out = []
    for r in rules:
        if r.type == 'qualified-rule':
            prelude = tinycss2.serialize(r.prelude).strip()
            sels = ', '.join(rewrite_selector(s.strip()) for s in prelude.split(','))
            out.append(f'{sels}{{{tinycss2.serialize(r.content)}}}')
        elif r.type == 'at-rule':
            kw = r.lower_at_keyword
            if kw == 'font-face':
                fonts.append(tinycss2.serialize([r]))
            elif kw in ('media', 'supports', 'layer', 'container') and r.content is not None:
                inner = tinycss2.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True)
                out.append(f'@{r.at_keyword}{tinycss2.serialize(r.prelude)}{{{"".join(process(inner, fonts))}}}')
            else:
                out.append(tinycss2.serialize([r]))
    return out


def build(doc_path: Path):
    s = doc_path.read_text(encoding='utf-8')
    css = '\n'.join(re.findall(r'<style\b[^>]*>([\s\S]*?)</style>', s, re.I))
    fonts = []
    rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
    scoped = '\n'.join(process(rules, fonts))
    body_m = re.search(r'<body\b([^>]*)>([\s\S]*)</body>', s, re.I)
    body_attrs, body = (body_m.group(1), body_m.group(2)) if body_m else ('', s)
    scripts = re.findall(r'<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>', s, re.I)
    body = re.sub(r'<script\b[\s\S]*?</script>', '', body, flags=re.I)
    cls = re.search(r'class="([^"]*)"', body_attrs)
    wrap_cls = 'post-body' + (' ' + cls.group(1) if cls else '')
    content = (f'<style>{scoped}</style>\n<div class="{wrap_cls}">{body}</div>\n'
               + ''.join(f'<script type="text/x-post">{js}</script>\n' for js in scripts))
    (doc_path.parent / 'content.html').write_text(content, encoding='utf-8')
    (doc_path.parent / 'fonts.css').write_text('\n'.join(fonts) + '\n', encoding='utf-8')
    return len(scoped), len(fonts), len(scripts)


if __name__ == '__main__':
    targets = [Path(a) for a in sys.argv[1:]] or sorted((ROOT / 'assets' / 'posts').glob('*/index.html'))
    for t in targets:
        n_css, n_font, n_js = build(t)
        print(f'  ✓ {t.parent.name}: css {n_css // 1000}k, {n_font} font faces, {n_js} scripts')
