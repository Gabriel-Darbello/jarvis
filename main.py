import asyncio
import sounddevice as sd
import warnings
from core.listener import *
from core.brain import agent
from core.speaker import speak
from core.transcriber import transcribe
from core.executor import execute_action

# Silencia avisos de bibliotecas de terceiros
warnings.filterwarnings("ignore", category=UserWarning)

async def main():
    # instancia o modelo
    model_v1 = Model()
    # cria um array messages vazio
    messages = []
    # abre um canal de microfone mono tipo float32
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
    blocksize=frame_size, callback=callback):
        while True:
            try:
                model_v1 = await_wake_word(model_v1)
                voice_command, model_v1 = record_command()
                command = transcribe(voice_command)
                print(command)
                agent_response = agent(command, messages)
                while True:
                    # executa ação e salva o resultado
                    if agent_response.get("action"):
                        result = execute_action(agent_response["action"])
                        messages.append({ "role": "user", "content": f"resultado da ação {result}"})
                        agent_response = agent(None, messages)
                        continue

                    # se não houver ação ele fala
                    speak_message = agent_response.get("message")
                    if speak_message:
                        await speak(agent_response["message"])

                    # reseta a lista de mensagens para o estado anterior para reduzir consumo de tokens
                    if agent_response.get("finished") and messages:
                        messages[:] = [messages[0]]
                        break

            except Exception as error:
                print(error)

if __name__ == "__main__":
   asyncio.run(main())
