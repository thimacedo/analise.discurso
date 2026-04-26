# ✅ Diagnóstico Atual + Roadmap de Migração

Projeto: Análise de Discurso Político e Detecção de Ódio

---

## 🩺 DIAGNÓSTICO DO SISTEMA ATUAL

### ✅ Pontos Positivos Existentes:
- Pipeline completo funcional
- Coleta anônima já implementada
- Processamento de texto com spaCy
- Classificação multi-categoria
- Visualização e relatórios
- Integração cloud básica

### ⚠️ Problemas Críticos Identificados:
| Problema | Impacto | Severidade |
|---|---|---|
| Pipeline 100% sequencial | Qualquer falha em qualquer etapa perde TODO o trabalho | 🔴 CRÍTICO |
| Armazenamento 100% em CSV | Sem histórico, sem consultas, alto consumo memória | 🔴 CRÍTICO |
| Sem isolamento de responsabilidades | Orquestrador faz tudo: coleta, processamento, IA, visualização | 🟠 ALTO |
| Classificação por API externa | Custo alto, latência, limite de rate, dependência terceiro | 🟠 ALTO |
| Sem monitoramento | Ninguém sabe que o sistema caiu até que alguém olhe | 🟠 ALTO |
| Frontend acoplado ao backend | Impossível evoluir visualização separadamente | 🟡 MÉDIO |

---

## 🗺️ ROADMAP DE IMPLEMENTAÇÃO 6 FASES

### Ordem de Execução Recomendada:
> ✅ NÃO FAÇA TUDO DE UMA VEZ. Cada fase entrega valor imediato.

---

## 🔹 FASE 1: MATAR OS CSVs - PostgreSQL (PRIORIDADE MÁXIMA)
**Objetivo:** Parar de salvar e ler arquivos CSV. Tudo vai para banco relacional.

### Tarefas:
- [ ] Criar schema do banco com tabelas:
  - `candidatos` (dados cadastrais, partido, cargo, metadata)
  - `comentarios` (texto bruto, data, autor, id post)
  - `classificacoes` (score, categoria, confiança, modelo versão)
  - `execucoes_pipeline` (log de cada rodada completa)
- [ ] Implementar classe `DatabaseRepository` com SQLAlchemy
- [ ] Modificar cada etapa para salvar no banco ao invés de retornar DataFrame
- [ ] Manter compatibilidade temporária: continuar gerando CSV por enquanto
- [ ] Criar script de migração dos dados históricos existentes

**Resultado:** Você pode parar o pipeline a qualquer momento e não perde nada. Dados são persistentes.
**Tempo estimado:** 1 dia

---

## 🔹 FASE 2: FASTAPI - SEPARAR BACKEND
**Objetivo:** Separar completamente lógica de dados da visualização.

### Tarefas:
- [ ] Substituir Flask por FastAPI na pasta `/api`
- [ ] Criar endpoints REST padronizados versão `v1`:
  ```
  GET /api/v1/candidatos
  GET /api/v1/comentarios
  GET /api/v1/estatisticas/resumo
  GET /api/v1/estatisticas/por-partido
  GET /api/v1/estatisticas/linha-do-tempo
  ```
- [ ] Implementar paginação e filtros dinâmicos
- [ ] Adicionar cache Redis nas consultas que rodam o dashboard
- [ ] Documentação automática Swagger /docs

**Resultado:** Frontend pode ser substituido completamente sem tocar na lógica. Qualquer ferramenta pode consumir os dados.
**Tempo estimado:** 1 dia

---

## 🔹 FASE 3: METABASE - BUSINESS INTELLIGENCE
**Objetivo:** Dashboard profissional sem escrever NENHUMA linha de frontend.

### Tarefas:
- [ ] Instalar Metabase com 1 comando Docker:
  ```bash
  docker run -d -p 3000:3000 --name metabase metabase/metabase
  ```
