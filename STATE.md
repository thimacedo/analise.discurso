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

**Erro Ativo: Supabase Realtime Broadcast Inconsistente (`fetch_pending.py`)**
- **Descrição:** O script `fetch_pending.py` falha ao tentar processar comentários devido a um erro de broadcast no Supabase Realtime. O erro específico original reportado era `42883: function realtime.broadcast_changes(...) does not exist`, mas a investigação revelou que a função existe. A causa raiz parece estar relacionada à configuração do Realtime, autorização e/ou invocações incorretas.
- **Contexto da Investigação:**
    - A função `realtime.broadcast_changes()` *existe* no schema `realtime`.
    - O trigger `realtime_broadcast_comentarios` (mencionado inicialmente) *não foi encontrado* associado à tabela `comentarios`.
    - A tabela `comentarios` está publicada na publicação `supabase_realtime`.
    - RLS está habilitado na tabela `public.comentarios`.
    - Políticas RLS *não estavam* configuradas na tabela `realtime.messages` (essencial para autorização de broadcast).
- **Tentativas de Resolução:**
    - Listagem de funções no schema `realtime` confirmou a existência de `realtime.broadcast_changes()`.
    - Listagem de triggers na tabela `public.comentarios` não encontrou um trigger com nome `realtime_broadcast_comentarios` ou similarmente relacionado a broadcast.
    - Verificação da publicação `supabase_realtime` confirmou que `public.comentarios` está incluída.
    - Verificação de RLS em `public.comentarios` confirmou que está habilitado.
    - Verificação de RLS em `realtime.messages` revelou que *nenhuma política estava definida*.
    - Tentativas de criar a política RLS `authenticated can receive broadcasts` na tabela `realtime.messages` usando `npx supabase db query` ou `npx supabase db execute` falharam devido a comandos não reconhecidos ou erros de sintaxe/formato na CLI do Supabase.
- **Estado Atual:** O problema persiste pois a política RLS essencial para autorização de broadcast não pôde ser aplicada via CLI. A causa raiz do erro `42883` ainda não está totalmente clara, mas a falta de RLS em `realtime.messages` é um fator crítico.
- **Próximos Passos Sugeridos:**
    1.  **Aplicação Manual da Política RLS:** Instruir o usuário ou encontrar um método alternativo para criar a política RLS em `realtime.messages` (ex: via Supabase Dashboard ou `psql` se credenciais forem obtidas).
    2.  **Investigar Triggers Existentes:** Procurar por triggers na tabela `public.comentarios` que possam estar tentando invocar `realtime.broadcast_changes()` ou similar, mesmo que com nome diferente.
    3.  **Revisar Configurações de Realtime:** Consultar o Supabase Dashboard para verificar as configurações de Realtime Broadcast para a tabela `comentarios` e o schema `realtime`.
    4.  **Modularização e Documentação:** Documentar as descobertas, o problema da CLI e as etapas de resolução.

