from skills.base import BaseSkill
import subprocess
import psutil

class GetFocusAppSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, params=None):
        try:
            window_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            window_title = subprocess.check_output(["xdotool", "getwindowname", window_id]).decode().strip()
            try:
                window_pid = subprocess.check_output(["xdotool", "getwindowpid", window_id]).decode().strip()
                process = psutil.Process(int(window_pid))
                app_name = process.name()
            except:
                app_name = "Desconhecido"

            return {
                "titulo": window_title,
                "app": app_name,
                "resumo": f"Você está no '{app_name}' focado em '{window_title}'"
            }
        except Exception as e:
            return f"Erro ao identificar janela: {e}."
