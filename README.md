# Assistente Gemini (Jarvis)

Este projeto é um assistente de voz inteligente que integra reconhecimento de fala, processamento de linguagem natural e automação local. Ele é capaz de detectar comandos de voz, entender o contexto do que você está fazendo no VSCode e executar ações via Gemini CLI.

## 🚀 Funcionalidades

- **Wake Word Detection:** Ativação por voz com "Hey Jarvis" usando `openwakeword`.
- **Transcrição de Alta Precisão:** Utiliza a API Whisper da Groq para transformar fala em texto.
- **Contexto Inteligente:** Detecta automaticamente qual projeto está aberto no VSCode para contextualizar as respostas.
- **Integração com Gemini CLI:** Envia comandos para o modelo Gemini para execução de tarefas.
- **Voz Neural:** Respostas em áudio com vozes naturais via Microsoft Edge TTS.
- **Feedback Sonoro:** Beeps de confirmação de gravação.

## 🛠️ Requisitos

- Python 3.10+
- `xdotool` (para detecção de janela ativa no Linux)
- Chave de API da [Groq](https://console.groq.com/)
- Gemini CLI instalado e configurado

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Assistente-gemini.git
   cd Assistente-gemini
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   GROQ_API_KEY=sua_chave_aqui
   ```

## 🎮 Como Usar

Basta rodar o script principal:

```bash
python main.py
```

O assistente ficará em standby. Diga **"Hey Jarvis"**, espere o sinal e fale seu comando.

## 📂 Estrutura do Projeto

- `main.py`: Loop principal de escuta e coordenação.
- `processor.py`: Lógica de transcrição, TTS e detecção de contexto.
- `requirements.txt`: Dependências do Python.
- `GEMINI.md`: Regras de contexto para o agente.
