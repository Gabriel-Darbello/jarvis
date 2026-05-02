from core.speaker import speak
from core.listener import record_command
from core.transcriber import transcribe

async def voice_confirm(llm_response):
    await speak(llm_response)
    audio, _ = record_command()
    texto = transcribe(audio)
    confirm_words = ["sim", "pode", "prossiga", "confirmado", "deve"]
    return any(word in texto.lower() for word in confirm_words)
