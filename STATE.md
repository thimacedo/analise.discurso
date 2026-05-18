# 📊 STATE.md - Sentinela Democrática

**Última Atualização:** 2026-05-18
**Versão Core:** PASA v49.8 (Diamond Real Data)
**Status do Sistema:** Operação Real Ativada (Zero Mocks)

## 1. Estado Atual do Ecossistema
O Sentinela Democrática concluiu a transição para o pipeline de dados 100% reais. O Nó Local (War Room) agora opera com coleta ativa via Playwright, processamento de IA em massa (Gemini/Groq) e auditoria anti-alucinação. Todas as simulações e dados fictícios foram removidos do repositório.

## 2. Componentes Principais (v49.8)

### Nó Local & Coleta (Real)
- **InstagramWorker:** Ativado com motor Playwright (`scraper_headless.py`). Realiza raspagem via navegação por modal e extração de comentários autênticos.
- **Scrapy Standby:** Motor Scrapy disponível em `InstagramScrapyWorker` para volumes massivos (mantido OFF).
- **Integridade:** Monitor de API (`api/monitor.py`) blindado contra dados fake; reporta erro ou zero em falhas no Supabase.

### Inteligência Analítica
- **Classificação IA:** Motor real ativado via `AIService` (Gemini 1.5 Flash + Groq Cascading).
- **CCF Framework:** Classificação baseada em Densidade, Sincronia e Performatividade.
- **Auditoria:** `AuditWorker` ativo para verificação cruzada e detecção de deriva (Drift Check).

### Governança e Interface
- **War Room UI:** Redesenhada para visual sutil e moderno com cores ANSI e logs em tempo real.
- **Watchdog:** Guardião ativo com auto-cura de dependências e alertas via WhatsApp (CallMeBot).

### Resiliência e Checkpointing (Novo)
- **State Manager:** Motor de persistência leve (`core/state_manager.py`) implementado para combate a OOM e crashes.
- **Recuperação Automática:** O `local_server.py` detecta quedas anormais, identifica o alvo que causou o crash e o pula na reinicialização para evitar loops de OOM.
- **Escrita Atômica:** Os estados são salvos via `os.replace`, garantindo que arquivos de checkpoint nunca corrompam em caso de falha no exato momento da escrita.
- **Memória de Ciclo:** Retoma a contagem de perfis raspados no ciclo atual, evitando retrabalho após reinício.

## 3. Proteções Jurídicas e Acadêmicas
- **MCA v2.2:** Manual de Classificação Analítica consolidado.
- **Terminologia:** Uso estrito de "Indícios Analíticos" e "Informação Situacional" para evitar conflitos forenses.
