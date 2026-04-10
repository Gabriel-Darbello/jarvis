import os
import time
import tempfile
import wave
import numpy as np
import subprocess
from processor import transcrever_audio, falar
import sounddevice as sd
from openwakeword.model import Model


SAMPLE_RATE = 16000  # Frequência de amostragem (padrão para voz)
CHUNK_SIZE = 1280    # Tamanho de cada "pedaço" de áudio processado (80ms)

# Configurações de silêncio
LIMITE_SILENCIO = 500
SEGUNDOS_SILENCIO = 1.5
CHUNKS_SILENCIO = int((SAMPLE_RATE / CHUNK_SIZE) * SEGUNDOS_SILENCIO)
COOLDOWN = 3

# Loop principal
print("Carregando modelos...")
model = Model() # Carrega o modelo de Wake Word (Hey Jarvis)

print("Assistente iniciado. Diga 'Hey Jarvis'...")

ultimo_disparo = 0

# Iniciamos a captura do microfone
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
    while True:
        # Lê um pedaço do áudio do microfone
        audio_chunk, _ = stream.read(CHUNK_SIZE)
        audio_data = np.squeeze(audio_chunk)

        # Envia para o modelo a palavra e ele faz um teste
        prediction = model.predict(audio_data)

        for wake_word, score in prediction.items():
            if score > 0.5: # Ativa somente se o score for maior que 50% de confiança
                agora = time.time()
                if agora - ultimo_disparo > COOLDOWN:
                    ultimo_disparo = agora
                    print("\nWake word detectada! Pode falar...")

                    frames_gravados = []
                    chunks_silencio = 0

                    # Gravar o comando
                    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as mic:
                        while True:
                            chunk, _ = mic.read(CHUNK_SIZE)
                            frames_gravados.append(chunk.copy())

                            # Cálculo de Volume
                            volume = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

                            if volume < LIMITE_SILENCIO:
                                chunks_silencio += 1
                            else:
                                chunks_silencio = 0

                            if chunks_silencio >= CHUNKS_SILENCIO:
                                break

                    # Processamento pós-gravação
                    gravacao = np.concatenate(frames_gravados, axis=0)
                    duracao = len(gravacao) / SAMPLE_RATE

                    if duracao < 1.0:
                        print("Ruído detectado, ignorando...")
                        continue

                    # Salva e Transcreve
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        caminho_audio = tmp.name

                    with wave.open(caminho_audio, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(SAMPLE_RATE)
                        wav_file.writeframes(gravacao.tobytes())

                    texto = transcrever_audio(caminho_audio)
                    try:
                        if texto and len(texto.strip()) > 3:
                            print(f"Enviando para o Gemini o seguinte prompt {texto}")
                            resultado = subprocess.run(
                                ["gemini", "--yolo", "-p", f"\nComando do usuário: {texto}"],
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                            if resultado.stdout:
                                    print(f"Gemini: {resultado.stdout}")
                                    falar(resultado.stdout)
                            if resultado.stderr:
                                print(f"Erro: {resultado.stderr}")
                        else:
                                print("Comando muito curto, ignorando...")
                    except subprocess.TimeoutExpired:
                        print("Gemini demorou demais, comando cancelado.")
                    except Exception as e:
                        print(f"Erro ao executar comando: {e}")

                    os.remove(caminho_audio) # Apaga o arquivo temp
                    ultimo_disparo = time.time()

                    # Limpeza de buffer
                    while stream.read_available > 0:
                        stream.read(stream.read_available)

                    # Reseta o modelo
                    model.reset()

                    print("\nPronto para o próximo comando...")
