# importa subprocess para executar comandos do sistema e json para manipular dados em formato JSON
import subprocess

# Função para executar uma ação recebida em dicionario python
def execute_action(action):
  try:
    command = action["command"]
    cwd = action.get("cwd")

    # Executa o comando especificado no JSON usando subprocess.run
    if command.strip().endswith("&"):
            # Popen inicia e o Python continua a execução do loop imediatamente
            subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.DEVNULL, # Joga a saída pro limbo pra não travar
                stderr=subprocess.DEVNULL, # Joga os erros pro limbo
                start_new_session=True     # Garante que o app não feche se o Jarvis fechar
            )
            return "Aplicativo iniciado em segundo plano."

    result = subprocess.run(
      command,
      shell=True,
      cwd=cwd,
      capture_output=True,
      text=True
    )

    # Verifica o código de retorno para determinar se a execução foi bem sucedida
    if result.returncode == 0:
      return result.stdout
    else:
      return result.stderr

  # caso de algum erro retorna o erro como string
  except Exception as e:
    return str(e)
