from skills.base import BaseSkill
from pathlib import Path
import os

class FileCreateSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, params):
        path = params.get("file_path")
        content = params.get("content")

        if not self._is_safe_path(path):
            return "Erro: Acesso a este diretório não é permitido por segurança."

        try:
            file_path = Path(os.path.expanduser(path))
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if content is not None:
                content = content.replace("\\n", "\n").replace("\\t", "\t")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                return f"Sucesso: O arquivo {file_path} foi criado com sucesso"
            else:
                file_path.touch()
                return f"Sucesso: Arquivo {file_path.name} criado vazio."

        except Exception as e:
            return f"Erro ao criar arquivo: {str(e)}"
