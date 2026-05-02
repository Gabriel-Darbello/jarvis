from skills.base import BaseSkill
import psutil

class CloseAppSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, params):
        apps = params.get("app_name")

        if isinstance(apps, str):
            apps = [apps]

        result = []
        for app in apps:
            app_name = app.lower()
            process_finished = 0

            if "python" in app_name:
                result.append("Erro: Por segurança, não posso encerrar processos Python.")
                continue

            for process in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in process.info['name'].lower():
                        process.kill()
                        process_finished += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            if process_finished > 0:
                result.append(f"Sucesso: o app {app} foi encerrado com sucesso ({process_finished} processos finalizados)")
            else:
                result.append(f"Erro: Nenhum processo correspondente a '{app}' foi encontrado.")
        return "\n".join(result)
