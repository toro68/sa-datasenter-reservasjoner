# Inline HTML Templates for Aftenbladet.no

Samling av mobile-first inline HTML-maler med korrekt håndtering av norske tegn (æ, ø, å) og Aftenbladets blå designprofil.

## Oversikt

### 1. `rutekutt/template.html` - Full funksjonell mal
Komplett artikkelmal med:
- Responsiv layout (mobil → tablet → desktop)
- Header, innhold, bilder, sitater, knapper
- CSS Grid for fleksibel kolonneoppbygning
- Print-vennlige stiler
- Tilgjengelighetsforbedringer (prefers-reduced-motion, high contrast)

**Bruksområde:** Fullstendige artikler med rikt innhold

### 2. `rutekutt/minimal.html` - Lettvekts mal
Kompakt versjon med:
- Minimalistisk design
- Raskere lasting
- Samme responsive struktur
- Perfekt for enkle nyhetsartikler

**Bruksområde:** Raske oppdateringer og enkle saker

### 3. `rutekutt/test-norske-tegn.html` - Testside
Omfattende verktøy for å validere:
- Alle norske tegn (æøå ÆØÅ)
- Tabeller med Unicode-referanser
- Skjemaelementer
- Responsiv visning
- JavaScript-håndtering

**Bruksområde:** Kvalitetssikring før publisering

### 4. `rutekutt/inline-buss-endringer.html` - Interaktiv sammenligning
Avansert datatabell med:
- 42+ busseruter (Nord-Jæren)
- Dropdown-navigasjon
- Automatisk highlighting av endringer
- Ekspanderbar bakgrunnskontekst
- Optimalisert for mobilvisning med auto-scroll

**Bruksområde:** Komplekse datavisualiseringer og sammenligninger

### 5. `strandsone/strandsone.html` - Strandsone-widget
Kompakt widget med:
- Kommune- og metrikktvalg
- Graf med Chart.js (pinnet CDN-versjon)
- Scoped CSS for trygg inline-publisering

**Bruksområde:** Interaktiv strandsone-grafikk i artikkel

### 6. `strandsone-statsforvalter/inline-statsforvalter.html` - Statsforvalteren (klager/innsigelser)
Mobile-first widget med:
- Datasetswitch (dispensasjoner/plansaker)
- Måltallsvelger, KPI-er og enkel SVG-linjeserie (ingen eksterne avhengigheter)
- Tabell under `<details>` (unngår scroll trap)

**Bruksområde:** Inline oversikt over Statsforvalteren Rogaland 2015–2025

### 7. `strandsone-12000/index.html` - Scrollytelling med teller
Enkel scrollytelling med:
- 4 slides (plassholdere for drone/video, kart, punkter, naturfoto)
- Scroll-triggered teller (konfigurerbar med `data-start`/`data-end`)
- Valgfri «røde punkter»-animasjon på kart via canvas

**Bruksområde:** Fortellergrafikk med teller/scroll

### 8. `tidslinje/index.html` - Historikk-tidslinje
Kompakt tidslinje-widget med:
- Vertikal tidslinje (mobil-first)
- Scoped CSS via unik wrapper-ID (trygg for inline-publisering)
- Semantisk markup med `<time>` og god tastaturnavigasjon

**Bruksområde:** Kort historikk/regelutvikling i artikkel

### 9. `ryfast/inline-ryfast-takster-i-dag.html` - Ryfast takster i dag
Kompakt takst-widget med:
- Toggle for takstgruppe 1/2 (under/over 3,5 tonn)
- Side-by-side visning: AutoPASS-avtale vs uten avtale
- «Takst fra 02.07.25» + tydelig «endring»-pill (mot takst før 02.07.25)
- Ekstra forklaring under `<details>` (unngår scroll trap)

**Bruksområde:** Rask oversikt over gjeldende takster og takstnedsettelsen

### 10. `ryfast/inline-ryfast-takster.html` - Ryfast (historisk før/etter)
Variant som viser «t.o.m. 01.07.25» vs «f.o.m. 02.07.25».

