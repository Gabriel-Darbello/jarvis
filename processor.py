import os
import asyncio
import tempfile
import pygame
import edge_tts
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (GROQ_API_KEY)
load_dotenv()

# Inicializa o mixer do pygame para tocar áudio
pygame.mixer.init()

# Pega a chave da API do Groq do .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Cria o cliente da Groq que será usado para transcrição
# É criado uma vez aqui e reutilizado em todas as chamadas
client = Groq(api_key=GROQ_API_KEY)


def transcrever_audio(caminho_arquivo):
    """
    Recebe o caminho de um arquivo .wav e retorna o texto transcrito.
    Usa o modelo Whisper da Groq, que é rápido e gratuito.
    Retorna None se ocorrer algum erro.
    """
    try:
        # Abre o arquivo de áudio em modo binário (rb = read binary)
        with open(caminho_arquivo, "rb") as file:
            transcription = client.audio.transcriptions.create(
                # Passa o nome e o conteúdo do arquivo
                file=(caminho_arquivo, file.read()),
                # Modelo Whisper large — melhor qualidade disponível no Groq
                model="whisper-large-v3",
                # Define o idioma para evitar confusão com outros idiomas
                language="pt",
                # Dica de contexto para o Whisper entender melhor os comandos
                prompt="Comandos para assistente: abrir github, terminal, projeto."
            )
        return transcription.text

    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return None


async def _falar_async(texto):
    """
    Função assíncrona que gera e toca o áudio usando Edge TTS.
    É assíncrona porque o Edge TTS precisa fazer uma requisição
    à Microsoft para gerar o áudio — isso leva um tempo e o
    async permite que o programa não trave enquanto espera.
    Usa underscore no nome (_falar_async) por convenção —
    indica que é uma função interna, não deve ser chamada diretamente.
    """
    # Cria o objeto de comunicação com a voz escolhida
    # pt-BR-AntonioNeural é uma voz masculina natural em português brasileiro
    communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")

    # Cria um arquivo .mp3 temporário para salvar o áudio gerado
    # delete=False porque precisamos que o arquivo exista após o with
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        caminho_mp3 = tmp.name

    # Gera o áudio e salva no arquivo temporário
    await communicate.save(caminho_mp3)

    # Carrega e toca o arquivo no pygame
    pygame.mixer.music.load(caminho_mp3)
    pygame.mixer.music.play()

    # Fica em loop até o áudio terminar de tocar
    # Clock().tick(10) limita o loop a 10 verificações por segundo
    # para não sobrecarregar a CPU
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Remove o arquivo temporário após tocar
    os.remove(caminho_mp3)


def falar(texto):
    """
    Função principal de fala — esta é a que o main.py chama.
    Ela executa a função assíncrona _falar_async de forma síncrona
    usando asyncio.run(), que cria um loop de eventos, roda a
    função async até terminar e fecha o loop.
    """
    try:
        asyncio.run(_falar_async(texto))
    except Exception as e:
        print(f"Erro no TTS: {e}")
