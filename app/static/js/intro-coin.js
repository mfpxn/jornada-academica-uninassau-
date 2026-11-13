/* Intro da UNINASSAU: moeda 3D e revelação da marca. Apenas na home. */
(() => {
  'use strict';
  const intro = document.querySelector('[data-ja-intro]');
  if (!intro) return;

  const skip = intro.querySelector('[data-ja-intro-skip]');
  const replay = document.querySelector('[data-ja-intro-replay]');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const key = 'ja-logo-intro-v1';
  let finishTimer = 0;
  let leaveTimer = 0;
  let playing = false;
  let restoreFocus = null;

  function hide() {
    intro.hidden = true;
    intro.classList.remove('is-playing', 'is-leaving');
    document.body.classList.remove('ja-intro-open');
    if (restoreFocus && restoreFocus.isConnected && typeof restoreFocus.focus === 'function') {
      restoreFocus.focus({ preventScroll: true });
    }
    restoreFocus = null;
  }

  function finish() {
    if (!playing) return;
    playing = false;
    window.clearTimeout(finishTimer);
    // Mantém o último quadro da moeda durante o desaparecimento.
    intro.classList.add('is-leaving');
    try { window.sessionStorage.setItem(key, '1'); } catch (_) { /* storage indisponível */ }
    window.clearTimeout(leaveTimer);
    leaveTimer = window.setTimeout(hide, 520);
  }

  function play(force = false) {
    if (reduceMotion) return;
    if (!force) {
      try { if (window.sessionStorage.getItem(key) === '1') return; } catch (_) { /* ignora */ }
    }
    window.clearTimeout(finishTimer);
    window.clearTimeout(leaveTimer);
    restoreFocus = document.activeElement;
    intro.hidden = false;
    intro.classList.remove('is-playing', 'is-leaving');
    document.body.classList.add('ja-intro-open');
    // Reinicia a linha do tempo quando o visitante escolhe 'Rever abertura'.
    void intro.offsetWidth;
    playing = true;
    intro.classList.add('is-playing');
    if (skip) skip.focus({ preventScroll: true });
    finishTimer = window.setTimeout(finish, 3900);
  }

  skip?.addEventListener('click', finish);
  replay?.addEventListener('click', () => play(true));
  document.addEventListener('keydown', (event) => {
    if (playing && event.key === 'Escape') {
      event.preventDefault();
      finish();
    }
    // Enquanto aparece, mantém tabulação no botão de pular.
    if (playing && event.key === 'Tab') {
      event.preventDefault();
      skip?.focus({ preventScroll: true });
    }
  });
  const forcar = new URLSearchParams(
    window.location.search
  ).get('intro') === '1';

  play(forcar);
})();
