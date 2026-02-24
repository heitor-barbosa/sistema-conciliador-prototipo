import streamlit as st

from core import resumo


def render_resumo(empresa_selecionada):


    def limpar_selecao_grid_conciliacao():
        st.session_state['limpar_selecao_conciliacao'] = True


    st.subheader(f'Resumo Conciliação')

    resumo_totais = st.session_state['dados_totais']
    df_resumo = st.session_state['dataframe_resumo']
    pdf_bytes = resumo.gerar_pdf_resumo(df_resumo, empresa_selecionada)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric('Previsto', resumo_totais['total_prev'])
    with c2:
        st.metric('Deposito', resumo_totais['total_dep'])
    with c3:
        st.metric('Saldo Conciliação', resumo_totais['total_diff'])
    with c4:
        st.download_button("Gerar Resumo Completo", pdf_bytes, file_name="Resumo Conciliacao.pdf", mime="application/pdf", on_click=limpar_selecao_grid_conciliacao)
        st.markdown("""
        <style>
            /* Personaliza o botão "Gerar Resumo" */
            div.stDownloadButton > button:first-child {
                background-color: #4CAF50;  
                color: white;               
                border: none;
                font-weight: bold;
                height: 3em;
                width: 100%;
                border-radius: 10px;
                margin-top: 20px;           /* espaçamento p/ alinhar */
                transition: 0.3s;
            }
            div.stDownloadButton > button:hover {
                background-color: #45a049;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric('Total de Dias', resumo_totais['n_total'])
    with c2:
        st.metric('Dias Conciliados', resumo_totais['n_conc'])
    with c3:
        st.metric('Dias Divergentes', resumo_totais['n_div'])
    with c4:
        st.metric('Dias Sem dados', resumo_totais['n_sem'])
