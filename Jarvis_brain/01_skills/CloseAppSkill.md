# CloseAppSkill

Encerra um ou mais aplicativos pelo nome do processo.

## Parâmetros
- `app_name` (string ou lista): nome do processo a encerrar. Ex: "firefox", ["firefox", "spotify"]

## Comportamento
- Aceita string ou lista de apps
- Processos Python são bloqueados por segurança
- Retorna sucesso com quantidade de processos encerrados, ou erro se não encontrado

## Exemplo
```json
{"skill_name": "CloseAppSkill", "params": {"app_name": "firefox"}}
```
