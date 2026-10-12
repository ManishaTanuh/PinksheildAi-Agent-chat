// /text avatar B: "Risk Gauge + DNA". A risk-assessment dial with a sweeping needle, a DNA helix
// scanned by a magnifier, and progress dots. Mounts into #robot-fallback.
// States via #robot-pane[data-state]: idle | listening | processing | speaking.
// Progress: window.skSetProgress(pct 0-100).
(function () {
  const DOTS = 10;
  const css = `
  #robot-fallback { width: 88%; max-width: 440px; height: auto; animation: none !important; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  .tb { transform-box: fill-box; transform-origin: center; }

  #tb-needle { transform-origin: 150px 190px; transform-box: view-box; animation: tb-sway 5s ease-in-out infinite; }
  @keyframes tb-sway { 0%,100% { transform: rotate(-24deg); } 50% { transform: rotate(24deg); } }
  #robot-pane[data-state="processing"] #tb-needle { animation: tb-scan 0.9s ease-in-out infinite; }
  @keyframes tb-scan { 0%,100% { transform: rotate(-70deg); } 50% { transform: rotate(70deg); } }
  #robot-pane[data-state="listening"] #tb-needle { animation: tb-listen 1.6s ease-in-out infinite; }
  @keyframes tb-listen { 0%,100% { transform: rotate(-8deg); } 50% { transform: rotate(8deg); } }
  #robot-pane[data-state="speaking"] #tb-needle { animation: tb-sway 2.2s ease-in-out infinite; }

  #tb-hub { animation: tb-hub 3s ease-in-out infinite; transform-origin: 150px 190px; transform-box: view-box; }
  @keyframes tb-hub { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }

  .tb-strand-a, .tb-strand-b { fill: none; stroke-width: 4; stroke-linecap: round; stroke-dasharray: 12 8; animation: tb-flow 2.4s linear infinite; }
  .tb-strand-a { stroke: #ec4899; } .tb-strand-b { stroke: #14868C; animation-direction: reverse; }
  @keyframes tb-flow { to { stroke-dashoffset: -40; } }
  #robot-pane[data-state="processing"] .tb-strand-a, #robot-pane[data-state="processing"] .tb-strand-b { animation-duration: 0.8s; }
  .tb-rung { stroke: #a5b4c4; stroke-width: 1.5; opacity: 0.55; }

  #tb-lens { animation: tb-glide 5s ease-in-out infinite; }
  @keyframes tb-glide { 0%,100% { transform: translateX(-70px); } 50% { transform: translateX(70px); } }
  #robot-pane[data-state="processing"] #tb-lens { animation-duration: 1.4s; }

  .tb-dot { fill: #d3ecee; transition: fill 0.5s, transform 0.5s; transform-box: fill-box; transform-origin: center; }
  .tb-dot.on { fill: #ec4899; transform: scale(1.25); }

  .tb-status { font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #0f6b70; text-anchor: middle; opacity: 0; transition: opacity 0.3s; }
  #robot-pane[data-state="idle"] #tb-s-idle, #robot-pane[data-state="listening"] #tb-s-listen,
  #robot-pane[data-state="processing"] #tb-s-proc, #robot-pane[data-state="speaking"] #tb-s-speak { opacity: 1; }

  .tb-spark { opacity: 0; animation: tb-spark 5s ease-in-out infinite; }
  .tb-spark:nth-of-type(2) { animation-delay: 1.6s; } .tb-spark:nth-of-type(3) { animation-delay: 3.2s; }
  @keyframes tb-spark { 0%,100% { opacity: 0; transform: scale(0.4); } 50% { opacity: 0.9; transform: scale(1.1); } }

  @media (max-width: 760px) { #robot-fallback { width: auto; height: 100%; } #robot-fallback svg { height: 100%; width: auto; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  function helix() {
    // two sine strands + rungs, x 50..250, centred on y=262
    const a = [], b = [];
    let rungs = '';
    for (let x = 50; x <= 250; x += 4) {
      const t = (x - 50) / 200 * Math.PI * 4;
      a.push(`${x},${(262 + 15 * Math.sin(t)).toFixed(1)}`);
      b.push(`${x},${(262 - 15 * Math.sin(t)).toFixed(1)}`);
    }
    for (let x = 58; x <= 246; x += 12) {
      const t = (x - 50) / 200 * Math.PI * 4;
      rungs += `<line class="tb-rung" x1="${x}" y1="${(262 + 15 * Math.sin(t)).toFixed(1)}" x2="${x}" y2="${(262 - 15 * Math.sin(t)).toFixed(1)}"/>`;
    }
    return rungs +
      `<polyline class="tb-strand-a" points="${a.join(' ')}"/><polyline class="tb-strand-b" points="${b.join(' ')}"/>`;
  }

  function dots() {
    let s = '';
    const w = 14, gap = 8, total = DOTS * w + (DOTS - 1) * gap, x0 = (300 - total) / 2;
    for (let i = 0; i < DOTS; i++) s += `<circle class="tb tb-dot" id="tb-dot-${i}" cx="${x0 + i * (w + gap) + w / 2}" cy="316" r="5"/>`;
    return s;
  }

  const svg = `
  <svg viewBox="0 0 300 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Risk assessment gauge">
    <defs>
      <radialGradient id="tb-bg"><stop offset="0%" stop-color="#e8f7f8"/><stop offset="100%" stop-color="#e8f7f8" stop-opacity="0"/></radialGradient>
    </defs>
    <circle cx="150" cy="180" r="148" fill="url(#tb-bg)"/>

    <!-- gauge arcs -->
    <path d="M40 190 A110 110 0 0 1 95 94.7" fill="none" stroke="#14868C" stroke-width="22" stroke-linecap="round"/>
    <path d="M95 94.7 A110 110 0 0 1 205 94.7" fill="none" stroke="#f6c453" stroke-width="22"/>
    <path d="M205 94.7 A110 110 0 0 1 260 190" fill="none" stroke="#ec4899" stroke-width="22" stroke-linecap="round"/>
    <g stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.9">
      <line x1="150" y1="68" x2="150" y2="76"/><line x1="78" y1="108" x2="84" y2="114"/><line x1="222" y1="108" x2="216" y2="114"/>
    </g>

    <!-- needle -->
    <g id="tb-needle"><path d="M150 190 L146 112 L150 98 L154 112 Z" fill="#0f6b70"/></g>
    <g id="tb-hub">
      <circle cx="150" cy="190" r="20" fill="#fff" stroke="#ec4899" stroke-width="3"/>
      <path d="M150 180 C143 180 143 190 150 196 C157 190 157 180 150 180 Z" fill="#ec4899"/>
    </g>

    <text x="62" y="212" font-size="11" font-weight="700" fill="#14868C" font-family="sans-serif">LOW</text>
    <text x="218" y="212" font-size="11" font-weight="700" fill="#ec4899" font-family="sans-serif">HIGH</text>

    <!-- sparkles -->
    <path class="tb tb-spark" d="M258 70 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3z" fill="#f472b6"/>
    <path class="tb tb-spark" d="M36 78 l2 6 6 2 -6 2 -2 6 -2 -6 -6 -2 6 -2z" fill="#14868C"/>
    <path class="tb tb-spark" d="M270 238 l2 6 6 2 -6 2 -2 6 -2 -6 -6 -2 6 -2z" fill="#ec4899"/>

    <!-- DNA helix + magnifier -->
    ${helix()}
    <g id="tb-lens" class="tb">
      <circle cx="150" cy="262" r="24" fill="#fff" fill-opacity="0.35" stroke="#0f6b70" stroke-width="4"/>
      <line x1="168" y1="280" x2="184" y2="298" stroke="#0f6b70" stroke-width="6" stroke-linecap="round"/>
    </g>

    ${dots()}

    <text id="tb-s-idle" class="tb-status" x="150" y="342">Risk assessment ready</text>
    <text id="tb-s-listen" class="tb-status" x="150" y="342">Listening to your answer</text>
    <text id="tb-s-proc" class="tb-status" x="150" y="342">Analysing your answers...</text>
    <text id="tb-s-speak" class="tb-status" x="150" y="342">Here is your next question</text>
  </svg>`;

  window.skSetProgress = function (pct) {
    const on = Math.round(Math.max(0, Math.min(100, pct)) / 100 * DOTS);
    for (let i = 0; i < DOTS; i++) {
      const d = document.getElementById('tb-dot-' + i);
      if (d) d.classList.toggle('on', i < on);
    }
  };

  function mount() {
    const host = document.getElementById('robot-fallback');
    if (!host) return;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    host.innerHTML = svg;
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
