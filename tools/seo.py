#!/usr/bin/env python3
"""Maakt de gebundelde site leesbaar voor zoekmachines en linkvoorbeelden.

Het probleem: index.html is een bundel. De echte pagina staat als JSON-string
in een script-tag en wordt pas in de browser opgebouwd, met
`document.documentElement.replaceWith(...)`. Wie geen JavaScript draait ziet
daardoor 66 tekens: "LuzeX  This page requires JavaScript to display."

Dat raakt niet alleen Google (die rendert wel, maar vertraagd en niet altijd):
linkvoorbeelden in WhatsApp, LinkedIn, Slack en iMessage draaien nooit
JavaScript, en de meeste AI-crawlers ook niet.

De oplossing maakt gebruik van het feit dat de runtime het hele <html>-element
vervangt. Alles wat in de oorspronkelijke <body> staat verdwijnt dus zodra
JavaScript draait. Daar kan de echte inhoud in: crawlers en mensen zonder
JavaScript lezen hem, iedereen met JavaScript ziet hem nooit. Dat is geen
cloaking maar progressive enhancement, want de tekst is woordelijk dezelfde
als wat de browser opbouwt. Dat is ook precies waarom dit script de inhoud
rendert in plaats van hem met de hand over te typen: dan kan hij niet gaan
afwijken.

    python3 tools/seo.py          -> werkt index.html, robots.txt en sitemap.xml bij

Draai dit na elke inhoudelijke wijziging aan de site, ná bundle.py pack.
Het script is herhaalbaar: het vervangt zijn eigen blokken tussen de markers
en laat de rest van het bestand met rust.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent
INDEX = WORTEL / "index.html"
SITE = WORTEL / "site.html"

BASIS = "https://luzex.nl"
TITEL = "LuzeX — software op maat. Minder. Maar beter."
OMSCHRIJVING = (
    "L u z e X bouwt gerichte software op maat voor werk dat niemand ooit heeft "
    "ontworpen. ACCRD, CMMNTY en RSLNT draaien."
)
# Liggend 1200x630, gemaakt door tools/og.py. Een vierkant logo werd door
# WhatsApp en LinkedIn bijgesneden of klein getoond.
DEEL_BEELD = f"{BASIS}/og-image.png"
DEEL_BEELD_ALT = "Het woordmerk L U Z E X met de slogan Minder. Maar beter."
LOGO = f"{BASIS}/icon-512.png"

KOP_START = "<!-- seo:kop:start -->"
KOP_EIND = "<!-- seo:kop:eind -->"
ROMP_START = "<!-- seo:romp:start -->"
ROMP_EIND = "<!-- seo:romp:eind -->"


def _render():
    """Haalt de opbouw uit de pagina zoals de browser hem echt neerzet."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(INDEX.as_uri())
        pg.wait_for_selector("h1", timeout=15000)
        pg.wait_for_timeout(1200)
        blokken = pg.evaluate(
            """() => {
              const uit = [];
              const zie = (n) => {
                const s = getComputedStyle(n);
                if (s.display === 'none' || s.visibility === 'hidden') return false;
                // tekst die alleen voor schermlezers bedoeld is telt niet mee
                return !(n.clientWidth <= 1 && n.clientHeight <= 1);
              };
              for (const n of document.querySelectorAll('h1,h2,h3,p,li,a[href]')) {
                if (!zie(n)) continue;
                const t = (n.innerText || '').replace(/\\s+/g, ' ').trim();
                if (!t) continue;
                const tag = n.tagName.toLowerCase();
                if (tag === 'a') {
                  const h = n.getAttribute('href') || '';
                  if (!/^https?:/.test(h)) continue;   // ankers voegen niets toe
                  uit.push({ tag: 'a', tekst: t, href: h });
                } else {
                  // een <p> of <li> die zelf al een kop bevat zou dubbelen
                  if (n.querySelector('h1,h2,h3')) continue;
                  uit.push({ tag, tekst: t });
                }
              }
              return uit;
            }"""
        )
        b.close()
    return blokken


