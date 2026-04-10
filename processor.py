import os
from dotenv import load_dotenv
from groq import Groq

# Carrega variaveis ambiente
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inicialização do cliente da Groq globalmente
client = Groq(api_key=GROQ_API_KEY)
# Função para transcrição de audio para texto
def transcrever_audio(caminho_arquivo):
    # Envia o arquivo de áudio para a Groq e retorna o texto
    try:
        with open(caminho_arquivo, "rb") as file:
            # Whisper da Groq: traduz audio em texto
            transcription = client.audio.transcriptions.create(
                file=(caminho_arquivo, file.read()),
                model="whisper-large-v3",
                language="pt",
                prompt="Comandos para assistente: abrir github, terminal, projeto."
            )
            return transcription.text
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return None
