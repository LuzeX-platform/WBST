# WBST
Overkoepelende website ter tentoonstelling van LuzeX-projecten

## Website bewerken

De site is één gebundeld bestand: `index.html`. De echte pagina-inhoud staat
daarin als JSON-string in de `__bundler/template`-tag, met fonts en
afbeeldingen base64 in de manifest-tag. Bewerk `index.html` daarom niet
rechtstreeks, maar via:

```bash
python3 tools/bundle.py unpack   # -> site.html (leesbare pagina)
# bewerk site.html
python3 tools/bundle.py pack     # -> schrijft terug naar index.html
```

`site.html` is een werkkopie en staat in `.gitignore`; alleen `index.html`
wordt uitgeleverd. Uitpakken en direct weer inpakken laat `index.html`
byte-identiek.

`support.js` en `image-slot.js` worden niet door `index.html` geladen — het
zijn restanten van het build-gereedschap.
