#!/usr/bin/env python3

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""
Gerador do PDF: Sentinela Democrática — Estratégia de Monetização e Gamificação v19.6.0
Usa ReportLab para gerar um relatório profissional multi-páginas.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from reportlab.graphics import renderPDF

# -------------------------------------------------------------------
# Fontes
# -------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype"

pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(FONT_DIR, 'dejavu', 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', os.path.join(FONT_DIR, 'dejavu', 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSerif', os.path.join(FONT_DIR, 'dejavu', 'DejaVuSerif.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', os.path.join(FONT_DIR, 'dejavu', 'DejaVuSerif-Bold.ttf')))
pdfmetrics.registerFont(TTFont('Carlito', os.path.join(FONT_DIR, 'english', 'calibri-regular.ttf')))
pdfmetrics.registerFont(TTFont('Carlito-Bold', os.path.join(FONT_DIR, 'english', 'calibri-bold.ttf')))
pdfmetrics.registerFont(TTFont('SimHei', os.path.join(FONT_DIR, 'chinese', 'SimHei.ttf')))

# -------------------------------------------------------------------
# Cores
# -------------------------------------------------------------------
PRIMARY = HexColor("#0f172a")       # Slate 900
SECONDARY = HexColor("#1e293b")     # Slate 800
ACCENT = HexColor("#dc2626")        # Red 600
ACCENT_LIGHT = HexColor("#fecaca")  # Red 200
ACCENT_DARK = HexColor("#991b1b")   # Red 800
BLUE = HexColor("#1d4ed8")          # Blue 700
BLUE_LIGHT = HexColor("#dbeafe")    # Blue 100
GREEN = HexColor("#15803d")         # Green 700
GREEN_LIGHT = HexColor("#dcfce7")   # Green 100
AMBER = HexColor("#d97706")         # Amber 600
AMBER_LIGHT = HexColor("#fef3c7")   # Amber 100
PURPLE = HexColor("#7c3aed")        # Violet 600
PURPLE_LIGHT = HexColor("#ede9fe")  # Violet 100
GRAY_50 = HexColor("#f8fafc")
GRAY_100 = HexColor("#f1f5f9")
GRAY_200 = HexColor("#e2e8f0")
GRAY_300 = HexColor("#cbd5e1")
GRAY_500 = HexColor("#64748b")
GRAY_700 = HexColor("#334155")
GRAY_900 = HexColor("#0f172a")

# -------------------------------------------------------------------
# Estilos
# -------------------------------------------------------------------
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    'CustomTitle', parent=styles['Title'],
    fontName='DejaVuSans-Bold', fontSize=28, leading=34,
    textColor=PRIMARY, spaceAfter=6*mm, alignment=TA_LEFT
)

style_h1 = ParagraphStyle(
    'CustomH1', parent=styles['Heading1'],
    fontName='DejaVuSans-Bold', fontSize=18, leading=24,
    textColor=PRIMARY, spaceBefore=10*mm, spaceAfter=4*mm,
    borderPadding=(0, 0, 2, 0),
)

style_h2 = ParagraphStyle(
    'CustomH2', parent=styles['Heading2'],
    fontName='DejaVuSans-Bold', fontSize=14, leading=18,
    textColor=SECONDARY, spaceBefore=7*mm, spaceAfter=3*mm,
)

style_h3 = ParagraphStyle(
    'CustomH3', parent=styles['Heading3'],
    fontName='DejaVuSans-Bold', fontSize=11, leading=15,
    textColor=GRAY_700, spaceBefore=5*mm, spaceAfter=2*mm,
)

style_body = ParagraphStyle(
    'CustomBody', parent=styles['Normal'],
    fontName='Carlito', fontSize=10, leading=15,
    textColor=GRAY_900, spaceAfter=3*mm,
    alignment=TA_JUSTIFY,
)

style_body_indent = ParagraphStyle(
    'CustomBodyIndent', parent=style_body,
    leftIndent=8*mm,
)

style_bullet = ParagraphStyle(
    'CustomBullet', parent=style_body,
    leftIndent=10*mm, firstLineIndent=-5*mm,
    spaceAfter=1.5*mm,
)

style_callout = ParagraphStyle(
    'CustomCallout', parent=style_body,
    fontName='DejaVuSans-Bold', fontSize=10, leading=15,
    textColor=ACCENT_DARK, backColor=ACCENT_LIGHT,
    borderPadding=(3*mm, 4*mm, 3*mm, 4*mm),
    spaceAfter=4*mm,
)

style_quote = ParagraphStyle(
    'CustomQuote', parent=style_body,
    leftIndent=10*mm, rightIndent=5*mm,
    fontName='Carlito', fontSize=10, leading=15,
    textColor=GRAY_500, borderColor=ACCENT,
    borderWidth=2, borderPadding=(2*mm, 0, 2*mm, 4*mm),
)

style_small = ParagraphStyle(
    'CustomSmall', parent=style_body,
    fontSize=8, leading=11, textColor=GRAY_500,
)

style_table_header = ParagraphStyle(
    'TableHeader', fontName='DejaVuSans-Bold', fontSize=9, leading=12,
    textColor=white, alignment=TA_CENTER,
)

style_table_cell = ParagraphStyle(
    'TableCell', fontName='Carlito', fontSize=9, leading=12,
    textColor=GRAY_900, alignment=TA_CENTER,
)

style_table_cell_left = ParagraphStyle(
    'TableCellLeft', fontName='Carlito', fontSize=9, leading=12,
    textColor=GRAY_900, alignment=TA_LEFT,
)

style_table_cell_bold = ParagraphStyle(
    'TableCellBold', fontName='DejaVuSans-Bold', fontSize=9, leading=12,
    textColor=PRIMARY, alignment=TA_LEFT,
)

style_code = ParagraphStyle(
    'CustomCode', parent=style_body,
    fontName='DejaVuSans', fontSize=8.5, leading=12,
    backColor=GRAY_100, borderColor=GRAY_300,
    borderWidth=0.5, borderPadding=(2*mm, 3*mm, 2*mm, 3*mm),
    leftIndent=5*mm, rightIndent=5*mm,
)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def heading1(text):
    """Cria heading H1 com linha decorativa abaixo."""
    return [
        Paragraph(text, style_h1),
        HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=4*mm),
    ]

def heading2(text):
    return Paragraph(text, style_h2)

def heading3(text):
    return Paragraph(text, style_h3)

def body(text):
    return Paragraph(text, style_body)

def bullet(text):
    return Paragraph(f"\u2022 {text}", style_bullet)

def callout(text):
    return Paragraph(text, style_callout)

def code_block(text):
    return Paragraph(text.replace('\n', '<br/>'), style_code)

def spacer(h=4):
    return Spacer(1, h*mm)

