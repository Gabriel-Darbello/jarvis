import os
import asyncio
import tempfile
import subprocess
import pygame
import edge_tts
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa o mixer do pygame para reprodução de áudio
pygame.mixer.init()

# Pega a chave da API do Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Cria o cliente Groq uma vez e reutiliza em todas as chamadas
client = Groq(api_key=GROQ_API_KEY)


def transcrever_audio(caminho_arquivo):
    """
    Recebe o caminho de um arquivo .wav e retorna o texto transcrito.
    Usa o Whisper da Groq. Retorna None se ocorrer algum erro.
    """
    try:
        with open(caminho_arquivo, "rb") as file:
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


def pegar_projeto_ativo():
    """
    Usa o xdotool para ler o título da janela ativa do sistema.
    Se for o VSCode, extrai o nome do projeto e monta o caminho.
    Retorna (nome_projeto, pasta_projeto) ou (None, None).
    """
    try:
        resultado = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True
        )
        titulo = resultado.stdout.strip()

        # Formato do título do VSCode: "arquivo - NomeProjeto - Visual Studio Code"
        if "Visual Studio Code" in titulo:
            partes = titulo.split(" - ")
            if len(partes) >= 2:
                # O nome do projeto é sempre o penúltimo item
                nome_projeto = partes[-2]
                pasta_projeto = f"~/programação/pessoal/{nome_projeto}"
                return nome_projeto, pasta_projeto

        return None, None
    except:
        return None, None


async def _falar_async(texto):
    """
    Função assíncrona que gera o áudio via Edge TTS e toca com pygame.
    É assíncrona porque o Edge TTS faz uma requisição à Microsoft —
    o async evita que o programa trave enquanto espera a resposta.
    """
    # pt-BR-AntonioNeural é uma voz masculina natural em português brasileiro
    communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")

    # Cria arquivo temporário para salvar o áudio gerado
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        caminho_mp3 = tmp.name

    # Gera e salva o áudio
    await communicate.save(caminho_mp3)

    # Toca o áudio e aguarda terminar
    pygame.mixer.music.load(caminho_mp3)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Remove o arquivo temporário
    os.remove(caminho_mp3)


def falar(texto):
    """
    Função principal de fala chamada pelo main.py.
    Executa a função async de forma síncrona via asyncio.run().
    """
    try:
        asyncio.run(_falar_async(texto))
    except Exception as e:
        print(f"Erro no TTS: {e}")


def simular_commit():
    """
    Função de simulação para demonstração de commit.
    """
    print("Simulando um commit com uma nova função.")
    return True
