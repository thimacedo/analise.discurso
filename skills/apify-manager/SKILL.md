---
name: apify-manager
description: Gerencia e orquestra a coleta de dados via Apify MCP. Use para automatizar raspagem de redes sociais, notícias e portais da transparência nos projetos Sentinela e InovaSys.
---

# Gestor Apify

Este skill automatiza a interação com o Apify MCP, garantindo que o agente utilize a melhor ferramenta para cada necessidade de dados.

## 📋 Comandos e Fluxo de Trabalho

### 1. Descoberta e Configuração
- Antes de coletar, verifique se o Actor ideal está configurado.
- Use `mcp_apify_search-actors` para buscar novos scrapers.
- Consulte `E:\Projetos\sentinela-democratica\APIFY_TOOLS.md` para referência rápida.

### 2. Coleta de Dados Sociais (Instagram)
- **Posts e Comentários:** Use `apify/instagram-scraper`.
- **Vídeos e Transcrições:** Use `apify/instagram-reel-scraper`.
- **Perfis Específicos:** Use `apify/instagram-post-scraper`.

### 3. Pesquisa Web e Notícias
- **Contexto RAG:** Use `apify/rag-web-browser` para alimentar a inteligência preditiva com notícias do dia.

### 4. Recuperação de Resultados
- Sempre após um `call-actor`, use `mcp_apify_get-actor-output` com o `datasetId` para processar os dados.

## 🛡️ Regras de Segurança
- NUNCA exponha a API Key em logs ou arquivos não protegidos.
- Utilize variáveis de ambiente (.env) para credenciais.

## 🗺️ Projetos Integrados
- **Sentinela Democrática:** Monitoramento político e social.
- **InovaSys ERP:** Extração de dados de Diários Oficiais e Transparência.
