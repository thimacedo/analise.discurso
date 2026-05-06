# 📊 ESTADO ATUAL DOS KPIs - SENTINELA DEMOCRÁTICA
**Data de Verificação:** 6 de maio de 2026  
**Status Geral:** ✅ Operacional - Arquitetura v18.5 Estável

---

## 📈 KPIs CONSOLIDADOS

### 1. **Cobertura de Monitoramento**
- **Alvos Ativos**: 46 candidatos/políticos
- **Última atualização de coleta**: 5 de maio de 2026, 01:30 UTC (mais recente)
- **Histórico de coletas**: Cobertura contínua desde 19 de abril de 2026

**Alvos monitorados:**
- Prefeitos e vereadores (RN)
- Senadores e deputados federais
- Personalidades políticas em nível nacional

### 2. **Volume de Dados Coletados** 
- **Plataformas**: Instagram (nativa via API Scrapy)
- **Período**: Abril - Maio 2026
- **Status**: Coleta ativa e processada via PASA v16.4

**Ciclo de coleta:**
```
Scrapy (Coleta) → Supabase (Armazenamento) → TextProcessor (Limpeza)
→ AIService (Classificação PASA) → DataMiner (Clustering) → Relatórios PDF
```

### 3. **Classificação e Análise**
- **Motor IA**: PASA v16.4 (Qwen 2.5) + Critérios Forenses
- **Categorias**: NEUTRO, ODIO, POLITICO, etc.
- **Confiança**: Scoring entre 0.0 e 1.0 por comentário
- **Processamento**: Batch de até 200 comentários/ciclo

**Exemplos de classificação recente (05/05/2026):**
- Sentimento positivo: 0.95-0.99 confiança → NEUTRO
- Engajamento cívico: 0.90+ confiança → NEUTRO
- Comentários vazios/navegação: 1.0 confiança → NEUTRO

### 4. **Qualidade e Resiliência**
- **Taxa de Resiliência**: Dinâmica (calculada por endpoint `/api/v1/summary`)
  - Fórmula: `((Total - Ódio) / Total) * 100`
- **Idempotência**: ✅ UPSERTS no Supabase (à prova de duplicatas)
- **Recuperação de Falhas**: IA com retry automático em lotes

### 5. **Infraestrutura de Alertas**
- **Sistema de Alertas**: Firebase + Supabase
- **Redes Coordenadas**: Detecção de clusters de coordenação
- **Tabelas**:
  - `candidatos` (alvos)
  - `comentarios` (dados brutos processados)
  - `metricas_diarias` (KPIs diários)
  - `redes_coordenadas` (clusters detectados)
  - `alertas_ativos` (notificações em tempo real)
  - `anuncios` (Meta Ad Library tracking)

---

## 🔄 CICLO DE ATUALIZAÇÃO

### Processo Padrão (Orchestrator)
1. **[1/5] Extração**: Scrapy + Fila Central (`fila_coleta`)
2. **[1.5/5] Re-perícia**: Verificação de alvos marcados para re-análise
3. **[1.7/5] Meta Ads**: Rastreamento de anúncios política (Top 5 prioridade)
4. **[2/5] Perícia PASA**: Classificação em lote (até 200 comentários)
5. **[3/5] Normalização**: Limpeza + mapping de colunas
6. **[4/5] Mineração**: KMeans clustering + Z-Score (picos de agressividade)
7. **[5/5] Relatórios**: Geração PDF FPDF2 (UTF-8 nativo)

---

## 📌 ÚLTIMA OPERAÇÃO EXECUTADA

**Timestamp**: 5 de maio de 2026, 01:30:47 UTC  
**Alvo**: @lulaoficial (e outros)  
**Volume**: +100 comentários processados  
**Resultado**: ✅ Classificados como NEUTRO (0.95-0.99 confiança)  

---

## ⚙️ STATUS DE COMPONENTES

| Componente | Status | Observação |
|-----------|--------|-----------|
| **Scrapy** | ✅ Online | Coleta contínua de dados |
| **Supabase** | ✅ Online | RLS + Segurança v25.0 |
| **PASA v16.4** | ✅ Online | Classificação forense ativa |
| **DataMiner** | ✅ Online | Clustering e mineração |
| **Firebase** | ✅ Online | Alertas em tempo real |
| **TextProcessor** | ✅ Online | Limpeza + lematização |
| **Dashboard** | ⚠️ Em desenvolvimento | Métricas de latência (próximo release) |

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Imediato**: Validar performance dos workers em carga real
2. 🔄 **Próximo ciclo**: Implementar dashboard de latência dos workers
3. 📹 **Roadmap v21.0**: Expansão para TikTok/YouTube (vídeos)
4. 📊 **Épico**: Refatoração Arquitetural v2.0 - CONCLUÍDA ✅

---

## 📁 ARQUIVOS DE REFERÊNCIA

- **Estado Atual**: [STATE.md](STATE.md)
- **Roteiro Técnico**: [ROADMAP.md](ROADMAP.md)
- **Critérios de Treinamento**: [CRITERIOS_TREINAMENTO.md](CRITERIOS_TREINAMENTO.md)
- **Últimas Métricas**: [data/collection_state.json](data/collection_state.json)
- **Scripts de Verificação**: `scripts/check_kpi_values.py`, `scripts/update_kpis.py`

---

## 🔐 GOVERNANÇA E CONFORMIDADE

✅ **TSE 2026**: Rotulagem de IA conforme diretrizes  
✅ **Transparência**: Dados de domínio público digital  
✅ **Integridade Arquitetural**: v18.5 estável, PASA v16.4 forense  
✅ **Segurança Admin**: TOTP + RLS configurado

