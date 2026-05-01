from base import BaseSkill
import os, subprocess

class OpenAppSkill(BaseSkill):
    def __init__(self):
        super().__init__()

    def execute(self, apps = []):
        if isinstance(apps, str):
            apps = [apps]

        app_folder = [
            "/usr/share/applications",
            "/var/lib/flatpak/exports/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]

        result = []

        for app in apps:
            open_app = False
            for pasta in app_folder:
                if open_app: break

                if os.path.exists(pasta):
                    arquivos = os.listdir(pasta)
                    for arquivo in arquivos:
                        if app.lower() in arquivo.lower() and arquivo.endswith(".desktop"):
                            id_app = arquivo.replace(".desktop", "")
                            try:
                                subprocess.Popen(
                                    ["gtk-launch", id_app],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    stdin=subprocess.DEVNULL,
                                    start_new_session=True,
                                )
                                result.append(f"Sucesso: {id_app} aberto.")
                                open_app = True
                                break
                            except Exception as e:
                                open_app = True
                                result.append(f"Erro ao abrir aplicativo: {str(e)}")
            if not open_app:
                result.append(f"Erro: o aplicativo {app} não foi encontrado")

        return "\n".join(result)
