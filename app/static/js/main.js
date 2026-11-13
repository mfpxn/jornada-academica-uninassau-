(() => {
  const button = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.nav');
  if (!button || !menu) return;
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    button.setAttribute('aria-label', expanded ? 'Abrir menu' : 'Fechar menu');
    menu.classList.toggle('is-open', !expanded);
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    menu.classList.remove('is-open');
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'Abrir menu');
  }));
})();
