import streamlit as st
from core import resumo, utils
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, DataReturnMode


def default_locale():
    pt_br = {
        "noRowsToShow": "Sem registros",
        "loadingOoo": "Carregando...",
        "page": "Página", "of": "de", "to": "a",
        "first": "Primeira", "previous": "Anterior", "next": "Próxima", "last": "Última",
        "sortAscending": "Ordenar crescente", "sortDescending": "Ordenar decrescente",
        "filterOoo": "Filtrar...", "applyFilter": "Aplicar", "clearFilter": "Limpar",
        "searchOoo": "Buscar",
        "selectAll": "Selecionar Todos",
        "selectAllSearchResults": "Selecionar todos os resultados",
        "blanks": "(Em branco)",
        "noMatches": "Sem correspondências",
        "cancel": "Cancelar",
        "pageSizeSelectorLabel": "Itens por página",
        "copy": "Copiar",
        "copyWithHeaders": "Copiar com cabeçalhos",
        "copyWithGroupHeaders": "Copiar com cabeçalhos agrupados",
        "cut": "Recortar",
        "paste": "Colar",
        "export": "Exportar",
        "csvExport": "Exportar CSV",
        "excelExport": "Exportar Excel",
        "contains": "Contém",
        "notContains": "Não contém",
        "equals": "Igual a",
        "notEqual": "Diferente de",
        "startsWith": "Começa com",
        "endsWith": "Termina com",
        "blank": "Em branco",
        "notBlank": "Não está em branco",
        "andCondition": "E",
        "orCondition": "OU",
        "greaterThan": "Maior que",
        "greaterThanOrEqual": "Maior ou igual a",
        "lessThan": "Menor que",
        "lessThanOrEqual": "Menor ou igual a",
        "inRange": "Entre",        
    }
    return pt_br


