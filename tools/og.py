#!/usr/bin/env python3
"""Maakt og-image.png: het plaatje dat verschijnt als iemand luzex.nl deelt.

Linkvoorbeelden in WhatsApp, LinkedIn, Slack en iMessage willen een liggend
beeld van 1200x630. Stond daar een vierkant logo, dan sneden ze het bij of
toonden ze het klein.

Het logo wordt uit de bundel gehaald in plaats van overgetekend: zo kan het
deelplaatje niet gaan afwijken van het woordmerk op de site. De achtergrond
gebruikt dezelfde kleuren en hetzelfde glas als de pagina zelf.

    python3 tools/og.py          -> schrijft og-image.png

Draai dit opnieuw als het woordmerk of de productnamen veranderen.
"""
import base64
import json
import sys
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent
INDEX = WORTEL / "index.html"
UIT = WORTEL / "og-image.png"

# Het woordmerk met de slogan eronder: "L U Z E X / Minder. Maar beter."
WOORDMERK = "730711f1-cb25-4f3d-9351-dd979901cab4"
PRODUCTEN = "ACCRD &middot; CMMNTY &middot; RSLNT"
BREED, HOOG = 1200, 630


def _logo():
    lines = INDEX.read_text(encoding="utf-8").split("\n")
    i = next(n for n, r in enumerate(lines)
             if r.strip() == '<script type="__bundler/manifest">') + 1
    e = json.loads(lines[i])[WOORDMERK]
    if e["compressed"]:
        sys.exit("woordmerk is ingepakt; uitpakken nog niet nodig geweest")
    return base64.b64decode(e["data"]).decode("utf-8")


PAGINA = """<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {breed}px; height: {hoog}px; background: #cfc6bc; position: relative;
    overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display',
    'Segoe UI', Helvetica, sans-serif; -webkit-font-smoothing: antialiased; }}
  /* Hetzelfde licht als onder het glas op de site. */
  .vlek {{ position: absolute; border-radius: 50%; filter: blur(90px); }}
  .glas {{ position: absolute; inset: 62px; border-radius: 44px;
    background: linear-gradient(142deg, rgba(255,255,255,0.60),
      rgba(255,255,255,0.24) 46%, rgba(255,255,255,0.40));
    backdrop-filter: blur(30px) saturate(190%);
    border: 1px solid rgba(255,255,255,0.58);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.95),
      inset 0 -18px 34px rgba(255,255,255,0.20),
      0 26px 64px rgba(29,29,31,0.20);
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 46px; }}
  .merk {{ width: 660px; display: block; }}
  .producten {{ font-size: 25px; font-weight: 600; letter-spacing: 0.26em;
    color: #3b2e24; text-indent: 0.26em; }}
</style></head><body>
  <div class="vlek" style="width:560px;height:560px;left:-140px;top:-170px;
    background:#c98a63;opacity:0.55"></div>
  <div class="vlek" style="width:470px;height:470px;right:-90px;top:-120px;
    background:#8d9472;opacity:0.42"></div>
  <div class="vlek" style="width:620px;height:620px;right:-150px;bottom:-280px;
    background:#3b2e24;opacity:0.32"></div>
  <div class="vlek" style="width:380px;height:380px;left:330px;bottom:-190px;
    background:#e8dccc;opacity:0.60"></div>
  <div class="glas">
    <div class="merk">{logo}</div>
    <div class="producten">{producten}</div>
  </div>
</body></html>"""


def main():
    from playwright.sync_api import sync_playwright

    logo = _logo()
    # De SVG draagt een vaste breedte en hoogte; die moeten weg, anders negeert
    # hij de 660px van .merk en staat hij op ware grootte in de hoek.
    logo = logo.replace('width="574.7" height="120"', 'width="100%" height="auto"', 1)
    pagina = PAGINA.format(breed=BREED, hoog=HOOG, logo=logo, producten=PRODUCTEN)

    tijdelijk = WORTEL / ".og-tijdelijk.html"
    tijdelijk.write_text(pagina, encoding="utf-8")
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            p = b.new_page(viewport={"width": BREED, "height": HOOG})
            p.goto(tijdelijk.as_uri())
            p.wait_for_timeout(1200)
            p.screenshot(path=str(UIT))
            b.close()
    finally:
        tijdelijk.unlink(missing_ok=True)
    print(f"{UIT.name} geschreven ({UIT.stat().st_size} bytes, {BREED}x{HOOG})")


if __name__ == "__main__":
    main()
