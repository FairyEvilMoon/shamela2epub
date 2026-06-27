from __future__ import annotations
import re

HARAKAT_RE = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")

SPECIAL_SYMBOLS = {
    "ﷺ": "صلى الله عليه وسلم",
    "﵌": "عليه الصلاة والسلام",
    "﵍": "صلى الله عليه وسلم",
    "ﷻ": "جل جلاله",
    "ﷲ": "الله",
    "﷽": "بسم الله الرحمن الرحيم",
    "﵀": "رحمه الله",
    "ﵐ": "رحمه الله تعالى",
    "﵁": "رضي الله عنه",
    "﵂": "رضي الله عنها",
    "﵃": "رضي الله عنهما",
    "﵄": "رضي الله عنهم",
    "﵅": "رضي الله عنها",
    "﵆": "رضي الله عنهم",
    "﵇": "رحمهم الله",
    "﵈": "قدس الله سره",
    "﵉": "عز وجل",
    "﵊": "عليه السلام",
    "﵋": "عليهما السلام",
    "﵎": "سلام عليه",
}

def remove_harakat(text: str) -> str:
    return HARAKAT_RE.sub("", text)

def expand_symbols(text: str) -> str:
    for src, dst in SPECIAL_SYMBOLS.items():
        text = text.replace(src, dst)
    return text

def normalize(text: str, mode: str) -> str:
    if mode == "original":
        return text
    if mode == "original-no-harakat":
        return remove_harakat(text)
    if mode == "expanded":
        return expand_symbols(text)
    if mode == "expanded-no-harakat":
        return remove_harakat(expand_symbols(text))
    return text