def _ontdubbel(blokken):
    gezien, uit = set(), []
    for b in blokken:
        sleutel = (b["tag"], b["tekst"], b.get("href"))
        if sleutel in gezien:
            continue
        gezien.add(sleutel)
        uit.append(b)
    return uit


def _kop_blok():
    gegevens = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "LuzeX",
        "url": BASIS + "/",
        "logo": LOGO,
        "slogan": "Minder. Maar beter.",
        "description": OMSCHRIJVING,
    }
    e = html.escape
    return "\n".join([
        KOP_START,
        "  <!-- Door tools/seo.py gezet. Niet met de hand bewerken: draai het script. -->",
        f'  <meta name="description" content="{e(OMSCHRIJVING)}">',
        f'  <link rel="canonical" href="{BASIS}/">',
        '  <meta name="robots" content="index, follow, max-image-preview:large">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:site_name" content="LuzeX">',
        '  <meta property="og:locale" content="nl_NL">',
        f'  <meta property="og:title" content="{e(TITEL)}">',
        f'  <meta property="og:description" content="{e(OMSCHRIJVING)}">',
        f'  <meta property="og:url" content="{BASIS}/">',
        f'  <meta property="og:image" content="{DEEL_BEELD}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        f'  <meta property="og:image:alt" content="{e(DEEL_BEELD_ALT)}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{e(TITEL)}">',
        f'  <meta name="twitter:description" content="{e(OMSCHRIJVING)}">',
        f'  <meta name="twitter:image" content="{DEEL_BEELD}">',
        f'  <meta name="twitter:image:alt" content="{e(DEEL_BEELD_ALT)}">',
        '  <script type="application/ld+json">'
        + json.dumps(gegevens, ensure_ascii=False).replace("</", "<\\/")
        + "</script>",
        KOP_EIND,
    ])


def _romp_blok(blokken):
    e = html.escape
    regels = [
        ROMP_START,
        "  <!-- De pagina in platte HTML, voor wie geen JavaScript draait: zoekmachines,",
        "       linkvoorbeelden in WhatsApp en LinkedIn, en AI-crawlers. De runtime",
        "       vervangt het hele html-element, dus wie wél JavaScript heeft ziet dit",
        "       nooit. De tekst wordt uit de gerenderde pagina gehaald door tools/seo.py",
        "       en is dus woordelijk gelijk aan wat de browser opbouwt. Met de hand",
        "       bewerken heeft geen zin: draai het script.",
        "       De kleuren komen overeen met de site, zodat dit bij een trage",
        "       verbinding niet als een kapotte pagina oogt. -->",
        '  <div id="seo-inhoud" style="max-width:48rem;margin:0 auto;padding:3rem 1.25rem;'
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;"
        'color:#1d1d1f;line-height:1.6">',
    ]
    links = []
    for b in blokken:
        t = e(b["tekst"])
        if b["tag"] == "a":
            links.append(b)
        elif b["tag"] == "h1":
            regels.append(f'    <h1 style="font-size:2rem;line-height:1.15">{t}</h1>')
        elif b["tag"] == "h2":
            regels.append(f'    <h2 style="font-size:1.5rem;line-height:1.2;margin-top:2rem">{t}</h2>')
        elif b["tag"] == "h3":
            regels.append(f'    <h3 style="font-size:1.2rem;margin-top:1.5rem">{t}</h3>')
        elif b["tag"] == "li":
            regels.append(f"    <p>{t}</p>")
        else:
            regels.append(f"    <p>{t}</p>")
    if links:
        regels.append('    <h2 style="font-size:1.5rem;margin-top:2rem">Onze producten</h2>')
        regels.append('    <ul>')
        for b in links:
            regels.append(f'      <li><a href="{e(b["href"])}">{e(b["tekst"])}</a></li>')
        regels.append('    </ul>')
    regels += ["  </div>", ROMP_EIND]
    return "\n".join(regels)


