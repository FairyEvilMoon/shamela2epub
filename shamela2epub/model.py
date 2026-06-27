from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Page:
    page_no: int
    part: Optional[int]
    printed_page: Optional[int]
    body: str

@dataclass
class TitleNode:
    id: int
    page: int
    parent: int
    text: str
    depth: int = 1

@dataclass
class BookMetadata:
    id: str
    title: str
    author: str = ""
    language: str = "ar"
    category: str = ""

@dataclass
class Book:
    meta: BookMetadata
    pages: list[Page] = field(default_factory=list)
    titles: list[TitleNode] = field(default_factory=list)
    cover: Optional[bytes] = None
    cover_media_type: str = "image/jpeg"
