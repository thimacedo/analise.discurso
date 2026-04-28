# ROADMAP - Sentinela Democrática

## Status: v18.5.0 (The Pipeline Integration)
- **Refatoração Crítica**: Remoção de 6 scripts redundantes. Unificação em 3 workers robustos (`text_processor.py`, `data_miner.py`, `report_generator.py`).
- **Orquestração**: Implementado `orquestrador.py` e integrado ao `worker_sentinela.py`, unificando Extração (Scrapy), IA (Qwen/PASA), NLP e Relatórios.
- **Scrapy Migration**: Substituição de dependências pagas (RapidAPI) por coleta nativa Scrapy + REST API.
- **Correção de Encoding**: Resolvido bug histórico de acentuação nos PDFs através da migração para `fpdf2` + fontes TTF.
- **Critérios PASA**: Criado `CRITERIOS_TREINAMENTO.md` baseado no Protocolo PASA v16.4 para balizar a IA.

## Próximos Passos (v19.0.0)
- [ ] **Segurança (Proxy API)**: Remover a injeção direta do `SUPABASE_KEY` no frontend, criando um proxy Python (FastAPI) para servir os dados ao `ui.js`.
- [ ] **Dashboard Avançado**: Integrar `PredictiveTrends.js` e `BrazilMap.js` para visualização geo-espacial do ódio.
- [ ] **Multi-Model IA**: Adicionar fallback automático para Groq (Llama-3) caso o Qwen local esteja offline.
- [ ] **Alerta em Tempo Real**: Notificação via Telegram para picos de hostilidade (Z-Score > 3).

---
*Atualizado em 28/04/2026 - Pipeline de integração concluída.*
