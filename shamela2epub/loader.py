from __future__ import annotations
from pathlib import Path
from .paths import ShamelaPaths
from .model import Book, Page
from .sqlite_reader import read_page_meta, read_title_map, read_book_metadata, read_cover
from .lucene_helper import dump_index


def load_book(library: Path, book_id: str, project_root: Path) -> Book:
    paths = ShamelaPaths(library)
    book_db = paths.book_db(book_id)

    page_meta = read_page_meta(book_db)
    meta = read_book_metadata(paths.master_db, book_id)

    raw_titles = dump_index(project_root, paths.title_index, "title", book_id)
    title_texts: dict[int, str] = {}
    for key, value in raw_titles["documents"].items():
        try:
            title_texts[int(key)] = value
        except ValueError:
            if "-" in key:
                _, suffix = key.split("-", 1)
                try:
                    title_texts[int(suffix)] = value
                except ValueError:
                    pass
    titles = read_title_map(book_db, title_texts)

    raw_pages = dump_index(project_root, paths.page_index, "page", book_id)
    pages: list[Page] = []
    for page_no_s, body in raw_pages["documents"].items():
        try:
            page_no = int(page_no_s)
        except ValueError:
            continue
        part, printed_page = page_meta.get(page_no, (None, None))
        pages.append(Page(page_no=page_no, part=part, printed_page=printed_page, body=body))
    pages.sort(key=lambda p: p.page_no)

    cover = read_cover(paths.cover_db, book_id)
    return Book(meta=meta, pages=pages, titles=titles, cover=cover)
