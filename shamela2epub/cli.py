from __future__ import annotations
import argparse
from pathlib import Path
from .loader import load_book
from .html_exporter import write_html, MODES
from .epub_exporter import write_epub


def main(argv=None):
    parser = argparse.ArgumentParser(prog="shamela2epub")
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="Export a Shamela 4 book")
    exp.add_argument("--library", required=True, help="Path to Shamela 4 root, e.g. D:\\shamela4")
    exp.add_argument("--book", required=True, help="Book ID, e.g. 4445")
    exp.add_argument("--out", default="output", help="Output directory")
    exp.add_argument("--mode", choices=[*MODES, "all"], default="all")
    exp.add_argument("--html-only", action="store_true", help="Only write HTML files")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent.parent
    if args.command == "export":
        out = Path(args.out)
        book = load_book(Path(args.library), args.book, project_root)
        modes = MODES if args.mode == "all" else (args.mode,)
        print(f"Loaded: {book.meta.title} | pages={len(book.pages)} | titles={len(book.titles)}")
        for mode in modes:
            html = write_html(book, out, mode)
            print(f"HTML: {html}")
            if not args.html_only:
                ep = write_epub(book, out, mode)
                print(f"EPUB: {ep}")

if __name__ == "__main__":
    main()
