import streamlit as st

from core import adquirentes



def render_gerenciador_catalogo(catalogo_adquirentes, empresa_id):
    """
    Acessa o catalogo de adquirentes da empresa, e
    renderiza o gerenciador de adquirentes desse catalogo.

    Args: 
    Returns: -
    """

    if not catalogo_adquirentes:
        st.warning("Não há adquirentes cadastradas. Cadastre pelo menos uma para usar o filtro.")
    mensagem_catalogo = st.session_state.pop("catalogo_msg") if "catalogo_msg" in st.session_state else None
    if mensagem_catalogo:
        st.success(mensagem_catalogo)

    # Sinalizadores usados para ajustar a seleção após ações de formulário
    if "editar_adquirente_pending" in st.session_state:
        st.session_state["editar_adquirente"] = st.session_state.pop("editar_adquirente_pending")
    if "palavras_edicao_pending" in st.session_state:
        st.session_state["palavras_edicao"] = st.session_state.pop("palavras_edicao_pending")

    def limpar_selecao_grid_conciliacao():
        st.session_state['limpar_selecao_conciliacao'] = True

    def _atualizar_palavras_edicao():
        limpar_selecao_grid_conciliacao()
        selecionado = st.session_state.get("editar_adquirente")
        if not selecionado:
            return
        st.session_state["palavras_edicao"] = "\n".join(catalogo_adquirentes.get(selecionado, []))

    
    with st.popover("Gerenciar Adquirentes"):
        col_editar, col_adicionar = st.columns(2)

        with col_editar:
            st.markdown("**Editar adquirente existente**")
            if catalogo_adquirentes:
                nomes_adquirentes = sorted(catalogo_adquirentes.keys())

                if st.session_state.get("editar_adquirente") not in nomes_adquirentes:
                    st.session_state["editar_adquirente"] = nomes_adquirentes[0]
                    st.session_state["palavras_edicao"] = "\n".join(
                        catalogo_adquirentes[st.session_state["editar_adquirente"]]
                    )

                if "palavras_edicao" not in st.session_state:
                    st.session_state["palavras_edicao"] = "\n".join(
                        catalogo_adquirentes[st.session_state["editar_adquirente"]]
                    )

                st.selectbox(
                    "Adquirente",
                    nomes_adquirentes,
                    key="editar_adquirente",
                    on_change=_atualizar_palavras_edicao,
                )

                with st.form("form_editar_catalogo"):
                    st.text_area(
                        "Palavras-chave (uma por linha)",
                        height=150,
                        key="palavras_edicao",
                    )
                    col_salvar, col_remover = st.columns(2)
                    salvar = col_salvar.form_submit_button("Salvar alterações")
                    remover = col_remover.form_submit_button("Remover adquirente")
                    if salvar:
                        selecionado = st.session_state.get("editar_adquirente")
                        texto_palavras = st.session_state.get("palavras_edicao", "")
                        novas_palavras = [linha.strip() for linha in texto_palavras.splitlines() if linha.strip()]
                        if not novas_palavras:
                            st.warning("Informe ao menos uma palavra-chave.")
                        else:
                            catalogo_atualizado = dict(catalogo_adquirentes)
                            catalogo_atualizado[selecionado] = novas_palavras
                            adquirentes.save_adquirente_catalog(empresa_id, catalogo_atualizado)
                            st.session_state["palavras_edicao_pending"] = "\n".join(novas_palavras)
                            st.session_state["catalogo_msg"] = f"Palavras-chave de '{selecionado}' atualizadas."
                            st.rerun()
                    elif remover:
                        catalogo_atualizado = dict(catalogo_adquirentes)
                        selecionado = st.session_state.get("editar_adquirente")
                        if selecionado in catalogo_atualizado:
                            catalogo_atualizado.pop(selecionado)
                        if not catalogo_atualizado:
                            st.error("Não é possível remover o último adquirente. Cadastre outro antes de prosseguir.")
                            st.stop()
                        adquirentes.save_adquirente_catalog(empresa_id, catalogo_atualizado)
                        proximo = sorted(catalogo_atualizado.keys())[0]
                        st.session_state["editar_adquirente_pending"] = proximo
                        st.session_state["palavras_edicao_pending"] = "\n".join(catalogo_atualizado[proximo])
                        st.session_state["catalogo_msg"] = f"Adquirente '{selecionado}' removido."
                        st.rerun()
            else:
                st.info("Ainda não há adquirentes cadastrados.")

        with col_adicionar:
            st.markdown("**Adicionar novo adquirente**")
            with st.form("form_adicionar_catalogo"):
                novo_nome = st.text_input("Nome do adquirente")
                novas_palavras_texto = st.text_area("Palavras-chave (uma por linha)", height=150)
                adicionar = st.form_submit_button("Adicionar adquirente")
                if adicionar:
                    st.session_state["limpar_selecao_conciliacao"] = True
                    nome_limpo = novo_nome.strip()
                    palavras_lista = [linha.strip() for linha in novas_palavras_texto.splitlines() if linha.strip()]
                    if not nome_limpo:
                        st.warning("Informe um nome válido.")
                    elif nome_limpo in catalogo_adquirentes:
                        st.warning("Já existe um adquirente com esse nome.")
                    elif not palavras_lista:
                        st.warning("Adicione ao menos uma palavra-chave.")
                    else:
                        catalogo_atualizado = dict(catalogo_adquirentes)
                        catalogo_atualizado[nome_limpo] = palavras_lista
                        adquirentes.save_adquirente_catalog(empresa_id, catalogo_atualizado)
                        st.session_state["catalogo_msg"] = f"Adquirente '{nome_limpo}' adicionado."
                        st.session_state["editar_adquirente_pending"] = nome_limpo
                        st.session_state["palavras_edicao_pending"] = "\n".join(palavras_lista)
                        st.rerun()
    