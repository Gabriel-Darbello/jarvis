import os
import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280

print("Carregando modelos...")
model = Model()

print("Assistente iniciado. Diga 'Hey Jarvis' para ativar.")

ultimo_disparo = 0
COOLDOWN = 3

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
                    print(f"Wake word detectada! Pode falar seu comando...")
