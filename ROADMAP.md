# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto monitora o clima político digital, utilizando coleta massiva de dados (Apify), análise de linguagem (Supabase + Groq/Qwen) com detecção avançada de sarcasmo (PASA), e apresenta os insights através de um Hub Informativo responsivo e monetizado.

## 📌 Status Atual
**Data:** 25 de Abril de 2026
**Fase:** Produção de Alta Fidelidade (v15.4.4 - Engine Responsiva)
**Resumo:** Versão 15.4.4 consolidada. 
- **Engine Responsiva**: Dashboard adaptado para Mobile-First (Sidebar dinâmica, Grid fluida, KPIs 2x2).
- **Modais de Alta Fidelidade**: Modais com larguras relativas e rolagem garantida para telas pequenas.
- **Checkout UX**: Fluxo de retorno ("Voltar") e legibilidade PIX Emerald 400 validados.
- **Versionamento**: Sincronização de logs e scripts para v15.4.4 concluída.
- **Infraestrutura**: Vercel MCP configurado e operacional.

## 🎯 Próximos Passos
1. [x] **Infraestrutura**: Concluir a configuração do Vercel MCP no Gemini CLI.
2. [ ] **Fase 4: Automação de Coleta** - Deploy do Apify Actor customizado (TS/Worker).
3. [ ] **Integração Realtime**: Ativação do Step 6 (Chat/Feedback em tempo real) via Supabase.
4. [ ] **Pipeline de CI/CD**: Automação total dos testes Playwright no GitHub Actions.
5. [ ] **Expansão de Canais**: Inclusão de monitoramento via RapidAPI para redes sociais emergentes.

## 🛠️ Instruções de Execução (Como Deve Ser Feito)
- **Gestor:** Gemini (Arquiteto de Software e PM)
- **Assistência Local:** Qwen Local Coder para latência zero.
- **Regras:**
  - Código deve ser gerado completo, sem placeholders, e seguir Clean Code e SOLID.
  - O `ROADMAP.md` e o `MASTER_ROADMAP.md` DEVEM ser atualizados após cada entrega.
