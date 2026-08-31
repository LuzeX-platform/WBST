#!/usr/bin/env python3
"""Uitpakken en inpakken van de site-inhoud in index.html.

index.html is een gebundelde pagina: de echte site staat als JSON-string in
de <script type="__bundler/template"> tag, en alle fonts/afbeeldingen staan
base64 in de manifest-tag. Handmatig bewerken van index.html is daardoor
foutgevoelig.

    python3 tools/bundle.py unpack          -> schrijft site.html
    python3 tools/bundle.py pack            -> leest site.html terug in index.html

De inpak-stap escapet '</' als '<\\u002F', precies zoals de bundler zelf doet.
Zonder die escape sluit een '</script>' in de inhoud de script-tag voortijdig
en breekt de pagina. Uitpakken + direct inpakken geeft een byte-identiek
index.html.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SITE = ROOT / "site.html"
TAG = '<script type="__bundler/template">'


def _split():
    lines = INDEX.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        if line.strip() == TAG:
            return lines, i + 1
    sys.exit(f"template-tag niet gevonden in {INDEX}")


def unpack():
    lines, idx = _split()
    SITE.write_text(json.loads(lines[idx]), encoding="utf-8")
    print(f"{SITE.name} geschreven ({SITE.stat().st_size} bytes)")


def pack():
    lines, idx = _split()
    text = SITE.read_text(encoding="utf-8")
    lines[idx] = json.dumps(text, ensure_ascii=False).replace("</", "<\\u002F")
    INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(f"{INDEX.name} bijgewerkt ({INDEX.stat().st_size} bytes)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "unpack":
        unpack()
    elif cmd == "pack":
        pack()
    else:
        sys.exit(__doc__)
