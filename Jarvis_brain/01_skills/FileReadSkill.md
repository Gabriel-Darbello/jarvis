# FileReadSkill

Lê o conteúdo de um arquivo de texto.

## Parâmetros
- `file_path` (string): caminho completo do arquivo a ler.

## Comportamento
- Só opera dentro das zonas permitidas: `~/Área de trabalho` e `~/programação/pessoal`
- Lê no máximo 10.000 caracteres
- Retorna o conteúdo bruto do arquivo

## REGRA CRÍTICA
Após receber o resultado desta skill, analise o conteúdo e responda ao usuário.
Nunca chame FileReadSkill e responda ao usuário na mesma iteração.

## Exemplo
```json
{"skill_name": "FileReadSkill", "params": {"file_path": "/home/gabriel/programação/pessoal/projeto/main.py"}}
```
