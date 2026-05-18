from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

async def speak(message):
    load_dotenv()
    elevenlabs = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
    )

    audio = elevenlabs.text_to_speech.convert(
        text=message,
        voice_id="z8nSmGenK7262wkXE6gb",
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )

    play(audio)
