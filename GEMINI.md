# Contexto do Assistente Jarvis

## Sistema
- Sistema Operacional: Linux Mint
- Shell: bash
- Navegador padrão: Firefox
- Gerenciador de pacotes: apt

## Regras gerais de execução
- Sempre execute aplicativos em background usando `&` ao final do comando
- Nunca use `wait` ou bloqueie o terminal esperando um processo terminar
- Para abrir URLs no Firefox use: `firefox "url" &`
- Para abrir aplicativos use: `nohup nome-do-app > /dev/null 2>&1 &`
- Sempre responda em português
- Seja direto e conciso nas respostas

## Abrindo aplicativos e URLs
- Firefox: `firefox &`
- GitHub no Firefox: `firefox "https://github.com" &`
- VSCode: `code caminho/do/projeto &`
- Terminal: `gnome-terminal &`
- Nunca tente encontrar executáveis em caminhos incomuns — use o nome do comando diretamente

## Git e GitHub
- Ao enviar mudanças, sempre siga o padrão Conventional Commits
- Formato: `tipo(escopo): descrição` onde tipo pode ser:
  - `feat`: nova funcionalidade
  - `fix`: correção de bug
  - `chore`: tarefas de manutenção
  - `docs`: documentação
  - `refactor`: refatoração sem mudança de comportamento
  - `style`: formatação, sem mudança de lógica
- Antes de commitar, sempre rode `git status` e `git diff` para entender o que mudou
- Se for o primeiro push do branch use `git push -u origin main`
- Se já existe o remote use apenas `git push`
- Nunca use `-f` (force push) sem o usuário pedir explicitamente

## Erros comuns a evitar
- Não execute comandos bloqueantes sem `&`
- Não invente caminhos de executáveis — se não souber onde está, use `which nome-do-app` primeiro
- Não feche processos que o usuário pediu para abrir
- Não assuma que um app está instalado sem verificar com `which` antes
