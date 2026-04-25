import asyncio
import sounddevice as sd
from core.listener import *
from core.brain import agent
from core.speaker import speak
from core.transcriber import transcribe

async def main():
    model_v1 = Model()
    print("Iniciando teste do Jarvis...")
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
    blocksize=frame_size, callback=callback):
        while True:
            try:
                model_v1 = await_wake_word(model_v1)
                voice_command, model_v1 = record_command()
                command = transcribe(voice_command)
                print(command)
                agent_response = agent(command)
                print(agent_response)
                await speak(agent_response["message"])
            except Exception as error:
                print(error)

if __name__ == "__main__":
   asyncio.run(main())