### 11. `restauranter/2024-gjesdal-jæren/inline-gjesdal-jaeren.html` - Restaurantaktører (Gjesdal + Jærkommunene)
Mobile-first widget med:
- Søk + kommune-filter + sortering (omsetning/ansatte/årsresultat)
- Toppliste med nøkkeltall, og detaljer per selskap via `<details>` (ingen scroll-trap)
- Metodeforklaring «Gjesdal + Jærkommunene» inkludert (forretningsadresse vs driftssted)

**Datagrunnlag:** Innebygd JSON i HTML-fila (generert fra `Gjesdal + Jæren.xlsx`)

### 12. `vestlandspakker/inline-vestlandspakkene.html` - Vestlandspakkene (nord/sør)
Inline widget med:
- Søk + pakkefilter (Vestlandspakke nord/sør)
- Prosjektkort med distanse og kostnad
- Scoped CSS via `#vp-app` + vanilla JS (ingen eksterne avhengigheter)

**Datagrunnlag:** Hentet manuelt fra `vestlandspakker/Vestlandspakkene-2-1.pdf` (Februar 2026)

### 13. `moifjellet/inline-moifjellet-kompensasjon.html` - Moifjellet kompensasjon
Kompakt widget med:
- Kort oppsummering av kompensasjonssatser
- Inline tabell med tydelige beløp
- Scoped CSS i egen widget-ID

**Bruksområde:** Kort forklaring + satser i artikkel

### 14. `Vassøy/inline-vassoy-ferge.html` - Vassøy ferge
Kompakt widget med:
- Ruteoversikt og nøkkelinformasjon
- Mobil-tilpasset liste
- Scoped CSS for trygg inline-publisering

**Bruksområde:** Ruteinformasjon i artikkel

### 15. `restauranter/2024-stavanger-sandnes/inline-stavanger-sandnes.html` - Restaurantaktører (Stavanger + Sandnes)
Mobile-first widget med:
- Søk + kommune-filter + sortering
- Toppliste med nøkkeltall
- Metodeforklaring inkludert

**Bruksområde:** Inline oversikt over restaurantaktører i Stavanger/Sandnes

## Designsystem

### Fargepalett (Aftenbladet blå profil)
```css
--ab-blue: #0f2d52;        /* Primærfarge */
--ab-blue-dark: #0a1e36;   /* Hover-tilstand */
--ab-dark: #1a1a1a;        /* Tekst */
--ab-grey: #555555;        /* Sekundær tekst */
--ab-light: #f5f7fa;       /* Bakgrunn */
--ab-border: #d8e1eb;      /* Skillelinjer */
--ab-highlight: #dbe8f8;   /* Markering (ny) */
--ab-highlight-old: #eef3fb; /* Markering (gammel) */
```

### Responsivt design
- **Mobil:** < 768px (base styles)
- **Tablet:** ≥ 768px
- **Desktop:** ≥ 1024px

## Optimaliseringer

### Ytelse
- System fonts med fallback: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- Font-smoothing for bedre rendering
- Tabular numbers for tallkolonner (`font-variant-numeric`)
- Minimal CSS med CSS custom properties

### Tilgjengelighet
- Semantisk HTML5 (`<main>`, `<article>`, `<header>`)
- ARIA-attributter (`role`, `aria-expanded`, `aria-controls`, `aria-live`)
- `scope` på tabellceller for skjermlesere
- Keyboard-navigasjon
- `prefers-reduced-motion` support
- `prefers-contrast: high` support
- Print-optimaliserte stiler

### Brukeropplevelse
- Auto-scroll til resultat på mobil
- Smooth transitions (respekterer brukerpreferanser)
- Focus states på interaktive elementer
- Tydelige hover-indikatorer

## Teknisk Stack

- **HTML5:** Moderne semantisk markup
- **CSS3:** Custom properties, Grid, Flexbox, Media queries
- **Vanilla JavaScript:** Ingen avhengigheter
- **UTF-8:** Full støtte for norske tegn
- **Inline kommentarer:** Relevante forklaringer ved hver kodeseksjon

## Kommentarstruktur

