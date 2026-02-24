from pathlib import Path
import json
import unicodedata, re

from . import adquirentes, data_sources

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
EMPRESAS_FILE = CONFIG_DIR / "empresas.json"

def listar_empresas():
    """
    Acessa o json com a lista de 
    empresas disponiveis, e a retorna

    Args: -
    Returns: [{'nome': , 'id': }]
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    caminho = EMPRESAS_FILE

    try:
        dados = json.loads(caminho.read_text(encoding='utf-8'))
        return dados

    except (json.JSONDecodeError, OSError):
        print('Erro no json')
        return {}
    
def gerar_id(nome_empresa: str):
    """
    Cria o id (slug) da empresa desejada.
    retorna o id em caso positivo, e False
    em caso de já haver uma empresa de mesmo nome.
    
    :param nome_empresa: Nome da empresa que o id terá de base
    :type nome_empresa: str
    """
    # Gerar o id com base no nome
    empresa_id = unicodedata.normalize("NFKD", nome_empresa).encode("ascii", "ignore").decode().lower()
    # Tudo que nao for letra ou numero é rejeitado (aceita acentos e 'ç')
    if not re.fullmatch(r'[a-zA-ZÀ-Öø-ÿ0-9 ]+', empresa_id):
        return False

    empresas = listar_empresas()

    # Verificar se o id é unico
    for empresa in empresas:
        if empresa_id in empresa.values():
            return False
    
    return empresa_id

def criar_empresa(nome_empresa: str):
    """
    Recebe o nome da empresa, deriva o id,
    acessa o json com a lista de empresas
    disponiveis e adiciona uma nova entrada
    ((dict) {"nome": , "id": })

    Args: nome (str)
    Returns: sucesso (bool)
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    empresas = listar_empresas()

    empresa_id = gerar_id(nome_empresa)
    if empresa_id is False:
        return False

    empresas.append({'nome': nome_empresa, 'id':empresa_id})

    with open(EMPRESAS_FILE, 'w', encoding='utf-8') as arquivo:
        json.dump(empresas, arquivo, ensure_ascii=False, indent=2)
    
    return True

def editar_empresa(empresa_selecionada: str, nome_empresa: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    empresas = listar_empresas()

    # Gerar id da empresa
    empresa_id = gerar_id(nome_empresa)
    if empresa_id is False:
        return False

    # Salvar alterações no empresas.json
    for e in empresas:
        if e.get('nome') == empresa_selecionada:
            id_antigo = e['id']
            e['id'] = empresa_id
            e['nome'] = nome_empresa
            break
    with open(EMPRESAS_FILE, 'w', encoding='utf-8') as arquivo:
        json.dump(empresas, arquivo, ensure_ascii=False, indent=2)

    # Renomear catalogo de adquirentes
    adquirentes.rename_adquirente_catalog(id_antigo, empresa_id)

    # Renomear pasta de uploads
    data_sources.renomear_diretorio_uploads(id_antigo, empresa_id)

    return True


def remover_empresa(empresa_selecionada: str):
    """
    Recebe o nome da empresa selecionada, e a exclui, bem como
    todos seus arquivos (empresas.json, catalogo adq., uploads)
    
    :param empresa_selecionada: empresa a ser excluida
    :type empresa_selecionada: str
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remover entrada do json
    empresas = listar_empresas()
    for i, e in enumerate(empresas):
        if e.get('nome') == empresa_selecionada:
            empresa_id = e['id']
            empresas.pop(i)
            break
    with open(EMPRESAS_FILE, 'w', encoding='utf-8') as arquivo:
        json.dump(empresas, arquivo, ensure_ascii=False, indent=2)
    
    # Remover catalogo de adquirentes
    adquirentes.delete_adquirente_catalog(empresa_id)

    # Remover pasta de uploads
    data_sources.deletar_diretorio_uploads(empresa_id)