import streamlit as st

def render_opcoes(empresas):
    """
    Recebe dados das empresas vindos do json, e renderiza
    um selecionador de empresas, que altera o session_state

    Args: empresas(list) --> [{'nome': '', 'id': ''}, ...]
    Returns: -
    """
    
    def resetar_chaves_session_state():
        # Limpar a selecao do modal
        st.session_state["limpar_selecao_conciliacao"] = True

        keys = [
            'periodo', "uploader_banco", "uploads_adq_prontos", 
            "tratar_arquivo_banco", "tratar_arquivo_adquirente",
            "catalogo_adquirentes", "dia_selecionado",
            "mostrar_modal", "adquirente_filtro", "catalogo_msg",
            "editar_adquirente", "editar_adquirente_pending",
            "palavras_edicao", "palavras_edicao_pending"
            ]
        for key in keys:
            st.session_state.pop(key, None)

    selecionado = st.selectbox(
        label='Empresa',
        options= empresas,
        format_func= lambda x: x['nome'],
        key='empresa_selecionada',
        on_change=resetar_chaves_session_state,
    )

    return selecionado
