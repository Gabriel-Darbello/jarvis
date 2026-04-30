from base import BaseSkill
import os

class FileReadSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, path):
        if not self._is_safe_path(path):
            return "Erro: Acesso a este diretório não é permitido por segurança."
        try:
            with open(os.path.expanduser(path), 'r', encoding='utf-8') as f:
                content = f.read(10000)
                return content
        except FileNotFoundError:
            return "Erro: arquivo não encontrado"
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

