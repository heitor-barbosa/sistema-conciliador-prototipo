from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json

LOG_PATH = Path('logs') / 'historico.jsonl'

def registrar_acao(usuario: str, acao: str, alvo: dict|None = None):
    # possiveis acoes = ['Empresa Criada', 'Empresa Editada', 'Empresa Excluída', 'Arquivo uploadado', 'Arquivo excluído']
    linha_registrada = {
        'horario': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(timespec="seconds"),
        'usuario': usuario,
        'acao': acao,
        'alvo': alvo,
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_PATH, 'a', encoding='utf-8') as arquivo:
        arquivo.write(json.dumps(linha_registrada, ensure_ascii=True) + '\n')