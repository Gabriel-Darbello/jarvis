import os

class BaseSkill:
    def __init__(self):
        self.whitelist = ['ls', 'git', 'cat', 'echo', 'mkdir', 'touch', 'cp', 'rm']
        self.allowed_zones = [
            os.path.expanduser("~/Área de trabalho"),
            os.path.expanduser("~/programação/pessoal"),
        ]

    def _is_safe_path(self, path):
        if not path:
            return False

        target_path = os.path.abspath(os.path.expanduser(path))
        for zone in self.allowed_zones:
            if target_path.startswith(os.path.abspath(zone)):
                return True

        return False

    def execute(self, **kwargs):
        raise NotImplementedError("Você deve implementar o método execute!")