# -------------------------------------------------------------------
# Custom Flowable: Color Badge
# -------------------------------------------------------------------
class ColorBadge(Flowable):
    """Badge colorido com texto."""
    def __init__(self, text, bg_color, text_color=white, width=None, height=18):
        Flowable.__init__(self)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.badge_width = width or len(text)*7 + 16
        self.badge_height = height

    def wrap(self, availWidth, availHeight):
        return (self.badge_width, self.badge_height)

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.roundRect(0, 0, self.badge_width, self.badge_height, 4, fill=1, stroke=0)
        self.canv.setFillColor(self.text_color)
        self.canv.setFont('DejaVuSans-Bold', 8)
        tw = self.canv.stringWidth(self.text, 'DejaVuSans-Bold', 8)
        self.canv.drawString((self.badge_width - tw) / 2, 5, self.text)


# -------------------------------------------------------------------
# Página de capa
# -------------------------------------------------------------------
def create_cover_page():
    """Gera os elementos da página de capa."""
    elements = []
    elements.append(Spacer(1, 25*mm))

    # Badge
    elements.append(ColorBadge("CONFIDENCIAL", ACCENT, white, width=120, height=22))
    elements.append(Spacer(1, 8*mm))

    # Titulo principal
    elements.append(Paragraph("SENTINELA DEMOCRATICA", ParagraphStyle(
        'CoverTitle', fontName='DejaVuSans-Bold', fontSize=32, leading=38,
        textColor=PRIMARY, alignment=TA_LEFT,
    )))
    elements.append(Spacer(1, 2*mm))

    # Subtítulo
    elements.append(Paragraph("Estrategia de Monetizacao e Gamificacao", ParagraphStyle(
        'CoverSub', fontName='DejaVuSans-Bold', fontSize=18, leading=24,
        textColor=ACCENT, alignment=TA_LEFT,
    )))
    elements.append(Spacer(1, 2*mm))

    # Versão
    elements.append(Paragraph("v19.6.0 — Modelo de Creditos (Tokens STN)", ParagraphStyle(
        'CoverVer', fontName='Carlito', fontSize=12, leading=16,
        textColor=GRAY_500, alignment=TA_LEFT,
    )))
    elements.append(Spacer(1, 15*mm))

    # Descrição
    desc_style = ParagraphStyle(
        'CoverDesc', fontName='Carlito', fontSize=11, leading=17,
        textColor=GRAY_700, alignment=TA_JUSTIFY,
    )
    elements.append(Paragraph(
        "Este documento apresenta a estrategia completa de monetizacao do Sentinela Democratica, "
        "um sistema de inteligencia forense para monitoramento de discurso em redes sociais. "
        "A estrategia substitui o modelo de assinatura por um modelo de creditos gamificados "
        "(Tokens STN), inspirado em mecanicas de jogos free-to-play e plataformas de dados SaaS, "
        "com o objetivo de maximizar o faturamento por usuario por meio de ancoragem de preco, "
        "oclusao seletiva de informacao e ciclos de recompensa variavel.",
        desc_style
    ))
    elements.append(Spacer(1, 20*mm))

    # Metadata
    meta_style = ParagraphStyle(
        'CoverMeta', fontName='Carlito', fontSize=9, leading=13,
        textColor=GRAY_500, alignment=TA_LEFT,
    )
    today = datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Data: {today}", meta_style))
    elements.append(Paragraph("Classificacao: Confidencial — Uso interno", meta_style))
    elements.append(Paragraph("Autor: Equipe Sentinela Democratica", meta_style))

    return elements


