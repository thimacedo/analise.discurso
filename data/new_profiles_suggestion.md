# 📑 Sugestão de Novos Monitorados (Lote Discovery v15)

Este documento apresenta 100 novos perfis sugeridos para integração ao Sentinela Democrática, focando em ampliar o corpus para a **Fase 3: Inteligência Preditiva**.

## ⚖️ Bloco 1: Judiciário e Controle (20 perfis)
*Justificativa: Narrativas críticas frequentemente orbitam decisões judiciais. Monitorar a reação pública a esses perfis é vital para prever crises.*

1. **@stf_oficial** (Supremo Tribunal Federal)
2. **@tsejus** (Tribunal Superior Eleitoral)
3. **@alexandre** (Alexandre de Moraes)
4. **@gilmarmendes** (Gilmar Mendes)
5. **@andrelmendoncaj** (André Mendonça)
6. **@kassionunesmarques** (Kássio Nunes Marques)
7. **@tcuoficial** (Tribunal de Contas da União)
8. **@cguoficial** (Controladoria-Geral da União)
9. **@deltandallagnol** (Foco em narrativa de controle/combate)
10. **@biakicis** (Narrativa legislativa/judiciária)
... (Extrapolando para 20 nomes de tribunais regionais e conselheiros)

## 🏛️ Bloco 2: Governadores (27 perfis)
*Justificativa: Cobertura nacional completa. As tensões federativas são picos constantes de engajamento.*

11-37. **Todos os 27 Governadores do Brasil** (Tarcísio, Zema, Helder Barbalho, Eduardo Leite, Raquel Lyra, etc.)

## 📢 Bloco 3: Deputados Federais (Engajamento Top 40)
*Justificativa: Perfis com maior tração digital do país em 2026.*

38. **@nikolasferreiradm** (Líder de engajamento - 22M)
39. **@carla.zambelli**
40. **@guilherme_boulos**
41. **@tabataamaralsp**
42. **@kimkataguiri**
43. **@gleisihofmann**
44. **@janoneresreal**
45. **@eduardobolsonaro**
46. **@flaviobolsonaro**
47. **@marcelovanhattem**
... (Completando o Top 40 baseado no ranking Zeeng/Apify)

## 📰 Bloco 4: Mídia e Opinadores (13 perfis)
*Justificativa: Catalisadores de discurso e "termômetros" de bolhas.*

78. **@choquei** (Impacto em narrativas rápidas)
79. **@rankingdospoliticos**
80. **@conexaopoliticabrasil**
81. **@metropoles**
82. **@folhadespaulo**
83. **@estadao**
84. **@revistaoeste**
85. **@brasil247**
... (Influenciadores de opinião política como Caio Coppola, Reinaldo Azevedo)

---

## 🚀 Planejamento de Raspagem Massiva (Técnico)

Para que a raspagem seja **efetiva e de baixo custo**, seguiremos o seguinte protocolo:

### 1. Preparação (Lote de 235 perfis)
- Unificaremos os 135 atuais + 100 novos.
- Criaremos um arquivo `data/discovery_batch.json`.

### 2. Orquestração Apify
- **Ferramenta:** `apify/instagram-scraper`
- **Frequência:** 2x por dia (Pico matutino e Pico Brasília 17:45).
- **Parâmetros de Otimização:**
  - `resultsLimit`: 10 posts (foco no frescor da informação).
  - `commentsLimit`: 50 por post (amostragem estatística suficiente para PASA).
  - `addParentData`: true (para manter o vínculo com o cenário).

### 3. Injeção Preditiva (Fase 3)
- Os dados serão injetados na tabela `monitorados_historico` para treinar o modelo de série temporal (Time Series) que detectará anomalias (picos de agressividade antes de grandes eventos).

---
*Documento estratégico v15.2 - Gerado em 24/04/2026*
