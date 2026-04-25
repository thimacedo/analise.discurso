# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto monitora o clima político digital, utilizando coleta massiva de dados, análise de linguagem (Supabase + Groq/Qwen) com detecção avançada de sarcasmo (PASA), e apresenta os insights através de um Hub Informativo responsivo e monetizado.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** Produção de Alta Fidelidade (v15.4.4 - Engine Responsiva)
**Resumo:** Versão 15.4.4 consolidada. 
- **Engine de Coleta**: Substituição do Apify por Worker Python local (`raspar.py`).
- **Worker PASA (Node.js)**: Orquestrador em tempo real para classificação de narrativas via Gemma/Groq.
- **Análise PASA**: Avaliação de narrativas e detecção de sarcasmo ativa.
- **Engine Responsiva**: Dashboard adaptado para Mobile-First com Matriz de Risco estatística.
- **Infraestrutura**: Vercel + Render operacionais.

## 🎯 Próximos Passos
1. [x] **Infraestrutura**: Migração da coleta para Worker Python.
2. [x] **Inteligência**: Implementação do PASA Worker em Node.js (Sem Python).
3. [ ] **Fase 4: Automação 24h**: Ativar serviços no Render com polling de 60s.
4. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback em tempo real) via Supabase.
5. [ ] **Expansão de Canais**: Inclusão de monitoramento via RapidAPI para redes sociais emergentes.

## 🛠️ Instruções de Execução (Como Deve Ser Feito)
- **Gestor:** Gemini (Arquiteto de Software e PM)
- **Rotina PASA:** O `pasa-worker.js` deve rodar 24/7 no Render, processando lotes de 20 comentários a cada 60s.
- **Coleta:** O `worker_sentinela.py` executa a raspagem diária dos prioritários + sequenciais.
- **Regras:**
  - Código deve ser gerado completo, sem placeholders.
  - O `ROADMAP.md` e o `MASTER_ROADMAP.md` DEVEM ser atualizados após cada entrega.
