# Audit luzex.nl — 20 november 2026

Nulmeting vóór het herontwerp. Gemeten op commit `7b13c0f`, lokaal geserveerd
uit `index.html`, in Chromium 1440x900 en 390x844.

Alles hieronder is nagemeten, niet geschat. Waar een bevinding uit de briefing
niet klopt met de code staat dat er expliciet bij, met het bewijs ernaast.

---

## 1. De belangrijkste vondst: twee verschillende sites

De bevindingen in de briefing beschrijven vrijwel allemaal de **versie zonder
JavaScript**, niet de site zoals een bezoeker hem ziet.

`index.html` is een gebundelde pagina. De echte site staat als JSON-string in
een `<script type="__bundler/template">` en wordt pas in de browser opgebouwd.
Voor zoekmachines en linkvoorbeelden staat er sinds 11 november een platte
terugvalversie in de oorspronkelijke `<body>`; die wordt weggegooid zodra
JavaScript draait.

Gemeten verschil op dezelfde pagina:

| | mét JavaScript | zonder JavaScript |
|---|---|---|
| navigatielinks | 6 | **0** |
| afbeeldingen | 4 | **0** |
| knoppen | 10 | **0** |

Dat verklaart punt 1, 4, 5, 6, 7 en 9 van de briefing in één keer. Wie de
ruwe HTML leest — een SEO-tool, een linkvoorbeeld, een AI-crawler — ziet
precies wat daar beschreven staat: geen menu, geen beeld, losse tekstregels,
dubbele productlinks en "Unpacking...".

Dat is een echt probleem, maar een ander probleem dan "de site heeft geen
navigatie". Het herontwerp moet beide kanten bedienen.

---

## 2. Lighthouse, nulmeting

Lighthouse 12, mobiele emulatie (de standaard), lokale server.

| Categorie | Score |
|---|---|
| Performance | 91 |
| Accessibility | 96 |
| Best Practices | 96 |
| SEO | 100 |

| Meetwaarde | |
|---|---|
| First Contentful Paint | 2,4 s |
| Largest Contentful Paint | 2,8 s |
| Total Blocking Time | 150 ms |
| Cumulative Layout Shift | 0 |
| Speed Index | 2,4 s |

Twee controles zakken:

**Contrast** — vijf elementen in de voettekst halen AA niet:

| Element | Verhouding | Eis |
|---|---|---|
| voetnoot-alinea (13px) | 3,64:1 | 4,5:1 |
| drie kolomkoppen (12px) | 3,22:1 | 4,5:1 |
| copyright (12px) | 2,85:1 | 4,5:1 |

Alle vijf `color-mix` van de tekstkleur op 50–60% over `#cfc6bc`. De rest van
de pagina haalt AA ruim; eerder nagemeten tussen 5,2:1 en 13,8:1.

**Beeldverhouding** — het logo staat op `height:47px;width:auto` maar wordt
145x47 (3,09) getoond terwijl het bestand 575x120 (4,79) is. Het woordmerk
wordt dus in de breedte samengedrukt.

---

## 3. De tien punten uit de briefing, nagelopen

| # | Punt | Bevinding |
|---|---|---|
| 1 | Geen beeldmateriaal | **Deels juist.** Er zijn vier abstracte SVG-mockups, maar geen echte productschermen van ACCRD. Zonder JavaScript: nul beeld. |
| 2 | Meerdere slogans | **Juist.** Drie naast elkaar: "Minder. Maar beter." (woordmerk), "Laat uw tijd weer naar uw vak gaan." (H1), "Wij beginnen bij het werk, niet bij de techniek." (H2). |
| 3 | Subheadline te lang | **Juist.** 123 tekens, twee zinnen: "Om elk vak heen groeit werk dat niemand ooit heeft ontworpen en dat iedereen is gaan accepteren. LuzeX bouwt gerichte producten op maat." |
| 4 | CTA "LIEVER DIRECT" onduidelijk | **Deels juist.** Met JavaScript is het een klein kopje boven mail/WhatsApp/bellen, naast het formulier. Zonder JavaScript staat het als losse regel zonder context. |
| 5 | Geen zichtbare navigatie | **Onjuist op desktop, juist op mobiel.** Er is een zwevende balk met Aanpak, Producten, Op maat, Contact. Onder 700px worden die vier verborgen zonder vervanging: er is geen mobiel menu. |
| 6 | Dubbele productlinks | **Artefact van de platte versie.** Met JavaScript: drie knoppen in de productsectie plus drie links in de voettekst, wat normaal is. Zonder JavaScript staan ze als twee naamloze rijtjes onder elkaar. |
| 7 | "Unpacking..." onderaan | **Juist in de ruwe HTML.** Staat in `index.html` als laadmelding van de bundelaar (`#__bundler_loading`). In de browser verdwijnt hij en is hij niet zichtbaar; een tool die de HTML leest ziet hem wel. |
| 8 | Wordmerk als "L U Z E X" | **Juist, maar niet waar verwacht.** In de pagina staat `.merk` met `letter-spacing: 0.22em` en de tekst "LuzeX", precies zoals gevraagd. De spaties staan in de **meta-omschrijving**: "L u z e X bouwt gerichte software op maat…". Die tekst komt in zoekresultaten en linkvoorbeelden terecht. |
| 9 | Drie "bouwen"-regels zijn fragmenten | **Artefact van de platte versie.** Met JavaScript is het een vinkjeslijst onder "En wat er nog niet is, bouwen we." met één knop eronder. Zonder JavaScript drie kale regels. |
| 10 | Contrast en focus | **Contrast: deels juist** (zie §2, vijf elementen in de voettekst). **Focus: al aanwezig.** Zes regels, waaronder `:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px }`. Nog te verifiëren of die zichtbaar is op het glas en op de donkerbruine baan. |

---

## 4. Wat ik daarnaast tegenkwam

- **De pagina is lang.** 7.895px op desktop, **10.520px op mobiel**. Dat is
  ruim twaalf schermen scrollen op een telefoon.
- **Geen mobiel menu.** Zie punt 5. Alle sectielinks verdwijnen onder 700px.
- **Het logo wordt vervormd.** Zie §2.

---

## 5. Waar de briefing afwijkt van de repository

Deze punten zijn geen fout maar een verschil in aanname. Ze raken het
ontwerp, dus ze staan als open vraag in het plan.

| Briefing | In de code |
|---|---|
| Kleuren #4a3f37 en #d4cec4 | `--color-bg: #cfc6bc`, `--color-text: #1d1d1f`, `--color-diep: #3b2e24` |
| Cormorant Garamond + DM Sans | Systeemstack: `-apple-system, BlinkMacSystemFont, 'SF Pro Text'…`. Geen enkel extern lettertype; nul `@font-face`, nul Google Fonts. |
| Producten: ACCRD, CMMNTY, SCRNN | ACCRD, CMMNTY en **RSLNT**. SCRNN komt alleen nog voor in één CSS-commentaarregel en is in oktober van de pagina gehaald. |
| CMMNTY in ontwikkeling | CMMNTY staat sinds oktober als draaiend product op de pagina, met een knop naar cmmnty.luzex.nl. |
| GGZ-advies voor praktijkhouders | **Nul vermeldingen** van "GGZ" of "praktijkhouder" op de hele site. |

---

## 6. Bestanden

Schermafdrukken en de ruwe Lighthouse-uitvoer staan in de werkmap van de
sessie en zijn niet in de repository opgenomen (te groot, en ze zijn opnieuw
te maken met `tools/bundle.py unpack` plus de stappen hierboven).
