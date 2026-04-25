# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto monitora o clima político digital, utilizando coleta massiva de dados (Apify), análise de linguagem (Supabase + Groq/Qwen) com detecção avançada de sarcasmo (PASA), e apresenta os insights através de um Hub Informativo responsivo e monetizado.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** Produção de Alta Fidelidade (v15.4.1 - Consolidada)
**Resumo:** Versão 15.4.1 concluída e comitada. 
- **Validação de UI**: Testes de integridade realizados com Playwright (v15_check.spec.ts).
- **Diagnóstico de Linguagem PASA**: Lógica dinâmica baseada em resiliência real.
- **Governança**: Terminologia de monitoramento 100% saneada e commitada.
- **Sincronização**: Estrutura de scripts para Supabase Master preparada.

## 🎯 Próximos Passos
1. [ ] **Fase 4: Automação de Coleta** - Deploy do Apify Actor customizado (TS/Worker).
2. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback em tempo real) via Supabase.
3. [ ] **Pipeline de CI/CD**: Automação total dos testes Playwright no GitHub Actions.
4. [ ] **Expansão de Canais**: Inclusão de monitoramento via RapidAPI para redes sociais emergentes.

## 🛠️ Instruções de Execução (Como Deve Ser Feito)
- **Gestor:** Gemini (Arquiteto de Software e PM)
- **Assistência Local:** Qwen Local Coder para latência zero.
- **Regras:**
  - Código deve ser gerado completo, sem placeholders, e seguir Clean Code e SOLID.
  - O `ROADMAP.md` e o `MASTER_ROADMAP.md` DEVEM ser atualizados após cada entrega.
