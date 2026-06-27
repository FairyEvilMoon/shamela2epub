from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path

from .model import Book
from .text import normalize

CSS = """
html, body { direction: rtl; }

body {
  font-family: "Amiri", "Scheherazade New", "Noto Naskh Arabic", serif;
  line-height: 2.05;
  font-size: 1.18em;
  text-align: justify;
  margin: 3em;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: bold;
  text-align: right;
  line-height: 1.8;
  margin-top: 1.7em;
  margin-bottom: 0.8em;
}

h1 {
  font-size: 1.8em;
  text-align: center;
}

h2 { font-size: 1.55em; }
h3 { font-size: 1.35em; }
h4 { font-size: 1.2em; }

.page {
  margin-top: 0;
  margin-bottom: 1.6em;
  padding-top: 0.4em;
}

.page-id {
  color: #777777;
  font-size: 0.82em;
  text-align: left;
  direction: rtl;
  margin-top: 1.2em;
  margin-bottom: 0.35em;
}

.page-separator {
  border: 0;
  border-top: 1px solid #8a8a8a;
  height: 0;
  opacity: 0.6;
  margin: 0.6em 0 1.6em 0;
}

.cover {
  text-align: center;
  margin: 2em 0;
}

.cover img {
  max-width: 80%;
  max-height: 80vh;
}

a {
  text-decoration: none;
}
"""

MODES = ("original", "original-no-harakat", "expanded", "expanded-no-harakat")


def title_for(book: Book, mode: str) -> str:
    suffix = {
        "original": "",
        "original-no-harakat": " - بلا تشكيل",
        "expanded": " - موسع الرموز",
        "expanded-no-harakat": " - موسع بلا تشكيل",
    }[mode]
    return f"{book.meta.title}{suffix}"


def page_label(p) -> str:
    if p.part is not None and p.printed_page is not None:
        return f"ج {p.part} / ص {p.printed_page}"
    return f"Page {p.page_no}"


def write_html(book: Book, out_dir: Path, mode: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{book.meta.id}_{mode}.html"

    pages = sorted(book.pages, key=lambda p: p.page_no)
    titles_by_page = defaultdict(list)

    for t in sorted(book.titles, key=lambda x: (x.page, x.id)):
        titles_by_page[t.page].append(t)

    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="ar" dir="rtl">\n')
        f.write("<head>\n")
        f.write('<meta charset="UTF-8">\n')
        f.write(f"<title>{escape(title_for(book, mode))}</title>\n")
        f.write(f"<style>{CSS}</style>\n")
        f.write("</head>\n")
        f.write("<body>\n")

        f.write(f"<h1>{escape(title_for(book, mode))}</h1>\n")

        if book.meta.author:
            f.write(f"<h2>{escape(book.meta.author)}</h2>\n")

        for p in pages:
            for t in titles_by_page.get(p.page_no, []):
                title = normalize(t.text, mode).strip()
                if not title:
                    continue

                h = min(max(t.depth, 1), 6)
                f.write(f'<div id="toc-{t.id}" class="toc-anchor"></div>\n')
                f.write(f'<h{h}>{escape(title)}</h{h}>\n')

            f.write('<div class="page">\n')
            f.write(normalize(p.body, mode))
            f.write("\n")
            f.write(f'<div class="page-id">{escape(page_label(p))}</div>\n')
            f.write("</div>\n")

            if p is not pages[-1]:
                f.write('<hr class="page-separator"/>\n')

        f.write("</body>\n")
        f.write("</html>\n")

    return path