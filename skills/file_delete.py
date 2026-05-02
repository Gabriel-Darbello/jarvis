from skills.base import BaseSkill
from pathlib import Path
import os

class FileDeleteSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, params):
        path = params.get("file_path")

        if not self._is_safe_path(path):
            return "Erro: Acesso a este diretório não é permitido por segurança."
        try:
            file_path = Path(os.path.expanduser(path))
            if file_path.exists():
                if file_path.is_file():
                    os.remove(file_path)
                    return "Sucesso: Arquivo deletado com sucesso!"
                else:
                    return "Erro: Isto é uma pasta não um arquivo"
            else:
                return "Erro: Arquivo não encontrado"
        except Exception as e:
            return f"Erro ao deletar arquivo: {str(e)}"


