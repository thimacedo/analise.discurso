# STATE
**Status Atual:** Refatoração Épica (Epic Refactor v2.0) CONCLUÍDA. Sistema de IA estabilizado.

**Foco:** Dashboard de Métricas de Workers (v20.1+) e Estabilidade de IA - CONCLUÍDO.

**Implementação Atual:** 
- ✅ Sistema de IA Resiliente (`core/ai_service.py`):
    - Cascata de motores corrigida (Gemini -> Groq -> Ollama).
    - Proteção contra chaves inválidas (Gemini AIza prefix check).
    - Fallback local (Ollama) funcional com modelo dinâmico.
    - Timeouts otimizados (60s para local, 30s para cloud).
- ✅ Configurações Dinâmicas: `load_dotenv(override=True)` no `core/config.py`.
- ✅ Monitoramento PASA: Auditoria forense v16.4 centralizada.
- ✅ Dashboard de Workers: Coleta de métricas e API prontas.

**Erro Resolvido: Comentários sem Texto (Causa Raiz Identificada e Corrigida)**
- **Causa Raiz:** O `InstagramHeadlessScraper` utilizava seletores DOM genéricos (`span[dir="auto"]`) que capturavam nomes de usuários e elementos de navegação como se fossem o texto do comentário. Além disso, o scraper não extraía nem persistia o campo `autor_username`, resultando em registros "anônimos" ou mal atribuídos.
- **Solução:** 
    - Refatoração de `core/instagram_headless.py` para usar extração estruturada (autor + texto) dentro de cada item de lista (`li`).
    - Adição do campo `autor_username` ao payload enviado ao Supabase.
    - Implementação de filtro para evitar captura redundante do nome do autor no campo de texto.
- **Status:** FIX IMPLEMENTADO. Aguardando próximo ciclo de coleta automática para validação definitiva em larga escala.

**Erro Antigo: Supabase Realtime Broadcast Inconsistente (`fetch_pending.py`)** - **RESOLVIDO.**
- A inconsistência foi resolvida, e o `fetch_pending.py` está funcional.

