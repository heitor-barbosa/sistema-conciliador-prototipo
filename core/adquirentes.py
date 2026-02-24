import json
from pathlib import Path
from typing import Dict, Iterable, List
import pandas as pd

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
CATALOGO_DIR = CONFIG_DIR / "catalogo_adquirentes"

def load_adquirente_catalog(empresa_id: str, path: Path = CATALOGO_DIR) -> Dict[str, List[str]]:
    """
    Lê o catálogo de adquirentes a partir de um arquivo JSON.
    Se o arquivo não existir retorna um dicionário vazio.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path = path / f"{empresa_id}.json"

    if not path.exists():
        return {}
    try:
        dados = json.loads(path.read_text(encoding="utf-8"))
        return {
            str(nome): [str(keyword) for keyword in keywords]
            for nome, keywords in dados.items()
        }
    except (json.JSONDecodeError, OSError):
        return {}


def save_adquirente_catalog(empresa_id: str, catalog: Dict[str, Iterable[str]], path: Path = CATALOGO_DIR) -> None:
    """
    Persiste o catálogo de adquirentes em disco.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path = path / f"{empresa_id}.json"

    normalized = {
        str(nome): [str(keyword) for keyword in keywords if str(keyword).strip()]
        for nome, keywords in catalog.items()
    }
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def delete_adquirente_catalog(empresa_id: str):
    """
    Recebe o id de uma determinada empresa, 
    e exclui seu catalogo de adquirentes.
    
    :param empresa_id: id da empresa a ser excluida
    :type empresa_id: str
    """
    arquivo_catalogo_adquirentes = CATALOGO_DIR / f'{empresa_id}.json'
    if arquivo_catalogo_adquirentes.exists():
        arquivo_catalogo_adquirentes.unlink()


def rename_adquirente_catalog(id_antigo: str, empresa_id: str):
    """
    Renomeia o arquivo de catalogo de adquirentes utilizando
    o id antigo da empresa para buscar o arquivo.
    
    :param id_antigo: antigo id da empresa, utilizado para buscar seus arquivos
    :type id_antigo: str
    :param empresa_id: novo id da empresa
    :type empresa_id: str
    """
    antigo_arquivo_catalogo_adquirentes = CATALOGO_DIR / f'{id_antigo}.json'
    novo_arquivo_catalogo_adquirentes = CATALOGO_DIR / f'{empresa_id}.json'

    if antigo_arquivo_catalogo_adquirentes.exists():
        antigo_arquivo_catalogo_adquirentes.rename(novo_arquivo_catalogo_adquirentes)


def classificar_adquirente(descricao: str, catalogo: Dict[str, Iterable[str]]) -> str:
    """
    Retorna o nome do adquirente com base nas palavras-chave.
    Caso não haja correspondência, devolve 'Outros'.
    """
    if not isinstance(descricao, str):
        if pd.isna(descricao): descricao = "" 
        else: descricao = str(descricao)

    texto = descricao
    for adquirente, palavras in catalogo.items():
        for palavra in palavras:
            if palavra and palavra in texto:
                return adquirente
    return "Outros"


def aplicar_classificacao_adquirente(df: pd.DataFrame, catalogo: Dict[str, Iterable[str]]) -> pd.DataFrame:
    """
    Adiciona a coluna 'Adquirente' ao dataframe com base nas palavras-chave.
    """
    df["Adquirente"] = df["Descricao"].apply(lambda valor: classificar_adquirente(valor, catalogo))
    
    return df
