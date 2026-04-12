import os
import asyncio
import tempfile
import subprocess
import pygame
import edge_tts
import json
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa o mixer do pygame para reprodução de áudio
pygame.mixer.init()

# Pega a chave da API do Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Cria o cliente Groq uma vez e reutiliza em todas as chamadas
client = Groq(api_key=GROQ_API_KEY)

# Caminho do vault do obsidian para memoria
VAULT_PATH = Path.home() / "programação/pessoal/vault-ia"
PROJETOS_PATH = VAULT_PATH / "AI/memoria/projetos"
DIARIO_PATH = VAULT_PATH / "AI/memoria/diario"


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

def beep():
    """Toca um beep curto para confirmar que a gravação foi encerrada."""
    try:
        # Gera um tom de 440hz (Lá) por 150ms matematicamente
        # sem precisar de arquivo de áudio externo
        sample_rate = 44100
        duracao = 0.15
        frequencia = 440

        t = np.linspace(0, duracao, int(sample_rate * duracao))
        onda = (np.sin(2 * np.pi * frequencia * t) * 32767).astype(np.int16)
        onda_stereo = np.column_stack([onda, onda])

        som = pygame.sndarray.make_sound(onda_stereo)
        som.play()
        pygame.time.wait(int(duracao * 1000))
    except Exception as e:
        print(f"Erro no beep: {e}")

def pegar_projeto_ativo():
    """
    Usa o xdotool para ler o título da janela ativa do sistema.
    Detecta VSCode, Obsidian, Firefox e terminal, extraindo contexto relevante.
    Retorna uma string descrevendo o contexto atual.
    """
    try:
        resultado = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True
        )
        titulo = resultado.stdout.strip()

        # VSCode — formato: "arquivo - NomeProjeto - Visual Studio Code"
        if "Visual Studio Code" in titulo:
            partes = titulo.split(" - ")
            if len(partes) >= 2:
                nome_projeto = partes[-2]
                pasta_projeto = f"~/programação/pessoal/{nome_projeto}"
                return f"VSCode aberto no projeto '{nome_projeto}' em {pasta_projeto}"

        # Obsidian — formato: "NomeDaNota - NomeDoVault - Obsidian"
        if "Obsidian" in titulo:
            partes = titulo.split(" - ")
            if len(partes) >= 2:
                nome_nota = partes[0]
                nome_vault = partes[-2] if len(partes) >= 3 else "vault"
                return f"Obsidian aberto na nota '{nome_nota}' do vault '{nome_vault}'"

        # Firefox — formato: "Título da Página — Mozilla Firefox"
        if "Firefox" in titulo or "Mozilla" in titulo:
            pagina = titulo.replace("— Mozilla Firefox", "").replace("- Mozilla Firefox", "").strip()
            return f"Firefox aberto em: '{pagina}'"

        # Terminal — formato: "pasta — Terminal" ou "gabriel@machine: ~/pasta"
        if "Terminal" in titulo or "bash" in titulo:
            return f"Terminal aberto: '{titulo}'"

        # Qualquer outra janela
        if titulo:
            return f"Janela ativa: '{titulo}'"

        return "Nenhuma janela identificada"

    except Exception as e:
        return f"Erro ao detectar janela: {e}"

def salvar_memoria(comando, resposta, contexto):
    """
    Salva o que foi feito no diário do dia e no arquivo do projeto relevante.
    Chamado automaticamente após cada comando executado.
    """
    try:
        agora = datetime.now()
        data_hoje = agora.strftime("%Y-%m-%d")
        hora_agora = agora.strftime("%H:%M")

        # Salva no diário do dia
        arquivo_diario = DIARIO_PATH / f"{data_hoje}.md"
        entrada_diario = f"\n### {hora_agora}\n- **Contexto:** {contexto}\n- **Comando Recebido:** {comando}\n- **Execução:**\n{resposta}\n"

        with open(arquivo_diario, "a", encoding="utf-8") as f:
            if not arquivo_diario.exists() or arquivo_diario.stat().st_size == 0:
                f.write(f"# Diário {data_hoje}\n")
            f.write(entrada_diario)

        # Detecta qual projeto foi tocado e atualiza o arquivo do projeto
        projeto = extrair_projeto_do_contexto(contexto)
        if projeto:
            atualizar_projeto(projeto, comando, resposta, hora_agora)

    except Exception as e:
        print(f"Erro ao salvar memória: {e}")


def extrair_projeto_do_contexto(contexto):
    """
    Extrai o nome do projeto do contexto da janela ativa.
    """
    # Se tiver VSCode aberto num projeto
    if "VSCode aberto no projeto" in contexto:
        partes = contexto.split("'")
        if len(partes) >= 2:
            return partes[1]

    # Palavras-chave comuns nos comandos
    projetos_conhecidos = ["RoadUp", "Assistente-gemini", "assistente"]
    for projeto in projetos_conhecidos:
        if projeto.lower() in contexto.lower():
            return projeto

    return None


def atualizar_projeto(projeto, comando, resposta, hora):
    """
    Atualiza o arquivo de memória do projeto com o que foi feito.
    Cria o arquivo se não existir.
    """
    arquivo_projeto = PROJETOS_PATH / f"{projeto}.md"

    # Cria o arquivo do projeto se não existir
    if not arquivo_projeto.exists():
        with open(arquivo_projeto, "w", encoding="utf-8") as f:
            f.write(f"# {projeto}\n\n## Sobre o Projeto\n_Preencher_\n\n## Stack\n_Preencher_\n\n## Histórico de Ações\n")

    # Adiciona a ação no histórico
    entrada = f"\n- **{hora}** — {comando} → {resposta[:100]}{'...' if len(resposta) > 100 else ''}"
    with open(arquivo_projeto, "a", encoding="utf-8") as f:
        f.write(entrada)


def carregar_contexto_projeto(projeto):
    """
    Lê o arquivo de memória do projeto pra passar como contexto pro Gemini.
    Retorna string vazia se não existir.
    """
    arquivo_projeto = PROJETOS_PATH / f"{projeto}.md"
    if arquivo_projeto.exists():
        return arquivo_projeto.read_text(encoding="utf-8")
    return ""
