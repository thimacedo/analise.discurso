# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.7.3 (Turbo Mode & Chunk Persistence)
- **Data da última atualização:** 30/04/2026
- **Status:** Pipeline ultra-resiliente. Aguardando renovação de Session ID do Instagram para expandir corpus.

## ✅ O que está funcionando
- **Modo Turbo (Ollama):** Modelo `llama3.2` configurado para processamento local instantâneo em CPU.
- **Persistência em Tempo Real:** Comentários classificados são salvos no Supabase imediatamente (Fim da perda de dados em crash).
- **Filtro de IA Corrigido:** Orquestrador usa `not.eq.true` para capturar comentários com `processado_ia = NULL`.
- **Blindagem Scrapy:** Delay de 5s e concorrência 1 para evitar banimento do Instagram.
- **Fila Circular Inteligente:** TargetManager prioriza os 15 perfis mais antigos/nulos por ciclo.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] Llama3 pesado no Ollama:** Muito lento para volume. Substituído por Llama 3.2.
- **[DESCARTADO] Persistência em Lote (Batch no final):** Risco de perda de dados. Substituído por salvamento individual em tempo real.

## 🐛 Bugs Atuais / Bloqueios
- **Bloqueio Instagram:** `sessionid` expirado. Necessário atualizar o `.env` com novo cookie de conta focalizadora para raspar os 245 alvos restantes.
