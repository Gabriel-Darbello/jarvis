# FolderDeleteSkill

Deleta uma pasta e todo seu conteúdo recursivamente. Operação destrutiva — requer confirmação do usuário.

## Parâmetros
- `file_path` (string): caminho completo da pasta a deletar.

## Comportamento
- Só opera dentro das zonas permitidas: `~/Área de trabalho` e `~/programação/pessoal`
- Deleta a pasta e tudo dentro dela sem recuperação
- Retorna erro se o caminho for um arquivo — use FileDeleteSkill nesse caso
- Retorna erro se a pasta não existir

## Exemplo
```json
{"skill_name": "FolderDeleteSkill", "params": {"file_path": "/home/gabriel/programação/pessoal/projeto-antigo"}}
```
