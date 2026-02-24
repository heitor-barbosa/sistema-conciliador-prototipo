import pandas as pd
import streamlit as st

from core import adquirentes, conciliacao, data_sources, empresas, audit_logger
from app import ui


def run(nome_usuario: str):
    # Cabeçalho
    ui.header.render_header(nome_usuario)
   
    # Renderizar seletor de empresas
    catalogo_empresas = empresas.listar_empresas()
    espaco_seletor, _, espaco_filtro = st.columns(3)
    with espaco_seletor:
        ui.seletor_empresas.render_opcoes(catalogo_empresas)

    # Renderizar gerenciador de adquirentes da empresa // Renderizar catálogo de adquirentes
    empresa_id = st.session_state['empresa_selecionada']['id']
    catalogo_adquirentes = adquirentes.load_adquirente_catalog(empresa_id)
    st.session_state['catalogo_adquirentes'] = catalogo_adquirentes
    
    espaco_catalogo, _, espaco_gerenciador = st.columns(3)
    with espaco_catalogo:
        ui.catalogo.render_catalogo_adquirentes(empresa_id)
    with espaco_gerenciador:
        ui.gerenciador_catalogo.render_gerenciador_catalogo(catalogo_adquirentes, empresa_id)     
    

    # Tenta carregar os arquivos da empresa selecionada sem ter que fazer upload
    sucesso, df_banco, dict_df_adq = data_sources.tentar_carregar_arquivos_existentes(empresa_id)
    if sucesso:  
        df_banco, df_adq = conciliacao.preparar_para_conciliar(df_banco, dict_df_adq, catalogo_adquirentes)
        conciliado = conciliacao.conciliar(df_banco, df_adq)


    # Renderizar campo de upload de arquivos
    ui.arquivos_uploader.render_uploader(catalogo_adquirentes)

        # Lidar com upload de arquivos
    caminho_diretorio_banco, caminho_diretorio_adquirente = data_sources.obter_caminhos_uploads(empresa_id)

    if st.session_state.get('tratar_arquivo_banco'):
        st.session_state['tratar_arquivo_banco'] = False
        
        conteudo_arquivo_banco = st.session_state.pop('uploader_banco', None)
        # Verificar se existe arquivo uploadado ou não
        if conteudo_arquivo_banco:
            nomes_arquivos = [a.get("name") for a in conteudo_arquivo_banco if a.get("name")]

            foi_salvo, caminho_diretorio_banco = data_sources.tratar_arquivo_banco(conteudo_arquivo_banco, empresa_id)
            st.cache_data.clear()

            if foi_salvo:
                st.success('Arquivo salvo com sucesso.')
                audit_logger.registrar_acao(
                    usuario=st.session_state.get('username'),
                    acao='Arquivo Uploadado',
                    alvo={'empresa': st.session_state.get('empresa_selecionada')['nome'], 'tipo':'banco', 'arquivos': nomes_arquivos},
                )
                df_banco, df_adq, conciliado = conciliacao.tentar_conciliar(caminho_diretorio_banco, caminho_diretorio_adquirente, st.session_state['catalogo_adquirentes'])
            else:
                # Nesse caso, caminho_diretorio_banco vai conter as colunas faltando
                colunas_faltando = ', '.join(caminho_diretorio_banco)
                st.error(f'Arquivo inválido. Não foram encontradas as colunas: {colunas_faltando}')
        
    if st.session_state.get('tratar_arquivo_adquirente'):
        st.session_state['tratar_arquivo_adquirente'] = False
        
        conteudo_arquivo_adquirente = st.session_state.pop('uploads_adq_prontos', None)
        # Verificar se existe arquivo uploadado ou não
        if conteudo_arquivo_adquirente:
            nomes_arquivos = [{"arquivo": arq.name, "adquirente": adq} for arq, adq in conteudo_arquivo_adquirente.items()]

            foi_salvo, caminho_diretorio_adquirente = data_sources.tratar_arquivo_adquirente(conteudo_arquivo_adquirente, empresa_id)
            st.cache_data.clear()

            if foi_salvo:
                st.success('Arquivo salvo com sucesso.')
                audit_logger.registrar_acao(
                    usuario=st.session_state.get('username'),
                    acao='Arquivo Uploadado',
                    alvo={'empresa': st.session_state.get('empresa_selecionada')['nome'], 'tipo':'adquirente', 'arquivos': nomes_arquivos},
                )
                df_banco, df_adq, conciliado = conciliacao.tentar_conciliar(caminho_diretorio_banco, caminho_diretorio_adquirente, st.session_state['catalogo_adquirentes'])
            else:
                # Nesse caso, caminho_diretorio_adquirente vai conter as colunas faltando
                colunas_faltando = ', '.join(caminho_diretorio_adquirente)
                st.error(f'Arquivo inválido. Não foram encontradas as colunas: {colunas_faltando}')
    
        # Impedir continuação do programa caso não hajam dados prévios nem upload de extratos
    if not sucesso and (not caminho_diretorio_banco or not caminho_diretorio_adquirente):
        st.warning('Faça o upload para vizualizar a conciliação.')
        st.stop()


    # Renderizar filtro de tempo
    with espaco_filtro:
        ui.filtro_tempo.render_filtro_periodo(df_banco)


    # Renderizar dataframe da conciliação 
    empresa_selecionada = st.session_state['empresa_selecionada']['nome']
    st.subheader(f'Conciliação - {empresa_selecionada}')
    response = ui.grids.render_conciliacao(conciliado)

    # Lidar com a seleção de linhas no grid de conciliação principal
    selected = response.get('selected_rows', None)
    if isinstance(selected, pd.DataFrame) and not selected.empty:
        st.session_state['dia_selecionado'] = selected
        st.session_state['mostrar_modal'] = True
        
    if st.session_state.get('mostrar_modal'):
        ui.modal.render_detalhes(linha_selecionada=st.session_state['dia_selecionado'], df_extrato_base=df_banco, df_adquirente_base=df_adq)
        st.session_state['dia_selecionado'] = None
        st.session_state['mostrar_modal'] = False

    
    # Renderizar resumo da conciliação
    ui.resumo.render_resumo(empresa_selecionada)
