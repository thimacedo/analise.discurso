# 🗺️ ROADMAP.md - Sentinela Democrática

## 📖 Visão Geral
Plataforma de **Inteligência Situacional e Tendências de Opinião Pública**. O projeto monitora o clima político digital, utilizando coleta massiva de dados (Apify), análise de linguagem (Supabase + Groq/Qwen) com detecção avançada de sarcasmo (PASA), e apresenta os insights através de um Hub Informativo responsivo e monetizado.

## 📌 Status Atual
**Data:** 24 de Abril de 2026
**Fase:** Produção de Alta Fidelidade (v15.2 - Inteligência em Tempo Real)
**Resumo:** Versão 15.2 concluída. 
- **Feed de Alertas Críticos**: Implementado feed dinâmico de comentários negativos na Home.
- **Dados Reais**: Injeção de alertas extraídos via Apify (Ex: Nikolas Ferreira) para validação da UI.
- **Gestor Apify**: Skill `apify-manager` operacional e centralizada.
- **Expansão do Corpus**: Inclusão de 87 novos perfis (STF, TSE, Governadores, Deputados Top Engajamento).
- **Monetização v15.1**: Stripe, PayPal e PIX (com QR Code dinâmico) integrados a R$ 49,99.
- **Localização**: Padronização total para Horário de Brasília e normas brasileiras.
- **Arquitetura UX**: Substituição global de "monitorados" por **Monitorados**, rolagem fluida e mapas reais.

## 🎯 Próximos Passos
1. [x] **Fase 3: Inteligência Preditiva** - Motor de detecção de anomalias operacional (Momentum de Agressividade).
2. [x] **Expansão Institucional** - Inclusão de atores do poder judiciário e órgãos de controle concluída.
3. [x] **Precisão Geográfica**: Mapa real do Brasil com geometrias detalhadas operacional.
4. [x] **Responsividade**: Dashboard adaptado para todos os dispositivos.

## 🛠️ Instruções de Execução (Como Deve Ser Feito)
- **Gestor:** Gemini (Arquiteto de Software e PM)
- **Assistência Local:** Qwen Local Coder para latência zero.
- **Regras:**
  - Código deve ser gerado completo, sem placeholders, e seguir Clean Code e SOLID.
  - O `ROADMAP.md` e o `MASTER_ROADMAP.md` DEVEM ser atualizados após cada entrega.
