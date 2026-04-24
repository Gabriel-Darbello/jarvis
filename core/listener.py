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

def listen():
    # Abre o microfone definindo configurações basicas sendo elas:
    # samplerate(16kHz), blocksize, canais (mono), callback e tipo(float32)
    global model # cria a variavel global "model"
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
                    blocksize=frame_size, callback=callback):

        print("Esperando wake word...")
        state = "ESPERANDO" # define o estado como esperando
        frames_command = [] # cria uma lista vazia
        silence = 0 # tempo em silencio
        ignore_frames = 40 # frames a ser ignorados

        # faz um loop que limpa a lista de audio
        while not audio_queue.empty(): audio_queue.get()

        # inicia o loop principal
        while True:
            # pega um byte frame da lista
            byte_frame = audio_queue.get()

            # se o estado for "ESPERANDO"
            if state == "ESPERANDO":
                # ignora os primeiros 40 frames da lista
                if ignore_frames > 0:
                    ignore_frames -= 1

                    # quando ignora todos limpa a lista novamente e inicia o modelo
                    if ignore_frames == 0:
                        while not audio_queue.empty():
                            audio_queue.get()
                        model = Model()
                    continue

                # converte de float32 para int16 (formato utilizado pelo OpenWakeWord)
                frame_np = np.frombuffer(byte_frame, dtype=np.int16)
                # faz com que o modelo verifique o audio e retorna um score de previsões
                prediction = model.predict(frame_np)
                # pega o score da frase "Hey jarvis"
                score = prediction.get("hey_jarvis", 0)
                # se o score for acima de 0.5 em uma escala de 0 a 1
                if score > 0.5:
                    # reseta o frames command
                    frames_command = []
                    print("WAKE WORD DETECTADA!")
                    # limpa a lista novamente
                    while not audio_queue.empty():
                        audio_queue.get()
                    # reinicia o modelo
                    model = Model()
                    # altera o estado par gravando
                    state = "GRAVANDO"
                    # reseta o tempo de silencio
                    silence = 0

            # se o estado for "GRAVANDO"
            elif state == "GRAVANDO":
                # adiciona um byte frame na lista
                frames_command.append(byte_frame)
                # verifica se está gravando audio
                is_speech = vad.is_speech(byte_frame, sample_rate)

                # se não estiver falando adiciona 1 a lista
                if not is_speech:
                    silence += 1
                    # imprime de 10 em 10 o tempo em silencio
                    if silence % 10 == 0: print(f"Silêncio: {silence}")
                    # se o contador de silencio for igual a 50
                    if silence >= 50:
                        # reseta os frames para serem ignorados
                        ignore_frames = 40
                        # reseta o silencio
                        silence = 0
                        #defino o estado para "ESPERANDO"
                        state = "ESPERANDO"
                        # limpa a lista
                        while not audio_queue.empty():
                            audio_queue.get()
                        # reseta o modelo
                        model = Model()
                        # reseta as previsões do modelo
                        prediction = {}
                        # abre e fecha automaticamente a criação de um arquivo wav com o apelido wf
                        # ele inicia o objeto que vai ser criado com caminho e modo de abertura
                        with wave.open("temp/comand.wav", "wb") as wf:
                            wf.setnchannels(1) # define no wf quantos canais no caso mono
                            wf.setsampwidth(2) # define no wf a largura da amostra em bytes em 2 bytes que equivale a 16bits
                            wf.setframerate(sample_rate) # define no wf a taxa de amostragem no caso 16kHz
                            wf.writeframes(b"".join(frames_command)) # define no wf conteudo do audio pegando os frames
                        print("Áudio salvo em temp/comand.wav!")
                        return "temp/comand.wav"


listen()