Alle maler har **fokuserte inline-kommentarer** som forklarer spesifikke deler:

### CSS-kommentarer
```css
/* Fargepalett - Aftenbladet blå profil */
:root { ... }

/* System fonts + antialiasing */
body { ... }

/* Høykontrast-støtte */
@media (prefers-contrast: high) { ... }
```

### JavaScript-kommentarer
```javascript
// Toggle-funksjon for ekspanderbar bakgrunnskontekst
function toggleContext() { ... }

// Sammenlign verdier for automatisk highlighting
const valuesDiffer = (a, b) => { ... }

// Auto-scroll til resultat på mobil for bedre UX
if (window.innerWidth < 768) { ... }
```

**Fordeler:**
- Lettere å forstå hva hver del gjør
- Enklere vedlikehold og feilsøking
- Fungerer som innebygd dokumentasjon
- Raskere onboarding for nye utviklere

## Kopierbar boilerplate

```html
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Widget-tittel</title>
  <style>
    :root {
      --ab-blue: #0f2d52;
      --ab-blue-dark: #0a1e36;
      --ab-dark: #1a1a1a;
      --ab-grey: #555555;
      --ab-light: #f5f7fa;
      --ab-border: #d8e1eb;
      --ab-highlight: #dbe8f8;
      --ab-highlight-old: #eef3fb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    #topic-widget .tw-card { background: var(--ab-light); }
    #topic-widget .tw-button:focus-visible { outline: 2px solid var(--ab-blue); }
  </style>
</head>
<body>
  <div id="topic-widget">
    <main class="tw-card" aria-live="polite">
      <h2>Widget-tittel</h2>
      <p>Kort intro.</p>
      <button class="tw-button" type="button">Knapp</button>
    </main>
  </div>

  <script type="application/json" id="topic-data">
    []
  </script>

  <script>
    (() => {
      const data = JSON.parse(document.getElementById('topic-data').textContent);
      const button = document.querySelector('#topic-widget .tw-button');
      button.addEventListener('click', () => {
        console.log('Klikk', data.length);
      });
    })();
  </script>
</body>
</html>
```

## Testing

Før publisering, sjekk:
1. Åpne `test-norske-tegn.html` i nettleseren
2. Verifiser at alle æ, ø, å vises korrekt
3. Test på flere enheter (mobil, tablet, desktop)
4. Sjekk i ulike nettlesere (Chrome, Safari, Firefox, Edge)
5. Valider med screenreader hvis mulig
6. Kjør `npx html-validate <fil>.html`

## Filstruktur

```
sa-inline-html/
├── AGENTS.md
├── README.md
├── Vassøy/
├── aking/
├── moifjellet/
├── oalsgata/
├── restauranter/
├── rutekutt/
├── ryfast/
├── strandsone/
├── strandsone-12000/
├── strandsone-statsforvalter/
├── tidslinje/
└── vestlandspakker/
```

## Best Practices

1. **Alltid sett `lang="no"`** i `<html>`-taggen
2. **Bruk UTF-8:** `<meta charset="UTF-8">`
3. **Mobile-first:** Design for mobil først, utvid oppover
4. **Test norske tegn:** Bruk test-siden før produksjon
5. **Inline CSS:** Hold alt i én fil for enkel distribusjon
6. **Semantisk HTML:** Bruk riktige tags (`<article>`, `<section>`, etc.)
7. **Tilgjengelighet:** Legg til ARIA-attributter der det gir mening
8. **Performance:** Minimer DOM-manipulasjon, bruk event delegation
9. **SRI:** Bruk alltid `integrity` + `crossorigin="anonymous"` på CDN-lenker
10. **Data-separasjon:** Store store datasett i `<script type="application/json">`

## SRI-eksempel
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" integrity="sha384-<HASH>" crossorigin="anonymous"></script>
```

## Lisens

Disse malene er utviklet for internt bruk hos Aftenbladet.

---

**Sist oppdatert:** 7. februar 2026
**Versjon:** 2.1 (Standardisert)
**Kontakt:** tor.inge.jossang@aftenbladet.no