def render_conciliacao(df_conciliacao):
    """
    Define e cria a estrutura que exibirá o dataframe da conciliação.

    Args:   df_conciliacao (dataframe)
    Returns: response (??)
    """

    # Incrementar o valor da key para limpar o grid (No caso de rerun com linha selecionada)
    grid_key = st.session_state.setdefault("conciliacao_grid_key", 0)
    limpar_selecao = st.session_state.pop("limpar_selecao_conciliacao", False)
    if limpar_selecao:
        grid_key += 1
        st.session_state["conciliacao_grid_key"] = grid_key

    def preparar_grid_conciliacao(df_origem):
        """ Realiza as configurações necessárias para exibir o grid de conciliação """

        # Aplicar filtro de tempo
        inicio, fim = st.session_state["periodo"]
        mascara = df_origem["Data"].between(inicio, fim)
        df_view = df_origem.loc[mascara].copy()

        # Aplicar filtro adquirente
        if st.session_state['adquirente_filtro'] is not None:
            mascara = df_view['Adquirente'] == st.session_state['adquirente_filtro']
            df_view = df_view.loc[mascara].copy()

        # Formatar as datas
        df_view["Data"] = df_view["Data"].astype(str)
        fmt_data = JsCode("""
            function(params){
                if (!params.value) return '';
                const [year, month, day] = String(params.value).split('T')[0].split('-');
                if (!year || !month || !day) return params.value;
                return `${day}/${month}/${year}`;
            }
        """)

        # Formatar os valores no padrão BRL
        fmt_brl = JsCode("""
        function(p){
        if(p.value==null) return '';
        try { return new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(p.value); }
        catch(e){ return p.value; }
        }
        """)

        # Configurações gerais do grid
        gb = GridOptionsBuilder.from_dataframe(df_view)
        gb.configure_default_column(resizable=True, sortable=True, filter=True)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
        gb.configure_column("Data", valueFormatter=fmt_data)
        gb.configure_column("Previsto", type=["numericColumn"], valueFormatter=fmt_brl)
        gb.configure_column("Deposito", type=["numericColumn"], valueFormatter=fmt_brl)
        gb.configure_column("Saldo Conciliação", type=["numericColumn"], valueFormatter=fmt_brl)
        gb.configure_selection('single', use_checkbox=False, rowMultiSelectWithClick=True, suppressRowClickSelection=False)
        grid_options = gb.build()
        
        # Formatação das linhas (Cores dependem do status)
        grid_options["getRowStyle"] = JsCode("""
            function(params) {
                if (!params.data) return {};
                if (params.data.Status === 'Conciliado') {
                    return { color: '#4CAF50' };
                }
                if (params.data.Status === 'Sem Dados') {
                    return { color: '#E53935'};
                }
                if (params.data.Status === 'Divergente')
                   return { color: '#E67E22' };
                }
        """)

        # Verificar se é necessario limpar o grid (No caso de rerun com linha selecionada)
        if limpar_selecao:
            grid_options["onGridReady"] = JsCode("""
            function(params){
                params.api.deselectAll();
            }
            """)
            st.session_state["limpar_selecao_conciliacao"] = False

        # Traduzir elementos em ingles do grid
        grid_options["localeText"] = default_locale()

        # Selecionar elementos do menu
        grid_options["getMainMenuItems"] = JsCode("""
            function(params) {
            return ['sortAscending', 'sortDescending'];
            }
        """)

        # Calculo do total dinamicamente
        recompute_js = """
        function(api){
            function toNumber(x){
                if (typeof x === 'number') return x;
                if (x == null) return 0;
                let s = String(x).trim();
                if (!s) return 0;
                s = s.replace(/R\\$\\s?/g, '').replace(/[^\\d.,-]/g, '');
                s = s.replace(/\\./g, '').replace(',', '.');
                const n = Number(s);
                return isNaN(n) ? 0 : n;
            }

            let previsto = 0, deposito = 0, saldo = 0;
            api.forEachNodeAfterFilterAndSort(function(node){
                if (!node || !node.data) return;
                previsto += toNumber(node.data.Previsto);
                deposito += toNumber(node.data.Deposito);
                saldo    += toNumber(node.data["Saldo Conciliação"]);
            });

            api.setGridOption('pinnedBottomRowData', [{
                Data: 'TOTAL',
                Adquirente: '',
                Previsto: previsto,
                Deposito: deposito,
                "Saldo Conciliação": saldo,
                Status: ''
            }]);
        }
        """

        grid_options["onFirstDataRendered"] = JsCode(f"""
        function(e){{
            const api = e.api;
            window.conciliacaoRecomputeTotal = function(){{
                ({recompute_js})(api);
            }};
            window.conciliacaoRecomputeTotal();
        }}
        """)

        grid_options["onModelUpdated"] = JsCode("""
        function(e){
            if (window.conciliacaoRecomputeTotal) {
                window.conciliacaoRecomputeTotal();
            }
        }
        """)

        grid_options["onFilterChanged"] = grid_options["onModelUpdated"]
        grid_options["onSortChanged"] = grid_options["onModelUpdated"]
        grid_options["onPaginationChanged"] = grid_options["onModelUpdated"]
        grid_options["onDisplayedColumnsChanged"] = grid_options["onModelUpdated"]


        return df_view, grid_options
    
    
    # Cria o grid
    conciliado, grid_conciliado = preparar_grid_conciliacao(df_conciliacao)
    response = AgGrid(
        conciliado, 
        gridOptions=grid_conciliado, 
        height=600, 
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_on=['selectionChanged'],
        fit_columns_on_grid_load=True, 
        allow_unsafe_jscode=True,
        key=f"conciliacao_{grid_key}",
        theme='material'
        )
    
    df_visivel = response.get('data', None)
    st.session_state['dados_totais'] = resumo.calcular_totais(df_visivel)
    st.session_state['dataframe_resumo'] = resumo.gerar_dataframe_resumo(df_visivel)

    return response



