# importação de bibliotecas e modelos
import os
import time
import tempfile
import wave
import numpy as np
import sounddevice as sd
from openwakeword.model import Model
from dotenv import load_dotenv

# carrega o .env e acessa o GROQ_API_KEY
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# padrão de reconhecimento de voz
SAMPLE_RATE = 16000
# amostras processadas a cada 80ms
CHUNK_SIZE = 1280

# configurações de detecção de silêncio
LIMITE_SILENCIO = 500
SEGUNDOS_SILENCIO = 1.5
CHUNKS_SILENCIO = int((SAMPLE_RATE / CHUNK_SIZE) * SEGUNDOS_SILENCIO)
COOLDOWN = 3

# carrega os modelos
print("Carregando modelos...")
model = Model()

print("Assistente iniciado. Diga 'Hey Jarvis' para ativar.")

ultimo_disparo = 0

# loop principal — fica escutando wake word
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
    while True:
        audio_chunk, _ = stream.read(CHUNK_SIZE)
        audio_data = np.squeeze(audio_chunk)

        prediction = model.predict(audio_data)

        for wake_word, score in prediction.items():
            if score > 0.5:
                agora = time.time()
                if agora - ultimo_disparo > COOLDOWN:
                    ultimo_disparo = agora
                    print("Wake word detectada! Pode falar seu comando...")

                    # grava o comando com detecção de silêncio
                    frames_gravados = []
                    chunks_silencio = 0

                    print("Gravando... (para quando você parar de falar)")

                    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as mic:
                        while True:
                            chunk, _ = mic.read(CHUNK_SIZE)
                            frames_gravados.append(chunk.copy())

                            # calcula volume do pedaço atual
                            volume = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))

                            if volume < LIMITE_SILENCIO:
                                chunks_silencio += 1
                            else:
                                chunks_silencio = 0

                            if chunks_silencio >= CHUNKS_SILENCIO:
                                print("Silêncio detectado, encerrando gravação.")
                                break

                    # junta os pedaços gravados
                    gravacao = np.concatenate(frames_gravados, axis=0)

                    # salva o .wav temporário
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        caminho_audio = tmp.name

                    with wave.open(caminho_audio, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(SAMPLE_RATE)
                        wav_file.writeframes(gravacao.tobytes())

                    print(f"Áudio salvo em: {caminho_audio}")
