# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto utiliza coleta massiva via RapidAPI, análise híbrida (PASA + GEO) via Gemma2, e um motor de conformidade fundamentado em Linguística Forense e normas do TSE 2026.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** v15.4.5 - Inteligência Forense & Balizamento TSE
**Resumo:** 
- **Conformidade TSE 2026**: Integrado painel de regras eleitorais e documento de balizamento ético (`ETHICS_TSE.md`).
- **Cérebro Linguístico**: Consolidada base de parâmetros forenses (N-Gramas, Idioleto, POS Tagging).
- **Worker Híbrido**: Automatizado o processamento de geolocalização e narrativas 24/7.
- **UI de Alto Impacto**: Matriz de Risco estatística ativa para visualização imediata de crises.

## 🎯 Próximos Passos
1. [x] **Inteligência Híbrida**: Classificação automática de novos alvos e comentários.
2. [x] **Cérebro Linguístico**: Mapeamento da biblioteca forense.
3. [x] **Governança Ética**: Integração das regras do TSE 2026 para uso de IA.
4. [ ] **Auditoria de Rotulagem**: Desenvolver skill para detectar propaganda política via IA sem rótulo nas redes sociais.
5. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback) via Supabase Realtime.
6. [ ] **Relatórios Forenses**: Geração automática de dossiês em PDF com validade pericial.

## 🛠️ Instruções de Execução
- **Balizador TSE:** O motor PASA está proibido de gerar deepfakes ou conteúdos não rotulados.
- **Worker PASA+GEO:** `pasa-worker.js` roda no Render com polling de 60s.
- **Regras:** Manter a exclusividade de geolocalização e rotulagem obrigatória de IA.
