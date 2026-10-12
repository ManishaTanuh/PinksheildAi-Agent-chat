// /text avatar A: "AI Neural Ribbon". Pink awareness ribbon inside an AI node network,
// a detection scan line and a progress ring. Mounts into #robot-fallback.
// States via #robot-pane[data-state]: idle | listening | processing | speaking.
// Progress: window.skSetProgress(pct 0-100).
(function () {
  const R = 124, C = 2 * Math.PI * R;
  const css = `
  #robot-fallback { width: 88%; max-width: 440px; height: auto; animation: none !important; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  .ta { transform-box: fill-box; transform-origin: center; }

  #ta-progress { transition: stroke-dashoffset 0.8s ease; }
  .ta-node { fill: #14868C; animation: ta-node 3s ease-in-out infinite; }
  @keyframes ta-node { 0%,100% { opacity: 0.35; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.25); } }
  .ta-link { stroke: #14868C; stroke-width: 1; opacity: 0.25; }
  #robot-pane[data-state="processing"] .ta-node { fill: #ec4899; animation-duration: 0.7s; }
  #robot-pane[data-state="processing"] .ta-link { stroke: #ec4899; opacity: 0.5; }
  #robot-pane[data-state="listening"] .ta-node { fill: #0ea5a4; animation-duration: 1.2s; }

  #ta-ribbon { animation: ta-float 4s ease-in-out infinite; transform-origin: 150px 150px; transform-box: view-box; }
  @keyframes ta-float { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-6px) scale(1.03); } }
  #robot-pane[data-state="speaking"] #ta-ribbon { animation: ta-beat 0.8s ease-in-out infinite; }
  @keyframes ta-beat { 0%,100% { transform: scale(1); } 35% { transform: scale(1.08); } 65% { transform: scale(0.99); } }

  #ta-scan { opacity: 0; animation: ta-scan 2.6s ease-in-out infinite; }
  @keyframes ta-scan { 0% { transform: translateY(-80px); } 50% { transform: translateY(80px); } 100% { transform: translateY(-80px); } }
  #robot-pane[data-state="processing"] #ta-scan { opacity: 1; animation-duration: 1.1s; }
  #robot-pane[data-state="idle"] #ta-scan { opacity: 0.35; }

  .ta-pulse { fill: none; stroke: #ec4899; stroke-width: 2; opacity: 0; }
  #robot-pane[data-state="speaking"] .ta-pulse, #robot-pane[data-state="listening"] .ta-pulse { animation: ta-pulse 1.6s ease-out infinite; }
  .ta-pulse:nth-of-type(2) { animation-delay: 0.5s !important; }
  @keyframes ta-pulse { 0% { opacity: 0.7; transform: scale(0.6); } 100% { opacity: 0; transform: scale(1.4); } }

  #ta-orbit { transform-origin: 150px 150px; transform-box: view-box; animation: ta-spin 18s linear infinite; }
  #robot-pane[data-state="processing"] #ta-orbit { animation-duration: 3s; }
  @keyframes ta-spin { to { transform: rotate(360deg); } }

  .ta-status { font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #0f6b70; text-anchor: middle; opacity: 0; transition: opacity 0.3s; }
  #robot-pane[data-state="idle"] #ta-s-idle, #robot-pane[data-state="listening"] #ta-s-listen,
  #robot-pane[data-state="processing"] #ta-s-proc, #robot-pane[data-state="speaking"] #ta-s-speak { opacity: 1; }

  @media (max-width: 760px) { #robot-fallback { width: auto; height: 100%; } #robot-fallback svg { height: 100%; width: auto; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  // AI node network: two rings of nodes joined to neighbours
  function network() {
    const pts = [];
    [[92, 8, 0], [140, 12, 15]].forEach(([r, n, off]) => {
      for (let i = 0; i < n; i++) {
        const a = ((i * 360) / n + off) * Math.PI / 180;
        pts.push([150 + r * Math.cos(a), 150 + r * Math.sin(a)]);
      }
    });
    let lines = '', dots = '';
    pts.forEach((p, i) => {
      pts.forEach((q, j) => {
        if (j <= i) return;
        const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
        if (d < 62) lines += `<line class="ta-link" x1="${p[0].toFixed(1)}" y1="${p[1].toFixed(1)}" x2="${q[0].toFixed(1)}" y2="${q[1].toFixed(1)}"/>`;
      });
      dots += `<circle class="ta ta-node" cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="4" style="animation-delay:${(i * -0.35).toFixed(2)}s"/>`;
    });
    return lines + dots;
  }

  const svg = `
  <svg viewBox="0 0 300 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AI breast health risk assessment">
    <defs>
      <linearGradient id="ta-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#14868C"/><stop offset="100%" stop-color="#ec4899"/></linearGradient>
      <linearGradient id="ta-r" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f472b6"/><stop offset="100%" stop-color="#db2777"/></linearGradient>
      <radialGradient id="ta-bg"><stop offset="0%" stop-color="#ffe4ef"/><stop offset="100%" stop-color="#ffe4ef" stop-opacity="0"/></radialGradient>
      <linearGradient id="ta-sl" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#14868C" stop-opacity="0"/><stop offset="50%" stop-color="#14868C" stop-opacity="0.9"/><stop offset="100%" stop-color="#14868C" stop-opacity="0"/></linearGradient>
      <clipPath id="ta-clip"><circle cx="150" cy="150" r="104"/></clipPath>
    </defs>

    <circle cx="150" cy="150" r="148" fill="url(#ta-bg)"/>
    <circle cx="150" cy="150" r="${R}" fill="none" stroke="#d3ecee" stroke-width="8"/>
    <circle id="ta-progress" cx="150" cy="150" r="${R}" fill="none" stroke="url(#ta-g)" stroke-width="8" stroke-linecap="round"
            stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${C.toFixed(1)}" transform="rotate(-90 150 150)"/>

    <g>${network()}</g>
    <circle class="ta ta-pulse" cx="150" cy="150" r="100"/><circle class="ta ta-pulse" cx="150" cy="150" r="100"/>

    <g id="ta-orbit"><circle cx="150" cy="40" r="6" fill="#f472b6"/><circle cx="260" cy="150" r="4" fill="#14868C"/><circle cx="40" cy="150" r="4" fill="#a78bfa"/></g>

    <circle cx="150" cy="150" r="82" fill="#fff" opacity="0.92"/>
    <g id="ta-ribbon">
      <path fill-rule="evenodd" fill="url(#ta-r)" d="M150 82 C104 82 104 138 150 176 C196 138 196 82 150 82 Z M150 104 C134 104 134 128 150 146 C166 128 166 104 150 104 Z"/>
      <path d="M150 168 L116 226 L137 218 L150 240 L163 218 L184 226 Z" fill="url(#ta-r)"/>
    </g>
    <g clip-path="url(#ta-clip)"><rect id="ta-scan" x="40" y="146" width="220" height="8" fill="url(#ta-sl)"/></g>

    <text id="ta-s-idle" class="ta-status" x="150" y="338">AI risk analysis ready</text>
    <text id="ta-s-listen" class="ta-status" x="150" y="338">Listening to your answer</text>
    <text id="ta-s-proc" class="ta-status" x="150" y="338">Analysing your answers...</text>
    <text id="ta-s-speak" class="ta-status" x="150" y="338">Here is your next question</text>
  </svg>`;

  window.skSetProgress = function (pct) {
    const el = document.getElementById('ta-progress');
    if (el) el.style.strokeDashoffset = (C * (1 - Math.max(0, Math.min(100, pct)) / 100)).toFixed(1);
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
