"""Geração do certificado demonstrativo e cálculo das horas registradas."""
from io import BytesIO
from pathlib import Path

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from sqlalchemy import func

from app import db
from app.models import Atividade, Presenca


# O template do professor é rasterizado; pontos são posicionados no sistema
# normalizado de 1447 x 1024 observado no modelo enviado.
REFERENCIA_LARGURA = 1447
REFERENCIA_ALTURA = 1024


def horas_participante(participante_id):
    """Horas distintas por atividade; UNIQUE no banco impede duplicidade."""
    horas = (db.session.query(func.coalesce(func.sum(Atividade.carga_horaria), 0))
             .select_from(Presenca)
             .join(Atividade, Atividade.id == Presenca.atividade_id)
             .filter(Presenca.participante_id == participante_id)
             .scalar())
    return int(horas or 0)


def pode_emitir(participante_id):
    return horas_participante(participante_id) >= current_app.config['CERTIFICATE_MIN_HOURS']


def url_verificacao(codigo):
    base = current_app.config.get('PUBLIC_BASE_URL', '')
    if not base:
        return None
    return f'{base}/certificados/verificar/{codigo}'


def gerar_pdf_certificado(participante, certificado):
    """Gera uma página A4 paisagem, preservando o template acadêmico.

    Não insere assinatura, selo de autenticidade institucional ou certificação
    digital que a instituição não tenha efetivamente autorizado.
    """
    caminho = (Path(current_app.root_path) / 'static' / 'img'
               / 'modelo-certificado.jpeg')
    largura, altura = landscape(A4)
    escala_x = largura / REFERENCIA_LARGURA
    escala_y = altura / REFERENCIA_ALTURA

    def X(px):
        return px * escala_x

    def Y(px):
        return altura - px * escala_y

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(largura, altura), pageCompression=1)
    pdf.setTitle('Modelo academico de certificado - 6a Jornada Academica')
    pdf.setAuthor('Protótipo acadêmico de gestão de eventos')
    pdf.drawImage(ImageReader(str(caminho)), 0, 0,
                  width=largura, height=altura, preserveAspectRatio=False)

    nome = ' '.join(participante.nome.upper().split())
    fonte = 'Helvetica-Bold'
    tamanho = 17.0
    largura_max = X(700)
    while pdfmetrics.stringWidth(nome, fonte, tamanho) > largura_max and tamanho > 10:
        tamanho -= 0.5

    pdf.setFillColor(colors.HexColor('#09265c'))
    pdf.setFont(fonte, tamanho)
    pdf.drawCentredString(X(654), Y(627), nome)

    # Verificação de caráter acadêmico. Não se trata de chancela oficial.
    pdf.saveState()
    pdf.setFillColor(colors.HexColor('#B33423'))
    pdf.setFont('Helvetica-Bold', 8.3)
    pdf.drawString(X(70), Y(781), 'DOCUMENTO DE DEMONSTRACAO - SEM VALIDADE INSTITUCIONAL')
    pdf.restoreState()

    pdf.saveState()
    pdf.setFillColor(colors.HexColor('#35405a'))
    pdf.setFont('Helvetica', 7.8)
    pdf.drawString(X(70), Y(803), 'Codigo de verificacao (prototipo): ' + certificado.codigo_verificacao)
    pdf.restoreState()

    # Sinalização visível que não cobre o texto do documento.
    pdf.saveState()
    pdf.setFillColor(colors.HexColor('#B33423'))
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawCentredString(X(743), Y(390), 'MODELO DE DEMONSTRACAO')
    pdf.restoreState()

    # Não inserir QR Code se a aplicação não possui URL pública configurada;
    # 127.0.0.1 não é um endereço verificável em outros computadores.
    destino = url_verificacao(certificado.codigo_verificacao)
    if destino:
        try:
            import qrcode
            codigo_qr = qrcode.make(destino)
            pdf.drawImage(ImageReader(codigo_qr.get_image()), X(1265), Y(824),
                          width=X(83), height=Y(824) - Y(907), mask='auto')
        except ImportError:
            current_app.logger.warning('Biblioteca qrcode indisponível; PDF sem QR Code.')

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
