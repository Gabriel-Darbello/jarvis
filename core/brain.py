# importa os, json, groq, dotenv e o execute_action de executor.py
import os, json
from core.executor import execute_action
from groq import Groq
from dotenv import load_dotenv

load_dotenv() # carrega o .env
instructions = open("./Jarvis.md").read() #lê o Jarvis.md
client = Groq(api_key=os.environ.get("GROQ_API_KEY")) # inicia o Groq utilizando a API

# cria a função agent que recebe o comando do usuario e o array messages
def agent(user_message, messages):
    # cria um array messages que contém as mensagens que o Groq recebe, no caso instruções e user message
    if not messages:
        messages.extend([
            {
            "role": "system",
            "content": instructions
            },
            {
            "role": "user",
            "content": user_message
            }
        ])
    elif user_message is not None:
        messages.append(
            {
            "role": "user",
            "content": user_message
            }
        )


    # loop infinito para o Groq trabalhar o quanto ele quiser
    while True:
        # envia as messagens e escolhe o modelo
        chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile"
        )

        # resposta crua do Groq sem tratamento
        raw_response = chat_completion.choices[0].message.content
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
            return response
        except:
            # caso ocorra algum erro ocorra devido estrutura do json envia um aviso para o Groq e continua o loop
            messages.append({
                "role": "user",
                "content": "Erro: O formato JSON enviado é inválido. Por favor, envie apenas o JSON sem mensagens adicionais."
            })
            continue
