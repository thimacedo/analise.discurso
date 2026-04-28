# ROADMAP - Sentinela Democrática

## Status: v18.0.0 (The Backend Unification)
- **Refatoração Crítica**: Remoção de 6 scripts redundantes. Unificação em 3 workers robustos (`text_processor.py`, `data_miner.py`, `report_generator.py`).
- **Scrapy Migration**: Substituição de dependências pagas (RapidAPI) e instáveis (GraphQL Hashes) por coleta nativa Scrapy + REST API.
- **Correção de Encoding**: Resolvido bug histórico de acentuação nos PDFs através da migração para `fpdf2` + fontes TTF.
- **Performance KMeans**: Adicionado segurança matemática contra crash por falta de amostras no clusterizador.

## Próximos Passos (v19.0.0)
- [ ] **Worker de IA (PASA Classifier)**: Integrar `ollama_intelligence.py` ou Groq para popular a coluna `is_hate_speech` e `categoria_ia` no banco.
- [ ] **Orquestrador (Airflow/Cron)**: Integrar o `main.py` do Scrapy com os Workers de NLP em uma pipeline única e automatizada.
- [ ] **Segurança (Proxy API)**: Remover a injeção direta do `SUPABASE_KEY` no frontend, criando um proxy Python (FastAPI) para servir os dados ao `ui.js`.
- [ ] **UI Cross-Reference**: Atualizar o motor frontend para consumir as colunas renomeadas (`owner_username`, `post_shortcode`).

---
*Atualizado em 28/04/2026 - Refletindo a arquitetura real do código.*
