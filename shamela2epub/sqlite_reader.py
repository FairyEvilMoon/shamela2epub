from __future__ import annotations
import sqlite3
from pathlib import Path
from .model import BookMetadata, TitleNode


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def read_page_meta(book_db: Path) -> dict[int, tuple[int | None, int | None]]:
    conn = sqlite3.connect(book_db)
    try:
        cols = _columns(conn, "page")
        query_cols = ["id"]
        query_cols.append("part" if "part" in cols else "NULL AS part")
        query_cols.append("page" if "page" in cols else "NULL AS page")
        sql = "SELECT " + ", ".join(query_cols) + " FROM page ORDER BY id"
        out: dict[int, tuple[int | None, int | None]] = {}
        for page_id, part, printed_page in conn.execute(sql):
            out[int(page_id)] = (part, printed_page)
        return out
    finally:
        conn.close()


def read_title_map(book_db: Path, title_texts: dict[int, str]) -> list[TitleNode]:
    conn = sqlite3.connect(book_db)
    nodes: list[TitleNode] = []
    by_id: dict[int, TitleNode] = {}
    try:
        for id_, page, parent in conn.execute("SELECT id, page, parent FROM title ORDER BY page, id"):
            node = TitleNode(id=int(id_), page=int(page), parent=int(parent), text=title_texts.get(int(id_), ""))
            nodes.append(node)
            by_id[node.id] = node
    finally:
        conn.close()

    for n in nodes:
        depth = 1
        p = n.parent
        seen = set()
        while p and p in by_id and p not in seen:
            seen.add(p)
            depth += 1
            p = by_id[p].parent
        n.depth = min(depth, 6)
    return nodes


def read_book_metadata(master_db: Path, book_id: str) -> BookMetadata:
    if not master_db.exists():
        return BookMetadata(id=book_id, title=f"كتاب {book_id}")
    conn = sqlite3.connect(master_db)
    conn.row_factory = sqlite3.Row
    try:
        # Known Shamela 4 schema.
        row = conn.execute("SELECT * FROM book WHERE book_id = ? LIMIT 1", (book_id,)).fetchone()
        if row:
            title = row["book_name"] or f"كتاب {book_id}"
            author = ""
            if "main_author" in row.keys() and row["main_author"]:
                a = conn.execute("SELECT author_name FROM author WHERE author_id = ? LIMIT 1", (row["main_author"],)).fetchone()
                if a and a["author_name"]:
                    author = a["author_name"]
            category = ""
            if "book_category" in row.keys() and row["book_category"]:
                c = conn.execute("SELECT category_name FROM category WHERE category_id = ? LIMIT 1", (row["book_category"],)).fetchone()
                if c and c["category_name"]:
                    category = c["category_name"]
            return BookMetadata(id=book_id, title=str(title), author=str(author), category=str(category))
    finally:
        conn.close()
    return BookMetadata(id=book_id, title=f"كتاب {book_id}")


def read_cover(cover_db: Path, book_id: str) -> bytes | None:
    if not cover_db.exists():
        return None
    conn = sqlite3.connect(cover_db)
    conn.row_factory = sqlite3.Row
    try:
        for table_row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            table = table_row[0]
            cols = _columns(conn, table)
            id_cols = [c for c in ["id", "book", "book_id", "bkid"] if c in cols]
            blob_cols = [c for c in cols if c.lower() in {"cover", "image", "img", "data", "blob", "content"}]
            for id_col in id_cols:
                for blob_col in blob_cols:
                    try:
                        row = conn.execute(f"SELECT {blob_col} FROM {table} WHERE {id_col} = ? LIMIT 1", (book_id,)).fetchone()
                    except Exception:
                        continue
                    if row and row[0]:
                        return bytes(row[0])
    except Exception:
        return None
    finally:
        conn.close()
    return None
