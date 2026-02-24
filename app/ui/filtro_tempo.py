import streamlit as st

def render_filtro_periodo(df):
    """
    Renderiza a estrutura que realiza o filtro por período de tempo, alterando o 
    st.session_state. Recebe as datas de um dataframe (a princípio, extrato bancário).

    Args: df (dataframe)
    """

    # Definir maximo e minimo, e preenchimento do 1° session_state
    data_min = df["Data"].min()
    data_max = df["Data"].max()
    if "periodo" not in st.session_state:
        st.session_state["periodo"] = (data_min, data_max)

    # Resetar o periodo para a data mínima e máxima possível
    def reset_periodo():
        st.session_state.periodo = (data_min, data_max)
        st.session_state["limpar_selecao_conciliacao"] = True

    # Estrutura do filtro
    with st.form("filtro_periodo"):
        data_inicial, data_final = st.date_input(
            format="DD/MM/YYYY",
            label="Período",
            min_value=data_min,
            max_value=data_max,
            key="periodo",
        )
        col_aplicar, col_limpar = st.columns([1,1])
        aplicar = col_aplicar.form_submit_button("Aplicar período")
        col_limpar.form_submit_button("Limpar período", on_click=reset_periodo)

        if aplicar:
            st.session_state["limpar_selecao_conciliacao"] = True
