<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Strandsone Monitor</title>
  <style>
    /* Scoped variables for the component */
    .strand-widget {
      --sw-bg-primary: #0f2d52;
      --sw-bg-secondary: #0a1e36;
      --sw-text: #ffffff;
      --sw-accent: #60a5fa; /* Lysere blå for bedre kontrast */
      --sw-radius: 18px;
      --sw-chart-line: rgba(255, 255, 255, 0.9);
      --sw-chart-grid: rgba(255, 255, 255, 0.1);

      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      box-sizing: border-box;
      width: 100%;
      max-width: 720px;
      margin: 0 auto 2rem;
    }

    .strand-widget * { box-sizing: inherit; }

    .strand-widget-card {
      border-radius: var(--sw-radius);
      padding: 20px;
      background: linear-gradient(180deg, rgba(15, 45, 82, 0.95), rgba(10, 30, 54, 0.98));
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      color: var(--sw-text);
      text-align: center;
      position: relative;
      overflow: hidden;
    }

    /* Subtle background effect */
    .strand-widget-card::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 60%);
      pointer-events: none;
    }

    .strand-value {
      font-size: clamp(2.5rem, 8vw, 4.5rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.1;
      font-variant-numeric: tabular-nums;
      margin: 0;
      background: linear-gradient(180deg, #fff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .strand-caption {
      font-size: 1rem;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 0.5rem;
    }

    .strand-chart-container {
      margin-top: 2rem;
      opacity: 0; /* Hidden until rendered */
      transition: opacity 0.6s ease;
    }

    .strand-chart-container.is-ready { opacity: 1; }

    .strand-chart {
      width: 100%;
      height: auto;
      display: block;
      background: rgba(0, 0, 0, 0.1);
      border-radius: 12px;
    }

    .strand-source {
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.5);
      margin-top: 1rem;
      text-align: right;
    }

    /* Screen Reader Only class */
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
  </style>
</head>
<body>

  <div class="strand-widget"
    data-series="31643,34085,34665,35311,35954,36485,37067,37559,38128,38624,39092,39495,39927,40315,40733,41350,41793,42233,42691,43114,43424,43723"
    data-labels="2000,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025"
    data-caption="Bygninger i strandsonen (Rogaland)"
    data-source="Kilde: SSB (tabell 06505)"
    data-duration="2500">

    <div class="strand-widget-card">
      <div class="sr-only" data-js="sr-text">Antall bygninger i strandsonen økte fra 31 643 i 2000 til 43 723 i 2025.</div>

      <div class="strand-value" aria-hidden="true" data-js="counter">0</div>
      <div class="strand-caption" data-js="caption"></div>

      <div class="strand-chart-container" data-js="chart-wrap">
        <svg class="strand-chart" viewBox="0 0 640 180" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
          <defs>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="rgba(255,255,255,0.4)" />
              <stop offset="100%" stop-color="rgba(255,255,255,1)" />
            </linearGradient>
          </defs>
          <g data-js="grid-group"></g>
          <path fill="none" stroke="url(#lineGradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" data-js="chart-line"></path>
          <g data-js="labels-group"></g>
          <circle r="6" fill="#e74c3c" stroke="#fff" stroke-width="2" data-js="chart-marker"></circle>
        </svg>
      </div>

      <div class="strand-source" data-js="source"></div>
    </div>
  </div>

  <script>
    /**
     * Strandsone Counter Widget Factory
     * Initializes all widgets found on the page.
     */
    (function initStrandWidgets() {
      const widgets = document.querySelectorAll('.strand-widget');
      const formatter = new Intl.NumberFormat('nb-NO');

      // Configuration constants
      const CONFIG = {
        chartWidth: 640,
        chartHeight: 180,
        padding: { top: 20, bottom: 30, left: 20, right: 20 }
      };

      widgets.forEach(widget => {
        setupWidget(widget);
      });

      function setupWidget(root) {
        // Elements
        const els = {
          counter: root.querySelector('[data-js="counter"]'),
          caption: root.querySelector('[data-js="caption"]'),
          source: root.querySelector('[data-js="source"]'),
          chartWrap: root.querySelector('[data-js="chart-wrap"]'),
          chartLine: root.querySelector('[data-js="chart-line"]'),
          chartMarker: root.querySelector('[data-js="chart-marker"]'),
          gridGroup: root.querySelector('[data-js="grid-group"]'),
          labelsGroup: root.querySelector('[data-js="labels-group"]'),
          srText: root.querySelector('[data-js="sr-text"]')
        };

        // Data Parsing
        const rawSeries = root.dataset.series || '';
        const rawLabels = root.dataset.labels || '';
        const series = rawSeries.split(',').map(n => Number(n.trim()));
        const labels = rawLabels.split(',').map(s => s.trim());
        const duration = Number(root.dataset.duration || 2000);

        if (series.length < 2) return; // Not enough data

        const startVal = series[0];
        const endVal = series[series.length - 1];

        // Populate static text
        if (els.caption) els.caption.textContent = root.dataset.caption;
        if (els.source) els.source.textContent = root.dataset.source;

        // Update SR text dynamically based on data
        if (els.srText) {
          els.srText.textContent = `${root.dataset.caption}: Økning fra ${formatter.format(startVal)} (${labels[0]}) til ${formatter.format(endVal)} (${labels[labels.length -1]}).`;
        }

        // Initialize Chart
        const chartData = buildChartPath(series, CONFIG);
        if (els.chartLine) els.chartLine.setAttribute('d', chartData.pathString);

        drawGrid(els.gridGroup, CONFIG);
        drawLabels(els.labelsGroup, chartData.points, labels, series, CONFIG);

        // Setup Animation Variables
        const totalLength = els.chartLine.getTotalLength();
        els.chartLine.style.strokeDasharray = totalLength;
        els.chartLine.style.strokeDashoffset = totalLength;

        // Set initial marker position
        if (chartData.points.length > 0) {
          const first = chartData.points[0];
          els.chartMarker.setAttribute('cx', first.x);
          els.chartMarker.setAttribute('cy', first.y);
        }

        els.chartWrap.classList.add('is-ready');

        // Animation Logic
        let hasAnimated = false;

        const animate = () => {
          if (hasAnimated) return;
          hasAnimated = true;

          const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

          if (prefersReducedMotion) {
            els.counter.textContent = formatter.format(endVal);
            els.chartLine.style.strokeDashoffset = 0;
            const last = chartData.points[chartData.points.length - 1];
            els.chartMarker.setAttribute('cx', last.x);
            els.chartMarker.setAttribute('cy', last.y);
            return;
          }

          const startTime = performance.now();

          const tick = (now) => {
            const progress = Math.min((now - startTime) / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3); // Cubic ease-out

            // Update Number
            const currentVal = Math.round(startVal + (endVal - startVal) * ease);
            els.counter.textContent = formatter.format(currentVal);

            // Update Chart Line
            els.chartLine.style.strokeDashoffset = totalLength * (1 - ease);

            // Update Marker Position (Interpolation)
            const pointIndex = ease * (chartData.points.length - 1);
            const i = Math.floor(pointIndex);
            const t = pointIndex - i;

            const p0 = chartData.points[Math.min(i, chartData.points.length - 1)];
            const p1 = chartData.points[Math.min(i + 1, chartData.points.length - 1)];

            if (p0 && p1) {
              const x = p0.x + (p1.x - p0.x) * t;
              const y = p0.y + (p1.y - p0.y) * t;
              els.chartMarker.setAttribute('cx', x);
              els.chartMarker.setAttribute('cy', y);
            }

            if (progress < 1) {
              requestAnimationFrame(tick);
            } else {
              // Ensure final state is exact
              els.counter.textContent = formatter.format(endVal);
              els.counter.removeAttribute('aria-hidden'); // Reveal to accessibility tree if needed
            }
          };

          requestAnimationFrame(tick);
        };

        // Scroll Trigger
        if ('IntersectionObserver' in window) {
          const observer = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting) {
              animate();
              observer.disconnect();
            }
          }, { threshold: 0.3 });
          observer.observe(root);
        } else {
          animate(); // Fallback
        }
      }

      // Helper: Calculate Chart Coordinates
      function buildChartPath(values, conf) {
        const min = Math.min(...values);
        const max = Math.max(...values);
        // Add 5% padding to range to prevent sticking to edges
        const range = (max - min) || 1;
        const paddedMin = min - (range * 0.1);
        const paddedMax = max + (range * 0.1);

        const innerW = conf.chartWidth - conf.padding.left - conf.padding.right;
        const innerH = conf.chartHeight - conf.padding.top - conf.padding.bottom;

        const points = values.map((val, i) => {
          const x = conf.padding.left + (i / (values.length - 1)) * innerW;
          const normalizedVal = (val - paddedMin) / (paddedMax - paddedMin);
          const y = conf.padding.top + innerH - (normalizedVal * innerH);
          return { x, y };
        });

        const pathString = points.map((p, i) =>
          (i === 0 ? 'M' : 'L') + `${p.x.toFixed(1)},${p.y.toFixed(1)}`
        ).join(' ');

        return { points, pathString };
      }

      // Helper: Draw Background Grid
      function drawGrid(group, conf) {
        if (!group) return;
        const lines = 3;
        const innerH = conf.chartHeight - conf.padding.top - conf.padding.bottom;

        for (let i = 0; i <= lines; i++) {
          const y = conf.padding.top + (i / lines) * innerH;
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', conf.padding.left);
          line.setAttribute('x2', conf.chartWidth - conf.padding.right);
          line.setAttribute('y1', y);
          line.setAttribute('y2', y);
          line.setAttribute('stroke', 'rgba(255,255,255,0.1)');
          line.setAttribute('stroke-width', '1');
          group.appendChild(line);
        }
      }

      // Helper: Draw Start/End Labels on Chart
      function drawLabels(group, points, labels, values, conf) {
        if (!group || points.length < 2) return;

        const bottomY = conf.chartHeight - 10;

        const createEndpoint = (point, year, numVal, align) => {
          // Dot at the endpoint
          const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          dot.setAttribute('cx', point.x);
          dot.setAttribute('cy', point.y);
          dot.setAttribute('r', 3);
          dot.setAttribute('fill', '#fff');
          group.appendChild(dot);

          // Year label on x-axis (bottom)
          const yearText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          yearText.setAttribute('fill', 'rgba(255,255,255,0.7)');
          yearText.setAttribute('font-size', '12');
          yearText.setAttribute('font-family', 'inherit');
          yearText.setAttribute('text-anchor', align);
          yearText.setAttribute('x', point.x);
          yearText.setAttribute('y', bottomY);
          yearText.textContent = year;
          group.appendChild(yearText);

          // Value label above the line (near endpoint)
          const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          valueText.setAttribute('fill', 'rgba(255,255,255,0.92)');
          valueText.setAttribute('font-size', '12');
          valueText.setAttribute('font-family', 'inherit');
          valueText.setAttribute('text-anchor', align);
          valueText.setAttribute('stroke', 'rgba(10,30,54,0.7)');
          valueText.setAttribute('stroke-width', '4');
          valueText.setAttribute('paint-order', 'stroke');
          valueText.setAttribute('stroke-linejoin', 'round');

          const xOffset = align === 'start' ? 10 : -10;
          const desiredY = point.y - 12;
          const y = desiredY < (conf.padding.top + 10) ? (point.y + 18) : desiredY;
          valueText.setAttribute('x', point.x + xOffset);
          valueText.setAttribute('y', y);
          valueText.textContent = formatter.format(numVal);
          group.appendChild(valueText);
        };

        createEndpoint(points[0], labels[0], values[0], 'start');
        createEndpoint(points[points.length - 1], labels[labels.length - 1], values[values.length - 1], 'end');
      }
    })();
  </script>
</body>
</html>
