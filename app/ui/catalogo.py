import streamlit as st
from core import adquirentes


def render_catalogo_adquirentes(empresa_id: str):
    """
    Renderiza o catálogo de adquirentes (puxa do json), 
    alterando o st.session_state quando um é selecionado.

    Args: empresa_id (str)
    """    
    def limpar_selecao_grid_conciliacao():
        st.session_state['limpar_selecao_conciliacao'] = True

    adquirentes_atuais = adquirentes.load_adquirente_catalog(empresa_id)

    if 'adquirente_filtro' not in st.session_state:
        st.session_state['adquirente_filtro'] = None

    opcoes = list(adquirentes_atuais.keys()) + ['Outros']
    if opcoes:
        adquirente_selecionada = st.segmented_control(
            label='Adquirentes',
            options=opcoes,
            key='adquirente_filtro',
            on_change=limpar_selecao_grid_conciliacao
        )
        
