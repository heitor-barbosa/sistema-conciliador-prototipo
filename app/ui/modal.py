import streamlit as st
from datetime import datetime

from .grids import render_extratos


@st.dialog("Detalhes")
def render_detalhes(linha_selecionada, df_extrato_base, df_adquirente_base):
    """ linha_selecionada (Dataframe) - Data | Adquirente | Previsto | Deposito | Saldo Conciliação | Status """

    st.markdown(
    """
    <style>
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 95vw;
        max-width: 95vw;
    }    
    </style>
    """,
    unsafe_allow_html=True,
    )

    # Pegar data e adquirente da linha clicada
    data_selecionada = linha_selecionada['Data'].iat[0]
    data_selecionada = datetime.strptime(data_selecionada, '%Y-%m-%d').date()

    adquirente_selecionada = linha_selecionada['Adquirente'].iat[0]

    # Criar mascara booleana e aplicar para filtrar por data e adquirente
    mask_banco = ((df_extrato_base['Data'] == data_selecionada) & (df_extrato_base['Adquirente'] == adquirente_selecionada))
    df_extrato_filtrado = df_extrato_base.loc[mask_banco]

    mask_adquirente = ((df_adquirente_base['Data'] == data_selecionada) & (df_adquirente_base['Adquirente'] == adquirente_selecionada))
    df_adquirente_filtrado = df_adquirente_base.loc[mask_adquirente]

    # Dataframes de extrato bancario e adquirente
    left, _, right = st.columns([49, 1, 49])

    with left:
        st.subheader("Extrato Bancário")
        render_extratos(df_extrato_filtrado)

    with right:
        st.subheader("Extrato Adquirente")
        render_extratos(df_adquirente_filtrado)

