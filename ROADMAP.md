# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto utiliza coleta massiva via RapidAPI, análise híbrida de geolocalização e narrativas (PASA + GEO) via Gemma2, e apresenta os insights em um Dashboard de alta fidelidade estatística.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** v15.4.4 - Cérebro Linguístico Consolidado
**Resumo:** 
- **Cérebro Linguístico**: Criado `LINGUISTIC_BRAIN.md` com parâmetros de Linguística Forense e Estilometria (Base UFRN/Vichi).
- **Lógica Forense**: Estruturada em `FORENSIC_LOGIC.md` para processamento de N-Gramas e POS Tagging.
- **Worker Híbrido**: Processamento 24/7 de estados e narrativas ativo.

## 🎯 Próximos Passos
1. [x] **Inteligência Híbrida**: Classificação automática de novos alvos e comentários.
2. [x] **Cérebro Linguístico**: Mapeamento da biblioteca forense e criação da base de parâmetros.
3. [ ] **Treinamento PASA (Fase 1)**: Integrar algoritmos de N-Gramas e Lemmatização no `pasa-worker.js`.
4. [ ] **Detecção de Ataques Coordenados**: Implementar detecção de scripts via densidade lexical.
4. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback) via Supabase Realtime.
5. [ ] **Monetização**: Implementação de relatórios dinâmicos pós-checkout.

## 🛠️ Instruções de Execução
- **Worker PASA+GEO:** `pasa-worker.js` roda no Render com polling de 60s.
- **Coleta:** `worker_sentinela.py` executa a raspagem diária prioritária.
- **Regras:** Manter a exclusividade de geolocalização (um alvo, um estado).
