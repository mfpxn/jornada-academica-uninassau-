# Pitch de vendas — apresentação de 5 minutos, 16/11/2026

**Atenção:** dia 16/11 é a **apresentação do projeto**; a Jornada ocorre em 9 e 10 de dezembro de 2026. O aplicativo apresentado é um **protótipo** e os certificados são demonstrativos, sem validação institucional. Não alegue que o sistema já foi adotado oficialmente.

## 0:00 a 0:45 — O problema

"O controle manual de inscrições e presenças depende de várias planilhas e conferências. Isso consome tempo da coordenação, aumenta erros e dificulta calcular quem tem direito a certificado. Criamos uma plataforma web que reúne essas etapas em um só fluxo."

## 0:45 a 1:30 — A solução e arquitetura

Mostre a página inicial no navegador. "O front-end usa HTML, CSS e JavaScript. O back-end usa Python e Flask. Os registros ficam em banco relacional, com proteção a cadastros duplicados e área do professor com autenticação. A versão de apresentação usa dados fictícios e emite PDFs demonstrativos."

## 1:30 a 2:15 — Inscrição ao vivo

Abra `/inscricao` com dados fictícios preparados. Demonstre máscara de CPF/telefone e envio. Se houver tempo, mostre que tentar cadastrar o mesmo CPF gera bloqueio sem duplicar cadastro.

## 2:15 a 3:25 — Painel e frequência

Entre em `/professor/login`, mostre lista de atividades e registe o check-in de um aluno de teste. Demonstre que marcar o mesmo aluno duas vezes na mesma atividade não duplica a presença. Confira o relatório com a carga horária total.

## 3:25 a 4:20 — Certificado

Mostre a liberação do certificado quando o aluno simulado atingir a carga configurada. Gere e baixe o PDF demonstrativo com o nome do aluno e um código de consulta. Explique que a oficialização, as assinaturas e o critério final de frequência dependem da instituição.

## 4:20 a 5:00 — Qualidade e fechamento

"Além de funcionar no navegador, a aplicação tem testes automatizados de cadastro, presença, acesso e emissão. Ela pode ser publicada na nuvem, com banco relacional. Para uso real, o próximo passo é homologar os requisitos institucionais, revisar a LGPD e implementar monitoramento e backups."

Finalize com o link da demonstração ou retorno à página inicial.

## Plano B de apresentação

- Se a internet falhar, execute `python run.py` no Linux e abra `http://127.0.0.1:5000`.
- Mantenha um registro fictício pré-cadastrado e duas atividades de 10h.
- Abra o PDF demonstrativo previamente gerado.
- Se houver divergência de 20h e 75%, explique que a variável `CERTIFICATE_MIN_HOURS` está configurável e precisa ser homologada.
