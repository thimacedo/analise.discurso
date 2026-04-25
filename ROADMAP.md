# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto monitora o clima político digital, utilizando coleta massiva de dados, análise de linguagem (Supabase + Groq/Qwen) com detecção avançada de sarcasmo (PASA), e apresenta os insights através de um Hub Informativo responsivo e monetizado.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** Produção de Alta Fidelidade (v15.4.4 - Engine Responsiva)
**Resumo:** Versão 15.4.4 consolidada. 
- **Engine de Coleta**: Substituição do Apify por Worker Python local (`raspar.py`) com persistência direta no Supabase.
- **Análise PASA**: Avaliação de narrativas e detecção de sarcasmo ativa para perfis críticos.
- **Engine Responsiva**: Dashboard adaptado para Mobile-First.
- **Checkout UX**: Fluxo de monetização validado.

## 🎯 Próximos Passos
1. [x] **Infraestrutura**: Migração da coleta para Worker Python (Independência de Apify).
2. [ ] **Escalonamento de Coleta**: Implementar rotação de contas e proxies no `raspar.py`.
3. [ ] **Fase 4: Automação 24h**: Deploy do Worker em container Docker no Render para coleta contínua.
3. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback em tempo real) via Supabase.
4. [ ] **Pipeline de CI/CD**: Automação total dos testes Playwright no GitHub Actions.
5. [ ] **Expansão de Canais**: Inclusão de monitoramento via RapidAPI para redes sociais emergentes.

## 🛠️ Instruções de Execução (Como Deve Ser Feito)
- **Gestor:** Gemini (Arquiteto de Software e PM)
- **Assistência Local:** Qwen Local Coder para latência zero.
- **Regras:**
  - Código deve ser gerado completo, sem placeholders, e seguir Clean Code e SOLID.
  - O `ROADMAP.md` e o `MASTER_ROADMAP.md` DEVEM ser atualizados após cada entrega.
