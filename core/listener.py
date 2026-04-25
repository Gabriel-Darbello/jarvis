import webrtcvad
import queue
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import wave

audio_queue = queue.Queue() # Instancia a fila de audio
vad = webrtcvad.Vad(3) # Modo do Vad definido em 3
sample_rate = 16000 # rate de amostras
duration = 30 # duração em milissegundos
frame_size = int(sample_rate * duration / 1000) # Cálculo do tamanho do frame (em amostras)
model = Model()

def callback(indata, frames, time, status):
    # conversão para de float32 para int16
    audio_int16 = (indata * 32768).astype(np.int16)
    # Transforma o array em bytes brutos
    byte_frame = audio_int16.tobytes()
    # Coloca o audio em uma fila
    audio_queue.put(byte_frame)

def await_wake_word(model):
    print("Esperando wake word...")
    ignore_frames = 40

    # Limpa a fila antes de começar
    while not audio_queue.empty():
        audio_queue.get()

    while True:
        byte_frame = audio_queue.get()

        if ignore_frames > 0:
            ignore_frames -= 1
            if ignore_frames == 0:
                # Limpa novamente após estabilizar o mic
                while not audio_queue.empty():
                    audio_queue.get()
                model = Model() # Garante que o modelo está limpo após o ruído inicial
            continue # Pula o processamento enquanto ignore_frames > 0

        # Converte de float32 para int16 (utilizado pelo OpenWakeWord)
        frame_np = np.frombuffer(byte_frame, dtype=np.int16)
        # Faz a previsão com o modelo
        prediction = model.predict(frame_np)
        # recebe o score do hey jarvis
        score = prediction.get("hey_jarvis", 0)
        # se o score for maior que 0.5 retorna retorna o model
        if score > 0.5:
            print("Jarvis ativado")
            return Model()


def record_command():
    frames_command = []
    silence = 0
    while not audio_queue.empty():
        audio_queue.get()

    while True:
        byte_frame = audio_queue.get()
        # adiciona um byte frame na lista
        frames_command.append(byte_frame)

        # verifica se está gravando audio
        is_speech = vad.is_speech(byte_frame, sample_rate)

        # se não estiver falando adiciona 1 a lista
        if not is_speech:
            silence += 1

            # imprime de 10 em 10 o tempo em silencio
            if silence % 10 == 0:
                print(f"Silêncio: {silence}")

            # se o contador de silencio for igual a 50
            if silence >= 50:
                # reseta o silencio
                silence = 0

                # limpa a lista
                while not audio_queue.empty():
                    audio_queue.get()

                # abre e fecha automaticamente a criação de um arquivo wav com o apelido wf
                # ele inicia o objeto que vai ser criado com caminho e modo de abertura
                with wave.open("temp/command.wav", "wb") as wf:
                    wf.setnchannels(1)  # define no wf quantos canais no caso mono
                    wf.setsampwidth(2)  # define no wf a largura da amostra em bytes em 2 bytes que equivale a 16bits
                    wf.setframerate(sample_rate)  # define no wf a taxa de amostragem no caso 16kHz
                    wf.writeframes(b"".join(frames_command))  # define no wf conteudo do audio pegando os frames

                return "temp/command.wav", Model()
        else:
            silence = 0
