# importa subprocess para executar comandos do sistema e json para manipular dados em formato JSON
import subprocess

# Função para executar uma ação recebida em dicionario python
def execute_action(action):
  try:
    # Executa o comando especificado no JSON usando subprocess.run
    result = subprocess.run(
      action["command"],
      shell=True,
      cwd=action["cwd"],
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
