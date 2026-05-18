# Jarvis 🤖

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=flat&logo=linux&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

Assistente pessoal ativado por voz para Linux, controlado por comandos em linguagem natural. Diga **"Hey Jarvis"** e controle seu sistema com a voz — abra e feche aplicativos, gerencie arquivos e pastas, tudo com raciocínio real por trás de cada ação.

> Projeto de portfólio — foco em integração de LLMs agênticos, automação de sistemas Linux e arquitetura modular com POO.

---

## O que há de novo na V2?

A V1 executava comandos shell diretamente. A V2 é um agente real:

- **Skills modulares (POO):** cada ação do sistema é uma classe com parâmetros validados. O modelo nunca executa shell livre — ele chama uma skill com parâmetros estruturados. Isso elimina alucinações perigosas.
- **Memória de curto e longo prazo:** o Jarvis mantém o contexto da conversa atual e consulta informações de interações passadas quando necessário.
- **Contexto de janela ativa:** o assistente sabe qual programa você está usando no momento via `xdotool` e `psutil`, permitindo comandos como *"o que tem de errado nesse código?"* com base no que está na tela.
- **Conversa dinâmica:** modo de escuta contínua com VAD — sem precisar chamar o wake word a cada turno durante uma conversa.

---

## Demonstração do fluxo

```
"Hey Jarvis" → Groq Whisper (STT) → Brain (LLaMA 3.3 70B) → Skill (POO) → ElevenLabs (TTS)
```

Exemplo de comando:
> *"Jarvis, fecha o VS Code e abre o navegador"*

O que acontece por baixo:

1. Groq Whisper transcreve o áudio
2. LLaMA 3.3 70B interpreta a intenção e retorna JSON estruturado
3. Executor aciona `SystemSkill` com `action: close, app_name: vscode`
4. Em seguida aciona `SystemSkill` com `action: open, app_name: browser`
5. ElevenLabs responde em voz: *"Feito!"*

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        JARVIS V2                            │
│                                                             │
│  [Microfone] ──► OpenWakeWord ──► sounddevice grava         │
│                                         │                   │
│                                    webrtcvad                │
│                                 (detecta silêncio)          │
│                                         │                   │
│                                  Groq Whisper               │
│                               (áudio → texto)               │
│                                         │                   │
│               Jarvis.md + Memória ──► LLaMA 3.3 70B         │
│               Janela ativa (xdotool)        │               │
│                                         │                   │
│                                   JSON response             │
│                          { skill, params, message }         │
│                                         │                   │
│                               Executor de Skills            │
│                        ┌────────────────┴──────────────┐    │
│                   SystemSkill                      FileSkill │
│               (apps, janelas)              (arquivos, pastas)│
│                                                             │
│                                        ElevenLabs (TTS)     │
└─────────────────────────────────────────────────────────────┘
```

### Por que Skills em POO?

Na V1 o modelo retornava comandos shell livres (`subprocess.run`). O problema: LLMs alucinam, e um comando errado pode deletar arquivos sem querer.

Na V2 o modelo só pode chamar skills com parâmetros definidos. Antes de executar qualquer coisa, os parâmetros são validados pela classe. Ações destrutivas como deletar arquivos e pastas exigem confirmação por voz.

---

## Stack

| Componente | Tecnologia | Função |
|---|---|---|
| Wake word | `openwakeword` | Detecta "Hey Jarvis" |
| Captura de áudio | `sounddevice` | Grava do microfone |
| Detecção de silêncio | `webrtcvad` | Para a gravação automaticamente |
| STT | Groq Whisper API | Transcreve áudio para texto |
| LLM | Groq LLaMA 3.3 70B | Interpreta, raciocina e decide |
| Contexto | `Jarvis.md` + memória | Configuração, histórico e instruções |
| Janela ativa | `xdotool` + `psutil` | Identifica o app em foco |
| Skills | Python (POO) | Execução segura e validada |
| TTS | ElevenLabs | Resposta em voz natural |

---

## Estrutura do projeto

```
jarvis/
├── main.py               # Loop principal: wake word → STT → brain → skill → TTS
├── Jarvis.md             # Contexto pessoal, projetos e instruções do assistente
├── Jarvis.md.example     # Exemplo de configuração para novos usuários
├── core/
│   ├── listener.py       # OpenWakeWord + sounddevice + webrtcvad
│   ├── transcriber.py    # Integração com Groq Whisper
│   ├── brain.py          # Agente LLaMA 3.3 70B + gerenciamento de memória
│   ├── executor.py       # Orquestrador de skills via JSON
│   └── speaker.py        # ElevenLabs TTS
├── skills/
│   ├── base.py           # Classe abstrata — contrato de todas as skills
│   ├── system.py         # SystemSkill: apps e janelas
│   └── files.py          # FileSkill: arquivos e pastas
├── requirements.txt
└── README.md
```

---

## Formato JSON esperado do LLM

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

```json
{
  "finished": true,
  "skill": null,
  "params": null,
  "message": "Feito!"
}
```

---

## Pré-requisitos

- Linux (testado no Linux Mint)
- Python 3.10+
- Conta na [Groq](https://console.groq.com) (gratuita)
- Conta na [ElevenLabs](https://elevenlabs.io) (gratuita)
- `xdotool` instalado no sistema:

```bash
sudo apt install xdotool
```

---

## Instalação

```bash
git clone https://github.com/Gabriel-Darbello/jarvis
cd jarvis
pip install -r requirements.txt
cp Jarvis.md.example Jarvis.md  # edite com seus dados
```

Configure as variáveis de ambiente:

```bash
export GROQ_API_KEY="sua_chave_aqui"
export ELEVENLABS_API_KEY="sua_chave_aqui"
```

Execute:

```bash
python main.py
```

---

## Jarvis.md

O `Jarvis.md` é injetado no system prompt a cada requisição — é onde você configura quem o Jarvis é, seus projetos e suas regras.

```markdown
# Jarvis — Contexto Pessoal

## Sobre mim
- Nome: Gabriel
- Sistema: Linux Mint
- Shell: bash

## Comportamento esperado
- Respostas diretas e técnicas
- Confirmar antes de qualquer ação destrutiva
- Identificar o projeto ativo antes de ações relacionadas a código
```

---

## Roadmap

### V1 — MVP (Concluído)
- [x] Wake word com OpenWakeWord
- [x] Gravação e detecção de silêncio com webrtcvad
- [x] Transcrição via Groq Whisper
- [x] Execução de comandos via subprocess
- [x] Confirmação de comandos destrutivos por voz
- [x] Resposta em voz com ElevenLabs
- [x] Jarvis.md como contexto persistente

### V2 — Agente Inteligente (Concluído)
- [x] Skills modulares em POO
- [x] Memória de curto e longo prazo
- [x] Leitura de janela ativa (xdotool + psutil)
- [x] Conversa dinâmica sem wake word a cada turno

### V3 — Próximas features
- [ ] Action de commit automático no GitHub
- [ ] Integração com IA de visão (leitura de imagens na tela)
- [ ] Web scraping por voz

---

## Licença

MIT
