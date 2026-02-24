import pandas as pd
import re 
from pathlib import Path

def txt_collumn_to_dataframe(caminho_arquivo_entrada):
    def pega_campo(linha, colunas):
        """
            Pega informação de um determinado campo.
            colunas = [ini, fim]
        """
        return linha[colunas[0]-1:colunas[1]]

    PADRAO_DATA  = re.compile(r'^\s*\d{2}/\d{2}/\d{4}\b')
    PADRAO_VALOR = re.compile(r'\d{1,3}(?:\.\d{3})*,\d{2}\s+[CD]\b')
    PADRAO_CONT  = re.compile(r'^[ ]{30}\S')

    COLUNAS_DATA = (4, 14)
    COLUNAS_AGENCIA = (37, 41)
    COLUNAS_LOTE = (51, 56)
    COLUNAS_HISTORICO = (61, 85)
    COLUNAS_DOCUMENTO = (97, 115)
    COLUNAS_VALOR = (121, 130)
    COLUNAS_C_OU_D = (131, 132)

    with open(caminho_arquivo_entrada, 'r', encoding='latin-1') as f:
        linhas = f.readlines()

    linhas_filtradas = []
    ultima = None 

    for linha in linhas:
        linha = linha.rstrip('\n')

        if PADRAO_DATA.search(linha) and PADRAO_VALOR.search(linha):
            data      = pega_campo(linha, COLUNAS_DATA).strip()
            historico = pega_campo(linha, COLUNAS_HISTORICO).strip()

            if pega_campo(linha, COLUNAS_C_OU_D).strip() == "D":
                valor = "-" + pega_campo(linha, COLUNAS_VALOR).strip()
            elif pega_campo(linha, COLUNAS_C_OU_D).strip() == "C":
                valor = pega_campo(linha, COLUNAS_VALOR).strip()
            else:
                valor = pega_campo(linha, COLUNAS_VALOR).strip()

            transacao = {
                'Data': data,
                'Descricao': historico,
                'Valor': valor
            }

            linhas_filtradas.append(transacao)
            ultima = transacao 
            continue

        if PADRAO_CONT.match(linha) and ultima is not None:
            trecho = linha[30:].strip()
            if trecho:
                ultima['Descricao'] = ultima['Descricao'] + "" + trecho

    dataframe = pd.DataFrame(linhas_filtradas)

    dataframe = dataframe[~dataframe['Descricao'].astype(str).str.contains('SALDO ANTERIOR', case=False, na=False)]

    return dataframe


def convert_multiple_collumntxt(directory_path):
    extratos = []

    for path in Path(directory_path).iterdir():
        if path.is_file():
            extratos.append(txt_collumn_to_dataframe(path)) 

    extratos_unificados = pd.concat(extratos, ignore_index=True)

    return extratos_unificados



if __name__ == '__main__':
    caminho_arquivo_entrada = r'extratos\txt_collumn\extrato (10).txt'

    print(txt_collumn_to_dataframe(caminho_arquivo_entrada))