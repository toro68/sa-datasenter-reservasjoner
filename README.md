# Forslag til visualiseringer og produkter basert på datasettet

Dette repoet inneholder et tabelluttrekk (ca. 190 rader) med reserverte MW, næringstype, prisområde/områdeplan, stasjon, kunde/sluttkunde og datoer. Under er konkrete ideer til visualiseringer, interaktive tabeller, kart og andre produkter, samt anbefalt struktur for å gjøre dataene enkle å bruke i kode og publisering.

## Filer og anbefalt flyt

### Rådata
- `reservasjoner.tsv`: Tab-separert kopi av tabellen slik den ble hentet/limt inn.

### Anbefalt (for visualisering/publisering)
- `datasett_clean.csv`: Normalisert versjon for analyse og grafikk.
  - datoer: `YYYY-MM-DD`
  - numeriske felt: punktum som desimal (`560.00`)
  - stabile kolonnenavn (ASCII/snake_case)
- `datasett.json`: Publiseringsvennlig JSON (array av objekter) for inline-HTML.
- `datasett_clean.json`: Normalisert JSON (typed felter + snake_case) for kode/inline-HTML.
- `summary.json`: Enkel oppsummering (total MW + MW per næringstype/prisområde).

### Bygg
- Kjør `python3 scripts/build_clean.py` for å regenerere `datasett_clean.csv`, `datasett_clean.json` og `summary.json` fra `Reservasjoner - Ark 1.csv`.
- Kjør `python3 scripts/build_queue_clean.py` for å regenerere `kapasitetsko_clean.csv`, `kapasitetsko_clean.json` og `kapasitetsko_summary.json` fra `Reservasjoner - Kapasitetskø.csv`.

## Nettside (filtrering + topplister)

- Åpne `web/index.html` via en lokal webserver (ikke `file://`) slik at `fetch()` kan laste JSON-filene.
- Eksempel (Python): `python3 -m http.server 8000`
- Gå til: `http://localhost:8000/web/`

### Kartgrunnlag (velg én)
- `stasjoner.csv`: `stasjon,lat,lon` (WGS84 / EPSG:4326)
- `stasjoner.geojson`: punktlag med samme nøkkel som i datasettet (typisk `stasjon`).

Uten et slikt kartgrunnlag kan kart lages aggregert på `prisområde`/`områdeplan`, men ikke som punktkart per stasjon.

## Kolonner (kort forklaring)

Felt slik de står i `reservasjoner.tsv`:
- `Saksnr.`: saksnummer (forventes å være unik per rad, men må verifiseres).
- `Stasjon for tilknytning i transmisjonsnettet`: stasjonsnavn/tilknytningspunkt.
- `Områdeplan`: Statnetts områdeplan.
- `Prisområde`: prisområde (NO1–NO5 når oppgitt).
- `Statnetts kunde`: kunden Statnett forholder seg til (nett-/tilknytningskunde).
- `Sluttkunde`: sluttkunden/aktøren som skal bruke kapasiteten.
- `Næringstype`: bransjekategori.
- `Reservert kapasitet (MW)`: kapasitet i MW (lagret med desimal-komma i rådata).
- `Dato for når Statnett reserverte kapasitet til kunden`: dato for reservasjon.
- `Kundens ønskede tilknytningstidspunkt`: ønsket tilknytning.
- `Kundens referanse`: intern referanse (kan være tom).
- `Kunde og tilknytningsansvarlig`: personnavn (vurder anonymisering før publisering).

## Datakvalitet (ting å avklare tidlig)
- Definisjon: Hva betyr "reservert kapasitet" i praksis (bestilt, avtalt, reservert, maksimal)?
- Dubletter: Kan samme prosjekt finnes i flere rader (f.eks. ny sak, endring, flere faser)?
- Geografi: Er `stasjon` entydig nok til geokoding, eller trengs en egen stasjons-ID?
- Persondata: Skal personnavn publiseres, eller fjernes/erstattes?
 - Manglende verdier: Enkelte rader mangler `Prisområde` eller `Dato for når Statnett reserverte kapasitet til kunden`.

## Nøkkelspørsmål som kan besvares
- Hvor mye kapasitet er reservert totalt, og hvordan fordeler det seg på næringstype?
- Hvilke prisområder og områdeplaner har størst press?
- Hvilke kunder/sluttkunder står for mest kapasitet?
- Hvordan har reservasjoner utviklet seg over tid?
- Hvor langt fram i tid ligger ønsket tilknytning i snitt per næringstype?

## Visualiseringer

### 1) Tidslinje for reserverte MW
- Linje- eller arealdiagram: Sum reserverte MW per år (basert på dato for reservasjon).
- Variant: Brutt ned på næringstype for å vise skift i bransjemiks.

### 2) Bransjemiks
- Stablede stolper: MW per næringstype per prisområde.
- Donut/treemap: Andeler MW per næringstype nasjonalt.

### 3) Topplister
- Rangering av Statnetts kunde og sluttkunde etter MW.
- Pareto (80/20) for å vise konsentrasjon.

### 4) Frem i tid (pipeline)
- Histogram eller boksplott av differanse mellom reservasjon og ønsket tilknytningstidspunkt.
- Segmentering per næringstype eller prisområde.

### 5) Kapasitet per stasjon
- Stolper: MW per stasjon.
- Kombiner med områdeplan for å se klynger.

### 6) Porteføljeheatmap
- Heatmap med prisområde på x-akse og næringstype på y-akse, farge = MW.

## Interaktive tabeller

### A) Filtrerbar oversikt
- Filtre: prisområde, områdeplan, næringstype, tidsintervall.
- Søke­felt på stasjon, kunde, sluttkunde.
- Sortering på MW og dato.

### B) Drilldown
- Klikk på næringstype → vis tilhørende stasjoner og kunder.
- Klikk på prisområde → vis tidsserie og toppkunder.

## Kart

### 1) Kart pr områdeplan eller prisområde
- Choropleth med total MW per område.
- Tooltip med topp 3 kunder og hovednæringer.

### 2) Punktkart (hvis stasjon kan geokodes)
- Punkter for stasjoner med størrelse = MW.
- Fargekodet etter næringstype.

## Inline-HTML og fortellende grafikk
- Scrollytelling: nasjonal trend → regioner → toppkunder → enkeltprosjekter.
- Små KPI‑kort: total MW, antall saker, antall datasenter‑saker.
- Mini‑sparklines per næringstype i tabellen.

## Datakvalitet og normalisering
- Konverter MW til numerisk (komma som desimaltegn).
- Normaliser datoer til ISO‑format.
- Vurdér anonymisering av personnavn.
- Legg til koordinater eller kommune/fylke for presise kart.

## Mulige videre datatillegg
- Status (aktiv/tilbaketrukket) for å kunne vise churn.
- Faktisk tilknytningstidspunkt når tilgjengelig.
- Energiselskap/region‑metadata for mer presise kart.

## Leveranser som kan bygges
- Interaktiv dashbordside med kart, trend, bransjemiks og topplister.
- Nedlastbar CSV/TSV og enkel API‑endpoint.
- Grafikkpakke til publisering: kart, tidslinje, topp‑10 og bransjemiks.
