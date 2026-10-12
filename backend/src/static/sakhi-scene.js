// Shared scene around the avatar (both versions): backdrop, floating health icons,
// detection "radar" while thinking, badge and rotating awareness captions.
(function () {
  const TIPS = [
    'Early detection can save lives',
    'Know your risk. Act early.',
    'Regular screening helps catch changes sooner',
    'Your answers are private and confidential',
    'A screening aid, not a diagnosis',
    'Pink October: Breast Cancer Awareness Month',
  ];

  const ICONS = {
    ribbon: '<svg viewBox="0 0 24 24"><path d="M12 3c-3.5 0-3.5 5 0 8 3.5-3 3.5-8 0-8zM12 11l-4 9 3-1.2L12 22l1-3.2L16 20z" fill="currentColor"/></svg>',
    heart: '<svg viewBox="0 0 24 24"><path d="M12 21s-8-5.2-8-11a4.5 4.5 0 018-2.8A4.5 4.5 0 0120 10c0 5.8-8 11-8 11z" fill="currentColor"/></svg>',
    cross: '<svg viewBox="0 0 24 24"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z" fill="currentColor"/></svg>',
    shield: '<svg viewBox="0 0 24 24"><path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z" fill="currentColor"/></svg>',
    scope: '<svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="6" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M15 15l6 6" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
    drop: '<svg viewBox="0 0 24 24"><path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z" fill="currentColor"/></svg>',
  };

  const css = `
  #robot-pane {
    position: relative; overflow: hidden; flex-direction: column; gap: 14px;
    background:
      radial-gradient(circle at 20% 15%, rgba(244,114,182,0.28), transparent 45%),
      radial-gradient(circle at 85% 85%, rgba(20,134,140,0.25), transparent 50%),
      linear-gradient(160deg, #fff1f7 0%, #e8f7f8 100%) !important;
  }
  #robot-pane > * { position: relative; z-index: 2; }
  #robot-pane > .sk-decor, #robot-pane > .sk-radar { position: absolute; z-index: 0; }

  .sk-icon { position: absolute; width: 26px; height: 26px; opacity: 0.22; animation: sk-drift 9s ease-in-out infinite; }
  .sk-icon svg { width: 100%; height: 100%; display: block; }
  @keyframes sk-drift { 0%,100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-18px) rotate(12deg); } }

  .sk-radar { left: 50%; top: 46%; width: 78%; aspect-ratio: 1; max-width: 460px; transform: translate(-50%, -50%);
    border-radius: 50%; opacity: 0; transition: opacity 0.5s;
    background: conic-gradient(from 0deg, rgba(236,72,153,0) 0deg, rgba(236,72,153,0.38) 70deg, rgba(236,72,153,0) 72deg);
    border: 2px solid rgba(236,72,153,0.25); animation: sk-sweep 2.4s linear infinite; }
  .sk-radar::before, .sk-radar::after { content: ''; position: absolute; inset: 18%; border-radius: 50%; border: 1px dashed rgba(236,72,153,0.3); }
  .sk-radar::after { inset: 36%; }
  @keyframes sk-sweep { to { transform: translate(-50%, -50%) rotate(360deg); } }
  #robot-pane[data-state="processing"] .sk-radar { opacity: 1; }

  .sk-badge { position: absolute !important; top: 14px; left: 14px; z-index: 3; display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.8); backdrop-filter: blur(6px); border: 1px solid #f9a8d4; color: #be185d;
    font: 600 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 6px 12px; border-radius: 999px; }
  .sk-badge svg { width: 14px; height: 14px; color: #ec4899; }

  .sk-caption { min-height: 44px; max-width: 86%; display: flex; align-items: center; justify-content: center; gap: 8px; text-align: center;
    background: rgba(255,255,255,0.85); backdrop-filter: blur(6px); border: 1px solid #c8e8ea; border-radius: 14px; padding: 10px 16px;
    font: 600 14px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f6b70; box-shadow: 0 4px 14px rgba(20,134,140,0.12);
    transition: opacity 0.5s; }
  .sk-caption svg { width: 16px; height: 16px; color: #ec4899; flex-shrink: 0; }
  .sk-caption.sk-fade { opacity: 0; }

  @media (min-width: 761px) { #robot-fallback { width: auto; max-width: 100%; } #robot-fallback svg { width: auto; max-height: min(58vh, 520px); margin: 0 auto; } }
  @media (max-width: 760px) { .sk-caption, .sk-icon, .sk-badge { display: none !important; } #robot-pane { flex-direction: row; } }
  @media (prefers-reduced-motion: reduce) { .sk-icon, .sk-radar { animation: none !important; } }
  `;

  function mount() {
    const pane = document.getElementById('robot-pane');
    if (!pane) return;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    const decor = document.createElement('div');
    decor.className = 'sk-decor';
    decor.style.cssText = 'inset:0;pointer-events:none;';
    const spots = [['ribbon', 8, 62], ['heart', 84, 12], ['cross', 90, 55], ['shield', 12, 30],
                   ['scope', 78, 80], ['drop', 20, 84], ['heart', 6, 88], ['cross', 60, 6]];
    spots.forEach(([k, x, y], i) => {
      const d = document.createElement('div');
      d.className = 'sk-icon';
      d.style.cssText = `left:${x}%;top:${y}%;animation-delay:${i * -1.1}s;color:${i % 2 ? '#14868C' : '#ec4899'}`;
      d.innerHTML = ICONS[k];
      decor.appendChild(d);
    });
    pane.insertBefore(decor, pane.firstChild);

    const radar = document.createElement('div');
    radar.className = 'sk-radar';
    pane.insertBefore(radar, pane.firstChild);

    const badge = document.createElement('div');
    badge.className = 'sk-badge';
    badge.innerHTML = ICONS.ribbon + 'Breast Health Check-in';
    pane.appendChild(badge);

    const cap = document.createElement('div');
    cap.className = 'sk-caption';
    pane.appendChild(cap);
    let i = 0;
    function show() {
      cap.innerHTML = ICONS.heart + '<span>' + TIPS[i % TIPS.length] + '</span>';
      i++;
    }
    show();
    setInterval(() => { cap.classList.add('sk-fade'); setTimeout(() => { show(); cap.classList.remove('sk-fade'); }, 500); }, 5000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
