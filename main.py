import os
import time
import tempfile
import wave
import numpy as np
import subprocess
from processor import transcrever_audio, pegar_projeto_ativo, falar, beep, salvar_memoria, carregar_contexto_projeto
import sounddevice as sd
from openwakeword.model import Model

# Frequência de amostragem padrão para reconhecimento de voz
SAMPLE_RATE = 16000
# Número de amostras processadas por vez (80ms de áudio)
CHUNK_SIZE = 1280

# Configurações de detecção de silêncio
LIMITE_SILENCIO = 500       # Volume abaixo disso é considerado silêncio
SEGUNDOS_SILENCIO = 1.5     # Segundos em silêncio para encerrar gravação
CHUNKS_SILENCIO = int((SAMPLE_RATE / CHUNK_SIZE) * SEGUNDOS_SILENCIO)

# Tempo mínimo entre ativações para evitar disparos repetidos
COOLDOWN = 3

print("Carregando modelos...")
model = Model()
print("Assistente iniciado. Diga 'Hey Jarvis'...")

ultimo_disparo = 0

# Loop principal — fica escutando continuamente o microfone
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
    while True:
        # Lê um pedaço de áudio do microfone
        audio_chunk, _ = stream.read(CHUNK_SIZE)
        # np.squeeze remove dimensões desnecessárias: (1280,1) → (1280,)
        audio_data = np.squeeze(audio_chunk)

        # Verifica se a wake word foi detectada nesse pedaço
        prediction = model.predict(audio_data)

        for wake_word, score in prediction.items():
            # Só ativa se a confiança for maior que 50%
            if score > 0.5:
                agora = time.time()

                # Cooldown evita ativar múltiplas vezes na mesma fala
                if agora - ultimo_disparo > COOLDOWN:
                    ultimo_disparo = agora
                    print("\nWake word detectada! Pode falar...")
                    beep()

                    frames_gravados = []
                    chunks_silencio = 0

                    # Grava o comando até detectar silêncio
                    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as mic:
                        while True:
                            chunk, _ = mic.read(CHUNK_SIZE)
                            frames_gravados.append(chunk.copy())

                            # RMS — mede o volume do pedaço atual
                            volume = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

                            if volume < LIMITE_SILENCIO:
                                chunks_silencio += 1
                            else:
                                # Ainda tá falando — reseta o contador
                                chunks_silencio = 0

                            if chunks_silencio >= CHUNKS_SILENCIO:
                                print("Silêncio detectado, encerrando gravação.")
                                beep()
                                break

                    # Junta todos os pedaços numa array só
                    gravacao = np.concatenate(frames_gravados, axis=0)
                    duracao = len(gravacao) / SAMPLE_RATE

                    # Ignora gravações muito curtas (provavelmente ruído)
                    if duracao < 1.0:
                        print("Ruído detectado, ignorando...")
                        continue

                    # Salva o áudio num arquivo .wav temporário
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        caminho_audio = tmp.name

                    with wave.open(caminho_audio, 'wb') as wav_file:
                        wav_file.setnchannels(1)      # mono
                        wav_file.setsampwidth(2)      # 16 bits = 2 bytes
                        wav_file.setframerate(SAMPLE_RATE)
                        wav_file.writeframes(gravacao.tobytes())

                    # Transcreve o áudio para texto via Groq Whisper
                    texto = transcrever_audio(caminho_audio)
                    os.remove(caminho_audio)

                    if not texto or len(texto.strip()) < 3:
                        print("Comando não reconhecido.")
                        continue

                    # Detecta o projeto ativo
                    contexto = pegar_projeto_ativo()

                    # carrega memória do projeto se tiver
                    memoria_projeto = ""
                    if "VSCode aberto no projeto" in contexto:
                        nome = contexto.split("'")[1]
                        memoria_projeto = carregar_contexto_projeto(nome)

                    # monta prompt com memória
                    if memoria_projeto:
                        prompt = f"Contexto atual: {contexto}\n\nMemória do projeto:\n{memoria_projeto}\n\nComando: {texto}"
                    else:
                        prompt = f"Contexto: {contexto}\n\nComando: {texto}"
                    try:
                        resultado = subprocess.run(
                            ["gemini", "--yolo", "-p", prompt],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            timeout=120,
                            env=os.environ.copy()
                        )

                        resposta = resultado.stdout.strip() if resultado.stdout else ""

                        if resposta:
                          print(f"Gemini: {resposta}")
                          falar(resposta)
                          salvar_memoria(texto, resposta, contexto)

                    except subprocess.TimeoutExpired:
                        mensagem = "O comando demorou demais e foi cancelado."
                        print(mensagem)
                        falar(mensagem)
                    except Exception as e:
                        print(f"Erro ao executar comando: {e}")

                    ultimo_disparo = time.time()

                    # Limpa o buffer do microfone acumulado durante o processamento
                    while stream.read_available > 0:
                        stream.read(stream.read_available)

                    # Reseta o estado interno do modelo de wake word
                    model.reset()

                    print("\nPronto para o próximo comando...")
