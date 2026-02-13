<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Datasenter – reservasjoner og kapasitetskø</title>
  <style>
    .dc-map-widget {
      --dc-bg: #0f2d52;
      --dc-bg-2: #0a1e36;
      --dc-text: #ffffff;
      --dc-blue: #60a5fa;
      --dc-red: #f87171;
      --dc-border: rgba(255, 255, 255, 0.2);

      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      box-sizing: border-box;
      width: 100%;
      max-width: 880px;
      margin: 0 auto 2rem;
      color: var(--dc-text);
    }

    .dc-map-widget * { box-sizing: inherit; }

    .dc-card {
      border-radius: 18px;
      padding: 22px;
      background: linear-gradient(180deg, rgba(15, 45, 82, 0.95), rgba(10, 30, 54, 0.98));
      border: 1px solid var(--dc-border);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(6px);
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
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0 0 0.4rem 0;
    }

    .dc-note {
      font-size: 0.9rem;
      color: rgba(255, 255, 255, 0.75);
      margin: 0 0 1rem 0;
    }

    .dc-error {
      margin-top: 0.8rem;
      color: #fecaca;
      font-size: 0.85rem;
    }

    #dc-map {
      width: 100%;
      height: 820px;
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .dc-legend {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-top: 0.9rem;
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

    .dc-source {
      font-size: 0.8rem;
      color: rgba(255, 255, 255, 0.5);
      margin-top: 0.9rem;
      text-align: right;
    }

    .leaflet-container {
      background: #e5ecf3;
    }

    .dc-tooltip {
      font-family: inherit;
      font-size: 0.85rem;
    }
  </style>
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
</head>
<body>
  <div class="dc-map-widget">
    <div class="dc-card">
      <h1 class="dc-title">Datasenter – samlet press på strømnettet</h1>
      <p class="dc-note">Det er reservert 3&nbsp;480 MW og 5&nbsp;088 MW står i kapasitetskø (datasenter). Markørene viser summen per stasjon.</p>

      <div id="dc-map" aria-label="Kart over datasenter-reservasjoner"></div>

      <div class="dc-legend">
        <span class="dc-blue">Reservasjoner + kapasitetskø</span>
      </div>

      <div class="dc-source">Kilde: Statnett </div>
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script>
    const DATA = [
  {
    "stasjon": "Rød",
    "lat": 59.272877551747264,
    "lon": 9.544284802177907,
    "total": 816.0
  },
  {
    "stasjon": "Tegneby",
    "lat": 59.51613729743573,
    "lon": 10.739130093358563,
    "total": 797.0
  },
  {
    "stasjon": "Ringerike",
    "lat": 60.16839168694178,
    "lon": 10.204696998422605,
    "total": 714.5
  },
  {
    "stasjon": "Kristiansand",
    "lat": 58.259945167964645,
    "lon": 7.8984419779279955,
    "total": 625.0
  },
  {
    "stasjon": "Kvandal",
    "lat": 68.57723024132423,
    "lon": 17.610520177877387,
    "total": 520.0
  },
  {
    "stasjon": "Bjerkreim",
    "lat": 58.589922468196484,
    "lon": 5.9210624003690056,
    "total": 496.0
  },
  {
    "stasjon": "Fagrafjell",
    "lat": 58.78887890280912,
    "lon": 5.762082508675961,
    "total": 461.0
  },
  {
    "stasjon": "Rana",
    "lat": 66.30319686797459,
    "lon": 14.264233821003739,
    "total": 436.0
  },
  {
    "stasjon": "Brokke",
    "lat": 59.123166131136365,
    "lon": 7.510497690594326,
    "total": 365.0
  },
  {
    "stasjon": "Ertsmyra",
    "lat": 58.67120329936556,
    "lon": 6.75511131811346,
    "total": 300.0
  },
  {
    "stasjon": "Nedre Røssåga",
    "lat": 66.05121635919133,
    "lon": 13.783520594576954,
    "total": 270.0
  },
  {
    "stasjon": "Frogner",
    "lat": 60.00572636988464,
    "lon": 11.134150019259742,
    "total": 229.0
  },
  {
    "stasjon": "Frogner",
    "lat": 59.21289987567047,
    "lon": 9.612733869884867,
    "total": 229.0
  },
  {
    "stasjon": "Tveiten",
    "lat": 59.32977620275053,
    "lon": 10.381214232783394,
    "total": 225.0
  },
  {
    "stasjon": "Leirdøla",
    "lat": 61.43810034545789,
    "lon": 7.245854291850852,
    "total": 220.0
  },
  {
    "stasjon": "Ålfoten",
    "lat": 61.82885971909765,
    "lon": 5.5488066910014755,
    "total": 188.6
  },
  {
    "stasjon": "Eidum",
    "lat": 63.44784377171784,
    "lon": 11.00394866912433,
    "total": 180.0
  },
  {
    "stasjon": "Vang",
    "lat": 60.83575805658488,
    "lon": 11.267279292120397,
    "total": 179.0
  },
  {
    "stasjon": "Minne",
    "lat": 60.3887736099228,
    "lon": 11.23225786640332,
    "total": 175.0
  },
  {
    "stasjon": "Arendal Industrinett",
    "lat": 58.4875,
    "lon": 8.718,
    "total": 150.0
  },
  {
    "stasjon": "Ballangen",
    "lat": 68.26123906335339,
    "lon": 16.733262943348947,
    "total": 140.0
  },
  {
    "stasjon": "Spanne",
    "lat": 59.37899646000803,
    "lon": 5.334879300860679,
    "total": 120.0
  },
  {
    "stasjon": "Samnanger",
    "lat": 60.398015921737475,
    "lon": 5.840440568838517,
    "total": 100.0
  },
  {
    "stasjon": "Samnanger",
    "lat": 60.39779505056462,
    "lon": 5.840817222424526,
    "total": 100.0
  },
  {
    "stasjon": "Hasle",
    "lat": 59.31418458831606,
    "lon": 11.155002361910748,
    "total": 90.0
  },
  {
    "stasjon": "Follo",
    "lat": 59.728692588105545,
    "lon": 10.782531362357613,
    "total": 80.0
  },
  {
    "stasjon": "Tunnsjødal",
    "lat": 64.70377582917814,
    "lon": 12.834872400721109,
    "total": 76.0
  },
  {
    "stasjon": "Grenland",
    "lat": 59.12853724670371,
    "lon": 9.474554208437468,
    "total": 55.0
  },
  {
    "stasjon": "LIO",
    "lat": 59.46276790917881,
    "lon": 7.939387889693647,
    "total": 50.0
  },
  {
    "stasjon": "Lio",
    "lat": 59.46326075886191,
    "lon": 7.938437266746529,
    "total": 50.0
  },
  {
    "stasjon": "Kobbvatnet",
    "lat": 67.63722379198826,
    "lon": 15.987401376040973,
    "total": 50.0
  },
  {
    "stasjon": "Lindås",
    "lat": 60.79545413563989,
    "lon": 5.042206159111615,
    "total": 45.0
  },
  {
    "stasjon": "Blåfalli",
    "lat": 59.86340233372589,
    "lon": 6.009754566512007,
    "total": 40.0
  },
  {
    "stasjon": "Vinje",
    "lat": 59.624668533830636,
    "lon": 7.851879179645363,
    "total": 40.0
  },
  {
    "stasjon": "Rjukan",
    "lat": 59.882563048214294,
    "lon": 8.677868442678172,
    "total": 33.0
  },
  {
    "stasjon": "Ulven",
    "lat": 60.21011698502667,
    "lon": 5.447994515788124,
    "total": 31.9
  },
  {
    "stasjon": "Ulven",
    "lat": 59.92191237506248,
    "lon": 10.811170471506726,
    "total": 31.9
  },
  {
    "stasjon": "Svartisen",
    "lat": 66.72961646018842,
    "lon": 13.912006204116398,
    "total": 30.0
  },
  {
    "stasjon": "Haugsvær",
    "lat": 60.88926497714842,
    "lon": 5.527142526559735,
    "total": 30.0
  },
  {
    "stasjon": "Kirkenes",
    "lat": 69.72270354519604,
    "lon": 30.03403130535382,
    "total": 25.0
  },
  {
    "stasjon": "Skaidi",
    "lat": 70.43326695140196,
    "lon": 24.54246513286043,
    "total": 25.0
  },
  {
    "stasjon": "Hinnøy",
    "lat": 68.68322892720386,
    "lon": 15.499998046797268,
    "total": 25.0
  },
  {
    "stasjon": "Marka",
    "lat": 65.85201584662478,
    "lon": 13.290265705683845,
    "total": 23.0
  },
  {
    "stasjon": "Furuset",
    "lat": 59.94416641549855,
    "lon": 10.883705916763459,
    "total": 19.3
  },
  {
    "stasjon": "Bærheim",
    "lat": 58.88298798126405,
    "lon": 5.6942044433476475,
    "total": 16.0
  },
  {
    "stasjon": "Fræna",
    "lat": 62.85914644930167,
    "lon": 7.111159750853125,
    "total": 15.0
  },
  {
    "stasjon": "Balsfjord",
    "lat": 69.19029237717892,
    "lon": 19.205444381098022,
    "total": 12.72
  },
  {
    "stasjon": "Stølaheia",
    "lat": 58.96307494730643,
    "lon": 5.652175122434436,
    "total": 12.5
  },
  {
    "stasjon": "Vågåmo",
    "lat": 61.88124436435195,
    "lon": 9.081767748053462,
    "total": 10.0
  },
  {
    "stasjon": "Aura",
    "lat": 62.664140836633166,
    "lon": 8.52357968498045,
    "total": 8.0
  },
  {
    "stasjon": "Åfjord",
    "lat": 63.89171386306289,
    "lon": 10.2215649542643,
    "total": 8.0
  },
  {
    "stasjon": "Sautso",
    "lat": 69.71959419126219,
    "lon": 23.802119476632374,
    "total": 5.0
  },
  {
    "stasjon": "Vardal",
    "lat": 60.802021235821336,
    "lon": 10.564888176309438,
    "total": 4.0
  },
  {
    "stasjon": "Salten transformatorstasjon",
    "lat": 67.378,
    "lon": 15.6145,
    "total": 1.0
  }
];

    const map = L.map('dc-map', {
      zoomControl: true,
      scrollWheelZoom: false
    }).setView([65.2, 13.0], 4.6);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);

    const maxVal = Math.max(...DATA.map(d => d.total));
    DATA.forEach((d) => {
      const radius = 6 + (d.total / maxVal) * 22;
      const marker = L.circleMarker([d.lat, d.lon], {
        radius,
        color: '#60a5fa',
        weight: 2,
        fillColor: '#60a5fa',
        fillOpacity: 0.55
      }).addTo(map);

      marker.bindTooltip(
        `<div class="dc-tooltip"><strong>${d.stasjon}</strong><br/>Total: ${d.total.toFixed(1)} MW</div>`,
        { direction: 'top', offset: [0, -6], opacity: 0.9 }
      );
    });

  </script>
</body>
</html>
