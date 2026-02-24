import streamlit as st
import pandas as pd
from core import data_sources, audit_logger


def render_gerenciador_arquivos():
    # Funcoes que abrem modal
    @st.dialog('Atenção!')
    def confirmar_exclusao_arquivo(caminho):
        st.warning('A exclusão de arquivo é irreversível! Tem certeza que deseja continuar?')
        b1, b2 = st.columns(2)
        if b1.button('Confirmar exclusão', type='primary'):
            data_sources.deletar_arquivo(caminho)
            audit_logger.registrar_acao(
                usuario=st.session_state.get('username'),
                acao='Arquivo Excluido',
                alvo={'arquivo': str(caminho)}
            )
            st.cache_data.clear()
            st.rerun()

        if b2.button('Cancelar'):
            st.rerun()


    st.subheader(f'Arquivos Salvos - {st.session_state['empresa_selecionada_gerenciador']['nome']}')
    arquivos_banco, arquivos_adquirente = data_sources.listar_arquivos_diretorio_uploads(st.session_state['empresa_selecionada_gerenciador']['id'])

    col_banco, col_adquirente = st.columns(2)
    with col_banco:
        st.text('Extratos Bancários')

        if not arquivos_banco:
            st.info('Sem dados. Nenhum arquivo foi salvo.')
        else:
            arquivos_banco_df = pd.DataFrame(arquivos_banco)
            st.dataframe(data=arquivos_banco_df.drop(columns=['caminho']), hide_index=True)

            col_sel_banco, _ = st.columns(2)
            with col_sel_banco:
                arquivo_banco_selecionado = st.selectbox(label='Selecione o arquivo para excluir', options=arquivos_banco, format_func=lambda e: e['Arquivo'], key='arquivo_banco')
                if st.button('Excluir Arquivo', type='primary', key='excluir_arquivo_banco'):
                    confirmar_exclusao_arquivo(arquivo_banco_selecionado['caminho'])

    with col_adquirente:
        st.text('Relatórios de Adquirentes')

        if not arquivos_adquirente:
            st.info('Sem dados. Nenhum arquivo foi salvo.')
        else:
            arquivos_adquirente_df = pd.DataFrame(arquivos_adquirente)
            st.dataframe(data=arquivos_adquirente_df.drop(columns=['caminho']), hide_index=True)

            col_sel_adq, _ = st.columns(2)
            with col_sel_adq:
                arquivo_adquirente_selecionado = st.selectbox(label='Selecione o arquivo para excluir', options=arquivos_adquirente, format_func=lambda e: e['Arquivo'], key='arquivo_adq')
                if st.button('Excluir Arquivo', type='primary', key='excluir_arquivo_adquirente'):
                    confirmar_exclusao_arquivo(arquivo_adquirente_selecionado['caminho'])
            