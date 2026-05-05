import asyncio
import sounddevice as sd
import warnings
from core.listener import *
from core.brain import JarvisBrain
from core.speaker import speak
from core.transcriber import transcribe
from core.voice_confirm import voice_confirm

async def main():
    warnings.filterwarnings("ignore", category=UserWarning)
    agent = JarvisBrain("llama3.2:3b-instruct-q4_0")
    model_v1 = Model()

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
    blocksize=frame_size, callback=callback):
        while True:
            try:
                model_v1 = await_wake_word(model_v1)
                await speak("Olá como posso ajudar?")

                voice_command, model_v1 = record_command()
                command = transcribe(voice_command)
                print(f"Comando: {command}")

                agent_response = await agent.process_logic(command, voice_confirm)

                print(agent_response)
                await speak(agent_response)

            except Exception as error:
                print(f"Erro crítico no loop do Jarvis: {type(error).__name__} - {error}")
                await speak("Ocorreu um erro interno no meu sistema.")

if __name__ == "__main__":
   asyncio.run(main())
