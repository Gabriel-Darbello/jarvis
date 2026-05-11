# FileAppendSkill

Adiciona conteúdo ao final de um arquivo existente.

## Parâmetros
- `file_path` (string): caminho completo do arquivo.
- `content` (string): conteúdo a adicionar.

## Comportamento
- Só opera dentro das zonas permitidas: `~/Área de trabalho` e `~/programação/pessoal`
- O arquivo precisa existir — use FileCreateSkill primeiro se necessário
- Adiciona o conteúdo em nova linha no final do arquivo

## Exemplo
```json
{"skill_name": "FileAppendSkill", "params": {"file_path": "/home/gabriel/programação/pessoal/projeto/notas.md", "content": "nova linha aqui"}}
```
