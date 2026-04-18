# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Ponto de Partida (Status Atual)
**Data:** 18 de Abril de 2026
**Versão Atual:** v5.5.0 Modular
**Status:** ESTÁVEL (Deploy Vercel corrigido e online)

---

## 🚀 Conquistas do Dia (18/04/2026)

### 🏁 Sprint 7: Modularização e Prova Visual
- ✅ **Reorganização de Workspace:** Pastas `core`, `collectors`, `api`, `database` e `docs` criadas para modularidade real.
- ✅ **Inteligência Contextual:** Implementada captura de `post_image` e `post_caption` no coletor.
- ✅ **IA Local Híbrida:** Qwen 0.5B (Primário) e 1.5B (Fallback) configurados no Ollama.
- ✅ **Dashboard v5.5 Modular:**
  - Extração do HTML para `api/templates.py`.
  - Agrupamento de comentários por "Unidade de Incidente" (Post).
  - Scroll interno nos cards de postagem.
  - Exibição de prova visual (thumbnails do Instagram).
  - Radar Chart para tipificação criminal OSINT.
- ✅ **Deploy Resiliente:** Resolvidos erros 404 e 500 na Vercel através de roteamento direto via FastAPI e separação de dependências leves/pesadas.

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
