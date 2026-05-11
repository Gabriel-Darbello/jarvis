# FileDeleteSkill

Deleta um arquivo. Operação destrutiva — requer confirmação do usuário.

## Parâmetros
- `file_path` (string): caminho completo do arquivo a deletar.

## Comportamento
- Só opera dentro das zonas permitidas: `~/Área de trabalho` e `~/programação/pessoal`
- Retorna erro se o caminho for uma pasta — use FolderDeleteSkill nesse caso
- Retorna erro se o arquivo não existir

## Exemplo
```json
{"skill_name": "FileDeleteSkill", "params": {"file_path": "/home/gabriel/programação/pessoal/projeto/arquivo.py"}}
```
