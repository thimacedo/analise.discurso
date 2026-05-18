# Design Spec: Sentinela Local Node (PASA v35)

**Data:** 2026-05-14
**Status:** Implementado
**Versão:** 35.0

## 1. Objetivo
Transformar uma máquina local em um nó de processamento resiliente para o projeto Sentinela Democrática, operando de forma serial para otimizar recursos (RAM) e garantindo sincronização prioritária com o Supabase.

## 2. Arquitetura

### 2.1 Orquestrador Serial (`local_server.py`)
- **Modo de Operação:** Execução sequencial de tarefas (Sincronização -> Raspagem -> Processamento IA).
- **Interface:** "War Room" baseada em terminal, com atualização de status em tempo real.
- **Controle de Ciclo:** Intervalo de 15 minutos entre ciclos para evitar bloqueios de IP e fadiga de recursos.

### 2.2 Camada de Resiliência (`core/offline_cache.py`)
- **Cache Local:** Armazenamento em `data/cache/offline_queue.json` quando o Supabase estiver inacessível.
- **Sincronização:** Tentativa automática de "flush" da fila local no início de cada ciclo.

## 3. Fluxo de Dados
1. O servidor verifica se há dados offline para sincronizar.
2. Consulta a tabela `fila_coleta` no Supabase para identificar o próximo alvo.
3. Executa o `InstagramWorker` para coletar novos comentários.
4. Envia os comentários para a `scripts/mass_classify.py` para processamento via Gemini AI.
5. Entra em estado de espera até o próximo ciclo.

## 4. Requisitos de Sistema
- Python 3.10+
- Acesso à internet para Supabase e Gemini API.
- Variáveis de ambiente configuradas (`.env`).

## 5. Manutenção
- Logs unificados em `logs/worker.log`.
- Cache offline deve ser monitorado se o servidor ficar sem internet por longos períodos.
