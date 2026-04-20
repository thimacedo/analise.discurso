# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Status Atual
**Data:** 18 de Abril de 2026
**Versão Atual:** v5.8 (Dashboard Estruturado)
**Status:** ESTÁVEL (Deploy Vercel Online)

---

## 🚀 Conquistas Recentes

### 🏁 Sprint 10: Dashboard Estruturado Supabase (v5.8)
- ✅ **Clean Tech UI**: Interface minimalista de alto contraste com foco em dados.
- ✅ **Fluxo de Classificação**: Implementada listagem com prioridade `is_hate DESC` e filtros dinâmicos.
- ✅ **Integração Groq v2**: Coleta e análise síncrona com Llama 3.3 (Ódio, Categoria e Sarcasmo).
- ✅ **Políticas de Acesso**: Configurado para Dashboard Aberto (Anon Read-Only).

---

## 📋 Comandos e Estruturas Supabase (Fixos)

### 1. Visualização de KPIs (Views Recomendadas)
```sql
CREATE OR REPLACE VIEW public.dashboard_comentarios_kpis AS
SELECT
  count(*)::int AS total_comentarios,
  count(*) FILTER (WHERE is_hate IS true)::int AS total_hate,
  count(*) FILTER (WHERE is_hate IS false OR is_hate IS NULL)::int AS total_nao_hate,
  count(*) FILTER (WHERE processado_ia IS true)::int AS total_processados
FROM public.comentarios;
```

### 2. Filtros de Classificação
- **Texto**: `texto_bruto` (ILike para busca textual).
- **Gravidade**: `is_hate` (Booleano).
- **Categoria**: `categoria_ia` (Taxonomia Criminal).
- **Ordenação**: `is_hate DESC, data_coleta DESC`.

---

## 🎯 Próximos Passos

### 📈 Escalonamento e Perícia
1.  **Monitoramento Nacional:** Ciclo Lula → Bolsonaro → Nikolas → Flávio.
2.  **Detecção de Sarcasmo Local:** Refinar motor local para reduzir falsos positivos em elogios irônicos.
3.  **Laudos Dinâmicos:** Exportação do Corpus de Prova formatado para PDF pericial.

---

## 🛠️ Guia de Operação
- **Interface:** https://projeto-odio-politica.vercel.app
- **Trigger Coletor:** https://projeto-odio-politica.vercel.app/api/collect
- **Banco:** Supabase (PostgreSQL + PostgREST).
