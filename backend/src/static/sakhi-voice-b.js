// /voice avatar B: "Headset Sakhi". Friendly call-assistant with a headset, sound waves,
// an equaliser and an "On call" timer. Mounts into #robot-fallback.
// States via #robot-pane[data-state]: ready | disabled | recording | processing | speaking.
(function () {
  const css = `
  #robot-fallback { width: 88%; max-width: 420px; height: auto; animation: none !important; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  .vb { transform-box: fill-box; transform-origin: center; }

  #vb-body { transform-origin: 150px 330px; transform-box: view-box; animation: vb-breathe 4s ease-in-out infinite; }
  @keyframes vb-breathe { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
  #vb-head { transform-origin: 150px 200px; transform-box: view-box; animation: vb-nod 5s ease-in-out infinite; }
  @keyframes vb-nod { 0%,100% { transform: rotate(0); } 35% { transform: rotate(-2deg); } 70% { transform: rotate(2deg); } }
  #robot-pane[data-state="recording"] #vb-head { animation: vb-tilt 1.4s ease-in-out infinite; }
  @keyframes vb-tilt { 0%,100% { transform: rotate(-5deg); } 50% { transform: rotate(-8deg); } }
  #robot-pane[data-state="processing"] #vb-head { animation: vb-think 2s ease-in-out infinite; }
  @keyframes vb-think { 0%,100% { transform: rotate(3deg); } 50% { transform: rotate(5deg); } }

  .vb-eye { animation: vb-blink 4.5s infinite; }
  @keyframes vb-blink { 0%,93%,100% { transform: scaleY(1); } 96% { transform: scaleY(0.08); } }

  #vb-talk { opacity: 0; }
  #robot-pane[data-state="speaking"] #vb-smile { opacity: 0; }
  #robot-pane[data-state="speaking"] #vb-talk { opacity: 1; animation: vb-talk 0.3s ease-in-out infinite; }
  @keyframes vb-talk { 0%,100% { transform: scaleY(0.35); } 50% { transform: scaleY(1.1); } }

  .vb-arc { fill: none; stroke: #14868C; stroke-width: 4; stroke-linecap: round; opacity: 0; }
  #robot-pane[data-state="speaking"] .vb-arc { animation: vb-arc 1.2s ease-out infinite; }
  .vb-arc:nth-of-type(2) { animation-delay: 0.3s !important; } .vb-arc:nth-of-type(3) { animation-delay: 0.6s !important; }
  @keyframes vb-arc { 0% { opacity: 0.9; transform: scale(0.8); } 100% { opacity: 0; transform: scale(1.35); } }

  .vb-ear { fill: none; stroke: #ec4899; stroke-width: 3; opacity: 0; }
  #robot-pane[data-state="recording"] .vb-ear { animation: vb-ear 1.3s ease-out infinite; }
  .vb-ear:nth-of-type(2) { animation-delay: 0.5s !important; }
  @keyframes vb-ear { 0% { opacity: 0.8; transform: scale(0.5); } 100% { opacity: 0; transform: scale(1.7); } }

  #vb-think { opacity: 0; transition: opacity 0.3s; }
  #robot-pane[data-state="processing"] #vb-think { opacity: 1; }
  #vb-think .d { animation: vb-dot 1.2s infinite; transform-box: fill-box; transform-origin: center; }
  #vb-think .d:nth-child(3) { animation-delay: 0.2s; } #vb-think .d:nth-child(4) { animation-delay: 0.4s; }
  @keyframes vb-dot { 0%,80%,100% { transform: scale(0.5); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }

  .vb-eq { fill: #14868C; transform-box: fill-box; transform-origin: bottom; transform: scaleY(0.2); }
  #robot-pane[data-state="speaking"] .vb-eq { fill: #ec4899; animation: vb-eq 0.55s ease-in-out infinite; }
  #robot-pane[data-state="recording"] .vb-eq { fill: #0ea5a4; animation: vb-eq 0.8s ease-in-out infinite; }
  .vb-eq:nth-child(2n) { animation-delay: 0.12s !important; } .vb-eq:nth-child(3n) { animation-delay: 0.25s !important; }
  @keyframes vb-eq { 0%,100% { transform: scaleY(0.2); } 50% { transform: scaleY(1); } }

  #vb-live { animation: vb-live 1.4s ease-in-out infinite; }
  @keyframes vb-live { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
  .vb-cap { font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #0f6b70; text-anchor: middle; }

  #vb-ribbon { animation: vb-pulse 3s ease-in-out infinite; transform-origin: 62px 80px; transform-box: view-box; }
  @keyframes vb-pulse { 0%,100% { transform: scale(1) rotate(-8deg); } 50% { transform: scale(1.12) rotate(-3deg); } }

  @media (max-width: 760px) { #robot-fallback { width: auto; height: 100%; } #robot-fallback svg { height: 100%; width: auto; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  const eq = Array.from({ length: 9 }, (_, i) =>
    `<rect class="vb-eq" x="${96 + i * 12}" y="338" width="7" height="26" rx="3.5"/>`).join('');

  const svg = `
  <svg viewBox="0 0 300 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sakhi on a voice call">
    <defs>
      <radialGradient id="vb-bg"><stop offset="0%" stop-color="#ffe4ef"/><stop offset="100%" stop-color="#ffe4ef" stop-opacity="0"/></radialGradient>
    </defs>
    <circle cx="150" cy="190" r="150" fill="url(#vb-bg)"/>

    <g id="vb-ribbon">
      <path d="M62 56 C42 56 42 82 62 98 C82 82 82 56 62 56 Z" fill="#ec4899"/>
      <path d="M62 88 L44 126 L57 122 L62 136 L67 122 L80 126 Z" fill="#f472b6"/>
    </g>

    <!-- speaking waves -->
    <path class="vb vb-arc" d="M236 160 q14 14 0 30"/><path class="vb vb-arc" d="M248 150 q22 24 0 50"/><path class="vb vb-arc" d="M260 140 q30 34 0 70"/>

    <g id="vb-body">
      <!-- shoulders: pink top -->
      <path d="M70 392 C70 322 104 290 150 290 C196 290 230 322 230 392 Z" fill="#f472b6"/>
      <path d="M120 292 L150 330 L180 292 Z" fill="#fff"/>
      <path d="M190 322 c-6-7-14-1-8 6 l8 8 8-8 c6-7-2-13-8-6z" fill="#fff"/>
      <rect x="136" y="252" width="28" height="42" rx="12" fill="#d49a76"/>

      <g id="vb-head">
        <circle cx="150" cy="120" r="26" fill="#1f2937"/>
        <ellipse cx="150" cy="192" rx="66" ry="72" fill="#1f2937"/>
        <ellipse cx="150" cy="202" rx="54" ry="62" fill="#e0ac8a"/>
        <path d="M96 192 C96 132 204 132 204 192 C190 162 164 154 150 154 C130 154 108 164 96 192 Z" fill="#1f2937"/>
        <circle cx="97" cy="208" r="9" fill="#d49a76"/><circle cx="203" cy="208" r="9" fill="#d49a76"/>
        <circle class="vb vb-ear" cx="97" cy="208" r="14"/><circle class="vb vb-ear" cx="97" cy="208" r="14"/>
        <circle cx="150" cy="172" r="4" fill="#ec4899"/>
        <ellipse class="vb vb-eye" cx="126" cy="200" rx="8" ry="10" fill="#1f2937"/><circle cx="129" cy="196" r="3" fill="#fff"/>
        <ellipse class="vb vb-eye" cx="174" cy="200" rx="8" ry="10" fill="#1f2937"/><circle cx="177" cy="196" r="3" fill="#fff"/>
        <path d="M114 182 q12-8 24 0 M162 182 q12-8 24 0" fill="none" stroke="#111827" stroke-width="3" stroke-linecap="round"/>
        <circle cx="112" cy="224" r="9" fill="#f9a8d4" opacity="0.6"/><circle cx="188" cy="224" r="9" fill="#f9a8d4" opacity="0.6"/>
        <path id="vb-smile" d="M134 232 q16 16 32 0" fill="none" stroke="#9f1239" stroke-width="4" stroke-linecap="round"/>
        <ellipse id="vb-talk" class="vb" cx="150" cy="238" rx="13" ry="9" fill="#9f1239"/>

        <!-- headset -->
        <path d="M92 196 C88 120 212 120 208 196" fill="none" stroke="#0f6b70" stroke-width="7" stroke-linecap="round"/>
        <rect x="84" y="190" width="18" height="36" rx="9" fill="#14868C"/>
        <rect x="198" y="190" width="18" height="36" rx="9" fill="#14868C"/>
        <path d="M207 224 C206 252 190 258 170 256" fill="none" stroke="#0f6b70" stroke-width="5" stroke-linecap="round"/>
        <circle cx="166" cy="256" r="7" fill="#ec4899"/>

        <g id="vb-think">
          <circle cx="226" cy="118" r="5" fill="#fff" stroke="#c8e8ea"/><circle cx="238" cy="104" r="8" fill="#fff" stroke="#c8e8ea"/>
          <ellipse cx="262" cy="78" rx="30" ry="20" fill="#fff" stroke="#c8e8ea" stroke-width="2"/>
          <circle class="d" cx="250" cy="78" r="4" fill="#14868C"/><circle class="d" cx="262" cy="78" r="4" fill="#14868C"/><circle class="d" cx="274" cy="78" r="4" fill="#14868C"/>
        </g>
      </g>
    </g>

    <g>${eq}</g>

    <g transform="translate(150 20)">
      <rect x="-62" y="-14" width="124" height="28" rx="14" fill="#fff" stroke="#c8e8ea"/>
      <circle id="vb-live" cx="-40" cy="0" r="5" fill="#ec4899"/>
      <text id="vb-time" class="vb-cap" x="8" y="4">On call  00:00</text>
    </g>
  </svg>`;

  function startTimer() {
    const t0 = Date.now();
    setInterval(() => {
      const el = document.getElementById('vb-time');
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
