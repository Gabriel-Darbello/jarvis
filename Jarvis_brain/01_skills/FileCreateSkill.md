# FileCreateSkill

Cria um arquivo em um caminho especificado, com ou sem conteúdo.

## Parâmetros
- `file_path` (string): caminho completo do arquivo. Ex: "/home/gabriel/programação/pessoal/projeto/arquivo.py"
- `content` (string, opcional): conteúdo inicial do arquivo. Se omitido, cria o arquivo vazio.

## Comportamento
- Cria pastas intermediárias automaticamente se não existirem
- Só opera dentro das zonas permitidas: `~/Área de trabalho` e `~/programação/pessoal`
- Sobrescreve o arquivo se já existir

## Exemplo
```json
{"skill_name": "FileCreateSkill", "params": {"file_path": "/home/gabriel/programação/pessoal/projeto/main.py", "content": "print('hello')"}}
```
