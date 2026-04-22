# importa os, json, groq, dotenv e o execute_action de executor.py
import os, json
from core.executor import execute_action
from groq import Groq
from dotenv import load_dotenv

# cria a função agent que recebe o userMessage
def agent(userMessage):
  load_dotenv() # carrega o .env
  instructions = open("../Jarvis.md").read() #lê o Jarvis.md
  client = Groq(api_key=os.environ.get("GROQ_API_KEY")) # inicia o Groq utilizando a API
  # cria um array messages que contém as mensagens que o Groq recebe, no caso instruções e user message
  messages = [
    {
      "role": "system",
      "content": instructions
    },
    {
      "role": "user",
      "content": userMessage
    }
  ]

  # loop infinito para o Groq trabalhar o quanto ele quiser
  while True:
    # envia as messagens e escolhe o modelo
    chat_completion = client.chat.completions.create(
      messages=messages,
      model="llama-3.3-70b-versatile"
    )

    # resposta crua do Groq sem tratamento
    raw_response = chat_completion.choices[0].message.content
    print(f"\n--- PENSAMENTO DO JARVIS ---\n{raw_response}\n---------------------------")
    try:
      # pega a primeira chave e a ultima chave da resposta crua
      start = raw_response.find('{')
      end = raw_response.rfind('}') + 1
      if start == -1: raise ValueError("JSON não encontrado")
      # limpa a resposta
      json_clean = raw_response[start:end]
      # transforma em um dicionário
      response = json.loads(json_clean)
      # adiciona a resposta crua com a role assistant dentro de mensagens
      messages.append(
        {
          "role": "assistant",
          "content": raw_response
        }
      )

      # executa ação e salva o resultado
      if response.get("action"):
        print(f"Executando: {response["action"]}")
        result = execute_action(response["action"])
        messages.append({ "role": "user", "content": result})

      if response.get("finished"):
        return response

      if not response.get("action"):
        messages.append({"role": "user", "content": "Você não terminou a tarefa e não enviou uma ação. O que deve ser feito agora?"})
    except:
    # caso ocorra algum erro ocorra devido estrutura do json envia um aviso para o Groq e continua o loop
      messages.append({
        "role": "user",
        "content": "Erro: O formato JSON enviado é inválido. Por favor, envie apenas o JSON sem mensagens adicionais."
      })
      continue
