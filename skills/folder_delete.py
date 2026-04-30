from base import BaseSkill
from pathlib import Path
import shutil, os

class FolderDeleteSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, path):
        if not self._is_safe_path(path):
            return "Erro: Acesso a este diretório não é permitido por segurança."
        try:
            file_path = Path(os.path.expanduser(path))
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    return "Sucesso: Pasta deletada com sucesso!"
                else:
                    return "Erro: Isto é um arquivo não uma pasta"
            else:
                return "Erro: Pasta não encontrada"
        except Exception as e:
            return f"Erro ao deletar pasta: {str(e)}"
