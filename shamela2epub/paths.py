from __future__ import annotations
from pathlib import Path

class ShamelaPaths:
    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def database(self) -> Path:
        return self.root / "database"

    @property
    def master_db(self) -> Path:
        return self.database / "master.db"

    @property
    def cover_db(self) -> Path:
        return self.database / "cover.db"

    @property
    def page_index(self) -> Path:
        return self.database / "store" / "page"

    @property
    def title_index(self) -> Path:
        return self.database / "store" / "title"

    def book_db(self, book_id: str) -> Path:
        book_root = self.database / "book"
        name = f"{book_id}.db"
        if not book_root.exists():
            raise FileNotFoundError(f"Book database root not found: {book_root}")
        matches = list(book_root.rglob(name))
        if not matches:
            raise FileNotFoundError(f"Cannot find book database {name} under {book_root}")
        return matches[0]
