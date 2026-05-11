# OpenAppSkill

Abre um ou mais aplicativos instalados no sistema.

## Parâmetros
- `app_name` (string ou lista): nome do aplicativo. Ex: "firefox", ["firefox", "spotify"]

## Comportamento
- Busca o app nos diretórios de aplicativos do sistema, flatpak e local
- Faz match parcial pelo nome — "fire" encontra "firefox"
- Abre em segundo plano sem travar o Jarvis
- Retorna erro se o app não for encontrado

## Exemplo
```json
{"skill_name": "OpenAppSkill", "params": {"app_name": "firefox"}}
```
