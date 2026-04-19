# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Ponto de Partida (Status Atual)
**Data:** 18 de Abril de 2026
**Versão Atual:** v5.5.0 Modular
**Status:** ESTÁVEL (Deploy Vercel corrigido e online)

---

## 🚀 Conquistas do Dia (18/04/2026)

### 🏁 Sprint 9: Inteligência Groq de Elite (v5.7)
- ✅ **Motor Groq Integrado**: Implementação do SDK Groq com modelo Llama 3.3 70B para perícia em < 200ms.
- ✅ **Análise Multidimensional**: Captura automática de Ódio, Categoria, Justificativa e Sarcasmo.
- ✅ **Pipeline Inteligente**: Coleta e análise unificadas (os dados já entram no banco com veredito da IA).
- ✅ **Interface Industrial**: Dashboard e Topbar migrados para Skeuomorphism (Realismo Tátil).

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
