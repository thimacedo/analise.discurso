# 🗺️ ROADMAP.md - Projeto Ódio Política (Mapa de Voo)

## 📌 Ponto de Partida (Status Atual)
**Data:** 17 de Abril de 2026
**Gerenciamento:** Gemini (Gerente de Projetos) & Qwen 2.5 Coder 7B (Analista de Sistemas / Programador Local)
**Stack Tecnológica Atual:** Python 3.10+, SQLite (incipiente), CSV (legado), spaCy, Claude API (opcional).
**Situação:**
- Pipeline funcional mas sequencial (Frágil).
- Dependência excessiva de arquivos CSV para persistência.
- Sincronização GitHub: ✅ Realizada em 17/04/2026.
- Segurança: ⚠️ Bloqueio de Push detectado (Segredo em `.env.example`).

## 🎯 Destino Final
Transformar o sistema em uma plataforma de **Linguística Forense Enterprise**: resiliente, escalável, com IA local (Qwen/BERTimbau) e dashboard profissional (Metabase/FastAPI).

## 🛤️ Caminho Traçado (Próximos Passos)

### 🔴 Sprint 1: Saneamento e Segurança (IMEDIATO)
- [ ] **Limpeza de Histórico Git:** Remover o Apify Token do histórico para permitir push limpo.
- [ ] **Padronização de Ambiente:** Validar `.env` e `.gitignore` para evitar novos vazamentos.
- [ ] **Diagnóstico de Dados:** Verificar integridade do `odio_politica.db` vs CSVs atuais.

### 🟠 Sprint 2: Matar os CSVs (Persistência Robusta)
- [ ] Migrar lógica de salvamento de CSV para SQLite/PostgreSQL (SQLAlchemy).
- [ ] Criar script de migração de dados históricos (`dados_brutos_*.csv`).
- [ ] Implementar `DatabaseRepository` para isolar a camada de dados.

### 🟡 Sprint 3: IA Local & Inteligência Forense
- [ ] Integrar **Qwen 2.5 Coder** para análise de código e automação local.
- [ ] Implementar classificador BERTimbau local (Fase 4 do Diagnóstico).
- [ ] Refinar categorias de ódio baseadas na metodologia pericial do Prof. Vichi.

### 🔵 Sprint 4: API & Visualização Moderna
- [ ] Desenvolver Backend com FastAPI (v1).
- [ ] Integrar Metabase para Dashboards de BI.
- [ ] Criar Worker de monitoramento em tempo real (Fila Redis/Celery).

---

## 🤝 Divisão de Comando
- **Gemini (PM):** Responsável pelo Roadmap, validação de segurança, orquestração de prompts e visão arquitetural.
- **Qwen (Analista):** Responsável pela escrita de código Python, refatoração de funções, consultas SQL e otimização de modelos locais.

---
## 🏁 Última Entrega
- **17/04/2026:** Inicialização do Protocolo de Governança e sincronização inicial com GitHub (pendente de limpeza de segredos).

> *Atualizado automaticamente após cada entrega significativa.*
