# Etapa 6 · Interface 3D · 6ª Jornada Acadêmica UNINASSAU

## Conteúdo da atualização

Arquivos alterados/novos:
- `app/templates/base.html` (referência à nova folha CSS e ao novo JavaScript)
- `app/templates/index.html` (landing page repaginada)
- `app/templates/inscricao.html` (indicador de preenchimento)
- `app/static/css/experience.css` (visual responsivo e efeitos 3D com CSS)
- `app/static/js/experience.js` (interatividade e acessibilidade)
- `tests/test_frontend_3d.py` (três novos testes de integração)

Os arquivos Python, o banco de dados e os endpoints do projeto **não** são substituídos por esta atualização.

## Instalar no Linux

1. Interrompa o Flask com Ctrl+C, se estiver executando.
2. Baixe `jornada-frontend-3d.zip` para `Downloads`.
3. No terminal:

```bash
cd ~/Projetos/jornada-academica-uninassau
source .venv/bin/activate
mkdir -p ../backup-frontend-antes-3d
cp -a app/templates ../backup-frontend-antes-3d/
cp -a app/static ../backup-frontend-antes-3d/

ZIP=$(find "$HOME" -maxdepth 5 -type f -name 'jornada-frontend-3d*.zip' -print -quit 2>/dev/null)
if [ -f "$ZIP" ]; then
    python -m zipfile -t "$ZIP" && python -m zipfile -e "$ZIP" .
else
    echo 'Arquivo ZIP não encontrado. Confira o download.'
fi
```

4. Teste e inicie:

```bash
python -m pytest -q
python run.py
```

5. Acesse `http://127.0.0.1:5000` e pressione `Ctrl+Shift+R` para forçar atualização do cache do navegador.

**Resultado de testes esperado:** 27 testes (24 existentes + 3 novos). Caso o código local difira das etapas anteriores, a contagem poderá variar.

## Funcionalidades visuais

- Logo oficial em cartão com profundidade/perspectiva 3D e iluminação.
- Elementos de fundo, anéis orbitais e efeitos de flutuação.
- Cartões com resposta ao cursor em computadores, sem efeitos de tilt no celular.
- 5 abas interativas para os pilares do evento, com navegação por teclado.
- Contagem regressiva para 09/12/2026 (em horário de Teresina).
- Entrada sutil das seções ao rolar, com suporte a movimento reduzido.
- Progresso visual do formulário de inscrição sem alterar dados enviados ao servidor.
- Refinamentos nas telas do professor e do certificado, mantendo as funcionalidades.

## Limitações e observações

- A estética 3D é feita com CSS, não com WebGL/Three.js. Evita dependências pesadas.
- O protótipo continua sendo demonstrativo, sem validade institucional.
- As regras do certificado e hospedagem seguem as etapas anteriores.
- A versão deve ser testada com `python -m pytest -q` no computador do desenvolvedor.
- Para voltar à aparência anterior, restaure `templates` e `static` da pasta `../backup-frontend-antes-3d/`, e remova `tests/test_frontend_3d.py`.
