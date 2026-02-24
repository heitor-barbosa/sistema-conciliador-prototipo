import pandas as pd
from core import utils

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, KeepTogether, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
import io
from datetime import datetime

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker


def calcular_totais(df_visivel):
    """
    Calcula os valores totais com base no dataframe visivel atual
    e retorna um dicionario (para ser salvo no st.session_state)
    """
    # Converter colunas para numerico para poder somar
    prev = pd.to_numeric(df_visivel['Previsto'], errors='coerce').fillna(0)
    dep = pd.to_numeric(df_visivel['Deposito'], errors='coerce').fillna(0)
    saldo = pd.to_numeric(df_visivel['Saldo Conciliação'], errors='coerce').fillna(0)

    dados_totais = {
        "total_prev": utils.formato_brl(prev.sum()),
        "total_dep":  utils.formato_brl(dep.sum()),
        "total_diff": utils.formato_brl(saldo.sum()),
        "n_total":  int(len(df_visivel)),
        "n_conc":   int((df_visivel.get("Status","") == "Conciliado").sum()) if "Status" in df_visivel.columns else 0,
        "n_div":    int((df_visivel.get("Status","") == "Divergente").sum()) if "Status" in df_visivel.columns else 0,
        "n_sem":    int((df_visivel.get("Status","") == "Sem Dados").sum())   if "Status" in df_visivel.columns else 0,
    }

    return dados_totais


def gerar_dataframe_resumo(df_visivel):
    """
    Gera dataframe de resumo com base no dataframe visivel atual
    Data | Previsto | Depósito | Saldo conciliacao | Status | 
    """

    # Converter coluna data para datetime para agrupar
    df_visivel['Data'] = pd.to_datetime(df_visivel['Data'], errors='coerce')
    # Garantir conversão de colunas numericas para agrupar
    df_visivel['Previsto'] = pd.to_numeric(df_visivel['Previsto'], errors="coerce")
    df_visivel['Deposito'] = pd.to_numeric(df_visivel['Deposito'], errors="coerce")
    df_visivel['Saldo Conciliação'] = pd.to_numeric(df_visivel['Saldo Conciliação'], errors="coerce")

    # Criação das colunas utilizadas para o agrupamento
    df_visivel['Ano'] = df_visivel['Data'].dt.year
    df_visivel['MesNum'] = df_visivel['Data'].dt.month

    # Agrupar dados por ano e mês
    df_resumo = (
        df_visivel.groupby(['Ano', 'MesNum'], as_index=False).agg(
            Previsto = ('Previsto', 'sum'),
            Deposito = ('Deposito', 'sum'),
            Saldo = ('Saldo Conciliação', 'sum'),
            Dias = ('Data', 'size'),
            Conciliado=("Status", lambda s: (s == "Conciliado").sum()),
            Divergente=("Status", lambda s: (s == "Divergente").sum()),
            SemDados=("Status", lambda s: (s == "Sem Dados").sum())
        )
    )
    df_resumo['Previsto'] = df_resumo['Previsto'].round(2)
    df_resumo['Deposito'] = df_resumo['Deposito'].round(2)
    df_resumo['Saldo'] = df_resumo['Saldo'].round(2)

    df_resumo['Dias'] = df_resumo['Dias'].astype(int)
    df_resumo['Conciliado'] = df_resumo['Conciliado'].astype(int)
    df_resumo['Divergente'] = df_resumo['Divergente'].astype(int)
    df_resumo['% Conciliado'] = ((100 * df_resumo['Conciliado']) / df_resumo['Dias']).astype(int)

    return df_resumo


