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

### 🟢 Sprint 4: API & Visualização Moderna (CONCLUÍDA)
- [x] **Unificação FastAPI:** Backend unificado e migrado de Flask para FastAPI (v1.0).
- [x] **Deploy Vercel:** Sistema online e estável em ambiente serverless.
- [x] **Dashboard Premium v3.0:** Interface dinâmica com abas, gráficos e simulador de IA.
- [x] **IA Híbrida:** Fallback automático entre Ollama Local e Nuvem Gratuita (HF).

### 🟢 Sprint 5: Automação & Operação Forense (CONCLUÍDA)
- [x] **Carga de Dados:** Migração total de CSVs legados para o banco SQLite centralizado.
- [x] **Worker de Monitoramento:** Automação da coleta agendada (v1.0) via `worker_monitoramento.py`.
- [x] **Human-in-the-loop:** Interface de validação e correção pericial integrada ao Dashboard.
- [x] **Observabilidade Real-time:** Logs de execução do pipeline visíveis no Dashboard.

### 🟢 Sprint 6: Governança, Segurança & Laudos (CONCLUÍDA)
- [x] **Autenticação de Acesso:** Proteção do Dashboard com PIN Pericial (v1.0).
- [x] **Laudo Forense:** Exportação dinâmica de dados validados para Excel (OpenPyXL).
- [x] **Auditoria de Cadeia de Custódia:** Marcação visual e registro de revisões humanas.
- [x] **Refatoração YOLO:** API otimizada para segurança e exportação de alta volumetria.

---

## 🤝 Divisão de Comando
- **Gemini (PM):** Gestão de Roadmap, Segurança Git e Orquestração de Arquitetura.
- **Qwen (Analista):** Desenvolvimento Python, Classificação Local via Ollama e Otimização SQL.

---
## 🏁 Última Entrega (17/04/2026 - v2.2 Professional)
- **Entrega:** Consolidação da Plataforma ForenseNet com Automação, Segurança e Laudos Judiciais.
- **Impacto:** O sistema evoluiu de uma ferramenta de pesquisa para um ecossistema operacional de monitoramento político-eleitoral, com resiliência total contra falhas de IA externa e proteção de integridade dos dados.

> *Encerrado Ciclo de Desenvolvimento v2.2.*
