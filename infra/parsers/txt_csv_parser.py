import pandas as pd
from pathlib import Path

def txt_csv_to_dataframe(caminho_arquivo):

    # Colunas Arquivo: [Conta, Data_Mov, Nr_Doc, Historico, Valor, Deb_Cred]
    # Colunas Desejadas: [Data, Descricao, Valor]

    dataframe = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1', header=None)

    # Formatar data
    dataframe['Data_Mov'] = (
        pd.to_datetime(dataframe['Data_Mov'].astype(str), format='%Y%m%d', errors='coerce')
        .dt.strftime('%d/%m/%Y')
    )

    # Unificando colunas Valor e Deb_Cred
    valor = pd.to_numeric(dataframe['Valor'], errors='coerce')
    sinal = dataframe['Deb_Cred'].str.upper().map({'C': 1, 'D': -1}).fillna(1)
    dataframe['Valor'] = valor * sinal

    # Deletando colunas indesejadas, e renomeando
    dataframe = dataframe.drop(columns=['Conta', 'Nr_Doc', 'Deb_Cred'])
    dataframe = dataframe.rename(columns={'Data_Mov': 'Data', 'Historico': 'Descricao'})

    return dataframe


def convert_multiple_csv(directory_path):
    extratos = []

    for path in Path(directory_path).iterdir():
        if path.is_file():
            extratos.append(txt_csv_to_dataframe(path)) 

    extratos_unificados = pd.concat(extratos, ignore_index=True)

    return extratos_unificados


def bbt_to_dataframe(caminho_arquivo):
    # Colunas Arquivo: [? | ? | ? | data | data | ? | ? | ? | ? | descrição | valor | C ou D | detalhes]

    dataframe = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1', header=None, dtype=str)

    # RENOMEAR COLUNAS
    dataframe = dataframe.rename(columns={
        3: 'Data1',
        4: 'Data2',
        9: 'Descrição',
        10: 'Valor',
        11: 'C ou D',
        12: 'Detalhes'
    })

    # CONVERTE AS COLUNAS DE DATAS
    dataframe['Data1'] = pd.to_datetime(dataframe['Data1'].astype(str), format='%d%m%Y', errors='coerce').dt.date
    dataframe['Data2'] = pd.to_datetime(dataframe['Data2'].astype(str), format='%d%m%Y', errors='coerce').dt.date

    # COLOCA VALORES COM CENTAVOS // SINAL NOS NUMEROS
    dataframe['Valor'] = pd.to_numeric(dataframe['Valor'], errors="coerce") / 100
    dataframe.loc[dataframe['C ou D'] == 'D', 'Valor'] *= -1

    # TIRA PRIMEIRA E ULTIMA LINHA
    dataframe = dataframe.drop([dataframe.index[0], dataframe.index[-1]])

    return dataframe

def convert_multiple_bbt(directory_path):
    extratos = []

    for path in Path(directory_path).iterdir():
        if path.is_file() and path.suffix.lower() == ".bbt":
            extratos.append(bbt_to_dataframe(path)) 

    extratos_unificados = pd.concat(extratos, ignore_index=True)

    return extratos_unificados

    
if __name__ == '__main__':
    caminho_entrada = r'extratos\lamartine'
    df = convert_multiple_bbt(caminho_entrada)
    # df = bbt_to_dataframe(r'extratos\lamartine\Extrato3115152900 (2).bbt')
    df.to_excel('saida2.xlsx', index=False)
    
    

    