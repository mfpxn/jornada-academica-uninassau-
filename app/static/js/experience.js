/* Interações progressivas, sem dependências externas ou bibliotecas de terceiros. */
(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // Animações de entrada. Sem JS, o conteúdo continua visível.
  if (!reduceMotion && 'IntersectionObserver' in window) {
    document.body.classList.add('motion-ready');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.10, rootMargin: '0px 0px -18px 0px' });
    document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
  }

  // Tilt 3D discreto. Nunca ativo em touch/reduced-motion.
  if (!reduceMotion && finePointer) {
    document.querySelectorAll('[data-tilt]').forEach(element => {
      let frame = 0;
      const strength = Math.min(8, Number(element.dataset.tiltStrength) || 4);
      element.addEventListener('pointermove', event => {
        if (frame) return;
        const rect = element.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
        const y = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
        frame = requestAnimationFrame(() => {
          element.style.setProperty('--xp-tilt-x', `${(-y * strength).toFixed(2)}deg`);
          element.style.setProperty('--xp-tilt-y', `${(x * strength).toFixed(2)}deg`);
          frame = 0;
        });
      });
      const reset = () => {
        if (frame) cancelAnimationFrame(frame);
        frame = 0;
        element.style.setProperty('--xp-tilt-x', '0deg');
        element.style.setProperty('--xp-tilt-y', '0deg');
      };
      element.addEventListener('pointerleave', reset);
      element.addEventListener('blur', reset);
    });
  }

  // Pilares interativos com navegação de teclado por setas, Home e End.
  const pillarInfo = {
    ensino: { number: '01', title: 'Ensino', desc: 'Conhecimento compartilhado para abrir caminhos e ampliar horizontes.', glyph: '✳' },
    pesquisa: { number: '02', title: 'Pesquisa', desc: 'A curiosidade que impulsiona novas perguntas, descobertas e soluções.', glyph: '⌕' },
    extensao: { number: '03', title: 'Extensão', desc: 'A aproximação entre universidade e sociedade, levando conhecimento para além da sala de aula.', glyph: '✣' },
    inovacao: { number: '04', title: 'Inovação', desc: 'Novas abordagens, criatividade e tecnologia para transformar ideias em possibilidades.', glyph: '✧' },
    transformacao: { number: '05', title: 'Transformação', desc: 'O impacto do aprendizado quando ele se conecta a pessoas e realidades.', glyph: '↗' }
  };
  const tabs = [...document.querySelectorAll('[data-pillar][role="tab"]')];
  const panel = document.getElementById('xp-pillar-panel');
  if (tabs.length && panel) {
    const number = document.getElementById('xp-pillar-number');
    const title = document.getElementById('xp-pillar-title');
    const desc = document.getElementById('xp-pillar-description');
    const glyph = document.getElementById('xp-pillar-glyph');
    const counter = panel.querySelector('.xp-pillar-card-head > span:first-child');
    function activate(tab, focus) {
      const data = pillarInfo[tab.dataset.pillar];
      if (!data) return;
      tabs.forEach(item => {
        const selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
      });
      panel.setAttribute('aria-labelledby', tab.id);
      number.textContent = `${data.number} / 05`;
      title.textContent = data.title;
      desc.textContent = data.desc;
      glyph.textContent = data.glyph;
      counter.textContent = `EXPLORAR / ${data.number}`;
      if (focus) tab.focus();
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activate(tab, false));
      tab.addEventListener('keydown', event => {
        let targetIndex = null;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') targetIndex = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') targetIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') targetIndex = 0;
        if (event.key === 'End') targetIndex = tabs.length - 1;
        if (targetIndex !== null) {
          event.preventDefault();
          activate(tabs[targetIndex], true);
        }
      });
    });
  }

  // Contagem regressiva, com fallback para data estática caso JS falhe.
  const countdown = document.querySelector('[data-event-countdown]');
  if (countdown) {
    const target = new Date(countdown.dataset.eventCountdown);
    const refresh = () => {
      if (Number.isNaN(target.getTime())) return;
      const left = target.getTime() - Date.now();
      if (left <= 0) {
        countdown.textContent = '09–10 DEZEMBRO DE 2026';
        return;
      }
      const days = Math.ceil(left / 86400000);
      countdown.textContent = `${days} ${days === 1 ? 'DIA' : 'DIAS'} PARA O EVENTO`;
    };
    refresh();
    // O contador não precisa atualizar a cada segundo: evitar trabalho desnecessário.
    if (target > new Date()) window.setInterval(refresh, 60000);
  }

  // Indicador visual de preenchimento, sem interferir na validação do backend.
  const form = document.getElementById('form-inscricao');
  const progressBar = document.getElementById('xp-form-progress-bar');
  const progressLabel = document.getElementById('xp-form-progress-label');
  if (form && progressBar && progressLabel) {
    const fields = ['nome', 'email', 'telefone', 'cpf', 'matricula', 'curso'];
    const update = () => {
      const completed = fields.filter(id => {
        const field = document.getElementById(id);
        return field && field.value.trim().length > 0;
      }).length;
      progressBar.style.width = `${completed / fields.length * 100}%`;
      progressLabel.textContent = `${completed} de ${fields.length} campos preenchidos`;
    };
    form.addEventListener('input', update);
    update();
  }
})();
