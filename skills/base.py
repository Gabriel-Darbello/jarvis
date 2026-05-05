import os
from pathlib import Path

class BaseSkill:
    def __init__(self):
        self.whitelist = ['ls', 'git', 'cat', 'echo', 'mkdir', 'touch', 'cp', 'rm']
        self.allowed_zones = [
            Path(os.path.expanduser("~/Área de trabalho")).resolve(),
            Path(os.path.expanduser("~/programação/pessoal")).resolve(),
        ]

    def _is_safe_path(self, path):
        if not path:
            return False
        target_path = Path(os.path.abspath(os.path.expanduser(path))).resolve()
        for zone in self.allowed_zones:
            if target_path.is_relative_to(zone):
                return True

        return False

    def execute(self, **kwargs):
        raise NotImplementedError("Você deve implementar o método execute!")
