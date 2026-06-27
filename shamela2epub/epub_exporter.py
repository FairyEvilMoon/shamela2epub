from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path

from ebooklib import epub

from .model import Book, TitleNode, Page
from .html_exporter import write_html, title_for, page_label
from .text import normalize


def write_epub(book: Book, out_dir: Path, mode: str) -> Path:
    """Write a scholarly EPUB.

    This version splits the EPUB at every Shamela title. Each TOC item points to
    the beginning of its own XHTML file. This is more reliable on EPUB readers
    than internal anchors inside large chapter files.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    write_html(book, out_dir, mode)

    epub_book = epub.EpubBook()
    epub_book.set_identifier(f"shamela-{book.meta.id}-{mode}")
    epub_book.set_title(title_for(book, mode))
    epub_book.set_language(book.meta.language or "ar")

    if book.meta.author:
        epub_book.add_author(book.meta.author)

    if book.meta.category:
        epub_book.add_metadata("DC", "subject", book.meta.category)

    if book.cover:
        epub_book.set_cover("cover.jpg", book.cover)

    css_item = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=_css().encode("utf-8"),
    )
    epub_book.add_item(css_item)

    pages = sorted(book.pages, key=lambda p: p.page_no)
    titles = sorted(book.titles, key=lambda t: (t.page, t.id))

    if not titles:
        titles = [
            TitleNode(
                id=0,
                page=pages[0].page_no if pages else 1,
                parent=0,
                depth=1,
                text=title_for(book, mode),
            )
        ]

    title_ranges = _title_ranges(titles, pages)

    chapters = []
    title_to_file: dict[int, str] = {}

    for i, (title_node, section_pages) in enumerate(title_ranges, start=1):
        if not section_pages:
            continue

        file_name = f"sec_{i:05d}_t{title_node.id}.xhtml"
        chapter_title = _clean_title(title_node.text, mode) or f"Section {i}"

        content = _section_xhtml(
            title_node=title_node,
            chapter_title=chapter_title,
            pages=section_pages,
            mode=mode,
        )

        ch = epub.EpubHtml(
            title=chapter_title,
            file_name=file_name,
            lang="ar",
            direction="rtl",
        )
        ch.content = content.encode("utf-8")

        epub_book.add_item(ch)
        chapters.append(ch)
        title_to_file[title_node.id] = file_name

    if not chapters:
        file_name = "sec_00001.xhtml"
        content = _section_xhtml(
            title_node=None,
            chapter_title=title_for(book, mode),
            pages=pages,
            mode=mode,
        )

        ch = epub.EpubHtml(
            title=title_for(book, mode),
            file_name=file_name,
            lang="ar",
            direction="rtl",
        )
        ch.content = content.encode("utf-8")

        epub_book.add_item(ch)
        chapters.append(ch)

    epub_book.spine = ["nav", *chapters]
    epub_book.toc = _build_toc(book, title_to_file, mode)

    epub_book.add_item(epub.EpubNcx())
    epub_book.add_item(epub.EpubNav())

    output = out_dir / f"{book.meta.id}_{mode}.epub"
    epub.write_epub(str(output), epub_book)
    return output


def _title_ranges(
    titles: list[TitleNode],
    pages: list[Page],
) -> list[tuple[TitleNode, list[Page]]]:
    """Return each title with the pages belonging to that title section.

    A title section starts at title.page and ends before the next title that is
    at the same or higher hierarchy level.

    This avoids overlapping ranges and avoids duplicated page bodies.
    """
    results: list[tuple[TitleNode, list[Page]]] = []

    page_by_no = {p.page_no: p for p in pages}
    page_numbers = sorted(page_by_no)

    titles_sorted = sorted(titles, key=lambda t: (t.page, t.id))

    for i, t in enumerate(titles_sorted):
        start = t.page

        next_start = None
        for nxt in titles_sorted[i + 1 :]:
            if nxt.page <= start:
                continue

            if nxt.depth <= t.depth:
                next_start = nxt.page
                break

        section_pages = [
            page_by_no[n]
            for n in page_numbers
            if n >= start and (next_start is None or n < next_start)
        ]

        # If a title has no unique page range, still make a tiny section with
        # its starting page so TOC navigation opens a real file.
        if not section_pages and start in page_by_no:
            section_pages = [page_by_no[start]]

        results.append((t, section_pages))

    return results


def _section_xhtml(
    title_node: TitleNode | None,
    chapter_title: str,
    pages: list[Page],
    mode: str,
) -> str:
    parts: list[str] = []

    parts.append('<?xml version="1.0" encoding="utf-8"?>')
    parts.append('<html xmlns="http://www.w3.org/1999/xhtml" lang="ar" dir="rtl">')
    parts.append(
        "<head>"
        '<meta charset="utf-8"/>'
        f"<title>{escape(chapter_title)}</title>"
        '<link rel="stylesheet" href="style.css"/>'
        "</head>"
    )
    parts.append("<body>")

    if title_node is not None:
        h = min(max(title_node.depth, 1), 6)
        parts.append(f'<h{h} id="toc-{title_node.id}">{escape(chapter_title)}</h{h}>')
    else:
        parts.append(f"<h1>{escape(chapter_title)}</h1>")

    for idx, p in enumerate(pages):
        parts.append(f'<section class="page" id="page-{p.page_no}">')
        parts.append(normalize(p.body, mode))
        parts.append(f'<div class="page-id">{escape(page_label(p))}</div>')
        parts.append("</section>")

        if idx != len(pages) - 1:
            parts.append('<hr class="page-separator"/>')

    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts)


def _build_toc(book: Book, title_to_file: dict[int, str], mode: str):
    children: dict[int, list[TitleNode]] = defaultdict(list)
    by_id = {t.id: t for t in book.titles}

    for t in sorted(book.titles, key=lambda x: (x.page, x.id)):
        parent = t.parent if t.parent in by_id else 0
        children[parent].append(t)

    def build(parent_id: int):
        items = []

        for t in children.get(parent_id, []):
            title = _clean_title(t.text, mode)
            if not title:
                continue

            href = title_to_file.get(t.id)
            if not href:
                href = _nearest_file(t, by_id, title_to_file) or "sec_00001.xhtml"

            link = epub.Link(href, title, f"toc-{t.id}")
            kids = build(t.id)

            if kids:
                items.append((link, kids))
            else:
                items.append(link)

        return items

    toc = build(0)

    return toc if toc else [
        epub.Link("sec_00001.xhtml", title_for(book, mode), "toc-root")
    ]


def _nearest_file(
    t: TitleNode,
    by_id: dict[int, TitleNode],
    title_to_file: dict[int, str],
) -> str | None:
    current = t
    seen = set()

    while current and current.id not in seen:
        seen.add(current.id)

        if current.id in title_to_file:
            return title_to_file[current.id]

        current = by_id.get(current.parent)

    return None


def _clean_title(text: str, mode: str) -> str:
    return normalize(text or "", mode).strip()


def _css() -> str:
    return """
html, body {
  direction: rtl;
  writing-mode: horizontal-tb;
}

body {
  font-family: "Amiri", "Scheherazade New", "Noto Naskh Arabic", serif;
  font-size: 1.15em;
  line-height: 2.05;
  text-align: justify;
  margin: 1.4em;
}

h1, h2, h3, h4, h5, h6 {
  text-align: center;
  font-weight: bold;
  line-height: 1.7;
  margin: 1.6em 0 1em;
}

h1 { font-size: 1.75em; }
h2 { font-size: 1.45em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.1em; }

.page {
  margin: 1.2em 0 1.8em;
}

.page-id {
  text-align: left;
  font-size: 0.8em;
  opacity: 0.65;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
}

.page-separator {
  border: none;
  border-top: 1px solid currentColor;
  opacity: 0.35;
  margin: 0.8em 0 1.6em;
}

p {
  margin: 0.45em 0;
}

a {
  text-decoration: none;
}
"""