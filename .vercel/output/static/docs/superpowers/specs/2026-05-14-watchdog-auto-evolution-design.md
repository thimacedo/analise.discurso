# Design Spec: Nó Guardião e Auto-Evolução (PASA v37)

**Data**: 2026-05-14
**Status**: IMPLEMENTADO
**Autor**: Gemini CLI

## 1. Objetivo
Garantir que o Servidor de Raspagem Local seja imortal (auto-resurrect) e capaz de evoluir remotamente (auto-update) sem intervenção manual no terminal.

## 2. Arquitetura

### 2.1 Watchdog (`watchdog.py`)
- **Função**: Processo mestre que executa e monitora o `local_server.py`.
- **Resiliência**: Se o servidor travar por erro não tratado, o Watchdog aguarda 30s e o reinicia automaticamente.
- **Comando de Inicialização**: O operador agora deve rodar `python watchdog.py` em vez de `local_server.py`.

### 2.2 Auto-Updater (`core/auto_updater.py`)
- **Função**: Verifica a tabela `system_directives` no Supabase buscando comandos remotos.
- **Capacidades**:
  - `UPDATE_REPO`: Executa `git pull` e `pip install` para baixar melhorias de código.
  - `CHANGE_CONFIG`: Atualiza configurações de runtime (como tempos de pausa) dinamicamente.
  - `RESTART`: Força um reinício gracioso do servidor.

## 3. Interface Remota
O operador pode inserir um registro na tabela `system_directives` pelo Dashboard ou Supabase Studio para forçar o nó local a atualizar ou reiniciar, garantindo controle total à distância.
