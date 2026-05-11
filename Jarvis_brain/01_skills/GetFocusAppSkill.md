# GetFocusAppSkill

Retorna informações sobre a janela ativa no momento.

## Parâmetros
Nenhum parâmetro necessário.

## Retorno
- `titulo`: título da janela ativa
- `app`: nome do processo
- `resumo`: descrição em texto do que está em foco

## Uso típico
Use antes de operações que dependem do contexto atual, como "o que eu tenho aberto?" ou "analisa o que estou vendo".

## Exemplo
```json
{"skill_name": "GetFocusAppSkill", "params": {}}
```
