# Jarvis 🤖

Assistente pessoal ativado por voz para Linux, controlado por comandos em linguagem natural. Jarvis executa ações no sistema operacional, gerencia projetos, roda comandos Git, controla janelas e muito mais — tudo por voz.

> Projeto de portfólio — desenvolvido para demonstrar integração de STT, LLM agêntico e automação de sistema no Linux.

---

## Demonstração do fluxo

```
"Hey Jarvis" → grava áudio → transcreve → LLM raciocina → executa → responde por voz
```

Exemplo de comando:

> *"Jarvis, envia as mudanças do Projeto pro GitHub"*

O que acontece por baixo:
1. Detecta a janela ativa → identifica o projeto
2. Roda `git status` e `git diff` → lê as mudanças
3. Monta a mensagem de commit seguindo Conventional Commits (definido no `Jarvis.md`)
4. Executa `git add . && git commit -m "..." && git push`
5. Fala: *"Mudanças enviadas com sucesso!"*

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        JARVIS V1                            │
│                                                             │
│  [Microfone] ──► OpenWakeWord ──► sounddevice grava         │
│                                         │                   │
│                                    webrtcvad                │
│                                 (detecta silêncio)          │
│                                         │                   │
│                                  Groq Whisper               │
│                               (áudio → texto)               │
│                                         │                   │
│                    Jarvis.md ──► Groq LLaMA  ◄──────────┐   │
│                                         │               │   │
│                                   JSON response         │   │
│                              { finished, action,        │   │
│                                message }                │   │
│                                         │               │   │
│                               finished? ─── false ──────┘   │
│                                  │ true                     │
│                         Python executa action               │
│                       subprocess.run(command)               │
│                                         │                   │
│                                    edge-tts                 │
│                               (texto → voz)                 │
└─────────────────────────────────────────────────────────────┘
```

### Loop agêntico

O Jarvis não executa apenas um comando por vez. Quando necessário, ele opera em loop:

1. Groq retorna `finished: false` com uma `action` para buscar informação
2. Python executa e devolve o output para o Groq
3. Groq analisa o resultado e decide o próximo passo
4. Repete até `finished: true`

Isso permite tarefas como: *"commita o projeto"* — onde ele precisa primeiro identificar o projeto, ler as mudanças, montar a mensagem e só então executar o commit.

### Segurança

Comandos destrutivos (`rm`, `sudo`, `mkfs`, `dd`, `chmod`) exigem confirmação por voz antes de serem executados. Isso evita que alucinações do modelo causem danos ao sistema.

---

## Stack

| Componente | Biblioteca | Função |
|---|---|---|
| Wake word | `openwakeword` | Detecta "Hey Jarvis" |
| Captura de áudio | `sounddevice` | Grava do microfone |
| Detecção de silêncio | `webrtcvad` | Para a gravação automaticamente |
| STT | Groq Whisper API | Transcreve áudio para texto |
| LLM | Groq LLaMA 3.3 70B | Interpreta e raciocina |
| Contexto | `Jarvis.md` | Configuração, projetos, convenções |
| Execução | `subprocess` (Python) | Roda comandos no sistema |
| TTS | `edge-tts` | Resposta em voz natural |

---

## Estrutura do projeto

```
jarvis/
├── main.py               # Loop principal: wake word → STT → LLM → ação → TTS
├── Jarvis.md             # Contexto pessoal, projetos e instruções do assistente
├── core/
│   ├── listener.py       # OpenWakeWord + sounddevice + webrtcvad
│   ├── transcriber.py    # Integração com Groq Whisper
│   ├── brain.py          # Loop agêntico com Groq LLaMA
│   ├── executor.py       # subprocess + validação de comandos destrutivos
│   └── speaker.py        # edge-tts
├── requirements.txt
└── README.md
```

---

## Jarvis.md

O arquivo `Jarvis.md` é o coração da configuração do Jarvis. Ele é injetado no system prompt a cada requisição, dando ao modelo contexto sobre quem você é, seus projetos e suas regras.

Exemplo de estrutura:

```markdown
# Jarvis — Contexto Pessoal

## Sobre mim
- Nome: Gabriel
- Sistema: Linux Mint
- Shell: bash

## Convenções
### Git — Conventional Commits
- Formato: tipo(escopo): descrição
- Tipos: feat, fix, docs, chore, refactor, test
- Sempre em inglês, imperativo

## Comportamento esperado
- Respostas diretas e técnicas
- Sempre verificar o projeto ativo antes de rodar git
- Pedir confirmação antes de comandos destrutivos
```

---

## Formato JSON esperado do LLM

```json
{
  "finished": false,
  "action": {
    "type": "shell",
    "command": "git -C ~/projetos/roadup status",
    "destructive": false
  },
  "message": null
}
```

```json
{
  "finished": true,
  "action": null,
  "message": "Commit enviado com sucesso!"
}
```

---

## Roadmap

### V1 — MVP (escopo atual)
- [x] Arquitetura definida
- [ ] Wake word com OpenWakeWord
- [ ] Gravação e detecção de silêncio
- [x] Transcrição via Groq Whisper
- [x] Loop agêntico com Groq LLaMA
- [x] Execução de comandos via subprocess
- [ ] Confirmação de comandos destrutivos por voz
- [x] Resposta em voz com edge-tts
- [x] Jarvis.md como contexto persistente

 ### V2 — Controle e leitura de interfaces gráficas

- [ ] Sistema de skills modulares
- [ ] Modo offline com modelo local (fallback)
- [ ] Controle de janelas avançado (wmctrl / xdotool)
- [ ] Controle de mouse utilizando automações como pyautogui ou outras coisas
- [ ] Leitura da tela do computador para ler erros, entender imagens e etc

---

## Pré-requisitos

- Linux (testado no Linux Mint)
- Python 3.10+
- Conta gratuita na [Groq](https://console.groq.com)
- Microfone

---

## Instalação

```bash
git clone https://github.com/seu-usuario/jarvis
cd jarvis
pip install -r requirements.txt
cp Jarvis.md.example Jarvis.md  # edite com seus dados
```

Configure a variável de ambiente:

```bash
export GROQ_API_KEY="sua_chave_aqui"
```

Execute:

```bash
python main.py
```

---

## Licença

MIT
