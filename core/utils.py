import pandas as pd
from datetime import date, datetime

def formato_brl(valor):
    if pd.isna(valor):
        return ''
    if abs(valor) < 1e-6:
        return f'R$ 0,00'
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def formato_data(valor):
    if pd.isna(valor):
        return ""
    if isinstance(valor, pd.Timestamp):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)

def unify_dataframes(dataframes):
    """
        Args:
            dataframes (list): lista de dataframes a serem concatenados
    """
    unified_df = pd.concat(dataframes, ignore_index=True)

    # Converter coluna "valor" para numérico
    unified_df['Valor'] = (
        unified_df['Valor']
        .astype(str)
        .str.replace('.', '', regex=False)   # tira separador de milhar
        .str.replace(',', '.', regex=False)  # troca vírgula por ponto
        .pipe(pd.to_numeric, errors='coerce')
    )

    # Converter coluna "Data" para datetime
    unified_df['Data'] = pd.to_datetime(unified_df['Data'], dayfirst=True, errors='coerce').dt.date

    # Ordenar valores por data
    unified_df = unified_df.sort_values(by='Data')
    
    return unified_df

def positive_values_dataframe(dataframe):
    dataframe = dataframe[dataframe['Valor'] >= 0]
    return dataframe

def setar_adquirente(df: pd.DataFrame, adquirente: str) -> pd.DataFrame:
    """
    Recebe um dataframe de extratos de adquirentes, e define a adquirente (seta a coluna "Adquirentes").
    """
    df['Adquirente'] = adquirente
    return df

def converter_tamanho_arquivo(tamanho_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if tamanho_bytes < 1024:
            return f"{tamanho_bytes:.1f} {unit}"
        tamanho_bytes /= 1024
    return f"{tamanho_bytes:.1f} TB"

def formatar_data_e_hora(ts):
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")