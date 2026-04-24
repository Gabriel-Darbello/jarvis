import asyncio
from core.brain import agent
from core.speaker import speak
from core.listener import listen
from core.transcriber import transcribe

async def main():
    print("🚀 Iniciando teste do Jarvis...")
    voice_command = listen()
    print(voice_command)
    command = transcribe(voice_command)
    print(command)
    agent_response = agent(command)
    print(agent_response)
    await speak(agent_response["message"])

if __name__ == "__main__":
    while True:
        asyncio.run(main())