def _vervang(tekst, start, eind, nieuw, na):
    """Zet het blok terug op zijn plek, of plaatst het de eerste keer."""
    if start in tekst and eind in tekst:
        return re.sub(
            re.escape(start) + r".*?" + re.escape(eind), lambda _: nieuw, tekst, flags=re.S
        )
    i = tekst.index(na) + len(na)
    return tekst[:i] + "\n" + nieuw + tekst[i:]


def main():
    if not INDEX.exists():
        sys.exit("index.html niet gevonden")

    # 1 — de template krijgt dezelfde gegevens, want Google leest ná het renderen
    #     de vervangen <head> en niet meer die van de bundel.
    subprocess.run([sys.executable, str(WORTEL / "tools/bundle.py"), "unpack"],
                   check=True, capture_output=True)
    site = SITE.read_text(encoding="utf-8")
    site = site.replace("<title>LuzeX</title>", f"<title>{html.escape(TITEL)}</title>", 1)
    site = _vervang(site, KOP_START, KOP_EIND, _kop_blok(), f"<title>{html.escape(TITEL)}</title>")
    SITE.write_text(site, encoding="utf-8")
    subprocess.run([sys.executable, str(WORTEL / "tools/bundle.py"), "pack"],
                   check=True, capture_output=True)

    # 2 — de bundel zelf: titel, gegevens en de platte inhoud.
    #
    # Alleen de regels vóór de template-tag worden aangeraakt. De template-regel
    # bevat na stap 1 dezelfde markers, maar dan als tekst binnen een JSON-string;
    # zou de vervanging ook daar toeslaan, dan schrijft hij dwars door die string
    # heen en is de bundel stuk. Dat is één keer gebeurd.
    blokken = _ontdubbel(_render())
    alle = INDEX.read_text(encoding="utf-8").split("\n")
    grens = next(n for n, r in enumerate(alle)
                 if r.strip() == '<script type="__bundler/template">')
    index, staart = "\n".join(alle[:grens]), "\n".join(alle[grens:])
    index = index.replace("<html>", '<html lang="nl">', 1)
    index = index.replace("<title>LuzeX</title>", f"<title>{html.escape(TITEL)}</title>", 1)
    index = _vervang(index, KOP_START, KOP_EIND, _kop_blok(),
                     f"<title>{html.escape(TITEL)}</title>")
    index = _vervang(index, ROMP_START, ROMP_EIND, _romp_blok(blokken), "<body>")
    # De bundel meldde zonder JavaScript "This page requires JavaScript to
    # display." Dat was waar toen er niets stond, maar nu staat de hele pagina
    # er; de melding zou bezoekers en crawlers tegenspreken.
    index = index.replace("      This page requires JavaScript to display.\n",
                          "      Deze pagina toont zonder JavaScript alleen tekst.\n", 1)

    # Het miniatuur van de bundelaar beslaat het hele scherm en legt zich over
    # de platte versie heen: in de DOM stond de tekst er wel, maar een mens
    # zonder JavaScript keek tegen een leeg vlak aan. De noscript-stijl zette
    # het laadbericht al uit; het miniatuur hoort daar net zo goed bij.
    index = index.replace(
        "<style>#__bundler_loading { display: none; }</style>",
        "<style>#__bundler_loading, #__bundler_thumbnail { display: none; }</style>", 1)
    INDEX.write_text(index + "\n" + staart, encoding="utf-8")

    # 3 — de twee bestanden die elke crawler als eerste opvraagt.
    (WORTEL / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASIS, encoding="utf-8")
    (WORTEL / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url>\n    <loc>{BASIS}/</loc>\n    <changefreq>monthly</changefreq>\n"
        "    <priority>1.0</priority>\n  </url>\n</urlset>\n", encoding="utf-8")

    koppen = sum(1 for b in blokken if b["tag"].startswith("h"))
    print(f"{len(blokken)} blokken ({koppen} koppen, "
          f"{sum(1 for b in blokken if b['tag'] == 'a')} links) in de platte versie")


if __name__ == "__main__":
    main()
