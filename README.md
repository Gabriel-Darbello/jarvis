# Jarvis 🤖

Assistente pessoal ativado por voz para Linux, controlado por comandos em linguagem natural. O Jarvis evoluiu para um agente autônomo modular que utiliza **Programação Orientada a Objetos (POO)** para garantir que cada ação no sistema seja segura, previsível e eficiente.

> Projeto de portfólio — foco em integração de LLMs agênticos, automação de sistemas Linux e processamento local.

---

## 🚀 O que há de novo na V2?

Diferente da primeira versão, o Jarvis agora não apenas executa comandos, mas entende o ambiente:

*   **Sistema de Skills (POO):** As ações (abrir apps, criar arquivos, controlar Git) são classes modulares. Isso impede que a IA "alucine" comandos perigosos e garante que os parâmetros sejam validados antes da execução.
*   **Memória de Curto e Longo Prazo:** O Jarvis mantém o contexto da conversa atual e consegue consultar informações importantes de interações passadas.
*   **Contexto de Janela Ativa:** O assistente sabe qual programa você está usando no momento (ex: VS Code ou Navegador), permitindo comandos como "Jarvis, o que tem de errado nesse código?" com base no contexto real.

---

## Demonstração do fluxo
```
"Hey Jarvis" → Warm-up (esquenta o motor) → Transcreve (Groq) → Raciocínio (Brain) → Skills (POO) → Resposta (TTS)
```

---

## Arquitetura Atual

```
┌─────────────────────────────────────────────────────────────┐
│                        JARVIS V2                            │
│                                                             │
│  [Entrada] ──► Wake Word ──► Groq Whisper (STT)             │
│                                     │                       │
│  [Cérebro] ──► Brain Loop (Qwen 2.5 3B / Llama 3)           │
│                (Raciocínio lógico e decisão de ação)        │
│                                     │                       │
│  [Contexto] ──► Memória + Janela Ativa (xdotool/psutil)     │
│                                     │                       │
│  [Ação]    ──► Executor de Skills (Modulares em POO)        │
│                (FileSkill, GitSkill, SystemSkill)           │
│                                     │                       │
│  [Saída]   ──► Edge-TTS ──► Resposta em voz                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack Técnica

| Componente | Tecnologia | Função |
|---|---|---|
| **Wake Word** | `openwakeword` | Detecção do gatilho "Hey Jarvis" |
| **STT** | Groq Whisper API | Transcrição de áudio em tempo real |
| **LLM Principal** | Qwen 2.5 3B / Llama 3 | Motor de raciocínio e decisão |
| **Lógica de Ação** | Python (POO) | Skills modulares e seguras |
| **Contexto** | `psutil` / `xdotool` | Monitoramento de janelas e hardware |
| **TTS** | `edge-tts` | Síntese de voz natural |

---

## Estrutura do Projeto
```text
jarvis/
├── main.py               # Loop principal e aquecimento do modelo
├── Jarvis.md             # Instruções de sistema e contexto pessoal
├── core/
│   ├── brain.py          # Lógica do agente e gerenciamento de contexto
│   ├── executor.py       # Orquestrador que aciona as skills via JSON
│   └── ...               # Listener, Transcriber e Speaker
├── skills/
│   ├── base.py           # Classe abstrata (Contrato das Skills)
│   ├── system.py         # Controle de aplicações e hardware
│   └── files.py          # Manipulação de arquivos e diretórios
├── requirements.txt
└── README.md
```

---

## Exemplo de Comunicação (JSON)

Para garantir a integridade, o Jarvis se comunica com o sistema através de um formato estruturado:
```json
{
  "finished": false,
  "skill": "SystemSkill",
  "params": {
    "action": "close",
    "app_name": "vscode"
  },
  "message": "Entendido, fechando o VS Code agora."
}
```

---

## Roadmap

### V1 — MVP (Concluído)
- [x] Interface de voz básica e execução de shell simples.

### V2 — Agente Inteligente (Fase Atual)
- [x] **Skills Modulares (POO):** Maior segurança e facilidade de expansão.
- [x] **Memória Persistente:** Curto e longo prazo.
- [x] **Leitura de Contexto:** Identificação de janela ativa.
- [x] **Roteamento de Modelos:** Divisão entre Basic (llama3.2) e Pro (Qwen2.5).
- [ ] **Conversa Dinâmica:** Modo de escuta contínua (VAD).

---

## Instalação e Uso
1. Certifique-se de ter o **Ollama** rodando localmente com o modelo `qwen2.5:3b`.
2. Clone o repositório e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o assistente:
   ```bash
   python main.py
   ```

---

## Licença
MIT
