import streamlit as st
import st_file_uploader as stf
from core import data_sources

def render_uploader(opcoes_adquirentes):
    def preparar_tratar_arquivo_banco():
        st.session_state['tratar_arquivo_banco'] = True

    def preparar_tratar_arquivo_adq():
        st.session_state['tratar_arquivo_adquirente'] = True
    
    @st.dialog('Formato esperado do Excel')
    def mais_info():
        st.markdown("""<style> div[role="dialog"] {width: 85vw !important; max-width: 1100px !important;}
        div[role="dialog"] img {width: 100% !important; height: auto !important;}</style>""", unsafe_allow_html=True)

        col_banco, col_adquirente = st.columns(2)
        with col_banco:
            st.subheader('Banco:')
            st.text('Colunas Obrigatórias - Data, Descricao, Valor')
            st.text('Exemplo:')
            st.image(r'img\exbanco.png')
        with col_adquirente:
            st.markdown('**Adquirente:**')
            st.text('Colunas Obrigatórias - Data Pagamento, Produto, Valor Liquido')
            st.text('Exemplo:')
            st.image(r'img\exadq.png')

    custom = stf.create_custom_uploader(
        uploader_msg="Arraste ou Selecione seu arquivo",
        limit_msg="Tamanho máximo: 200MB",
        button_msg="Selecionar Arquivo",
        icon="MdFileUpload"
    )
    
    col_uploader, col_info = st.columns([0.97, 0.03])
    with col_info:
        if st.button('?'):
            mais_info()

    with col_uploader:
        with st.expander('📂 Uploads (Extratos e Adquirentes)', expanded=True):
            coluna_banco, coluna_adquirente = st.columns([0.5, 0.5])
            
            # Coluna de upload do banco (ESQUERDA)
            with coluna_banco:
                st.markdown("**Extratos Bancários**")
                c_uploader, _ = st.columns([70, 30])
                with c_uploader:
                    upload_banco = custom.file_uploader(label='Upload de Arquivos', type='xlsx', accept_multiple_files=True, key='uploader_banco')
                    
                    if upload_banco:
                        if st.button("Salvar extratos"):
                            preparar_tratar_arquivo_banco()
            
            # Coluna de upload das adquirentes (DIREITA)
            with coluna_adquirente:
                st.markdown("**Arquivos das Adquirentes**")
                espaco_uploader, _, espaco_seletor = st.columns([65, 5, 30])
                
                with espaco_uploader:
                    uploads_adq = custom.file_uploader(label='Upload de Arquivos', type='xlsx', accept_multiple_files=True, key='uploader_adq')
                    
                    if uploads_adq:
                        if not opcoes_adquirentes:
                            st.warning('Adicione pelo menos uma adquirente antes de fazer o upload.')
                            return
                        
                        with espaco_seletor:
                            st.markdown("Atribua a adquirente de cada arquivo:")
                            adq_de_cada_arquivo = {}
                            for arquivo in uploads_adq:
                                adq_escolhida = st.selectbox(f"Adquirente para {arquivo.name}", options=opcoes_adquirentes.keys(), key=f"adq_para_{arquivo.name}")
                                adq_de_cada_arquivo[arquivo] = adq_escolhida
                            if st.button("Salvar arquivos adquirentes"):
                                st.session_state["uploads_adq_prontos"] = adq_de_cada_arquivo
                                preparar_tratar_arquivo_adq()   

    return upload_banco, uploads_adq
        
        