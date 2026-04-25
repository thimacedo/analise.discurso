# Sentinela Democrática - Inteligência Política

## Escopo do Projeto
Este diretório contém o projeto de inteligência e monitoramento, focado em:
- Extração de dados de redes sociais (Instagram/Twitter) via Apify.
- Detecção de narrativas e desinformação.
- Análise de engajamento político.

## Regras de Engajamento para IA
1. **Foco em Inteligência:** Utilize ferramentas de extração e análise de dados (Apify, Abacus.ai) neste contexto.
2. **Schema do Banco:** Utilize o schema especializado para dados de inteligência.
3. **Privacidade:** Siga rigorosamente as diretrizes de proteção de dados e privacidade em monitoramento.
4. **Baseline de Inteligência (SIS):** Ao adicionar novos perfis em `perfis_monitorados.json`, é OBRIGATÓRIO ativar a skill `situational-intelligence-sync` para gerar o primeiro diagnóstico preditivo via fontes abertas.

## MCPs Autorizados
- Apify (Instagram Scrapers)
- Abacus.ai (Modelos de IA Customizados)
- Supabase (Projeto de Dados Políticos)
- Filesystem (E:\Projetos\sentinela-democratica\apify-actor)