def render_extratos(df_extrato):
    """
    Define e cria a estrutura que exibirá os dataframes de extrato (bancário e adquirente)

    Args:      df_extrato(dataframe)
    Returns:   -
    """

    def preparar_grid_extratos(df_origem):
        # Formatar as datas
        df_view = df_origem.copy()
        df_view["Dia"] = df_view["Data"].apply(utils.formato_data)
        df_view = df_view[["Dia", "Adquirente", "Descricao", "Valor"]]

        # Formatar os valores no padrão BRL
        fmt_brl = JsCode("""
        function(p){
        if(p.value==null) return '';
        try { return new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(p.value); }
        catch(e){ return p.value; }
        }
        """)

        # Configurações gerais do grid
        gb = GridOptionsBuilder.from_dataframe(df_view)
        gb.configure_default_column(resizable=True, sortable=True, filter=True)
        gb.configure_column("Valor", type=["numericColumn"], valueFormatter=fmt_brl)
        gb.configure_column("Adquirente", width=160)
        gb.configure_column("Descricao", wrapText=True, autoHeight=True, width=420)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)

        grid_options = gb.build()

        # Traduzir elementos em ingles do grid
        grid_options["localeText"] = default_locale()

        # Selecionar elementos do menu
        grid_options["getMainMenuItems"] = JsCode("""
        function(params) {
        return ['sortAscending', 'sortDescending'];
        }
        """)


        # Calcular linha de total dinamicamente
        grid_options["onGridReady"] = JsCode("""
        function(e){
        const api = e.api;

        function toNumber(x){
            if (typeof x === 'number') return x;
            if (x == null) return 0;
            let s = String(x).trim();
            if (!s) return 0;
            s = s.replace(/R\\$\\s?/g, '').replace(/[^\\d.,-]/g, ''); // remove R$, espaços, símbolos
            s = s.replace(/\\./g, '').replace(',', '.');              // milhar->remove, vírgula->ponto
            const n = Number(s);
            return isNaN(n) ? 0 : n;
        }

        function recompute(){
            let total = 0;
            api.forEachNodeAfterFilterAndSort(function(node){
            if (node && node.data) total += toNumber(node.data.Valor);
            });
            // v32+: atualiza opção em tempo real
            api.setGridOption('pinnedBottomRowData', [
            { Dia: 'TOTAL', Adquirente: '', Descricao: '', Valor: total }
            ]);
        }

        // 1ª renderização
        recompute();
        }
        """)

        # Recalcula quando o grid muda
        grid_options["onFilterChanged"]          = JsCode("function(e){ e.api.refreshClientSideRowModel('filter'); e.api.dispatchEvent({type:'dummy'}); e.api.setGridOption('pinnedBottomRowData', e.api.getGridOption('pinnedBottomRowData')); }")
        grid_options["onModelUpdated"]           = JsCode("function(e){ const api=e.api; let total=0; api.forEachNodeAfterFilterAndSort(n=>{ if(n&&n.data){ total += (typeof n.data.Valor==='number')?n.data.Valor:Number(String(n.data.Valor).replace(/R\\$\\s?|\\./g,'').replace(',','.'))||0; }}); api.setGridOption('pinnedBottomRowData',[{Dia:'TOTAL',Adquirente:'',Descricao:'',Valor:total}]); }")
        grid_options["onSortChanged"]            = JsCode("function(e){ const api=e.api; const cur=api.getGridOption('pinnedBottomRowData')||[]; api.setGridOption('pinnedBottomRowData',cur); }")
        grid_options["onPaginationChanged"]      = JsCode("function(e){ const api=e.api; const cur=api.getGridOption('pinnedBottomRowData')||[]; api.setGridOption('pinnedBottomRowData',cur); }")
        grid_options["onDisplayedColumnsChanged"]= JsCode("function(e){ const api=e.api; const cur=api.getGridOption('pinnedBottomRowData')||[]; api.setGridOption('pinnedBottomRowData',cur); }")

        return df_view, grid_options
    

    # Cria o Grid
    df_extrato_filtrado, grid_extrato = preparar_grid_extratos(df_extrato)
    AgGrid(
        df_extrato_filtrado,
        gridOptions=grid_extrato,
        height=600,
        width=600,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        theme='material'
    )