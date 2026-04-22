import asyncio
from core.brain import agent
from core.speaker import speak

async def test_drive():
    print("🚀 Iniciando teste do Jarvis...")
    # O comando precisa ser específico para testar o entendimento de contexto
    comando = "Jarvis, verifique as mudanças no projeto jarvis e faça um commit seguindo o padrão conventional commits, depois envie para o GitHub."

    resposta = agent(comando)

    print(f"\n✅ Jarvis Finalizou!")
    print(f"Mensagem: {resposta['message']}")

    # Chama a sua função de voz
    await speak(resposta["message"])

if __name__ == "__main__":
    asyncio.run(test_drive())
