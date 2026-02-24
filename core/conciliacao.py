import pandas as pd

from . import data_sources, adquirentes, utils

def tentar_conciliar(caminho_banco, caminho_adquirente, catalogo_adquirentes):
    """
    Função chamada sempre que é feito upload de um arquivo.
    Verifica se existem extratos bancarios e arquivos de adquirentes,
    e em caso positivo, chama a função de conciliação.
    """

    if not caminho_banco or not caminho_adquirente:
        return None, None, None
    
    df_banco = data_sources.carregar_extrato_banco(caminho_banco)
    dict_df_adq = data_sources.carregar_extrato_adquirente(caminho_adquirente)

    df_banco, df_adq = preparar_para_conciliar(df_banco, dict_df_adq, catalogo_adquirentes)

    return df_banco, df_adq, conciliar(df_banco, df_adq)


def preparar_para_conciliar(df_banco, dict_df_adquirentes, catalogo_adquirentes):
    """
        Aplica a classificação de adquirentes tanto para o datframe
        do extrato bancário, quanto para o dataframe das adquirentes.
        Utiliza o dataframe do banco e o catalogo para preparar o banco,
        e o dict de adquirentes (contendo df e adquirententes) para pre-
        parar os adquirentes.
    """

    df_banco = adquirentes.aplicar_classificacao_adquirente(df_banco, catalogo_adquirentes)

    dfs_adq = []
    for adquirente, lista_dfs in dict_df_adquirentes.items():
        df = pd.concat(lista_dfs, ignore_index=True)
        dfs_adq.append(utils.setar_adquirente(df, adquirente))
    
    df_adquirente = pd.concat(dfs_adq, ignore_index=True)
    
    return df_banco, df_adquirente


def conciliar(df_banco, df_adquirente):
    """
    Recebe dois dataframes e realiza a conciliação de seus 
    elementos, retornando um dataframe conciliado ao final 
        
    """
    # Criação de colunas Data, Previsto e Deposito
    previsto = df_adquirente.groupby(['Data', 'Adquirente'], as_index=False)['Valor'].sum()
    deposito = df_banco.groupby(['Data', 'Adquirente'], as_index=False)['Valor'].sum()
    df_conciliado = pd.merge(previsto, deposito, on=['Data', 'Adquirente'], how='outer', suffixes=(' Previsto', ' Deposito'))
    df_conciliado.rename(inplace=True, columns={'Valor Previsto': 'Previsto', 'Valor Deposito': 'Deposito'})
    df_conciliado['Previsto'] = df_conciliado['Previsto'].round(2)
    df_conciliado['Deposito'] = df_conciliado['Deposito'].round(2)

    # Criação de coluna Saldo Conciliação
    df_conciliado['Saldo Conciliação'] = df_conciliado['Deposito'].fillna(0) - df_conciliado['Previsto'].fillna(0)
    # Criação de coluna Status
    df_conciliado['Status'] = 'Divergente'
    
    # Conciliação - se saldo for 0, conciliar
    df_conciliado.loc[df_conciliado['Saldo Conciliação'] == 0, 'Status'] = 'Conciliado'

    # Caso não hajam dados em uma das partes, printar (Tratar futuramente)
    df_conciliado.loc[pd.isna(df_conciliado['Previsto']) | pd.isna(df_conciliado['Deposito']), 'Status'] = 'Sem Dados'


    return df_conciliado

