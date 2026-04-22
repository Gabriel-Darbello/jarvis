# importa o edge_tts para transcrição, os para remoção do audio e subprocess para tocar o audio
import edge_tts, os, subprocess

# Cria a função speak que recebe um dicionario python
async def speak(message):
  # Primeira letra da mensagem do Groq + mensagem completa devido atraso na fala
  TEXT = message[0] + message
  # Voz definida
  VOICE = "pt-BR-AntonioNeural"
  # Arquivo de audio temporario
  OUTPUT_FILE = "temp/audio.mp3"

  # Envia o texto e a voz para a nuvem
  communicate = edge_tts.Communicate(TEXT, VOICE)
  # Salva em um arquivo audio.mp3
  await communicate.save(OUTPUT_FILE)
  # Executa o audio utilizando o programa mpg123 que toca audios via terminal
  subprocess.run(["mpg123", "temp/audio.mp3"])
  # Apaga o audio
  os.remove("temp/audio.mp3")
