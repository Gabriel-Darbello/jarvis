from skills.base import BaseSkill
from pathlib import Path
import os

class FileAppendSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, params):
        path = params.get("file_path")
        content = params.get("content")

        if not self._is_safe_path(path):
            return "Erro: Acesso a este diretório não é permitido por segurança."
        try:
            file_path = Path(os.path.expanduser(path))

            if not file.exists():
                return "Erro: arquivo não existe. Use a skill de criar antes"

            with open(file_path, 'a', encoding='utf-8') as file:
                file.write('\n' + content)
            return f"Sucesso: Conteúdo adicionado ao arquivo {file_path.name}"

        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

