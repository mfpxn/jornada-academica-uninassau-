(() => {
    const intro = document.querySelector('[data-moeda-intro]');
    if (!intro) return;

    const pular = document.querySelector('[data-pular-intro]');
    const rever = document.querySelector('[data-rever-intro]');
    const chave = 'abertura-jornada-v2';

    const reduzir = window.matchMedia(
        '(prefers-reduced-motion: reduce)'
    ).matches;

    let tempo;
    let fim;

    function fechar() {
        clearTimeout(tempo);
        intro.classList.add('saindo');

        try {
            sessionStorage.setItem(chave, 'sim');
        } catch (_) {}

        clearTimeout(fim);

        fim = setTimeout(() => {
            intro.hidden = true;
            intro.classList.remove('tocando', 'saindo');
            document.body.classList.remove('moeda-ativa');
        }, 550);
    }

    function tocar(forcar = false) {
        if (reduzir) return;

        try {
            if (!forcar && sessionStorage.getItem(chave)) return;
        } catch (_) {}

        clearTimeout(tempo);
        clearTimeout(fim);

        intro.hidden = false;
        intro.classList.remove('tocando', 'saindo');
        document.body.classList.add('moeda-ativa');

        void intro.offsetWidth;

        intro.classList.add('tocando');
        pular.focus({ preventScroll: true });

        tempo = setTimeout(fechar, 3900);
    }

    pular.addEventListener('click', fechar);
    rever.addEventListener('click', () => tocar(true));

    document.addEventListener('keydown', (evento) => {
        if (!intro.hidden && evento.key === 'Escape') {
            fechar();
        }
        if (!intro.hidden && evento.key === 'Tab') {
            evento.preventDefault();
            pular.focus();
        }
    });

    const forcar = new URLSearchParams(
        location.search
    ).get('intro') === '1';

    tocar(forcar);
})();
