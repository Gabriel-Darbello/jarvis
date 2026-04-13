# main.py
import os
import time
import tempfile
import wave
import random
import numpy as np
import subprocess
from processor import transcrever_audio, pegar_projeto_ativo, falar, beep, salvar_memoria, carregar_contexto_projeto
import sounddevice as sd
from openwakeword.model import Model

# Fix vital para o systemd conseguir abrir janelas gráficas
os.environ['DISPLAY'] = ':0'
os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')

# Frequência de amostragem padrão para reconhecimento de voz
SAMPLE_RATE = 16000
# Número de amostras processadas por vez (80ms de áudio)
CHUNK_SIZE = 1280

# Configurações de detecção de silêncio
LIMITE_SILENCIO = 500
SEGUNDOS_SILENCIO = 1.5
CHUNKS_SILENCIO = int((SAMPLE_RATE / CHUNK_SIZE) * SEGUNDOS_SILENCIO)

# Tempo mínimo entre ativações para evitar disparos repetidos
COOLDOWN = 3

# Frases de ativação aleatórias
FRASES_ATIVACAO = ["Sim, mestre", "Ouvindo", "Pode falar", "À disposição"]

print("Carregando modelos...")
model = Model()
print("Assistente iniciado. Diga 'Hey Jarvis'...")

ultimo_disparo = 0


def capturar_comando(segundos_silencio=1.5):
    """
    Função reutilizável que grava áudio até detectar silêncio.
    Usada tanto na ativação normal quanto na escuta ativa após perguntas.
    Retorna o texto transcrito ou None se não captou nada útil.
    """
    chunks_silencio_local = int((SAMPLE_RATE / CHUNK_SIZE) * segundos_silencio)
    frames_gravados = []
    chunks_silencio = 0

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as mic:
        while True:
            chunk, _ = mic.read(CHUNK_SIZE)
            frames_gravados.append(chunk.copy())

            # RMS — mede o volume do pedaço atual
            volume = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

            if volume < LIMITE_SILENCIO:
                chunks_silencio += 1
            else:
                chunks_silencio = 0

            if chunks_silencio >= chunks_silencio_local:
                beep()
                break

    gravacao = np.concatenate(frames_gravados, axis=0)
    duracao = len(gravacao) / SAMPLE_RATE

    if duracao < 1.0:
        print("Ruído detectado, ignorando...")
        return None

    # Salva o .wav temporário
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        caminho_audio = tmp.name

    with wave.open(caminho_audio, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(gravacao.tobytes())

    texto = transcrever_audio(caminho_audio)
    os.remove(caminho_audio)
    return texto


def processar_comando(texto, contexto):
    """
    Envia o comando pro Gemini CLI e retorna a resposta.
    Trata erros de quota de forma amigável.
    """
    # Carrega memória do projeto se tiver VSCode aberto
    memoria_projeto = ""
    if "VSCode aberto no projeto" in contexto:
        nome = contexto.split("'")[1]
        memoria_projeto = carregar_contexto_projeto(nome)

    # Monta prompt com ou sem memória
    if memoria_projeto:
        prompt = f"Contexto atual: {contexto}\n\nMemória do projeto:\n{memoria_projeto}\n\nComando: {texto}"
    else:
        prompt = f"Contexto: {contexto}\n\nComando: {texto}"

    try:
        resultado = subprocess.run(
            ["gemini", "--yolo", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=os.environ.copy()
        )

        # Filtra erros de quota antes de qualquer coisa
        stderr = resultado.stderr or ""
        if any(x in stderr for x in ["QuotaError", "429", "exhausted"]):
            return "Mestre, atingimos o limite de uso do Gemini. Vamos aguardar um pouco."

        # Pega só a última linha não vazia — é o resumo final
        linhas = [l.strip() for l in resultado.stdout.strip().splitlines() if l.strip()]
        return linhas[-1] if linhas else ""

    except subprocess.TimeoutExpired:
        return "O comando demorou demais e foi cancelado."
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return ""


# Loop principal — fica escutando continuamente o microfone
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
    while True:
        # Lê um pedaço de áudio do microfone
        audio_chunk, _ = stream.read(CHUNK_SIZE)
        audio_data = np.squeeze(audio_chunk)

        # Verifica se a wake word foi detectada
        prediction = model.predict(audio_data)

        for wake_word, score in prediction.items():
            if score > 0.5:
                agora = time.time()

                if agora - ultimo_disparo > COOLDOWN:
                    ultimo_disparo = agora
                    print("\nWake word detectada!")

                    # Responde com frase aleatória
                    falar(random.choice(FRASES_ATIVACAO))

                    # Aguarda o eco da voz do Jarvis sumir antes de gravar
                    time.sleep(0.8)

                    print("Pode falar...")
                    texto = capturar_comando()

                    if not texto or len(texto.strip()) < 3:
                        print("Comando não reconhecido.")
                        continue

                    print(f"Você disse: {texto}")

                    contexto = pegar_projeto_ativo()
                    print(f"Contexto: {contexto}")

                    resposta = processar_comando(texto, contexto)

                    if resposta:
                        print(f"Gemini: {resposta}")
                        falar(resposta)
                        salvar_memoria(texto, resposta, contexto)

                        # Escuta ativa se terminar com pergunta
                        if resposta.strip().endswith("?"):
                            print("Escuta ativa — aguardando resposta...")
                            time.sleep(0.8)
                            texto_resposta = capturar_comando(segundos_silencio=3)

                            if texto_resposta and len(texto_resposta.strip()) > 3:
                                print(f"Resposta: {texto_resposta}")
                                contexto_followup = f"{contexto} | Pergunta anterior: {resposta}"
                                resposta_followup = processar_comando(texto_resposta, contexto_followup)

                                if resposta_followup:
                                    print(f"Gemini: {resposta_followup}")
                                    falar(resposta_followup)
                                    salvar_memoria(texto_resposta, resposta_followup, contexto)
                            else:
                                print("Nenhuma resposta captada, cancelando escuta ativa.")

                    ultimo_disparo = time.time()

                    # Limpa o buffer do microfone
                    while stream.read_available > 0:
                        stream.read(stream.read_available)

                    model.reset()
                    print("\nPronto para o próximo comando...")
