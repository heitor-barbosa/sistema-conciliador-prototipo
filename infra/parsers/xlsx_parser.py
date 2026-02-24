import pandas as pd
from pandas.api import types as ptypes
from pathlib import Path


def validar_extrato(arquivo, tipo):
    """
    Recebe os bytes do arquivo e seu tipo,
    e valida as colunas para saber se é o
    formato esperado. Retorna lista com as
    colunas faltantes.
    
    :param arquivo: conteudo do arquivo (bytes)
    :param tipo: banco, adq (str)
    """
    df = pd.read_excel(arquivo, nrows=0)
    colunas = set(df.columns)
    
    if tipo == 'banco':
        colunas_obrigatorias = ['Data', 'Descricao', 'Valor']
    elif tipo == 'adq':
        colunas_obrigatorias = ['Data Pagamento', 'Produto', 'Valor Liquido']

    # colunas_faltando = []
    # for col in colunas_obrigatorias:
    #     if col not in colunas:
    #         colunas_faltando.append(col)
            
    colunas_faltando = [col for col in colunas_obrigatorias if col not in colunas]

    return colunas_faltando


def xlsx_to_dataframe(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, usecols=['Data', 'Descricao', 'Valor'])
    # df = df.rename(columns={'DESCRIÇÃO': 'Descricao', 'DATA': 'Data', 'VALOR': 'Valor'})

    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce').dt.date
    df.sort_values("Data", inplace=True)

    return df    


def adquirente_xlsx_to_dataframe(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, usecols=['Data Pagamento', 'Produto', 'Valor Liquido'])
    df = df.rename(columns={'Data Pagamento': 'Data', 'Produto': 'Descricao', 'Valor Liquido': 'Valor'})
    
    # Tratar formatos que a data vem (if: ja vem como data; else: numerico ou string)
    if ptypes.is_datetime64_any_dtype(df['Data']) or ptypes.is_datetime64tz_dtype(df['Data']):
        datas = pd.to_datetime(df['Data'], errors='coerce')
    else:
        num = pd.to_numeric(df['Data'], errors='coerce')
        mask_num = num.notna()
        datas = pd.Series(pd.NaT, index=df.index, dtype='datetime64[ns]')
        datas[mask_num] = pd.to_datetime(num[mask_num], origin='1899-12-30', unit='D', errors='coerce')
        datas[~mask_num] = pd.to_datetime(df.loc[~mask_num, 'Data'], dayfirst=True, errors='coerce')

    df['Data'] = datas.dt.date
    df.sort_values('Data', inplace=True)

    return df
