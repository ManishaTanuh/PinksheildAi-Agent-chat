// /voice avatar A: "Voice Orb". Circular sound-wave visualiser around a pink ribbon,
// with an "On call" timer. Mounts into #robot-fallback.
// States via #robot-pane[data-state]: ready | disabled | recording | processing | speaking.
(function () {
  const BARS = 64;
  const css = `
  #robot-fallback { width: 90%; max-width: 440px; height: auto; animation: none !important; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }

  .va-bar { stroke: #14868C; stroke-width: 4; stroke-linecap: round; transform-box: fill-box; transform-origin: bottom center;
            transform: scaleY(0.25); animation: va-idle 3s ease-in-out infinite; }
  @keyframes va-idle { 0%,100% { transform: scaleY(0.22); } 50% { transform: scaleY(0.4); } }
  #robot-pane[data-state="recording"] .va-bar { stroke: #0ea5a4; animation: va-rec 0.5s ease-in-out infinite; }
  @keyframes va-rec { 0%,100% { transform: scaleY(0.3); } 50% { transform: scaleY(1.25); } }
  #robot-pane[data-state="speaking"] .va-bar { stroke: #ec4899; animation: va-speak 0.7s ease-in-out infinite; }
  @keyframes va-speak { 0%,100% { transform: scaleY(0.35); } 50% { transform: scaleY(1.6); } }
  #robot-pane[data-state="processing"] .va-bar { stroke: #a78bfa; animation: va-proc 1.4s ease-in-out infinite; }
  @keyframes va-proc { 0%,100% { transform: scaleY(0.2); } 50% { transform: scaleY(0.7); } }

  #va-spin { transform-origin: 150px 150px; transform-box: view-box; }
  #robot-pane[data-state="processing"] #va-spin { animation: va-rot 1.6s linear infinite; }
  @keyframes va-rot { to { transform: rotate(360deg); } }

  #va-core { transform-origin: 150px 150px; transform-box: view-box; animation: va-breathe 4s ease-in-out infinite; }
  @keyframes va-breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.04); } }
  #robot-pane[data-state="speaking"] #va-core { animation: va-beat 0.7s ease-in-out infinite; }
  @keyframes va-beat { 0%,100% { transform: scale(1); } 40% { transform: scale(1.08); } }
  #robot-pane[data-state="recording"] #va-core { animation: va-beat 1s ease-in-out infinite; }

  .va-halo { fill: none; stroke: #ec4899; stroke-width: 2; opacity: 0; transform-box: fill-box; transform-origin: center; }
  #robot-pane[data-state="recording"] .va-halo, #robot-pane[data-state="speaking"] .va-halo { animation: va-halo 1.8s ease-out infinite; }
  .va-halo:nth-of-type(2) { animation-delay: 0.6s !important; }
  @keyframes va-halo { 0% { opacity: 0.6; transform: scale(0.8); } 100% { opacity: 0; transform: scale(1.4); } }

  #va-mic { opacity: 0; transition: opacity 0.3s; }
  #robot-pane[data-state="recording"] #va-mic { opacity: 1; }
  #va-ribbon { transition: opacity 0.3s; }
  #robot-pane[data-state="recording"] #va-ribbon { opacity: 0; }

  #va-live { animation: va-blink 1.4s ease-in-out infinite; }
  @keyframes va-blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
  .va-cap { font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #0f6b70; text-anchor: middle; }

  @media (max-width: 760px) { #robot-fallback { width: auto; height: 100%; } #robot-fallback svg { height: 100%; width: auto; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  function bars() {
    let s = '';
    for (let i = 0; i < BARS; i++) {
      const a = (i * 360) / BARS;
      const dur = (0.45 + ((i * 37) % 10) / 20).toFixed(2);   // pseudo-random 0.45 - 0.9s
      const del = (-((i * 53) % 10) / 10).toFixed(2);
      s += `<g transform="rotate(${a} 150 150)"><line class="va-bar" x1="150" y1="40" x2="150" y2="62" style="animation-delay:${del}s;animation-duration:${dur}s"/></g>`;
    }
    return s;
  }

  const svg = `
  <svg viewBox="0 0 300 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sakhi voice assistant">
    <defs>
      <linearGradient id="va-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#14868C"/><stop offset="100%" stop-color="#ec4899"/></linearGradient>
      <radialGradient id="va-bg"><stop offset="0%" stop-color="#ffe4ef"/><stop offset="100%" stop-color="#ffe4ef" stop-opacity="0"/></radialGradient>
    </defs>
    <circle cx="150" cy="150" r="148" fill="url(#va-bg)"/>
    <circle class="va-halo" cx="150" cy="150" r="90"/><circle class="va-halo" cx="150" cy="150" r="90"/>

    <g id="va-spin">${bars()}</g>

    <g id="va-core">
      <circle cx="150" cy="150" r="72" fill="url(#va-g)"/>
      <circle cx="150" cy="150" r="64" fill="#fff" opacity="0.14"/>
      <g id="va-ribbon">
        <path fill-rule="evenodd" fill="#fff" d="M150 106 C124 106 124 142 150 164 C176 142 176 106 150 106 Z M150 120 C140 120 140 136 150 148 C160 136 160 120 150 120 Z"/>
        <path d="M150 158 L131 192 L144 187 L150 202 L156 187 L169 192 Z" fill="#fff" opacity="0.95"/>
      </g>
      <g id="va-mic" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round">
        <rect x="137" y="112" width="26" height="46" rx="13" fill="#fff" stroke="none"/>
        <path d="M124 150 a26 26 0 0 0 52 0 M150 176 v16 M136 192 h28"/>
      </g>
    </g>

    <g transform="translate(150 318)">
      <rect x="-62" y="-16" width="124" height="28" rx="14" fill="#fff" stroke="#c8e8ea"/>
      <circle id="va-live" cx="-40" cy="-2" r="5" fill="#ec4899"/>
      <text id="va-time" class="va-cap" x="8" y="3">On call  00:00</text>
    </g>
  </svg>`;

  function startTimer() {
    const t0 = Date.now();
    setInterval(() => {
      const el = document.getElementById('va-time');
      if (!el) return;
      const s = Math.floor((Date.now() - t0) / 1000);
      el.textContent = 'On call  ' + String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
    }, 1000);
  }

  function mount() {
    const host = document.getElementById('robot-fallback');
    if (!host) return;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    host.innerHTML = svg;
    startTimer();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
