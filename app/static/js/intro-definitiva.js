(() => {
    'use strict';

    if (location.pathname !== '/') return;
    if (document.getElementById('uni-abertura')) return;

    const chave = 'uni-abertura-refeita-v1';

    document.body.insertAdjacentHTML('afterbegin', `
        <div id="uni-abertura"
             role="dialog"
             aria-modal="true"
             aria-label="Abertura da 6ª Jornada Acadêmica"
             hidden>

            <button class="uni-pular"
                    type="button"
                    data-uni-pular>
                Pular abertura
            </button>

            <div class="uni-luz" aria-hidden="true"></div>

            <div class="uni-cenario">

                <div class="uni-cabecalho">
                    UNINASSAU · TERESINA
                </div>

                <div class="uni-sombra"
                     aria-hidden="true"></div>

                <div class="uni-moeda-queda"
                     aria-hidden="true">

                    <div class="uni-moeda-rotor">

                        <div class="uni-moeda-face uni-moeda-frente">
                            <img
                              src="/static/img/uninassau-escudo.png"
                              alt="">
                            <strong>UNINASSAU</strong>
                        </div>

                        <div class="uni-moeda-face uni-moeda-verso">
                            <strong>6ª</strong>
                            <span>
                                JORNADA<br>ACADÊMICA
                            </span>
                        </div>

                    </div>
                </div>

                <div class="uni-impacto"
                     aria-hidden="true"></div>

                <div class="uni-logo-revelada"
                     aria-hidden="true">

                    <div class="uni-logo-placa">
                        <img
                          src="/static/img/uninassau-teresina-logo.png"
                          alt="">
                    </div>

                    <h2>6ª JORNADA ACADÊMICA</h2>
                    <p>O FUTURO COMEÇA AQUI</p>

                </div>
            </div>
        </div>
    `);

    const tela = document.getElementById('uni-abertura');
    const pular = tela.querySelector('[data-uni-pular]');

    let tempoFim = 0;
    let tempoSaida = 0;

    function fechar() {
        clearTimeout(tempoFim);

        tela.classList.add('uni-saindo');
        document.body.classList.remove('uni-travado');

        try {
            sessionStorage.setItem(chave, '1');
        } catch (_) {}

        clearTimeout(tempoSaida);

        tempoSaida = setTimeout(() => {
            tela.hidden = true;
            tela.classList.remove('uni-tocando', 'uni-saindo');
        }, 560);
    }

    function tocar() {
        clearTimeout(tempoFim);
        clearTimeout(tempoSaida);

        tela.hidden = false;
        tela.classList.remove('uni-tocando', 'uni-saindo');

        document.body.classList.add('uni-travado');

        void tela.offsetWidth;

        tela.classList.add('uni-tocando');
        pular.focus({preventScroll: true});

        tempoFim = setTimeout(fechar, 4000);
    }

    pular.addEventListener('click', fechar);

    document.addEventListener('keydown', evento => {
        if (evento.key === 'Escape' && !tela.hidden) {
            fechar();
        }

        if (evento.key === 'Tab' && !tela.hidden) {
            evento.preventDefault();
            pular.focus();
        }
    });

    let rever = document.querySelector(
        '[data-ja-intro-replay]'
    );

    if (!rever) {
        rever = document.createElement('button');
        rever.type = 'button';
        rever.className = 'uni-rever';
        rever.textContent = '↻ Rever abertura';
        document.body.appendChild(rever);
    }

    rever.addEventListener('click', tocar);

    let jaViu = false;

    try {
        jaViu = sessionStorage.getItem(chave) === '1';
    } catch (_) {}

    const forcar = new URLSearchParams(
        location.search
    ).get('intro') === '1';

    if (forcar || !jaViu) {
        tocar();
    }
})();
