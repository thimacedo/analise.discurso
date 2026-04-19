# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Ponto de Partida (Status Atual)
**Data:** 18 de Abril de 2026
**Versão Atual:** v5.5.0 Modular
**Status:** ESTÁVEL (Deploy Vercel corrigido e online)

---

## 🚀 Conquistas do Dia (18/04/2026)

### 🏁 Sprint 8: Estabilidade de Coleta (v5.6)
- ✅ **Nova Arquitetura de Coleta**: Migração total do GraphQL (hashes instáveis) para a API REST privada do Instagram (`/api/v1/...`).
- ✅ **Motor de Upsert**: Implementada lógica de `on_conflict` no Supabase Pipeline, garantindo 0% de falhas por chaves duplicadas.
- ✅ **Coleta em Cascata**: Automação do fluxo Seguidos -> Últimos 3 Posts -> 100 Comentários por post.
- ✅ **Agendamento Industrial**: Configurado agendamento diário (08:00 e 20:00) via `CrawlerProcess`.

---

## 🎯 Próximos Passos (Destino Final)

### 📈 Escalonamento de Dados
1.  **Monitoramento Nacional:** Finalizar o ciclo Lula → Flávio Bolsonaro → Bolsonaro → Nikolas.
2.  **Mapeamento de Redes:** Identificar "perfis-satélite" que orbitam os alvos nacionais com discurso tóxico.

### 🛡️ Refinamento Pericial
3.  **Filtragem de Falsos Positivos:** Implementar no motor local um refinamento para desconsiderar elogios irônicos (detector de sarcasmo).
4.  **Laudos Dinâmicos:** Exportar o novo formato "Grouped by Post" diretamente para PDF pericial.

---

## 🛠️ Guia de Assunção de Comando
- **Interface:** https://projeto-odio-politica.vercel.app
- **Pipeline Local:** `python main_pipeline.py` (usa venv com local-ai).
- **Backend:** FastAPI modular em `api/`.
- **Banco:** Supabase (Cloud) + SQLite (Local Cache).

> *Iniciada Fase de Coleta Massiva v5.5.*