def gerar_pdf_resumo(df_resumo, nome_empresa):
    """
    Gera os bytes do pdf de resumo estilizado da conciliacao 
    atual, com base no dataframe de resumo gerado 
    """
    def draw_header(canvas, doc, empresa="Minha Empresa", logo_path=None, subtitulo="Relatório de Conciliação Retroativo"):
        canvas.saveState()
        # Área do cabeçalho (topo da página)
        x_left = doc.leftMargin
        y_top  = doc.pagesize[1] - 0.7*cm

        # Logo 
        if logo_path:
            try:
                logo_w, logo_h = 2.2*cm, 2.2*cm
                canvas.drawImage(logo_path, x_left, y_top - logo_h + 0.8*cm, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                text_x = x_left + logo_w + 0.5*cm
            except Exception:
                text_x = x_left
        else:
            text_x = x_left

        # Configurações do pdf
        if doc.page == 1:
            canvas.setTitle("Resumo - Sistema Conciliador")
            canvas.setAuthor("Sistema Conciliador")
            canvas.setSubject("Resumo de conciliação")
            canvas.setCreator("Sistema Conciliador")

        # Nome da empresa e subtítulo/data
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.HexColor("#375623"))
        canvas.drawString(text_x, y_top - 0.2*cm, empresa)

        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.black)
        canvas.drawString(text_x, y_top - 0.7*cm, subtitulo)

        hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, y_top - 0.2*cm, f"Gerado em: {hoje}")

        # Linha separadora
        canvas.setStrokeColor(colors.HexColor("#C4D79B"))
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, y_top - 1.2*cm, doc.pagesize[0] - doc.rightMargin, y_top - 1.2*cm)

        canvas.restoreState()


    # ================ ESTILOS ===============
    estilo_tabela = TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C4D79B')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Linhas zebradas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F9F1')]),
        
        # Linha total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#C4D79B')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # Centralizar colunas da tabela
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (4, 1), (8, -1), 'CENTER'),
    ])

    estilo_subtitulo = ParagraphStyle(
        name="TituloAno",
        fontName="Helvetica-Bold",         # fonte negrito
        fontSize=14,                       # tamanho do texto
        textColor=colors.HexColor("#375623"),  # verde escuro (contrasta bem com #C4D79B)
        alignment=0,                       # centralizado (0=esquerda, 1=centro, 2=direita)
        spaceBefore=12,                    # espaço acima do título
        spaceAfter=6,                      # espaço abaixo
        leading=16,                        # altura da linha (um pouquinho maior que a fonte)
        borderPadding=(6, 6, 6, 6),        # "respiro" interno no fundo colorido
        borderRadius=4                     # bordas arredondadas (só decorativo)
    )

    estilo_titulo = ParagraphStyle(
        name="TituloPrincipal",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#375623 "),
        alignment=1,  # 1 = centralizado
        spaceAfter=18
    )
    # ================ ESTILOS ===============


    # Construindo elementos do PDF
    elementos = []

        # Titulo com nome da empresa selecionada
    elementos.append(Paragraph(f'Conciliação Retroativa - {nome_empresa}', estilo_titulo))
    elementos.append(Spacer(1, 0.5*cm))

        # CARDS DE RESUMO (GERAL E POR ANO) 
    elementos.append(Paragraph("Resumo Geral da Conciliação", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3 * cm))

    # === CARD GERAL (total de todos os anos) ===
    total_prev = df_resumo["Previsto"].sum()
    total_dep  = df_resumo["Deposito"].sum()
    total_saldo = df_resumo["Saldo"].sum()

    dados_geral = [
        ["Previsto (R$)", "Depósito (R$)", "Saldo Conciliação (R$)"],
        [
            utils.formato_brl(total_prev),
            utils.formato_brl(total_dep),
            utils.formato_brl(total_saldo)
        ]
    ]

    tabela_geral = Table(dados_geral, colWidths=[6 * cm, 6 * cm, 6 * cm])
    tabela_geral.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C4D79B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#C4D79B")),
    ]))
    elementos.append(tabela_geral)
    elementos.append(Spacer(1, 0.5 * cm))


    # === CARDS POR ANO ===
    elementos.append(Paragraph("Totais Anuais", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3 * cm))

    cards_ano = []
    for ano, df_ano in df_resumo.groupby("Ano"):
        prev_ano = utils.formato_brl(df_ano["Previsto"].sum())
        dep_ano = utils.formato_brl(df_ano["Deposito"].sum())
        saldo_ano = utils.formato_brl(df_ano["Saldo"].sum())

        card = Table(
            [
                [f"{ano}"],
                [f"Previsto: {prev_ano}"],
                [f"Depósito: {dep_ano}"],
                [f"Saldo: {saldo_ano}"]
            ],
            colWidths=[6 * cm]
        )
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C4D79B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#C4D79B")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F9F1')]),
        ]))
        cards_ano.append(card)

    # Agrupa os cards em linhas de 3 por linha
    linhas = [cards_ano[i:i + 3] for i in range(0, len(cards_ano), 3)]
    tabela_cards_anos = Table(linhas, colWidths=[6 * cm] * 3)
    tabela_cards_anos.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elementos.append(tabela_cards_anos)
    elementos.append(Spacer(1, 0.8 * cm))

        # Tabelas de cada ano
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph("Resumo Anual Detalhado", estilo_subtitulo))

    contador = 0
    for ano, df_ano in df_resumo.groupby("Ano"):     # (2021, dataframe_2021)

        # Calculo do total de cada ano
        previsto_total = df_ano['Previsto'].sum()
        deposito_total = df_ano['Deposito'].sum()
        previsto_total = utils.formato_brl(previsto_total)
        deposito_total = utils.formato_brl(deposito_total)

        # Adicao da linha de total
        linha_total = {
            "MesNum": "Total",
            "Previsto": df_ano['Previsto'].sum(),
            "Deposito": df_ano['Deposito'].sum(),
            "Saldo": df_ano['Saldo'].sum(),
            "Dias": int(df_ano["Dias"].sum()),
            "Conciliado": int(df_ano["Conciliado"].sum()),
            "Divergente": int(df_ano["Divergente"].sum()),
            "SemDados": int(df_ano["SemDados"].sum()),
            "% Conciliado": int(round(df_ano['Conciliado'].sum()/df_ano['Dias'].sum() * 100))
        }
        df_ano = pd.concat([df_ano, pd.DataFrame([linha_total])], ignore_index=True)

        # Construção das tabelas
        df_ano = df_ano.drop('Ano', axis=1)
        df_ano = df_ano.rename(columns={
            "MesNum": "Mês",
            "Previsto": "Previsto (R$)",
            "Deposito": "Depósito (R$)",
            "Saldo": "Saldo\nConciliação",
            "Dias": "Total\nde Dias",
            "Conciliado": "Dias\nConciliados",
            "Divergente": "Dias\nDivergentes",
            "SemDados": "Dias\nSem dados",
            "% Conciliado": "Percentual de\nConciliação"
        })
            # versão reduzida da tabela
        df_ano = df_ano.drop('Total\nde Dias', axis=1)
        df_ano = df_ano.drop('Dias\nSem dados', axis=1)
        larguras_colunas = [
            1.8*cm,   # Mês
            3.2*cm,   # Previsto (R$)
            3.2*cm,   # Depósito (R$)
            3.2*cm,   # Saldo Conciliação
            2.4*cm,   # Dias Conciliados
            2.4*cm,   # Dias Divergentes
            2.4*cm,   # Percentual de Conciliação
        ]
            # Formatação das colunas numéricas
        larguras_colunas_versao_total = [1.2*cm, 3.0*cm, 3.0*cm, 3.0*cm, 1.2*cm, 2.1*cm, 2.1*cm, 2.1*cm, 2.5*cm]
        
        colunas_fmt = ["Previsto (R$)", "Depósito (R$)", "Saldo\nConciliação"]
        for col in colunas_fmt:
            df_ano[col] = df_ano[col].apply(utils.formato_brl)
        
        df_ano["Percentual de\nConciliação"] = df_ano["Percentual de\nConciliação"].apply(
            lambda v: f"{int(v)}%" if pd.notnull(v) else ""
        )

        # Criação da tabela
        dados_por_ano = [df_ano.columns.tolist()] + df_ano.to_numpy(dtype=object).tolist()
        tabela = Table(dados_por_ano, colWidths=larguras_colunas)                                                                   
        tabela.setStyle(estilo_tabela)

        bloco = KeepTogether([Paragraph(f'{ano}', estilo_subtitulo), tabela])
        elementos.append(bloco)

        # A cada duas tabelas, mudar de pagina
        contador += 1
        if contador % 2:
            elementos.append(PageBreak())
        else:
            elementos.append(Spacer(1, 2*cm))
    

    # Criação do buffer e do documento base
    buffer = io.BytesIO()                                                                  
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=3*cm, bottomMargin=1.5*cm)             

    header_fn = lambda c, d: draw_header(c, d, empresa="Sistema Conciliador", logo_path="img/sc.png")
    doc.build(elementos, onFirstPage=header_fn, onLaterPages=header_fn)            
    buffer.seek(0)

    return buffer.getvalue()      # Retornar bytes do PDF