- [ ] Conectar diretamente ao banco PostgreSQL
- [ ] Criar painéis pré-configurados:
  - ✅ Ódio por partido / candidato
  - ✅ Evolução temporal diária
  - ✅ Termos mais frequentes
  - ✅ Distribuição por categoria
  - ✅ Taxa de ódio por perfil
- [ ] Configurar atualização automática a cada 15 minutos

**Resultado:** Dashboard interativo profissional, com filtros, exportação, compartilhamento. Nível enterprise.
**Tempo estimado:** 4 horas

---

## 🔹 FASE 4: BERTIMBAU FINE-TUNED - IA LOCAL
**Objetivo:** Parar de pagar e depender de APIs externas para classificação em massa.

### Tarefas:
- [ ] Baixar modelo `neuralmind/bert-base-portuguese-cased` do HuggingFace
- [ ] Implementar classificador local com transformers
- [ ] Treinar com dataset público de ódio político brasileiro USP/TSE
- [ ] Implementar logica de confiança:
  - `> 0.85` = classificação automática
  - `0.45 - 0.85` = marcar para validação humana
  - `< 0.45` = descartar / revisar
- [ ] Manter fallback para Claude apenas para casos difíceis

**Resultado:** 100 comentários / segundo. Custo ZERO. Sem rate limits.
**Tempo estimado:** 2 dias

---

## 🔹 FASE 5: CELERY + REDIS - FILAS E RESILIÊNCIA
**Objetivo:** Pipeline a prova de falhas. Nada mais morre no meio.

### Tarefas:
- [ ] Instalar Redis e Celery
- [ ] Quebrar o orquestrador em workers independentes:
  1. `worker_coleta` -> recebe perfil, coleta comentários, envia para fila
  2. `worker_processamento` -> limpa texto, extrai features
  3. `worker_classificacao` -> executa modelo IA
  4. `worker_persistencia` -> salva no banco
- [ ] Cada etapa lê de uma fila e escreve na próxima
- [ ] Implementar retry com backoff exponencial em caso de falhas
- [ ] Limitar taxa de requisição por worker

**Resultado:** Se o Instagram bloquear, a IA continua processando. Se a IA cair, os dados ficam esperando. Você pode rodar 10 scrapers paralelos.
**Tempo estimado:** 2 dias

---

## 🔹 FASE 6: OBSERVABILIDADE E MONITORAMENTO
**Objetivo:** O sistema avisa VOCÊ que está quebrado.

### Tarefas:
- [ ] Logs estruturados JSON com `structlog`
- [ ] Métricas:
  - Taxa de sucesso da coleta
  - Tempo médio por comentário
  - Distribuição de scores do modelo
  - Tamanho das filas
- [ ] Alertas:
  - Taxa de erro > 20% = alerta Discord
  - Fila com mais de 1000 itens parados = alerta
  - Modelo classificando 90% neutro = provável falha
- [ ] Dashboard Grafana para métricas em tempo real

**Tempo estimado:** 1 dia

---

## 📊 COMPARAÇÃO ANTES / DEPOIS

| Métrica | Atual | Depois das 6 Fases |
|---|---|---|
| Resiliência | 0/10 | 10/10 |
| Escalabilidade | 1/10 | 10/10 |
| Custo operacional | 8/10 | 2/10 |
| Velocidade | 2/10 | 9/10 |
| Manutenibilidade | 2/10 | 8/10 |
| Nível Profissional | Hobby | Enterprise |

---

## 🎯 PRÓXIMOS PASSOS PARA AMANHÃ

1. **Comece AGORA pela Fase 1**
2. Quando terminar Fase 1, 2 e 3: o projeto já está melhor que 95% dos projetos de análise política existentes no Brasil
3. As outras fases podem ser implementadas gradualmente sem parar o sistema

> "A melhor arquitetura não é a mais perfeita. É aquela que você consegue implementar um pedaço por dia, e cada pedaço já entrega valor imediato."
