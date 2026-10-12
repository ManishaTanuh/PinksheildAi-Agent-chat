// Avatar version B: abstract "Pink Shield" orb. Mounts into #robot-fallback.
// Driven by #robot-pane[data-state]: idle | ready | disabled | listening (recording) | processing | speaking
(function () {
  const css = `
  #robot-fallback { width: 80%; max-width: 400px; height: auto; animation: none !important; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  .pb { transform-box: fill-box; transform-origin: center; }

  .pb-ring { fill: none; stroke: #ec4899; stroke-width: 2; opacity: 0; animation: pb-ring 4s ease-out infinite; }
  .pb-ring:nth-of-type(2) { animation-delay: 1.3s; } .pb-ring:nth-of-type(3) { animation-delay: 2.6s; }
  @keyframes pb-ring { 0% { transform: scale(0.55); opacity: 0.6; } 100% { transform: scale(1.35); opacity: 0; } }
  #robot-pane[data-state="listening"] .pb-ring, #robot-pane[data-state="recording"] .pb-ring { animation-duration: 1.4s; stroke: #14868C; }
  #robot-pane[data-state="speaking"] .pb-ring { animation-duration: 1.8s; }
  #robot-pane[data-state="processing"] .pb-ring { animation-duration: 2.4s; stroke: #a78bfa; }

  #pb-core { animation: pb-breathe 4s ease-in-out infinite; transform-origin: 150px 150px; transform-box: view-box; }
  @keyframes pb-breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
  #robot-pane[data-state="speaking"] #pb-core { animation: pb-beat 0.7s ease-in-out infinite; }
  @keyframes pb-beat { 0%,100% { transform: scale(1); } 30% { transform: scale(1.09); } 60% { transform: scale(0.98); } }

  #pb-orbit { transform-origin: 150px 150px; transform-box: view-box; animation: pb-spin 14s linear infinite; }
  #robot-pane[data-state="processing"] #pb-orbit { animation-duration: 2.2s; }
  @keyframes pb-spin { to { transform: rotate(360deg); } }

  #pb-eq rect { transform-box: fill-box; transform-origin: bottom; transform: scaleY(0.25); fill: #14868C; }
  #robot-pane[data-state="speaking"] #pb-eq rect { animation: pb-eq 0.6s ease-in-out infinite; }
  #pb-eq rect:nth-child(2) { animation-delay: 0.1s !important; } #pb-eq rect:nth-child(3) { animation-delay: 0.2s !important; }
  #pb-eq rect:nth-child(4) { animation-delay: 0.3s !important; } #pb-eq rect:nth-child(5) { animation-delay: 0.15s !important; }
  @keyframes pb-eq { 0%,100% { transform: scaleY(0.25); } 50% { transform: scaleY(1); } }

  #pb-ecg { stroke-dasharray: 300; stroke-dashoffset: 300; animation: pb-ecg 3s linear infinite; }
  @keyframes pb-ecg { 0% { stroke-dashoffset: 300; } 60% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -300; } }
  #robot-pane[data-state="processing"] #pb-ecg, #robot-pane[data-state="listening"] #pb-ecg { animation-duration: 1.2s; }

  .pb-petal { opacity: 0; animation: pb-rise 7s ease-in infinite; }
  .pb-petal:nth-child(2) { animation-delay: 2s; } .pb-petal:nth-child(3) { animation-delay: 4s; } .pb-petal:nth-child(4) { animation-delay: 5.5s; }
  @keyframes pb-rise { 0% { opacity: 0; transform: translateY(30px) rotate(0); } 20% { opacity: 0.8; } 100% { opacity: 0; transform: translateY(-90px) rotate(40deg); } }

  @media (max-width: 760px) { #robot-fallback { width: auto; height: 100%; } #robot-fallback svg { height: 100%; width: auto; } }
  @media (prefers-reduced-motion: reduce) { #robot-fallback * { animation: none !important; } }
  `;

  const svg = `
  <svg viewBox="0 0 300 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PinkShieldAI assistant">
    <defs>
      <linearGradient id="pb-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#14868C"/><stop offset="100%" stop-color="#ec4899"/></linearGradient>
      <radialGradient id="pb-bg" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffe4ef"/><stop offset="100%" stop-color="#ffe4ef" stop-opacity="0"/></radialGradient>
    </defs>
    <circle cx="150" cy="150" r="145" fill="url(#pb-bg)"/>
    <circle class="pb pb-ring" cx="150" cy="150" r="110"/>
    <circle class="pb pb-ring" cx="150" cy="150" r="110"/>
    <circle class="pb pb-ring" cx="150" cy="150" r="110"/>

    <g id="pb-orbit">
      <circle cx="150" cy="30" r="7" fill="#f472b6"/>
      <circle cx="270" cy="150" r="5" fill="#14868C"/>
      <circle cx="150" cy="270" r="6" fill="#ec4899"/>
      <circle cx="30" cy="150" r="5" fill="#a78bfa"/>
    </g>

    <g id="pb-core">
      <path d="M150 62 L222 88 V150 C222 196 192 228 150 246 C108 228 78 196 78 150 V88 Z" fill="url(#pb-g)"/>
      <path d="M150 74 L212 96 V150 C212 188 188 216 150 232 C112 216 88 188 88 150 V96 Z" fill="#fff" opacity="0.14"/>
      <!-- pink ribbon -->
      <path d="M150 112 C132 112 132 138 150 154 C168 138 168 112 150 112 Z" fill="#fff"/>
      <path d="M150 146 L132 184 L145 180 L150 194 L155 180 L168 184 Z" fill="#fff" opacity="0.92"/>
    </g>

    <g id="pb-eq">
      <rect x="112" y="270" width="10" height="34" rx="5"/><rect x="130" y="270" width="10" height="34" rx="5"/>
      <rect x="148" y="270" width="10" height="34" rx="5"/><rect x="166" y="270" width="10" height="34" rx="5"/>
      <rect x="184" y="270" width="10" height="34" rx="5"/>
    </g>

    <path id="pb-ecg" d="M10 318 H92 L104 296 L118 332 L132 306 L142 318 H290" fill="none" stroke="#ec4899" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>

    <g>
      <path class="pb pb-petal" d="M60 250 c-6-9-18-3-12 6 l12 11 12-11 c6-9-6-15-12-6z" fill="#f9a8d4"/>
      <path class="pb pb-petal" d="M245 240 c-6-9-18-3-12 6 l12 11 12-11 c6-9-6-15-12-6z" fill="#f472b6"/>
      <path class="pb pb-petal" d="M40 150 c-5-7-14-2-9 5 l9 8 9-8 c5-7-4-12-9-5z" fill="#ec4899"/>
      <path class="pb pb-petal" d="M265 120 c-5-7-14-2-9 5 l9 8 9-8 c5-7-4-12-9-5z" fill="#f9a8d4"/>
    </g>
  </svg>`;

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
