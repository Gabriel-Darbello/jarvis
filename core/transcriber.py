import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def transcribe(caminho_audio):
    with open(caminho_audio, "rb") as file:
        transcription = client.audio.transcriptions.create(
          file=file,
          model="whisper-large-v3-turbo",
          prompt= "O comando possui termos técnicos de programação, nomes de aplicativos como firefox, jogos como minecraft e sites da internet como teams." \
          "trancrição exata de voz sem legendas ou agradecimentos",
          language="pt",
          response_format="text"
        )
    return transcription
