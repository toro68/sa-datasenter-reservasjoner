<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Datasenter under planlegging</title>
  <style>
    .dc-widget {
      --dc-bg: #0f2d52;
      --dc-bg-2: #0a1e36;
      --dc-text: #ffffff;
      --dc-blue: #60a5fa;
      --dc-blue-fill: rgba(96, 165, 250, 0.28);
      --dc-red: #f87171;
      --dc-red-fill: rgba(248, 113, 113, 0.25);
      --dc-grid: rgba(255, 255, 255, 0.1);
      --dc-radius: 18px;

      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      box-sizing: border-box;
      width: 100%;
      max-width: 760px;
      margin: 0 auto 2rem;
      color: var(--dc-text);
    }

    .dc-widget * { box-sizing: inherit; }

    .dc-card {
      border-radius: var(--dc-radius);
      padding: 22px;
      background: linear-gradient(180deg, rgba(15, 45, 82, 0.95), rgba(10, 30, 54, 0.98));
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      position: relative;
      overflow: hidden;
    }

    .dc-card::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 60%);
      pointer-events: none;
    }

    .dc-title {
      font-size: 1.1rem;
      font-weight: 700;
      margin: 0 0 0.4rem 0;
    }

    .dc-subtitle {
      font-size: 0.95rem;
      color: rgba(255, 255, 255, 0.75);
      margin: 0 0 1.2rem 0;
    }

    .dc-metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.75rem;
      margin-bottom: 1.2rem;
    }

    .dc-metric {
      background: rgba(0, 0, 0, 0.15);
      border-radius: 12px;
      padding: 0.8rem 1rem;
    }

    .dc-metric span {
      display: block;
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.6);
    }

    .dc-metric strong {
      display: block;
      font-size: 1.5rem;
      font-weight: 800;
      margin-top: 0.2rem;
      letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
    }

    .dc-chart {
      width: 100%;
      height: auto;
      display: block;
      border-radius: 12px;
      background: rgba(0, 0, 0, 0.08);
    }

    .dc-chart.is-animating [data-js="area-queue"],
    .dc-chart.is-animating [data-js="area-res"] {
      opacity: 0;
    }

    .dc-chart.is-ready [data-js="area-queue"],
    .dc-chart.is-ready [data-js="area-res"] {
      opacity: 1;
      transition: opacity 0.8s ease;
    }

    .dc-legend {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-top: 0.8rem;
      font-size: 0.85rem;
      color: rgba(255, 255, 255, 0.7);
    }

    .dc-legend span::before {
      content: '';
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 999px;
      margin-right: 6px;
      vertical-align: middle;
    }

    .dc-legend .dc-blue::before { background: var(--dc-blue); }
    .dc-legend .dc-red::before { background: var(--dc-red); }

    .dc-note {
      font-size: 0.85rem;
      color: rgba(255, 255, 255, 0.75);
      margin-top: 0.6rem;
    }

    .dc-source {
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.5);
      margin-top: 1rem;
      text-align: right;
    }

    .dc-details {
      margin-top: 1.6rem;
      background: rgba(0, 0, 0, 0.18);
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      overflow: hidden;
    }

    .dc-details summary {
      cursor: pointer;
      padding: 0.9rem 1rem;
      font-weight: 700;
      list-style: none;
      color: rgba(255, 255, 255, 0.9);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .dc-details summary::-webkit-details-marker {
      display: none;
    }

    .dc-details summary::after {
      content: '›';
      transform: rotate(90deg);
      font-size: 1.2rem;
      transition: transform 0.2s ease;
    }

    .dc-details[open] summary::after {
      transform: rotate(-90deg);
    }

    .dc-details-content {
      padding: 0 1rem 1rem 1rem;
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.95rem;
      line-height: 1.45;
    }

    .dc-details-content h3 {
      margin: 1.1rem 0 0.4rem 0;
      font-size: 1rem;
      color: rgba(255, 255, 255, 0.92);
    }

    .dc-details-content p {
      margin: 0.5rem 0;
    }
  </style>
</head>
<body>
  <div class="dc-widget">
    <div class="dc-card">
      <h1 class="dc-title">Datasenter i Norge</h1>
      <p class="dc-note">Det er 88 registrerte datasentre (06.02.2026) i landet. I tillegg er mange under planlegging. Noen har fått reservert nettkapasitet, andre står i kapasitetskø.</p>

      <div class="dc-metrics">
        <div class="dc-metric">
          <span>Samlet total (reservasjoner + kapasitetskø)</span>
          <strong data-js="counter">0</strong>
        </div>
      </div>

      <svg class="dc-chart" viewBox="0 0 720 220" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <g data-js="grid"></g>
        <path data-js="area-queue" fill="var(--dc-red-fill)"></path>
        <path data-js="area-res" fill="var(--dc-blue-fill)"></path>
        <path data-js="line-total" fill="none" stroke="var(--dc-red)" stroke-width="3" stroke-linecap="round"></path>
        <path data-js="line-res" fill="none" stroke="var(--dc-blue)" stroke-width="3" stroke-linecap="round"></path>
        <g data-js="labels"></g>
      </svg>

      <div class="dc-legend">
        <span class="dc-blue">Reservasjoner</span>
        <span class="dc-red">Reservasjoner + kapasitetskø</span>
      </div>

      <div class="dc-source">Kilde: Statnett · Nkom (06.02.2026)</div>

      <details class="dc-details">
        <summary>Tilknytningsplikt og introduksjon for tilknytningsprosessen</summary>
        <div class="dc-details-content">
          <p>For å koble nye datasentre til strømnettet må prosjektene gjennom en formell tilknytningsprosess. Den består av flere steg – fra behovet meldes inn til det er inngått nettavtale og kapasiteten er klar til bruk.</p>

          <h3>Tilknytningsplikt</h3>
          <p>Norske nettselskaper har tilknytningsplikt. Det betyr at de i utgangspunktet skal gi kunder nettilknytning så lenge det er samfunnsmessig rasjonelt og kapasiteten kan håndteres.</p>

          <h3>Statnetts rolle</h3>
          <p>Statnett eier og drifter transmisjonsnettet ("motorveiene" i strømnettet). Det regionale og lokale nettet drives av nettselskaper. Store forbruks- eller produksjonsprosjekter blir meldt inn til Statnett via lokale nettselskaper.</p>

          <h3>Modenhet og kø</h3>
          <p>Prosjekter blir vurdert for modenhet før de kan gå videre. Datoen et prosjekt vurderes som modent avgjør plass i kapasitetskøen (førstemann til mølla).</p>

          <h3>Når det ikke er kapasitet</h3>
          <p>Hvis det ikke er plass i nettet, må kapasiteten bygges ut. Prosjekter kan da bli stående i kapasitetskø, eller få tilknytning på vilkår med lavere forsyningssikkerhet.</p>

          <h3>Reservasjon og oppfølging</h3>
          <p>Når kapasitet reserveres inngås en fremdriftsplan. Statnett kan kansellere reservasjoner ved store forsinkelser eller hvis prosjekter ikke blir realisert.</p>

          <p>Publisert 05.11.2018 – Sist oppdatert 28.01.2026</p>
        </div>
      </details>
    </div>
  </div>

  <script type="application/json" id="dc-data">
    {
      "labels": ["2018", "2020", "2021", "2022", "2023", "2024", "2025", "2026"],
      "reservasjoner": [1, 2, 3, 2, 6, 15, 19, 3],
      "kapasitetsko": [0, 0, 0, 6, 3, 18, 22, 4],
      "totalSamlet": 104
    }
  </script>

  <script>
    (() => {
      const data = JSON.parse(document.getElementById('dc-data').textContent);
      const formatter = new Intl.NumberFormat('nb-NO');

      const counter = document.querySelector('[data-js="counter"]');

      const svg = document.querySelector('.dc-chart');
      const gridGroup = svg.querySelector('[data-js="grid"]');
      const labelsGroup = svg.querySelector('[data-js="labels"]');
      const areaRes = svg.querySelector('[data-js="area-res"]');
      const areaQueue = svg.querySelector('[data-js="area-queue"]');
      const lineRes = svg.querySelector('[data-js="line-res"]');
      const lineTotal = svg.querySelector('[data-js="line-total"]');

      const width = 720;
      const height = 220;
      const padding = { top: 18, right: 28, bottom: 32, left: 28 };

      const cumulative = (values) => {
        const acc = [];
        let sum = 0;
        values.forEach(val => {
          sum += val;
          acc.push(sum);
        });
        return acc;
      };

      const resCumulative = cumulative(data.reservasjoner);
      const queueCumulative = cumulative(data.kapasitetsko);
      const totalSeries = resCumulative.map((val, i) => val + queueCumulative[i]);
      const maxVal = Math.max(...totalSeries);
      const innerW = width - padding.left - padding.right;
      const innerH = height - padding.top - padding.bottom;

      const makePoints = values => values.map((val, i) => {
        const x = padding.left + (i / (values.length - 1)) * innerW;
        const y = padding.top + innerH - ((val / maxVal) * innerH);
        return { x, y, val };
      });

      const resPoints = makePoints(resCumulative);
      const totalPoints = makePoints(totalSeries);

      const makeLine = points => points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
      const makeArea = points => {
        const baseY = padding.top + innerH;
        const line = makeLine(points);
        const end = points[points.length - 1];
        const start = points[0];
        return `${line} L${end.x.toFixed(1)},${baseY.toFixed(1)} L${start.x.toFixed(1)},${baseY.toFixed(1)} Z`;
      };

      const makeAreaBetween = (topPoints, bottomPoints) => {
        const topLine = makeLine(topPoints);
        const bottomLine = bottomPoints.slice().reverse().map((p, i) => {
          const cmd = i === 0 ? 'L' : 'L';
          return `${cmd}${p.x.toFixed(1)},${p.y.toFixed(1)}`;
        }).join(' ');
        return `${topLine} ${bottomLine} Z`;
      };

      lineRes.setAttribute('d', makeLine(resPoints));
      lineTotal.setAttribute('d', makeLine(totalPoints));
      areaRes.setAttribute('d', makeArea(resPoints));
      areaQueue.setAttribute('d', makeAreaBetween(totalPoints, resPoints));

      const totalLength = lineTotal.getTotalLength();
      const resLength = lineRes.getTotalLength();
      lineTotal.style.strokeDasharray = totalLength;
      lineTotal.style.strokeDashoffset = totalLength;
      lineRes.style.strokeDasharray = resLength;
      lineRes.style.strokeDashoffset = resLength;
      svg.classList.add('is-animating');


      const gridLines = 3;
      for (let i = 0; i <= gridLines; i++) {
        const y = padding.top + (i / gridLines) * innerH;
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', padding.left);
        line.setAttribute('x2', width - padding.right);
        line.setAttribute('y1', y);
        line.setAttribute('y2', y);
        line.setAttribute('stroke', 'var(--dc-grid)');
        line.setAttribute('stroke-width', '1');
        gridGroup.appendChild(line);
      }

      const startLabel = data.labels[0];
      const endLabel = data.labels[data.labels.length - 1];
      const bottomY = height - 10;
      const mkLabel = (x, text, anchor) => {
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', x);
        t.setAttribute('y', bottomY);
        t.setAttribute('fill', 'rgba(255,255,255,0.7)');
        t.setAttribute('font-size', '12');
        t.setAttribute('font-family', 'inherit');
        t.setAttribute('text-anchor', anchor);
        t.textContent = text;
        labelsGroup.appendChild(t);
      };

      mkLabel(resPoints[0].x, startLabel, 'start');
      mkLabel(resPoints[resPoints.length - 1].x, endLabel, 'end');

      const animate = () => {
        const endVal = data.totalSamlet;
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
          counter.textContent = formatter.format(endVal);
          lineTotal.style.strokeDashoffset = 0;
          lineRes.style.strokeDashoffset = 0;
          svg.classList.add('is-ready');
          svg.classList.remove('is-animating');
          return;
        }

        const duration = 2200;
        const startTime = performance.now();

        const tick = (now) => {
          const progress = Math.min((now - startTime) / duration, 1);
          const ease = 1 - Math.pow(1 - progress, 3);
          const currentVal = Math.round(endVal * ease);
          counter.textContent = formatter.format(currentVal);
          lineTotal.style.strokeDashoffset = totalLength * (1 - ease);
          lineRes.style.strokeDashoffset = resLength * (1 - ease);

          if (progress < 1) {
            requestAnimationFrame(tick);
          } else {
            counter.textContent = formatter.format(endVal);
            svg.classList.add('is-ready');
            svg.classList.remove('is-animating');
          }
        };

        requestAnimationFrame(tick);
      };

      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
          if (entries[0].isIntersecting) {
            animate();
            observer.disconnect();
          }
        }, { threshold: 0.3 });
        observer.observe(document.querySelector('.dc-widget'));
      } else {
        animate();
      }
    })();
  </script>
</body>
</html>
