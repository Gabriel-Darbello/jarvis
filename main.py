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
                await speak("Olá como posso ajudar?")
                voice_command, model_v1 = record_command()
                command = transcribe(voice_command)
                print(command)
                agent_response = agent(command, messages)
                while True:
                    # executa ação e salva o resultado
                    if agent_response.get("action"):
                        if agent_response["action"].get("destructive"):

                            await speak(agent_response["message"] or "Atenção, comando perigoso detectado. Devo prosseguir?")
                            voice_confirm, _ = record_command()
                            confirm_text = transcribe(voice_confirm)
                            print(confirm_text)
                            confirm_words = ["sim", "pode", "prossiga", "confirmado", "deve"]

                            if any(word in confirm_text.lower() for word in confirm_words):
                                result = execute_action(agent_response["action"])
                                messages.append({ "role": "user", "content": f"resultado da ação {result}"})
                                agent_response = agent(None, messages)
                                continue
                            else:
                                await speak("Comando cancelado")
                                messages[:] = [messages[0]]
                                break

                        result = execute_action(agent_response["action"])
                        messages.append({ "role": "user", "content": f"resultado da ação {result}"})
                        agent_response = agent(None, messages)

                    # reseta a lista de mensagens para o estado anterior para reduzir consumo de tokens
                    if agent_response.get("finished") and messages:
                        speak_message = agent_response.get("message")
                        if speak_message:
                            await speak(agent_response["message"])
                        messages[:] = [messages[0]]
                        break

                    if not agent_response.get("action") and not agent_response.get("finished"):
                        print("Erro de estado: IA não definiu próximo passo. Encerrando ciclo.")
                        break                                # se houver terminado ele fala

            except Exception as error:
                print(f"Erro crítico no loop do Jarvis: {type(error).__name__} - {error}")
                await speak("Ocorreu um erro interno no meu sistema, senhor. Reiniciando módulos.")
                messages = []

if __name__ == "__main__":
   asyncio.run(main())
