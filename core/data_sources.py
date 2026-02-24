import streamlit as st
import base64
from pathlib import Path
import pandas as pd
from infra.parsers import xlsx_parser
from core.utils import converter_tamanho_arquivo, formatar_data_e_hora
from datetime import datetime


UPLOADS_DIR = Path("extratos") / "uploads"

def obter_caminhos_uploads(empresa_id: str):
    """
    Utiliza o id da empresa selecionada para buscar e retornar
    os caminhos da pasta de uploads de arquivos do banco e adq.
    
    :param empresa_id: (str) id da empresa selecionada
    """
    diretorio_uploads = UPLOADS_DIR / empresa_id
    caminho_arquivos_banco = diretorio_uploads / 'banco'
    caminho_arquivos_adquirente = diretorio_uploads / 'adquirente'

    if (not caminho_arquivos_banco.exists()) or (not any(caminho_arquivos_banco.glob("*.xlsx"))):
        caminho_arquivos_banco = None
    if (not caminho_arquivos_adquirente.exists()) or (not any(caminho_arquivos_adquirente.rglob("*.xlsx"))):
        caminho_arquivos_adquirente = None

    return caminho_arquivos_banco, caminho_arquivos_adquirente


def deletar_diretorio_uploads(empresa_id: str):
    """
    Recebe o id de uma determinada empresa, 
    e exclui seu diretorio de uploads.
    
    :param empresa_id: id da empresa a ser excluida
    :type empresa_id: str
    """
    diretorio_uploads = UPLOADS_DIR / empresa_id

    if not diretorio_uploads.exists():
        return

    # Pegar timestamp atual para deixar arquivo único
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    for arquivo in diretorio_uploads.rglob('*.xlsx'):
        arquivo.rename(arquivo.with_suffix(f'.{timestamp}.deleted'))


def renomear_diretorio_uploads(id_antigo: str, empresa_id: str):
    """
    Renomeia o diretorio de uploads utilizando
    o id antigo da empresa para buscar o diretorio.
    
    :param id_antigo: id antigo da empresa
    :type id_antigo: str
    :param empresa_id: novo id
    :type empresa_id: str
    """
    antigo_diretorio_uploads = UPLOADS_DIR / id_antigo
    novo_diretorio_uploads = UPLOADS_DIR / empresa_id

    if antigo_diretorio_uploads.exists():
        antigo_diretorio_uploads.rename(novo_diretorio_uploads)


def listar_arquivos_diretorio_uploads(empresa_id: str):
    """
    Recebe o id de uma empresa, navega e varre seu 
    diretorio de uploads, retornando duas listas com
    todas as informações pertinentes de seus arquivos.
    [{1 dict / arquivo}, ..., {}]
    
    :param empresa_id: id da empresa buscada
    :type empresa_id: str
    """
    diretorio_selecionado = UPLOADS_DIR / empresa_id
    if not diretorio_selecionado.exists():
        return [], []
    
    diretorio_selecionado_banco = diretorio_selecionado / 'banco'
    diretorio_selecionado_adquirente = diretorio_selecionado / 'adquirente'

    arquivos_banco = []
    if diretorio_selecionado_banco.exists():
        for path in diretorio_selecionado_banco.glob('*'):
            if path.suffix == '.xlsx':
                stat = path.stat()
                arquivos_banco.append({
                    'Arquivo': path.name,
                    'Tamanho': converter_tamanho_arquivo(stat.st_size),
                    'Data de envio': formatar_data_e_hora(stat.st_mtime),
                    'caminho': path
                })

    arquivos_adquirente = []
    if diretorio_selecionado_adquirente.exists():
        for adq_dir in diretorio_selecionado_adquirente.iterdir():
            adquirente = adq_dir.name
            for path in adq_dir.glob('*'):
                if path.suffix == '.xlsx':
                    stat = path.stat()
                    arquivos_adquirente.append({
                        'Adquirente': adquirente,
                        'Arquivo': path.name,
                        'Tamanho': converter_tamanho_arquivo(stat.st_size),
                        'Data de envio': formatar_data_e_hora(stat.st_mtime),
                        'caminho': path
                    })

    return arquivos_banco, arquivos_adquirente


def deletar_arquivo(caminho_arquivo: Path):
    """
    Recebe o caminho de um arquivo xslx e troca sua 
    extensão para '.deleted', para ser oculto no sistema.
    
    :param caminho_arquivo: caminho do arquivo a ser ocultado
    :type caminho_arquivo: Path
    """
    # Pegar timestamp atual para deixar arquivo único
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    caminho_arquivo.rename(caminho_arquivo.with_suffix(f'.{timestamp}.deleted'))


