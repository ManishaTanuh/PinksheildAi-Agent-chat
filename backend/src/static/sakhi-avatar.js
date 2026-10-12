// Sakhi avatar: an animated SVG health assistant themed on breast cancer awareness.
// Mounts into #robot-fallback. Driven by #robot-pane[data-state]:
//   idle | ready | disabled | listening (recording) | processing | speaking
(function () {
  const css = `
  #robot-fallback { width: 86%; max-width: 420px; height: auto; animation: none !important; position: relative; }
  #robot-fallback svg { width: 100%; height: auto; display: block; overflow: visible; }
  #robot-fallback .sk { transform-box: fill-box; transform-origin: center; }

  /* breathing + gentle sway */
  #sk-body { animation: sk-breathe 4s ease-in-out infinite; transform-origin: 150px 330px; transform-box: view-box; }
  @keyframes sk-breathe { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-4px) scale(1.012); } }

  /* head */
  #sk-head { transform-origin: 150px 205px; transform-box: view-box; animation: sk-nod 6s ease-in-out infinite; }
  @keyframes sk-nod { 0%,100% { transform: rotate(0); } 30% { transform: rotate(-1.5deg); } 70% { transform: rotate(1.5deg); } }

  /* blink */
  .sk-eye { transform-box: fill-box; transform-origin: center; animation: sk-blink 4.5s infinite; }
  @keyframes sk-blink { 0%,93%,100% { transform: scaleY(1); } 96% { transform: scaleY(0.08); } }

  /* waving arm (idle) */
  #sk-wave { transform-origin: 214px 292px; transform-box: view-box; animation: sk-wave 5s ease-in-out infinite; }
  @keyframes sk-wave {
    0%,60%,100% { transform: rotate(0); }
    66% { transform: rotate(-22deg); } 72% { transform: rotate(8deg); }
    78% { transform: rotate(-22deg); } 84% { transform: rotate(6deg); } 90% { transform: rotate(0); }
  }

  /* mouth */
  #sk-talk { opacity: 0; transform-box: fill-box; transform-origin: center; }
  #robot-pane[data-state="speaking"] #sk-smile { opacity: 0; }
  #robot-pane[data-state="speaking"] #sk-talk { opacity: 1; animation: sk-talk 0.32s ease-in-out infinite; }
  @keyframes sk-talk { 0%,100% { transform: scaleY(0.35); } 50% { transform: scaleY(1.1); } }

  /* sound waves while speaking */
  .sk-wave-arc { opacity: 0; }
  #robot-pane[data-state="speaking"] .sk-wave-arc { animation: sk-arc 1.2s ease-out infinite; }
  #robot-pane[data-state="speaking"] .sk-wave-arc:nth-child(2) { animation-delay: 0.3s; }
  #robot-pane[data-state="speaking"] .sk-wave-arc:nth-child(3) { animation-delay: 0.6s; }
  @keyframes sk-arc { 0% { opacity: 0.9; transform: scale(0.8); } 100% { opacity: 0; transform: scale(1.3); } }

  /* listening: head tilt + ear glow */
  #robot-pane[data-state="listening"] #sk-head,
  #robot-pane[data-state="recording"] #sk-head { animation: sk-tilt 1.6s ease-in-out infinite; }
  @keyframes sk-tilt { 0%,100% { transform: rotate(-5deg); } 50% { transform: rotate(-8deg); } }
  #sk-listen { opacity: 0; }
  #robot-pane[data-state="listening"] #sk-listen,
  #robot-pane[data-state="recording"] #sk-listen { opacity: 1; }
  #sk-listen circle { transform-box: fill-box; transform-origin: center; animation: sk-ring 1.4s ease-out infinite; }
  #sk-listen circle:nth-child(2) { animation-delay: 0.5s; }
  @keyframes sk-ring { 0% { transform: scale(0.5); opacity: 0.8; } 100% { transform: scale(1.6); opacity: 0; } }

  /* processing: thought bubble */
  #sk-think { opacity: 0; transition: opacity 0.3s; }
  #robot-pane[data-state="processing"] #sk-think { opacity: 1; }
  #sk-think .dot { animation: sk-dot 1.2s infinite; transform-box: fill-box; transform-origin: center; }
  #sk-think .dot:nth-child(2) { animation-delay: 0.2s; }
  #sk-think .dot:nth-child(3) { animation-delay: 0.4s; }
  @keyframes sk-dot { 0%,80%,100% { transform: scale(0.5); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
  #robot-pane[data-state="processing"] #sk-head { animation: sk-think-tilt 2s ease-in-out infinite; }
  @keyframes sk-think-tilt { 0%,100% { transform: rotate(3deg); } 50% { transform: rotate(5deg); } }

  /* heartbeat line */
  #sk-ecg { stroke-dasharray: 260; stroke-dashoffset: 260; animation: sk-ecg 3s linear infinite; }
  @keyframes sk-ecg { 0% { stroke-dashoffset: 260; } 60% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -260; } }
  #robot-pane[data-state="processing"] #sk-ecg,
  #robot-pane[data-state="listening"] #sk-ecg { animation-duration: 1.2s; }

  /* ribbon pulse and shield glow */
  #sk-ribbon { transform-origin: 66px 96px; transform-box: view-box; animation: sk-pulse 3s ease-in-out infinite; }
  @keyframes sk-pulse { 0%,100% { transform: scale(1) rotate(-8deg); } 50% { transform: scale(1.12) rotate(-3deg); } }
  #sk-glow { animation: sk-glow 4s ease-in-out infinite; }
  @keyframes sk-glow { 0%,100% { opacity: 0.55; } 50% { opacity: 1; } }

  /* floating hearts */
  .sk-heart { opacity: 0; transform-box: fill-box; transform-origin: center; animation: sk-float 6s ease-in infinite; }
  .sk-heart:nth-child(2) { animation-delay: 2s; } .sk-heart:nth-child(3) { animation-delay: 4s; }
  @keyframes sk-float { 0% { opacity: 0; transform: translateY(20px) scale(0.6); } 20% { opacity: 0.9; }
                        100% { opacity: 0; transform: translateY(-70px) scale(1.1); } }

  @media (max-width: 760px) {
    #robot-fallback { width: auto; height: 100%; }
    #robot-fallback svg { height: 100%; width: auto; }
  }
  @media (prefers-reduced-motion: reduce) {
    #robot-fallback * { animation: none !important; }
  }
  `;

  const svg = `
  <svg viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sakhi, your breast health assistant">
    <defs>
      <radialGradient id="sk-bg" cx="50%" cy="45%" r="55%">
        <stop offset="0%" stop-color="#ffe4ef"/><stop offset="100%" stop-color="#ffe4ef" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="sk-coat" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#e6f4f5"/>
      </linearGradient>
      <linearGradient id="sk-shield" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#14868C"/><stop offset="100%" stop-color="#ec4899"/>
      </linearGradient>
    </defs>

    <!-- aura + shield -->
    <circle id="sk-glow" cx="150" cy="190" r="150" fill="url(#sk-bg)"/>
    <path d="M150 28 L255 62 V150 C255 215 210 262 150 288 C90 262 45 215 45 150 V62 Z"
          fill="none" stroke="url(#sk-shield)" stroke-width="4" opacity="0.35"/>

    <!-- pink awareness ribbon -->
    <g id="sk-ribbon">
      <path d="M66 70 C46 70 46 96 66 112 C86 96 86 70 66 70 Z" fill="#ec4899"/>
      <path d="M66 100 L46 140 L60 136 L66 150 L72 136 L86 140 Z" fill="#f472b6"/>
      <path d="M66 100 L86 140 L72 136 L66 150" fill="#db2777" opacity="0.6"/>
    </g>

    <!-- floating hearts -->
    <g>
      <path class="sk-heart" d="M240 150 c-6-9-18-3-12 6 l12 11 12-11 c6-9-6-15-12-6z" fill="#f472b6"/>
      <path class="sk-heart" d="M255 200 c-5-7-14-2-9 5 l9 8 9-8 c5-7-4-12-9-5z" fill="#ec4899"/>
      <path class="sk-heart" d="M50 210 c-5-7-14-2-9 5 l9 8 9-8 c5-7-4-12-9-5z" fill="#f9a8d4"/>
    </g>

    <!-- sound waves (speaking) -->
    <g>
      <path class="sk-wave-arc sk" d="M222 175 q16 14 0 30" fill="none" stroke="#14868C" stroke-width="4" stroke-linecap="round"/>
      <path class="sk-wave-arc sk" d="M234 165 q24 24 0 50" fill="none" stroke="#14868C" stroke-width="4" stroke-linecap="round"/>
      <path class="sk-wave-arc sk" d="M246 155 q32 34 0 70" fill="none" stroke="#14868C" stroke-width="4" stroke-linecap="round"/>
    </g>

    <!-- character -->
    <g id="sk-body">
      <!-- scrubs / coat -->
      <path d="M78 380 C78 318 104 288 150 288 C196 288 222 318 222 380 Z" fill="url(#sk-coat)" stroke="#b6dde0" stroke-width="2"/>
      <path d="M150 288 L128 380 M150 288 L172 380" stroke="#14868C" stroke-width="3" opacity="0.5"/>
      <path d="M118 290 L150 338 L182 290 Z" fill="#14868C"/>
      <!-- stethoscope -->
      <path d="M124 292 C112 330 126 350 146 346 C160 343 160 330 150 326" fill="none" stroke="#475569" stroke-width="4" stroke-linecap="round"/>
      <circle cx="150" cy="326" r="7" fill="#94a3b8" stroke="#475569" stroke-width="3"/>
      <!-- ribbon pin -->
      <path d="M192 322 c-6-7-14-1-8 6 l8 8 8-8 c6-7-2-13-8-6z" fill="#ec4899"/>

      <!-- resting arm -->
      <path d="M92 312 C80 335 84 360 98 380" fill="none" stroke="#e6f4f5" stroke-width="22" stroke-linecap="round"/>
      <!-- waving arm -->
      <g id="sk-wave">
        <path d="M208 312 C224 300 232 282 232 262" fill="none" stroke="#f3fafb" stroke-width="22" stroke-linecap="round"/>
        <circle cx="232" cy="252" r="12" fill="#e0ac8a"/>
      </g>

      <!-- neck -->
      <rect x="136" y="250" width="28" height="42" rx="12" fill="#d49a76"/>

      <!-- head -->
      <g id="sk-head">
        <!-- hair back + bun -->
        <circle cx="150" cy="118" r="26" fill="#1f2937"/>
        <ellipse cx="150" cy="190" rx="66" ry="72" fill="#1f2937"/>
        <!-- face -->
        <ellipse cx="150" cy="200" rx="54" ry="62" fill="#e0ac8a"/>
        <!-- fringe -->
        <path d="M96 190 C96 130 204 130 204 190 C190 160 164 152 150 152 C130 152 108 162 96 190 Z" fill="#1f2937"/>
        <!-- ears -->
        <circle cx="97" cy="206" r="9" fill="#d49a76"/>
        <circle cx="203" cy="206" r="9" fill="#d49a76"/>
        <g id="sk-listen"><circle cx="97" cy="206" r="14" fill="none" stroke="#14868C" stroke-width="3"/>
                          <circle cx="97" cy="206" r="14" fill="none" stroke="#14868C" stroke-width="3"/></g>
        <!-- bindi -->
        <circle cx="150" cy="170" r="4" fill="#ec4899"/>
        <!-- eyes -->
        <g class="sk-eye"><ellipse cx="126" cy="198" rx="8" ry="10" fill="#1f2937"/><circle cx="129" cy="194" r="3" fill="#fff"/></g>
        <g class="sk-eye"><ellipse cx="174" cy="198" rx="8" ry="10" fill="#1f2937"/><circle cx="177" cy="194" r="3" fill="#fff"/></g>
        <!-- brows -->
        <path d="M114 180 q12-8 24 0 M162 180 q12-8 24 0" fill="none" stroke="#111827" stroke-width="3" stroke-linecap="round"/>
        <!-- cheeks -->
        <circle cx="112" cy="222" r="9" fill="#f9a8d4" opacity="0.6"/>
        <circle cx="188" cy="222" r="9" fill="#f9a8d4" opacity="0.6"/>
        <!-- mouth -->
        <path id="sk-smile" d="M134 230 q16 16 32 0" fill="none" stroke="#9f1239" stroke-width="4" stroke-linecap="round"/>
        <ellipse id="sk-talk" cx="150" cy="236" rx="13" ry="9" fill="#9f1239"/>
        <!-- thought bubble -->
        <g id="sk-think">
          <circle cx="222" cy="120" r="5" fill="#fff" stroke="#c8e8ea"/>
          <circle cx="234" cy="106" r="8" fill="#fff" stroke="#c8e8ea"/>
          <ellipse cx="258" cy="80" rx="34" ry="22" fill="#fff" stroke="#c8e8ea" stroke-width="2"/>
          <circle class="dot" cx="244" cy="80" r="4" fill="#14868C"/>
          <circle class="dot" cx="258" cy="80" r="4" fill="#14868C"/>
          <circle class="dot" cx="272" cy="80" r="4" fill="#14868C"/>
        </g>
      </g>
    </g>

    <!-- heartbeat line -->
    <path id="sk-ecg" d="M20 366 H88 L100 346 L114 384 L128 356 L138 366 H280" fill="none"
          stroke="#ec4899" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
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
