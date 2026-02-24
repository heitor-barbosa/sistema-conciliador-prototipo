import streamlit as st
from core import empresas, audit_logger
import pandas as pd


def render_gerenciador_empresas(opcoes_empresas, is_admin: bool = False):
    """
    Recebe dados das empresas vindos do json, 
    e renderiza o gerenciador de empresas, 
    que altera o json conforme necessario
    
    :param opcoes_empresas: (list) [{'nome': , 'id': }, ... {}]
    :param is_admin: (bool)
    """
    @st.dialog('Atenção!')
    def dialog_excluir_empresa(empresa_selecionada):
        st.warning(f'Todos os dados da empresa {empresa_selecionada["nome"]} serão excluídos permanentemente! Tem certeza que deseja continuar?')
        b1, b2 = st.columns(2)
        if b1.button('Confirmar exclusão', type='primary'):
            empresas.remover_empresa(empresa_selecionada['nome'])
            audit_logger.registrar_acao(
                usuario=st.session_state.get('username'),
                acao='Empresa Excluida',
                alvo={'empresa': empresa_selecionada['nome']}
            )
            st.rerun()
        if b2.button('Cancelar'):
            st.rerun()


    col_editar, divider, col_criar_nova = st.columns([1, 0.02, 1])

    with col_editar:
        st.text('Editar Empresa')
        empresa_selecionada = st.selectbox(options=opcoes_empresas, label='Empresa', format_func=lambda e: e['nome'], key='empresa_selecionada_gerenciador')
        
        col_btn_editar, col_btn_excluir = st.columns(2)
        with col_btn_editar:
            if st.button('Editar Empresa'):
                st.session_state['mostrar_form_editar_empresa'] = True

            if st.session_state.get('mostrar_form_editar_empresa'):
                with st.form('editar_empresa'):
                    nome_empresa = st.text_input(label='Alterar Nome', value=empresa_selecionada['nome'])
                    c1, c2 = st.columns(2)
                    with c1:
                        enviado_form_editar = st.form_submit_button(label='Salvar')
                    with c2:
                        cancelar_form_editar = st.form_submit_button(label='Cancelar')
                
                if enviado_form_editar:
                    sucesso = empresas.editar_empresa(empresa_selecionada['nome'], nome_empresa.strip())
                    if not sucesso:
                        st.warning('Não foi possível Salvar. (Já existe uma empresa com esse nome, ou contém símbolos)')
                    else:
                        audit_logger.registrar_acao(
                            usuario=st.session_state.get('username'), 
                            acao='Empresa Editada', 
                            alvo={'empresa': empresa_selecionada['nome'].strip(), 'novo_nome': nome_empresa.strip()},
                        )
                        st.session_state['mostrar_form_editar_empresa'] = False
                        st.rerun()
                
                if cancelar_form_editar:
                    st.session_state['mostrar_form_editar_empresa'] = False
                    st.rerun()
        
        if is_admin:
            with col_btn_excluir:
                botao_remover_empresa = st.button(label='Excluir Empresa', type='primary')

                if botao_remover_empresa:
                    dialog_excluir_empresa(empresa_selecionada)

    with divider:
        st.markdown("<div style='border-left:1px solid #ddd; height:30vh;'></div>",unsafe_allow_html=True)

    with col_criar_nova:
        # Adicionar nova empresa
        st.text('Adicionar Nova Empresa')
        with st.form('form_adicionar_empresa'):
            nome_empresa_adicionar = st.text_input('Nome')
            enviado_form_adicionar = st.form_submit_button(label='Salvar Empresa')
    
        if enviado_form_adicionar:
            sucesso = empresas.criar_empresa(nome_empresa_adicionar.strip())
            if not sucesso:
                st.warning('Não foi possível Salvar. (Já existe uma empresa com esse nome, ou contém símbolos).')
            else:
                audit_logger.registrar_acao(
                    usuario=st.session_state.get('username'), 
                    acao='Empresa Criada', 
                    alvo={'empresa': nome_empresa_adicionar.strip()},
                )
                st.success('Empresa Criada!')

    st.divider()
    