# Animação 3D de abertura · UNINASSAU

## Instalação

1. Pare o Flask com Ctrl+C.
2. Entre na pasta do projeto e ative a venv.
3. Faça backup das pastas app/templates e app/static.
4. Extraia este ZIP na raiz do projeto, mesclando os arquivos (sem apagar o banco de dados).
5. Rode `python -m pytest -q` e depois `python run.py`.
6. Acesse `http://127.0.0.1:5000`.

A abertura aparece somente na página inicial, na primeira visita da aba/sessão. Clique em **Rever abertura** para vê-la novamente. **Pular abertura** e **Esc** pulam a animação. Quem ativou a opção de reduzir movimento não recebe a animação. Não tem áudio.

O pacote inclui a interface 3D anterior, para funcionar mesmo em instalações que ainda estavam com o front-end antigo. Não modifica o banco nem o back-end.

A logo oficial foi recortada do modelo de certificado fornecido no trabalho; mantenha seu uso apenas no contexto acadêmico e com autorização institucional caso haja divulgação pública.

O efeito é CSS 3D (não é modelo WebGL real), com sombras, perspectiva e rotação. Arquivos: `intro-coin.css` e `intro-coin.js`.