def persistir_arquivo(nome_arquivo, bytes_do_arquivo, tipo, empresa_id, adquirente = None):
    DESTINO_UPLOAD = Path('extratos') / 'uploads'

    # Criar pasta para persistencia dos arquivos
    pasta_destino = DESTINO_UPLOAD / empresa_id / tipo
    if adquirente: pasta_destino = pasta_destino / adquirente
    pasta_destino.mkdir(parents=True, exist_ok=True)

    caminho = pasta_destino / nome_arquivo

    with open(caminho, 'wb') as destino:
        destino.write(bytes_do_arquivo)

    return caminho


def tratar_arquivo_adquirente(mapa_arquivos, empresa_id):
    """ 
    Recebe um dicionario contendo as chaves como os arquivos uploadados, e os 
    valores, suas respectivas adquirentes selecionadas. Persiste cada arquivo
    em sua pasta, dependendo de sua adquirente, e retorna o caminho do dowload.
    """

    for arquivo, adquirente in mapa_arquivos.items():
        if hasattr(arquivo, 'getvalue'):
            arquivo_bytes = arquivo.getvalue()
            arquivo_nome = arquivo.name

        colunas_faltando = xlsx_parser.validar_extrato(arquivo=arquivo_bytes, tipo='adq')
        if colunas_faltando:
            return False, colunas_faltando
        
        caminho = persistir_arquivo(arquivo_nome, arquivo_bytes, tipo='adquirente', empresa_id=empresa_id, adquirente=adquirente)

    diretorio_adquirentes = Path(caminho).parent.parent

    return True, str(diretorio_adquirentes)

    
def tratar_arquivo_banco(lista_arquivos, empresa_id):
    """
    Tratamento dos extratos bancários uploadados.
    Recebe lista de arquivos, retorna o caminho
    do diretorio em que os arquivos foram salvos.
    Necessário converter de base64 para bytes.
    """

    for arquivo in lista_arquivos:
        # pegar arquivo em base 64 e converter
        header, dados = arquivo['data'].split(',', 1)
        arquivo_bytes = base64.b64decode(dados)
        arquivo_nome = arquivo['name']
        
        colunas_faltando = xlsx_parser.validar_extrato(arquivo=arquivo_bytes, tipo='banco')
        if colunas_faltando:
            return False, colunas_faltando

        caminho = persistir_arquivo(arquivo_nome, arquivo_bytes, tipo='banco', empresa_id=empresa_id)

    diretorio_banco = Path(caminho).parent

    return True, str(diretorio_banco)


def tentar_carregar_arquivos_existentes(empresa_id):
    """
        Verifica se ja existem arquivos para a empresa selecionada,
        e caso existam, retorna Verdadeiro e os conteudos dos arquivos
    """

    # Acesso a pasta dos uploads
    diretorio_empresa_selecionada = Path('extratos') / 'uploads' / empresa_id
    caminho_arquivo_banco = diretorio_empresa_selecionada / 'banco'
    caminho_arquivo_adquirente = diretorio_empresa_selecionada / 'adquirente'

    if not diretorio_empresa_selecionada.exists():
        return False, None, None
    if not caminho_arquivo_banco.exists():
        return False, None, None
    if not caminho_arquivo_adquirente.exists():
        return False, None, None

    # Carregar extratos bancarios
    df_banco = carregar_extrato_banco(caminho_arquivo_banco)

    # Carregar extratos adquirentes
    dict_df_adquirentes = carregar_extrato_adquirente(caminho_arquivo_adquirente)

    if df_banco is None or not dict_df_adquirentes:
        return False, None, None

    return True, df_banco, dict_df_adquirentes




@st.cache_data(show_spinner=False)
def carregar_extrato_banco(caminho_diretorio: str | Path):
    """
        Recebe o path do diretorio que guarda extratos bancarios, 
        e retorna uma lista de dataframes extraído dele.
    """
    dfs_banco = []
    caminho_diretorio = Path(caminho_diretorio)
    for extrato in caminho_diretorio.iterdir():
        if extrato.suffix.lower() == '.xlsx':
            dfs_banco.append(xlsx_parser.xlsx_to_dataframe(extrato))

    if not dfs_banco:
        return None

    df_extrato = pd.concat(dfs_banco, ignore_index=True)

    return df_extrato

@st.cache_data(show_spinner=False)
def carregar_extrato_adquirente(caminho_diretorio_base: str | Path):
    """
        Recebe o path do diretorio que guarda os extratos das adquirentes,
        e retorna um dicionario com o nome de cada adquirente, e uma lista
        com os datframes extraídos.
    """
    caminho_diretorio_base = Path(caminho_diretorio_base)
    
    dados = {}
    for dir_adq in caminho_diretorio_base.iterdir():
        nome = dir_adq.name
        dfs = []
        for arquivo in dir_adq.iterdir():
            if arquivo.suffix.lower() == '.xlsx':
                dfs.append(xlsx_parser.adquirente_xlsx_to_dataframe(arquivo))
        
        if dfs:
            dados[nome] = dfs

    return dados