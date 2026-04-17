# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Ponto de Partida (Status Atual)
**Data:** 17 de Abril de 2026
**Gerenciamento:** Gemini (Gerente de Projetos) & Qwen 2.5 Coder 7B (Analista de Sistemas / Programador Local)
**Stack Tecnológica:** Python 3.10+, SQLite (SQLAlchemy), IA Local (Qwen via Ollama), FastAPI.
**Situação:**
- Pipeline v2.1: ✅ Persistência robusta em DB e IA Local ativa.
- Sincronização GitHub: ✅ Realizada e Segura (Histórico limpo).
- Independência de API: ✅ Migração de Claude/OpenAI para Qwen Local concluída.

## 🎯 Destino Final
Consolidar a plataforma como referência em monitoramento pericial de ódio político, com dashboard em tempo real e análise forense automatizada.

## 🛤️ Caminho Traçado (Próximos Passos)

### 🟢 Sprint 1: Saneamento e Segurança (CONCLUÍDA)
- [x] **Limpeza de Histórico Git:** Removido Apify Token e segredos via squash de commits.
- [x] **Padronização de Ambiente:** `.env.example` saneado com placeholders.
- [x] **Push Seguro:** Sincronização total com o repositório remoto realizada em 17/04/2026.

### 🟢 Sprint 2: Matar os CSVs (CONCLUÍDA)
- [x] **Refatoração Pipeline:** `main_pipeline.py` agora salva em SQLite em tempo real.
- [x] **Logs de Execução:** Implementado rastreamento de status de cada rodada no banco.
- [x] **Script de Migração:** Criado `migrar_csv_para_db.py` para importar dados legados.

### 🟢 Sprint 3: IA Local & Inteligência Forense (CONCLUÍDA)
- [x] **Classificador Qwen Local:** Criado `local_qwen_classifier.py` integrado ao Ollama.
- [x] **Prompt Pericial:** IA treinada localmente para identificar Xenofobia, Misoginia e Ódio Político.
- [x] **Integração Total:** Pipeline utiliza o Qwen como motor primário de análise (Custo Zero).

### 🟡 Sprint 4: API & Visualização Moderna (EM ANDAMENTO)
- [ ] **Expansão de Endpoints:** Adicionar filtros avançados por "Grau de Severidade" na API.
- [ ] **Dashboard Realtime:** Criar interface web que consome os dados do SQLite via FastAPI.
- [ ] **Worker de Monitoramento:** Implementar execução agendada (Cron/Task Scheduler).

---

## 🤝 Divisão de Comando
- **Gemini (PM):** Gestão de Roadmap, Segurança Git e Orquestração de Arquitetura.
- **Qwen (Analista):** Desenvolvimento Python, Classificação Local via Ollama e Otimização SQL.

---
## 🏁 Última Entrega (17/04/2026)
- **Entrega:** Integração da IA Local Qwen e Persistência em Banco de Dados SQLite.
- **Impacto:** Redução de custos de API em 100% e aumento da resiliência dos dados coletados.

> *Atualizado automaticamente após cada entrega significativa.*
