// Avatar C (default): illustrated PinkShield doctor character with layered animation.
// Mounts into #robot-fallback. Driven by #robot-pane[data-state]:
// idle | ready | disabled | listening | recording | processing | speaking.
// Progress: window.skSetProgress(pct 0-100).
(function () {
  const css = `
  #robot-fallback { width: 88%; max-width: 400px; height: auto; animation: none !important; }
  #robot-fallback .sc { position: relative; width: 100%; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  .sc-body { transform-box: view-box; transform-origin: 50% 100%; animation: sc-float 4s ease-in-out infinite, sc-breathe 3.2s ease-in-out infinite; }
  @keyframes sc-float { 0%,100% { translate: 0 0; rotate: -0.8deg; } 50% { translate: 0 -5px; rotate: 0.8deg; } }
  @keyframes sc-breathe { 0%,100% { scale: 1 1; } 50% { scale: 1.012 1.02; } }
    .sc-glow { fill: none; stroke: #ec4899; stroke-width: 3; opacity: 0; transform-box: fill-box; transform-origin: center; }
  .sc-lid { transform-box: fill-box; transform-origin: 50% 0%; transform: scaleY(0); animation: sc-blink 4.6s infinite; }
  .sc-lid.r { animation-delay: 0.02s; }
  @keyframes sc-blink { 0%,93%,100% { transform: scaleY(0); } 95.5% { transform: scaleY(1); } }
  .sc-mouth { transform-box: fill-box; transform-origin: 50% 0%; transform: scaleY(0); }
  .sc-spark { transform-box: fill-box; transform-origin: center; opacity: 0; }
  .sc-note { margin: 12px 4% 0; text-align: center; font: 500 13px/1.5 -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f6b70; }
  .sc-bar { height: 8px; border-radius: 4px; background: #fbd0e2; margin: 10px 8% 0; overflow: hidden; }
  .sc-bar i { display: block; height: 100%; width: 0; background: linear-gradient(90deg,#f472b6,#ec4899); transition: width 0.5s; }

  #robot-pane[data-state="listening"] .sc-body, #robot-pane[data-state="recording"] .sc-body { animation: sc-float 4s ease-in-out infinite, sc-tilt 1.8s ease-in-out infinite; }
  @keyframes sc-tilt { 0%,100% { scale: 1; } 50% { scale: 1.02; } }
  #robot-pane[data-state="listening"] .sc-glow, #robot-pane[data-state="recording"] .sc-glow { stroke: #14868C; animation: sc-ring 1.4s ease-out infinite; }
  .sc-glow.g2 { animation-delay: 0.7s !important; }
  @keyframes sc-ring { 0% { opacity: 0.8; transform: scale(0.96); } 100% { opacity: 0; transform: scale(1.12); } }

  #robot-pane[data-state="processing"] .sc-body { animation: sc-float 1.6s ease-in-out infinite, sc-breathe 1s ease-in-out infinite; }
  #robot-pane[data-state="processing"] .sc-spark { animation: sc-spark 1.2s ease-in-out infinite; }
  .sc-spark.s2 { animation-delay: 0.4s !important; } .sc-spark.s3 { animation-delay: 0.8s !important; }
  @keyframes sc-spark { 0%,100% { opacity: 0; transform: scale(0.4) rotate(0); } 50% { opacity: 1; transform: scale(1.2) rotate(30deg); } }

  #robot-pane[data-state="speaking"] .sc-body { animation: sc-float 2.4s ease-in-out infinite, sc-breathe 1.2s ease-in-out infinite; }
  #robot-pane[data-state="speaking"] .sc-mouth { animation: sc-talk 0.32s ease-in-out infinite; }
  @keyframes sc-talk { 0%,100% { transform: scaleY(0.15); } 50% { transform: scaleY(0.85); } }
  #robot-pane[data-state="speaking"] .sc-glow { animation: sc-ring 1.8s ease-out infinite; }

  @media (max-width: 900px) { #robot-fallback { width: auto; height: 100%; max-width: 100%; } #robot-fallback .sc { height: 100%; } #robot-fallback svg { height: 100%; width: auto; max-width: 100%; } .sc-bar, .sc-note { display: none; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  const lid = (cls, cx, cy, rx, ry, rot) => `
    <g class="sc-lid ${cls}" transform="rotate(${rot} ${cx} ${cy})">
      <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#sc-skin)" filter="url(#sc-soft)"/>
      <path d="M${cx - rx + 2} ${cy + ry * 0.55} Q${cx} ${cy + ry * 0.95} ${cx + rx - 2} ${cy + ry * 0.55}" fill="none" stroke="#3a1f14" stroke-width="2.2" stroke-linecap="round"/>
    </g>`;

  const svg = `
  <svg viewBox="0 0 512 614" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PinkShield AI assistant">
    <defs>
      <radialGradient id="sc-skin" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fcc59b"/><stop offset="100%" stop-color="#f5b082"/></radialGradient>
      <radialGradient id="sc-lip" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fdc79d"/><stop offset="100%" stop-color="#f7b78a"/></radialGradient>
      <filter id="sc-soft"><feGaussianBlur stdDeviation="0.8"/></filter>
    </defs>
    <ellipse class="sc-glow" cx="256" cy="320" rx="215" ry="270"/>
    <ellipse class="sc-glow g2" cx="256" cy="320" rx="215" ry="270"/>
    <ellipse class="sc-shadow" cx="256" cy="602" rx="110" ry="9" fill="#ec4899" opacity="0.18"/>
    <g class="sc-body">
      <image href="/static/sakhi-character.png" width="512" height="614"/>
      ${lid('l', 207, 103, 17, 13, -10)}
      ${lid('r', 250, 94, 14, 13, -8)}
      <g class="sc-mouth">
        <path d="M217 122 Q233 119 249 120 Q246 135 233 140 Q222 136 217 122 Z" fill="url(#sc-lip)" filter="url(#sc-soft)"/>
        <path d="M219 126 Q233 134 247 122" fill="none" stroke="#e0827a" stroke-width="2.2" stroke-linecap="round"/>
      </g>
      <path class="sc-spark" d="M425 120 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4z" fill="#ec4899"/>
      <path class="sc-spark s2" d="M385 95 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z" fill="#f472b6"/>
      <path class="sc-spark s3" d="M450 215 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z" fill="#14868C"/>
    </g>
  </svg>
  <p class="sc-note">This is a quick health check-in about breast health. This check-in can help you understand your breast health better.</p>
  <div class="sc-bar"><i id="sc-prog"></i></div>`;

  window.skSetProgress = function (pct) {
    const el = document.getElementById('sc-prog');
    if (el) el.style.width = Math.max(0, Math.min(100, pct)) + '%';
  };

  function mount() {
    const host = document.getElementById('robot-fallback');
    if (!host) return;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    host.innerHTML = '<div class="sc">' + svg + '</div>';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
