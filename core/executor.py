# importa subprocess para executar comandos do sistema e json para manipular dados em formato JSON
import subprocess, json

# Função para executar uma ação recebida em formato JSON
def execute_action(action):
  try:
    # Converte o json recebido em um dicionário Python
    response = json.loads(action)
    # Verifica se a ação é destrutiva e solicita confirmação do usuário
    if response["destructive"]:
      confirm = input("A ação é destrutiva. Tem certeza que deseja continuar? (S/n): ")
      if confirm.lower() != 's':
        return "Execução cancelada."

    # Executa o comando especificado no JSON usando subprocess.run
    result = subprocess.run(
      response["command"],
      shell=True,
      cwd=response["cwd"],
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
