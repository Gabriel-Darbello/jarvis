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
# amostras processadas 80ms
CHUNK_SIZE = 1280

# carrega os modelos
print("Carregando modelos...")
model = Model()

print("Assistente iniciado. Diga 'Hey Jarvis' para ativar.")

# ultimo disparo e cooldown
ultimo_disparo = 0
COOLDOWN = 3

# abre o microfone com um canal (mono) e int16 formato dos numeros
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
    # loop infinito que lê o microfone
    while True:
        audio_chunk, _ = stream.read(CHUNK_SIZE) # pega as 1280 amostras e _ ignora o segundo valor
        audio_data = np.squeeze(audio_chunk) # remove dimensões desnecessarias
        # manda para o modelo onde ele retorna um dicionario  com o score da wake word
        prediction = model.predict(audio_data)
        # percorre cada wake word e seu score, se passou de 50% de confiança verifica se passaram 3 segundos desde o ultimo disparo
        for wake_word, score in prediction.items():
            if score > 0.5:
                agora = time.time()
                if agora - ultimo_disparo > COOLDOWN:
                    ultimo_disparo = agora
                    DURACAO_COMANDO = 5  # segundos
                    FRAMES_COMANDO = SAMPLE_RATE * DURACAO_COMANDO

                    # grava o comando do usuario
                    print("Gravando...")
                    gravacao = sd.rec(
                        frames=FRAMES_COMANDO,
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype='int16'
                    )
                    sd.wait()  # espera terminar a gravação
                    print("Gravação concluída.")

                    # Salva em um arquivo .wav temporário
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        caminho_audio = tmp.name
                    # salva em escrita binaria crua para gravação do audio
                    with wave.open(caminho_audio, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(SAMPLE_RATE)
                        wav_file.writeframes(gravacao.tobytes())

                    print(f"Áudio salvo em: {caminho_audio}")