# -------------------------------------------------------------------
# CONTEUDO PRINCIPAL
# -------------------------------------------------------------------
def build_content():
    """Constroi todo o conteudo do relatorio."""
    story = []

    # ===================== CAPA =====================
    story.extend(create_cover_page())
    story.append(PageBreak())

    # ===================== SUMARIO =====================
    story.extend(heading1("Sumario"))
    toc_items = [
        ("1.", "Diagnostico: Por que o Modelo de Assinatura Falhou"),
        ("2.", "A Moeda: Tokens de Sentinela (STN)"),
        ("3.", "Modelo de Escala e Ancoragem de Preco"),
        ("4.", "A Tecnica de Oclusao Seletiva (Fog of War)"),
        ("5.", "Ciclo de Recompensa Variavel (Gacha-Style)"),
        ("6.", "Barra de Nivel de Protecao"),
        ("7.", "Design de Interface: UX de Gamificacao"),
        ("8.", "Integracao Tecnica: Schema do Banco de Dados"),
        ("9.", "Webhook Stripe: Fluxo de Compra e Consumo"),
        ("10.", "Projecao Financeira"),
        ("11.", "Roadmap de Implementacao"),
        ("12.", "Consideracoes Legais e Eticas"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f'<b>{num}</b>  {title}',
            ParagraphStyle('TOCItem', fontName='Carlito', fontSize=11, leading=18,
                           textColor=GRAY_700, leftIndent=5*mm, spaceAfter=2*mm)
        ))
    story.append(PageBreak())

    # ===================== SECAO 1 =====================
    story.extend(heading1("1. Diagnostico: Por que o Modelo de Assinatura Falhou"))

    story.append(body(
        "O modelo tradicional de assinatura mensal ou anual para plataformas de inteligencia de dados "
        "apresenta barreiras significativas quando aplicado ao contexto de monitoramento de discurso "
        "politico. Diferente de ferramentas de produtividade ou entretenimento, onde o uso e diario e "
        "o valor percebido e constante, o monitoramento de ameacas discursivas e intrinsecamente "
        "episodico: o usuario precisa da informacao em momentos especificos de crise, nao de forma "
        "continua. Isso gera o fenomeno da 'friccao de compromisso' — o usuario hesita em assinar "
        "algo que pode nao usar todos os meses, resultando em taxas de conversao abaixo de 3% para "
        "visitantes anonimos e churn superior a 40% em assinaturas anuais."
    ))

    story.append(body(
        "Alem disso, o preco de R$ 249,00 por um unico relatorio revela que o valor esta no acesso "
        "pontual a informacao nominal — saber quem sao os agressores, quais sao seus alvos e como "
        "se organizam. O usuario nao quer uma 'plataforma'; ele quer desmascarar um alvo especifico. "
        "Essa e a unidade fundamental de valor: a revelacao. E ela que deve ser precificada, nao o "
        "acesso temporal a um painel."
    ))

    story.append(heading2("1.1 Comparativo de Modelos"))

    # Tabela comparativa
    table_data = [
        [
            Paragraph("Criterio", style_table_header),
            Paragraph("Assinatura Mensal", style_table_header),
            Paragraph("Creditos (Tokens STN)", style_table_header),
        ],
        [
            Paragraph("Friccao de compra", style_table_cell_left),
            Paragraph("Alta (compromisso recorrente)", style_table_cell),
            Paragraph("Baixa (compra avulsa)", style_table_cell),
        ],
        [
            Paragraph("Valor percebido", style_table_cell_left),
            Paragraph("Difuso (acesso a plataforma)", style_table_cell),
            Paragraph("Especifico (revelar um alvo)", style_table_cell),
        ],
        [
            Paragraph("Ticket medio", style_table_cell_left),
            Paragraph("R$ 49-99/mes", style_table_cell),
            Paragraph("R$ 149-249/unidade", style_table_cell),
        ],
        [
            Paragraph("Churn", style_table_cell_left),
            Paragraph("40-60% anual", style_table_cell),
            Paragraph("N/A (sem recursao)", style_table_cell),
        ],
        [
            Paragraph("Upsell natural", style_table_cell_left),
            Paragraph("Limitado (upgrade de plano)", style_table_cell),
            Paragraph("Ilimitado (mais tokens, mais revelacoes)", style_table_cell),
        ],
        [
            Paragraph("Gamificacao", style_table_cell_left),
            Paragraph("Dificil (progresso artificial)", style_table_cell),
            Paragraph("Nativa (desmascarar = recompensa)", style_table_cell),
        ],
        [
            Paragraph("Receita recorrente", style_table_cell_left),
            Paragraph("Alta previsibilidade", style_table_cell),
            Paragraph("Variavel, mas maior LTV", style_table_cell),
        ],
    ]

    t = Table(table_data, colWidths=[90, 155, 155])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, -1), GRAY_50),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(spacer(4))

    story.append(callout(
        "Conclusao do diagnostico: O modelo de creditos elimina a friccao de compromisso, "
        "alinha o preco ao valor real percebido (revelacao de informacao) e abre espaco "
        "para mecanicas de gamificacao que multiplicam o faturamento por usuario."
    ))

    # ===================== SECAO 2 =====================
    story.extend(heading1("2. A Moeda: Tokens de Sentinela (STN)"))

    story.append(body(
        "A decisao mais importante da estrategia e a nomenclatura da unidade de valor. "
        "Nao vendemos 'relatorios', 'downloads' ou 'acessos'. Vendemos <b>Tokens de Sentinela (STN)</b>. "
        "Essa escolha nao e cosmetic — e fundamentada em principios de psicologia comportamental "
        "e economia de jogos digitais que demonstram que a abstracao da moeda desacopla o usuario "
        "da nocao de custo financeiro e facilita o gasto impulsivo."
    ))

    story.append(heading2("2.1 Por que 'Tokens' e nao 'Relatorios'"))

    story.append(body(
        "Quando um usuario compra '1 relatorio por R$ 249', ele calcula o custo-beneficio "
        "conscientemente: 'Vale a pena pagar R$ 249 por este documento?'. Esse e um processo "
        "racional de deliberacao, que leva tempo e frequentemente resulta em abandono. Quando o "
        "mesmo usuario compra '1 Token STN por R$ 249', a deliberacao muda de natureza: 'Preciso "
        "desmascarar este alvo?'. O foco desloca-se do preco para a necessidade, e o Token "
        "funciona como moeda de troca que o usuario ja possui (ou deseja possuir). Estudos de "
        "economia comportamental em jogos como League of Legends e Genshin Impact demonstram que "
        "moedas virtuais aumentam o gasto medio por usuario em 40-60% comparado a precificacao "
        "direta em dinheiro."
    ))

    story.append(heading2("2.2 Propriedades do Token STN"))

    props_data = [
        [
            Paragraph("Propriedade", style_table_header),
            Paragraph("Definicao", style_table_header),
            Paragraph("Impacto", style_table_header),
        ],
        [
            Paragraph("Abstracao", style_table_cell_bold),
            Paragraph("Desacopla valor financeiro de valor informacional", style_table_cell_left),
            Paragraph("Reduz friccao de compra", style_table_cell),
        ],
        [
            Paragraph("Acumulavel", style_table_cell_bold),
            Paragraph("Tokens nao expiram; ficam na conta do usuario", style_table_cell_left),
            Paragraph("Incentiva compra em lote (maior ticket)", style_table_cell),
        ],
        [
            Paragraph("Gamificavel", style_table_cell_bold),
            Paragraph("Pode ser ganho, bonus, descontado", style_table_cell_left),
            Paragraph("Abre mecanicas de recompensa e retencao", style_table_cell),
        ],
        [
            Paragraph("Escalavel", style_table_cell_bold),
            Paragraph("1 Token = 1 revelacao (independente do alvo)", style_table_cell_left),
            Paragraph("Precificacao uniforme, margem constante", style_table_cell),
        ],
    ]
    t2 = Table(props_data, colWidths=[80, 180, 140])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    # ===================== SECAO 3 =====================
    story.extend(heading1("3. Modelo de Escala e Ancoragem de Preco"))

    story.append(body(
        "A ancoragem de preco e a tecnica mais poderosa em precificacao de pacotes. O principio e simples: "
        "apresente primeiro o preco unitario (ancora), depois ofereca descontos crescentes para volumes "
        "maiores. O usuario percebe que esta 'economizando' ao comprar mais, quando na verdade esta "
        "aumentando seu compromisso financeiro. Essa tecnica e usada por plataformas como Amazon, "
        "Shopify e todos os jogos free-to-play com moeda virtual."
    ))

    story.append(heading2("3.1 Pacotes de Tokens STN"))

    # Tabela de pacotes
    pkg_data = [
        [
            Paragraph("Pacote", style_table_header),
            Paragraph("Nome no Sistema", style_table_header),
            Paragraph("Tokens", style_table_header),
            Paragraph("Bonus", style_table_header),
            Paragraph("Total", style_table_header),
            Paragraph("Valor", style_table_header),
            Paragraph("Valor/Token", style_table_header),
        ],
        [
            Paragraph("Starter", style_table_cell_bold),
            Paragraph("Operacao Unica", style_table_cell),
            Paragraph("1", style_table_cell),
            Paragraph("--", style_table_cell),
            Paragraph("1", style_table_cell),
            Paragraph("R$ 249", style_table_cell),
            Paragraph("R$ 249", style_table_cell),
        ],
        [
            Paragraph("Squad", style_table_cell_bold),
            Paragraph("Celula de Inteligencia", style_table_cell),
            Paragraph("3", style_table_cell),
            Paragraph("+1", style_table_cell),
            Paragraph("4", style_table_cell),
            Paragraph("R$ 597", style_table_cell),
            Paragraph("R$ 149", style_table_cell),
        ],
        [
            Paragraph("War Room", style_table_cell_bold),
            Paragraph("Comando Geral", style_table_cell),
            Paragraph("10", style_table_cell),
            Paragraph("+5", style_table_cell),
            Paragraph("15", style_table_cell),
            Paragraph("R$ 1.497", style_table_cell),
            Paragraph("R$ 99", style_table_cell),
        ],
    ]
    t3 = Table(pkg_data, colWidths=[60, 85, 42, 35, 38, 62, 62])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        # Highlight o valor/token do War Room
        ('BACKGROUND', (-1, -1), (-1, -1), GREEN_LIGHT),
        ('TEXTCOLOR', (-1, -1), (-1, -1), GREEN),
    ]))
    story.append(t3)
    story.append(spacer(3))

    story.append(heading2("3.2 Economia Percebida"))

    story.append(body(
        "A colocacao estrategica dos bonus cria a ilusao de economia progressiva. No pacote Squad, "
        "o usuario recebe 4 tokens por R$ 597 — um desconto de 40% sobre o preco unitario. No "
        "pacote War Room, sao 15 tokens por R$ 1.497 — um desconto de 60%. O usuario que precisaria "
        "de apenas 2 tokens e tentado a comprar o Squad 'porque sai mais barato por token', gastando "
        "R$ 597 em vez de R$ 498. O usuario que precisa de 5 tokens e empurrado para o War Room "
        "'porque assim cada token sai por R$ 99', comprometendo R$ 1.497 em vez de R$ 1.245. A "
        "ancoragem funciona porque o cerebro humano avalia precos relativamente, nao absolutamente."
    ))

    story.append(callout(
        "Regra de ouro da ancoragem: O pacote intermediario (Squad) deve ser o mais atrativo "
        "visualmente na pagina de precos — e o que gera o maior volume de vendas e a melhor "
        "margem de lucro proporcional ao suporte operacional."
    ))

    story.append(heading2("3.3 Mecanicas de Bonus e Urgencia"))

    story.append(bullet(
        "<b>Primeira Compra:</b> +1 Token bônus no primeiro pacote (qualquer tier) para criar "
        "habito imediato de consumo e demonstrar o valor da revelacao."
    ))
    story.append(bullet(
        "<b>Pacote Rotativo:</b> A cada 2 semanas, um pacote especial com nome tematico "
        "(ex: 'Operacao Queima de Arquivo' — 5 tokens por R$ 449, economia de 64%) "
        "disponivel por apenas 48h, criando urgencia (FOMO)."
    ))
    story.append(bullet(
        "<b>Indicacao:</b> Quando um usuario convida um colega que compra qualquer pacote, "
        "ambos ganham +1 Token. Custo do CAC: R$ 249 em receita potencial por indicacao."
    ))
    story.append(bullet(
        "<b>Streak de Protecao:</b> Se o usuario consome pelo menos 1 Token por semana "
        "durante 4 semanas seguidas, ganha +1 Token no final do periodo. Incentiva "
        "uso continuo e combate o abandono."
    ))

    # ===================== SECAO 4 =====================
    story.extend(heading1("4. A Tecnica de Oclusao Seletiva (Fog of War)"))

    story.append(body(
        "O 'Fog of War' (Nebulina de Guerra) e a tecnica central de conversao gratuita-para-paga "
        "do Sentinela. Funciona exatamente como a mecanica de mapa oculto em jogos de estrategia "
        "(Civilization, StarCraft): o usuario ve que existe algo importante, mas precisa gastar "
        "recursos para revelar. No nosso caso, o recurso e o Token STN, e a revelacao e a "
        "identidade nominal do agressor."
    ))

    story.append(heading2("4.1 O que o usuario gratuito ve"))

    story.append(body(
        "No dashboard da versao gratuita, o usuario tem acesso a informacoes agregadas e anonimizadas "
        "que demonstram o valor da plataforma sem revelar dados nominais. A interface exibe "
        "indicadores de ameaca com contornos borrados, alertas pulsantes e metricas gerais que "
        "criam a sensacao de que ha algo importante acontecendo 'ali dentro' que o usuario nao "
        "consegue ver completamente. Essa tecnica de 'show, dont tell' e muito mais poderosa que "
        "qualquier copy de marketing, porque o usuario sente a perda de informacao, nao apenas "
        "a promessa de valor."
    ))

    fog_data = [
        [
            Paragraph("Elemento", style_table_header),
            Paragraph("Versao Gratuita (Oculto)", style_table_header),
            Paragraph("Versao Token (Revelado)", style_table_header),
        ],
        [
            Paragraph("Atores", style_table_cell_bold),
            Paragraph("'15 perfis hostis detectados' (nomes borrados)", style_table_cell_left),
            Paragraph("@usuario1, @usuario2, @usuario3... (nomes reais)", style_table_cell_left),
        ],
        [
            Paragraph("Sentimento", style_table_cell_bold),
            Paragraph("'Ataque coordenado em andamento' (icone vermelho pulsante)", style_table_cell_left),
            Paragraph("Detalhamento do ataque: quem, quando, onde", style_table_cell_left),
        ],
        [
            Paragraph("Classificacao", style_table_cell_bold),
            Paragraph("'34 interacoes hostis mapeadas' (grafico de barras)", style_table_cell_left),
            Paragraph("Lista completa com tipo: ODIO_IDENTITARIO, AMEACA, etc.", style_table_cell_left),
        ],
        [
            Paragraph("Rede", style_table_cell_bold),
            Paragraph("'2 conexoes ocultas identificadas' (visualizacao parcial)", style_table_cell_left),
            Paragraph("Grafo completo de relacoes entre perfis hostis", style_table_cell_left),
        ],
        [
            Paragraph("Dossie PDF", style_table_cell_bold),
            Paragraph("Previa com 3 linhas visiveis + 'Continue lendo...'", style_table_cell_left),
            Paragraph("Dossie completo com todos os comentarios classificados", style_table_cell_left),
        ],
    ]
    t4 = Table(fog_data, colWidths=[70, 165, 165])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t4)
    story.append(spacer(3))

    story.append(heading2("4.2 O Gatilho de Urgencia: O Radar Pulsante"))

    story.append(body(
        "O elemento mais poderoso do Fog of War e o 'Radar Pulsante' — um indicador visual "
        "que aparece no dashboard quando o sistema detecta uma ameaca critica em tempo real. "
        "Funciona assim: o usuario ve um icone de alerta vermelho pulsando sobre um alvo "
        "especifico (com o nome borrado), acompanhado da mensagem 'Sinal de Hostilidade Critica "
        "Detectado. Use 1 Token para desmascarar o agressor.' Esse gatilho combina tres "
        "principios psicologicos simultaneos: urgencia (algo esta acontecendo agora), curiosidade "
        "(quem e o agressor?) e escassez (o alerta pode desaparecer). A taxa de conversao "
        "esperada para esse gatilho especifico e de 15-25%, comparada a 2-5% de um CTA generico "
        "como 'Fazer Upgrade'."
    ))

    # ===================== SECAO 5 =====================
    story.extend(heading1("5. Ciclo de Recompensa Variavel (Gacha-Style)"))

    story.append(body(
        "A recompensa variavel e o principio mais poderoso de retencao em jogos digitais. "
        "Diferente de recompensas fixas (que o usuario aprende a esperar e perdem o apelo), "
        "recompensas variaveis criam um ciclo de anticipacao e surpresa que mantem o cerebro "
        "engajado. Esse e o mecanismo por tras de loot boxes, gacha games e ate notificacoes "
        "de redes sociais — a incerteza do que vira a seguir e mais viciante que a certeza."
    ))

    story.append(heading2("5.1 O Insight Extra Gratuito"))

    story.append(body(
        "Quando o usuario gasta 1 Token para desmascarar um alvo, o Sentinela nao entrega apenas "
        "o dossie esperado. Ele entrega o dossie <b>mais um Insight Extra</b> — uma informacao "
        "que o usuario nao sabia que existia e que cria um novo desejo. Por exemplo: ao desbloquear "
        "o alvo '@politico_x', o sistema apresenta o dossie completo e, logo abaixo, uma mensagem "
        "como: 'Ao analisar este alvo, nosso algoritmo identificou uma conexao oculta com outros "
        "2 perfis coordenados. Quer ver a rede completa por mais 1 Token?'. Essa tecnica funciona "
        "porque transforma cada consumo em uma nova oportunidade de venda, criando um efeito cascata "
        "onde 1 Token gera a vontade de gastar mais 1, que gera a vontade de gastar mais 1, e assim "
        "por diante."
    ))

    story.append(heading2("5.2 Tiers de Recompensa"))

    tier_data = [
        [
            Paragraph("Tier", style_table_header),
            Paragraph("Probabilidade", style_table_header),
            Paragraph("Conteudo Extra", style_table_header),
            Paragraph("Efeito", style_table_header),
        ],
        [
            Paragraph("Comum", style_table_cell_bold),
            Paragraph("60%", style_table_cell),
            Paragraph("1 conexao adicional identificada", style_table_cell_left),
            Paragraph("Upsell basico (+1 Token)", style_table_cell),
        ],
        [
            Paragraph("Raro", style_table_cell_bold),
            Paragraph("30%", style_table_cell),
            Paragraph("Rede completa de 3-5 perfis relacionados", style_table_cell_left),
            Paragraph("Upsell medio (+2 Tokens)", style_table_cell),
        ],
        [
            Paragraph("Epico", style_table_cell_bold),
            Paragraph("9%", style_table_cell),
            Paragraph("Padrao de coordenacao temporal com cronologia", style_table_cell_left),
            Paragraph("Upsell alto (+3 Tokens)", style_table_cell),
        ],
        [
            Paragraph("Lendario", style_table_cell_bold),
            Paragraph("1%", style_table_cell),
            Paragraph("Relatorio completo de campanha organizada com origens e financiadores suspeitos", style_table_cell_left),
            Paragraph("Viralizacao (compartilhamento)", style_table_cell),
        ],
    ]
    t5 = Table(tier_data, colWidths=[55, 65, 165, 105])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # Highlight Epico e Lendario
        ('BACKGROUND', (0, -2), (-1, -2), PURPLE_LIGHT),
        ('BACKGROUND', (0, -1), (-1, -1), AMBER_LIGHT),
    ]))
    story.append(t5)
    story.append(spacer(3))

    story.append(body(
        "O tier Lendario funciona como o 'jackpot' dos jogos gacha: e raro o suficiente para "
        "criar uma historia ('Meu colega ganhou um relatorio lendario!'), gerando marketing "
        "organico e competicao social entre usuarios. A probabilidade de 1% significa que, "
        "em media, a cada 100 Tokens consumidos, 1 usuario recebera um relatorio lendario — "
        "custo marginal proximo de zero para a plataforma, valor percebido altissimo para o usuario."
    ))

    # ===================== SECAO 6 =====================
    story.extend(heading1("6. Barra de Nivel de Protecao"))

    story.append(body(
        "A Barra de Nivel de Protecao e uma mecanica de retencao visual que traduz o consumo de "
        "Tokens em uma sensacao de progresso e seguranca. Funciona como a barra de experiencia "
        "em um RPG: quanto mais o usuario 'desmascara' ameacas, mais 'protegido' ele se sente. "
        "A genialidade da mecanica esta no fato de que a barra nunca esta cheia — sempre ha mais "
        "ameacas a revelar, mais alvos a investigar, mais territorio a 'limpar' no mapa."
    ))

    story.append(heading2("6.1 Funcionamento"))

    story.append(body(
        "A barra de protecao e calculada com base na proporcao entre ameacas detectadas e ameacas "
        "desmascaradas pelo usuario. Se o Sentinela identificou 50 ameacas na regiao do usuario "
        "e ele desmascarou 10, a barra mostra 20% — com cor laranja, indicando que 80% das "
        "ameacas continuam ocultas. A interface exibe mensagens contextuais como: 'Sua regiao "
        "tem 40 ameacas nao investigadas. Desmascare mais alvos para aumentar seu nivel de "
        "protecao.' Quando o usuario atinge 50%, a barra fica verde. Aos 80%, dourada. Aos 100%, "
        "uma animacao de 'Missao Cumprida' e exibida — seguida imediatamente pela revelacao de "
        "novas ameacas detectadas, reiniciando o ciclo."
    ))

    level_data = [
        [
            Paragraph("Nivel", style_table_header),
            Paragraph("Faixa", style_table_header),
            Paragraph("Cor", style_table_header),
            Paragraph("Mensagem", style_table_header),
        ],
        [
            Paragraph("Critico", style_table_cell_bold),
            Paragraph("0-25%", style_table_cell),
            Paragraph("Vermelho", style_table_cell),
            Paragraph("Sua regiao esta vulneravel. Ameacas nao investigadas.", style_table_cell_left),
        ],
        [
            Paragraph("Alerta", style_table_cell_bold),
            Paragraph("25-50%", style_table_cell),
            Paragraph("Laranja", style_table_cell),
            Paragraph("Parcialmente protegido. Continue investigando.", style_table_cell_left),
        ],
        [
            Paragraph("Seguro", style_table_cell_bold),
            Paragraph("50-80%", style_table_cell),
            Paragraph("Verde", style_table_cell),
            Paragraph("Bom nivel de protecao. Novos alvos disponiveis.", style_table_cell_left),
        ],
        [
            Paragraph("Elite", style_table_cell_bold),
            Paragraph("80-99%", style_table_cell),
            Paragraph("Dourado", style_table_cell),
            Paragraph("Quase completo! Restam poucas ameacas.", style_table_cell_left),
        ],
        [
            Paragraph("Sentinela", style_table_cell_bold),
            Paragraph("100%", style_table_cell),
            Paragraph("Azul brilhante", style_table_cell),
            Paragraph("Missao cumprida! Novas ameacas detectadas...", style_table_cell_left),
        ],
    ]
    t6 = Table(level_data, colWidths=[55, 50, 65, 230])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t6)

    # ===================== SECAO 7 =====================
    story.extend(heading1("7. Design de Interface: UX de Gamificacao"))

    story.append(body(
        "A interface do Sentinela v19.6.0 deve ser redesenhada para refletir a mudanca de paradigma "
        "de 'plataforma de assinatura' para 'sistema de inteligencia com creditos'. Todos os elementos "
        "de UX devem reforcar as mecanicas de gamificacao: escassez, progresso, recompensa e "
        "urgencia. O design visual deve evocar esteticas de centros de comando militar e interfaces "
        "de inteligencia, com cores escuras, tipografia monospacada e indicadores de status em "
        "tempo real."
    ))

    story.append(heading2("7.1 Elementos de Interface Obrigatorios"))

    story.append(bullet(
        "<b>Contador de Tokens (canto superior direito):</b> Sempre visivel, como em jogos "
        "moveis. Mostra o saldo atual de Tokens STN com um botao '+' para compra rapida. "
        "Quando o saldo e zero, o contador fica vermelho com efeito de pulsacao suave."
    ))
    story.append(bullet(
        "<b>Botao de Acao nos Alvos:</b> Em cada alvo bloqueado no dashboard, o botao NAO "
        "deve dizer 'Fazer Upgrade' ou 'Assine o Pro'. Deve dizer 'Desmascarar Alvo (1 Token)' "
        "com um icone de radar ou olho. A acao e especifica e o custo e claro."
    ))
    story.append(bullet(
        "<b>Mapa de Calor:</b> Visualizacao do territorio monitorado com areas 'limpas' (verde) "
        "e 'nebulosas' (vermelho). O usuario que nao desmascarou nenhum alvo ve todo o mapa "
        "vermelho. Cada Token gasto 'limpa' uma area."
    ))
    story.append(bullet(
        "<b>Feed de Atividade:</b> Log em tempo real mostrando 'Nova ameaca detectada', "
        "'Hostilidade critica em aumento', '3 novos comentarios hostis identificados'. "
        "Cria a sensacao de que a plataforma esta viva e trabalhando."
    ))
    story.append(bullet(
        "<b>Pagina de Pricing Redesenhada:</b> Deixa de ser sobre 'Planos' e passa a ser "
        "sobre 'Pacotes de Creditos'. Layout tipo loja de jogos (Steam, Epic Games) com "
        "cards visuais para cada pacote e badge de 'Mais Popular' no intermediario."
    ))

    story.append(heading2("7.2 Copy e Microcopys Estrategicos"))

    copy_data = [
        [
            Paragraph("Contexto", style_table_header),
            Paragraph("Copy Atual (Errada)", style_table_header),
            Paragraph("Copy Gamificada (Correta)", style_table_header),
        ],
        [
            Paragraph("Sem tokens", style_table_cell_bold),
            Paragraph("'Faca upgrade para ver'", style_table_cell),
            Paragraph("'Desmascarar Alvo (1 Token)'", style_table_cell),
        ],
        [
            Paragraph("Pricing", style_table_cell_bold),
            Paragraph("'Plano Pro - R$ 49/mes'", style_table_cell),
            Paragraph("'Operacao Unica — 1 Token — R$ 249'", style_table_cell),
        ],
        [
            Paragraph("Sem saldo", style_table_cell_bold),
            Paragraph("'Assine para continuar'", style_table_cell),
            Paragraph("'Seus Tokens acabaram. Reabastecer?'", style_table_cell),
        ],
        [
            Paragraph("Bonus", style_table_cell_bold),
            Paragraph("'Voce ganhou 1 mes gratis'", style_table_cell),
            Paragraph("'Intel BONUS desbloqueada! +1 conexao oculta'", style_table_cell),
        ],
        [
            Paragraph("Urgencia", style_table_cell_bold),
            Paragraph("'Oferta por tempo limitado'", style_table_cell),
            Paragraph("'Ameaca CRITICA detectada. Desmascarar agora?'", style_table_cell),
        ],
    ]
    t7 = Table(copy_data, colWidths=[60, 145, 195])
    t7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t7)

    # ===================== SECAO 8 =====================
    story.extend(heading1("8. Integracao Tecnica: Schema do Banco de Dados"))

    story.append(body(
        "A migracao do modelo de assinatura para o modelo de creditos requer alteracoes "
        "no schema do banco de dados Supabase. A tabela de perfis de usuario precisa incorporar "
        "o saldo de Tokens STN e o historico de consumo. A seguir, apresentamos o SQL completo "
        "das alteracoes necessarias, compativel com PostgreSQL 15+ (Supabase)."
    ))

    story.append(heading2("8.1 Tabela de Usuarios (Modificada)"))

    sql_text = """CREATE TABLE IF NOT EXISTS user_accounts (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT DEFAULT '',
    plan            TEXT NOT NULL DEFAULT 'free'
                    CHECK (plan IN ('free','pro','admin')),
    -- Colunas do modelo de creditos (v19.6.0)
    tokens_stn      INTEGER NOT NULL DEFAULT 0,
    tokens_bonus    INTEGER NOT NULL DEFAULT 0,
    total_consumed  INTEGER NOT NULL DEFAULT 0,
    protection_level REAL NOT NULL DEFAULT 0.0,
    streak_weeks    INTEGER NOT NULL DEFAULT 0,
    last_token_at   TIMESTAMPTZ,
    first_purchase_at TIMESTAMPTZ,
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);"""
    story.append(code_block(sql_text))

    story.append(heading2("8.2 Tabela de Transacoes de Tokens"))

    sql_text2 = """CREATE TABLE IF NOT EXISTS token_transactions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES user_accounts(id),
    type            TEXT NOT NULL CHECK (type IN (
                        'purchase','bonus','consumption',
                        'referral','streak','expired'
                    )),
    amount          INTEGER NOT NULL,  -- positivo = credito, negativo = debito
    balance_after   INTEGER NOT NULL,
    stripe_session_id TEXT,             -- ID da sessao Stripe (para compras)
    target_username TEXT,               -- Alvo desmascarado (para consumo)
    description     TEXT DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);"""
    story.append(code_block(sql_text2))

    story.append(heading2("8.3 Tabela de Pacotes Comprados"))

    sql_text3 = """CREATE TABLE IF NOT EXISTS token_purchases (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES user_accounts(id),
    package_slug    TEXT NOT NULL,       -- 'starter','squad','war_room'
    tokens_granted  INTEGER NOT NULL,
    tokens_bonus    INTEGER NOT NULL DEFAULT 0,
    amount_cents    INTEGER NOT NULL,    -- Valor em centavos (R$ 24900)
    stripe_payment_id TEXT,
    status          TEXT DEFAULT 'completed'
                    CHECK (status IN ('pending','completed','refunded')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);"""
    story.append(code_block(sql_text3))

    story.append(heading2("8.4 Funcao: Consumir Token"))

    sql_text4 = """CREATE OR REPLACE FUNCTION consume_token(
    p_user_id UUID,
    p_target_username TEXT
) RETURNS JSONB AS $$
DECLARE
    v_balance INTEGER;
    v_result JSONB;
BEGIN
    -- Verificar saldo (tokens comprados + bonus)
    SELECT (tokens_stn + tokens_bonus) INTO v_balance
    FROM user_accounts WHERE id = p_user_id;

    IF v_balance <= 0 THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'Saldo insuficiente de Tokens STN'
        );
    END IF;

    -- Debitar primeiro dos tokens bonus, depois dos comprados
    UPDATE user_accounts SET
        tokens_bonus = CASE
            WHEN tokens_bonus > 0 THEN tokens_bonus - 1
            ELSE 0
        END,
        tokens_stn = CASE
            WHEN tokens_bonus > 0 THEN tokens_stn
            ELSE tokens_stn - 1
        END,
        total_consumed = total_consumed + 1,
        last_token_at = now(),
        updated_at = now()
    WHERE id = p_user_id;

    -- Registrar transacao
    INSERT INTO token_transactions (
        user_id, type, amount, target_username, description
    ) VALUES (
        p_user_id, 'consumption', -1,
        p_target_username,
        'Token consumido: desmascarar @' || p_target_username
    );

    RETURN jsonb_build_object('success', true);
END;
$$ LANGUAGE plpgsql;"""
    story.append(code_block(sql_text4))

    # ===================== SECAO 9 =====================
    story.extend(heading1("9. Webhook Stripe: Fluxo de Compra e Consumo"))

    story.append(body(
        "A integracao com o Stripe e o componente critico que conecta o pagamento a liberacao "
        "de Tokens STN na conta do usuario. O fluxo utiliza Stripe Checkout Sessions para "
        "processar o pagamento e webhooks para atualizar o banco de dados de forma confiavel "
        "e idempotente. A idempotencia e essencial porque o Stripe pode enviar o mesmo webhook "
        "multiplas vezes em caso de falha de rede, e o sistema nao deve creditar Tokens duplicados."
    ))

    story.append(heading2("9.1 Fluxo Completo"))

    story.append(body(
        "O fluxo de compra segue uma sequencia linear com garantias de consistencia em cada etapa. "
        "Primeiro, o usuario seleciona um pacote na interface e clica em 'Comprar Tokens'. O "
        "frontend faz uma requisicao ao backend que cria uma Stripe Checkout Session com os dados "
        "do pacote selecionado, incluindo metadata com o user_id e o slug do pacote. O usuario e "
        "redirecionado para a pagina de pagamento do Stripe, que processa o cartao de credito ou "
        "PIX. Apos a confirmacao do pagamento, o Stripe envia um webhook do tipo "
        "'checkout.session.completed' para o endpoint do nosso backend. O backend valida a "
        "assinatura do webhook para garantir autenticidade, extrai o user_id e o package_slug "
        "dos metadados, e atualiza o banco de dados creditando os Tokens na conta do usuario."
    ))

    story.append(heading2("9.2 Implementacao do Webhook Handler"))

    webhook_code = """# webhook_handler.py (FastAPI)
from fastapi import FastAPI, Request, Header
from stripe import WebhookSignature
import os, json
from supabase import create_client

app = FastAPI()
supabase = create_client(os.environ["SUPABASE_URL"],
                         os.environ["SUPABASE_KEY"])

PACKAGE_CONFIG = {
    "starter":   {"tokens": 1,  "bonus": 0, "amount": 24900},
    "squad":     {"tokens": 3,  "bonus": 1, "amount": 59700},
    "war_room":  {"tokens": 10, "bonus": 5, "amount": 149700},
}

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request,
                         stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = WebhookSignature.verify_header(
            payload, stripe_signature,
            os.environ["STRIPE_WEBHOOK_SECRET"],
            tolerance=300
        )
    except Exception:
        return {"status": "invalid"}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        pkg = session["metadata"]["package_slug"]
        cfg = PACKAGE_CONFIG[pkg]

        # Creditar tokens (idempotente via stripe_session_id)
        existing = supabase.table("token_purchases") \\
            .select("id") \\
            .eq("stripe_payment_id", session["payment_intent"]) \\
            .execute()

        if not existing.data:
            supabase.table("token_purchases").insert({
                "user_id": user_id,
                "package_slug": pkg,
                "tokens_granted": cfg["tokens"],
                "tokens_bonus": cfg["bonus"],
                "amount_cents": cfg["amount"],
                "stripe_payment_id": session["payment_intent"],
            }).execute()

            supabase.table("user_accounts").update({
                "tokens_stn": cfg["tokens"],
                "tokens_bonus": cfg["bonus"],
                "first_purchase_at": "now()",
            }).eq("id", user_id).execute()

    return {"status": "ok"}"""
    story.append(code_block(webhook_code))

    # ===================== SECAO 10 =====================
    story.extend(heading1("10. Projecao Financeira"))

    story.append(body(
        "A projecao financeira abaixo estima a receita do modelo de creditos comparado ao "
        "modelo de assinatura, considerando um cenario conservador com 1.000 usuarios ativos "
        "nos primeiros 12 meses. Os numeros sao baseados em benchmarks de plataformas SaaS "
        "com modelo freemium e taxas de conversao de 5-8% para compras avulsas, com ticket "
        "medio de R$ 449 por transacao (media ponderada dos tres pacotes)."
    ))

    story.append(heading2("10.1 Cenario Conservador (12 meses)"))

    fin_data = [
        [
            Paragraph("Metrica", style_table_header),
            Paragraph("Assinatura", style_table_header),
            Paragraph("Creditos (STN)", style_table_header),
        ],
        [
            Paragraph("Usuarios registrados", style_table_cell_left),
            Paragraph("1.000", style_table_cell),
            Paragraph("1.000", style_table_cell),
        ],
        [
            Paragraph("Taxa de conversao", style_table_cell_left),
            Paragraph("3%", style_table_cell),
            Paragraph("8%", style_table_cell),
        ],
        [
            Paragraph("Usuarios pagantes", style_table_cell_left),
            Paragraph("30", style_table_cell),
            Paragraph("80", style_table_cell),
        ],
        [
            Paragraph("Ticket medio", style_table_cell_left),
            Paragraph("R$ 79/mes", style_table_cell),
            Paragraph("R$ 449/compra", style_table_cell),
        ],
        [
            Paragraph("Compras/usuario/ano", style_table_cell_left),
            Paragraph("12 (mensal)", style_table_cell),
            Paragraph("3,2 (recorrente)", style_table_cell),
        ],
        [
            Paragraph("Receita anual", style_table_cell_left),
            Paragraph("R$ 28.440", style_table_cell),
            Paragraph("R$ 114.944", style_table_cell),
        ],
        [
            Paragraph("LTV por usuario pagante", style_table_cell_left),
            Paragraph("R$ 948", style_table_cell),
            Paragraph("R$ 1.437", style_table_cell),
        ],
        [
            Paragraph("ARPU (todos os usuarios)", style_table_cell_left),
            Paragraph("R$ 28,44", style_table_cell),
            Paragraph("R$ 114,94", style_table_cell),
        ],
    ]
    t10 = Table(fin_data, colWidths=[150, 120, 120])
    t10.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Highlight receita
        ('BACKGROUND', (-1, -3), (-1, -3), GREEN_LIGHT),
        ('BACKGROUND', (-1, -2), (-1, -2), BLUE_LIGHT),
    ]))
    story.append(t10)
    story.append(spacer(3))

    story.append(callout(
        "O modelo de creditos gera 4x mais receita que a assinatura no cenario conservador, "
        "com LTV 51% maior por usuario pagante — sem considerar as mecanicas de gamificacao "
        "(insight extra, streak, indicacao) que devem aumentar o numero medio de compras "
        "por usuario para 4-5/ano no cenario realista."
    ))

    # ===================== SECAO 11 =====================
    story.extend(heading1("11. Roadmap de Implementacao"))

    story.append(body(
        "O roadmap abaixo organiza a implementacao do modelo de creditos em 4 sprints de 2 semanas "
        "cada, totalizando 8 semanas (2 meses) para a transicao completa do modelo de assinatura "
        "para o modelo de Tokens STN."
    ))

    roadmap_data = [
        [
            Paragraph("Sprint", style_table_header),
            Paragraph("Periodo", style_table_header),
            Paragraph("Entregaveis", style_table_header),
        ],
        [
            Paragraph("Sprint 1", style_table_cell_bold),
            Paragraph("Semanas 1-2", style_table_cell),
            Paragraph("Schema do banco (user_accounts, token_transactions, token_purchases); "
                      "API de saldo de tokens; Webhook Stripe (checkout.session.completed); "
                      "Testes de integracao com Stripe em modo teste", style_table_cell_left),
        ],
        [
            Paragraph("Sprint 2", style_table_cell_bold),
            Paragraph("Semanas 3-4", style_table_cell),
            Paragraph("Funcao consume_token() no Supabase; Pagina de pacotes de tokens; "
                      "Integracao Stripe Checkout no frontend; Fluxo de compra completo "
                      "end-to-end", style_table_cell_left),
        ],
        [
            Paragraph("Sprint 3", style_table_cell_bold),
            Paragraph("Semanas 5-6", style_table_cell),
            Paragraph("Fog of War: blur nos nomes de alvos; Radar pulsante de ameacas criticas; "
                      "Insight Extra (recompensa variavel); Barra de Nivel de Protecao; "
                      "Contador de Tokens no header", style_table_cell_left),
        ],
        [
            Paragraph("Sprint 4", style_table_cell_bold),
            Paragraph("Semanas 7-8", style_table_cell),
            Paragraph("Mecanica de indicacao (+1 Token); Streak semanal; "
                      "Pacote rotativo de 48h; Dashboard redesenhado; "
                      "Migracao de usuarios assinantes existentes; Testes A/B de copy; "
                      "Deploy em producao", style_table_cell_left),
        ],
    ]
    t11 = Table(roadmap_data, colWidths=[55, 65, 310])
    t11.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GRAY_50, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GRAY_300),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t11)

    # ===================== SECAO 12 =====================
    story.extend(heading1("12. Consideracoes Legais e Eticas"))

    story.append(body(
        "A implementacao de mecanicas de gamificacao em uma plataforma de inteligencia de dados "
        "suscita questoes legais e eticas que devem ser tratadas proativamente. A gamificacao "
        "do acesso a informacoes sobre ameacas discursivas pode ser percebida como exploracao "
        "do medo se nao for conduzida com responsabilidade. E fundamental que o valor entregue "
        "ao usuario seja real e proporcional ao valor cobrado — cada Token deve corresponder a "
        "informacao genuinamente util e verificavel."
    ))

    story.append(heading2("12.1 Compliance com a LGPD"))

    story.append(bullet(
        "<b>Base legal para tratamento de dados:</b> Os comentarios do Instagram sao publicos, "
        "mas a armazenagem sistematica em banco de dados constitui tratamento de dados pessoais "
        "nos termos da LGPD. A base legal recomendada e o 'legitimo interesse' (art. 7, IX), "
        "com balancing test documentado."
    ))
    story.append(bullet(
        "<b>Direito de exclusao:</b> O sistema deve implementar endpoint para que qualquer "
        "usuario mencionado nos dossies possa solicitar a remocao de seus dados, conforme "
        "art. 18 da LGPD."
    ))
    story.append(bullet(
        "<b>Retencao de dados:</b> Definir politica de retencao clara (ex: 90 dias para "
        "comentarios, 1 ano para perfis) e implementar purga automatica."
    ))

    story.append(heading2("12.2 Etica da Gamificacao"))

    story.append(bullet(
        "<b>Transparencia de precos:</b> O valor em reais de cada Token deve ser claramente "
        "exibido em todo momento. A abstracao da moeda nao deve ocultar o custo real."
    ))
    story.append(bullet(
        "<b>Padroes de stub:</b> O Fog of War nao deve criar falsas ameacas para incentivar "
        "compras. Os alertas devem corresponder a ameacas reais detectadas pelo sistema."
    ))
    story.append(bullet(
        "<b>Protecao de vulneraveis:</b> Usuarios em situacao de risco real (ameacas de "
        "morte, violencia domestica) devem ter acesso gratuito e imediato as informacoes, "
        "independentemente de saldo de Tokens."
    ))
    story.append(bullet(
        "<b>Auditoria:</b> O sistema de recompensa variavel (tiers de Insight Extra) deve "
        "ser auditavel, com probabilidades reais alinhadas as declaradas e registro de "
        "todas as distribuicoes."
    ))

    story.append(spacer(8))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY_300, spaceAfter=4*mm))
    story.append(Paragraph(
        "Documento confidencial — uso interno. Nao distribuir sem autorizacao.",
        ParagraphStyle('Footer', fontName='Carlito', fontSize=8, leading=11,
                       textColor=GRAY_500, alignment=TA_CENTER)
    ))

    return story


# -------------------------------------------------------------------
# BUILD PDF
# -------------------------------------------------------------------
def build_pdf():
    output_path = "/home/z/my-project/download/sentinela_democratica_monetizacao_v19.6.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        title="Sentinela Democratica - Estrategia de Monetizacao e Gamificacao v19.6.0",
        author="Equipe Sentinela Democratica",
        subject="Modelo de Creditos (Tokens STN)",
    )

    story = build_content()
    doc.build(story)
    print(f"PDF gerado com sucesso: {output_path}")

    # Verificar tamanho
    size = os.path.getsize(output_path)
    print(f"Tamanho: {size / 1024:.1f} KB")


if __name__ == "__main__":
    build_pdf()
