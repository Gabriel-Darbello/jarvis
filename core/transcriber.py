import os
from groq import Groq
from dotenv import load_dotenv


def transcrever(caminho_audio):
    load_dotenv()
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    with open(caminho_audio, "rb") as file:
        transcription = client.audio.transcriptions.create(
          file=file,
          model="whisper-large-v3-turbo",
          prompt= "O comando possui termos técnicos de programação e nomes de aplicativos e jogos",
          language="pt",
          response_format="text"
        )
    return transcription
