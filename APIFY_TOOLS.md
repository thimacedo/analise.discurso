# 🐝 Apify Ecosystem: Guia Completo de Ferramentas (MCP)

Este documento é a referência central para todas as capacidades de raspagem e inteligência de dados via Apify disponíveis no projeto Sentinela.

---

## 🛠️ Ferramentas de Orquestração (Core MCP)

Essas ferramentas permitem gerenciar o ciclo de vida de qualquer "Actor" (scraper) no Apify Store.

- **`mcp_apify_search-actors`**: Descobre novos scrapers no Apify Store. Use quando precisar coletar dados de uma plataforma nova (ex: TikTok, Amazon).
- **`mcp_apify_fetch-actor-details`**: Obtém o esquema de entrada (input schema) e README de um Actor específico. Essencial antes de chamar `call-actor`.
- **`mcp_apify_call-actor`**: Executa qualquer Actor. Requer o nome do actor e um JSON de entrada.
- **`mcp_apify_get-actor-output`**: Recupera os itens do dataset gerados por uma execução. É o comando padrão para ler os dados após a raspagem.
- **`mcp_apify_get-actor-run`**: Verifica o status de uma execução (READY, RUNNING, SUCCEEDED, etc).
- **`mcp_apify_get-dataset-items`**: Acesso direto a datasets, com suporte a filtros, paginação e ordenação.

---

## 🚀 Scrapers Especializados (Dedicados)

Ferramentas pré-configuradas para alta performance em plataformas específicas.

### 📸 Instagram
- **`apify/instagram-scraper`**: Coleta posts, perfis, hashtags e comentários. Ideal para monitoramento de engajamento político.
- **`apify/instagram-reel-scraper`**: Extrai transcrições de áudio, legendas e métricas de Reels. Útil para análise de narrativas em vídeo.
- **`apify/instagram-post-scraper`**: Focado em extração rápida de posts individuais ou feeds de perfis específicos.

### 🗺️ Google Maps & Local Business
- **`compass/crawler-google-places`**: Extrai dados de locais, incluindo avaliações, horários e preços.
- **`compass/google-maps-extractor`**: Raspagem rápida de contatos e detalhes de empresas no Maps.
- **`lukaskrivka/google-maps-with-contact-details`**: Enriquecimento de leads com e-mails e redes sociais extraídos dos sites das empresas encontradas.

### 🌐 Web & Notícias
- **`apify/rag-web-browser`**: Navegador otimizado para IA. Pesquisa no Google e retorna o conteúdo das páginas em Markdown. Use para alimentar o contexto do Gemini com fatos em tempo real.
- **`apify/web-scraper`**: Crawler genérico para qualquer site. Permite injetar JavaScript customizado para raspagens complexas.

### 🐦 Outras Redes e Plataformas
- **`apidojo/tweet-scraper`**: Raspagem ultra-rápida de tweets (X), perfis e buscas avançadas.
- **`streamers/youtube-scraper`**: Coleta metadados de vídeos, canais e playlists do YouTube.
- **`topaz_sharingan/Youtube-Transcript-Scraper-1`**: Extrai transcrições de vídeos do YouTube para análise de discurso.
- **`curious_coder/linkedin-jobs-scraper`**: Extrai vagas e detalhes de empresas do LinkedIn.
- **`apify/facebook-posts-scraper`**: Extrai posts e métricas de páginas públicas do Facebook.

---

## 💡 Fluxo de Decisão: O Que Usar?

1. **Monitoramento Político no IG?** -> `instagram-scraper` (posts/comentários).
2. **Análise de Discurso em Vídeo?** -> `youtube-scraper` + `Youtube-Transcript-Scraper-1`.
3. **Verificação de Fatos (Fact-checking)?** -> `rag-web-browser`.
4. **Mapeamento de Instituições (Maps)?** -> `google-maps-extractor`.
5. **Plataforma Desconhecida?** -> `search-actors` para encontrar a solução.

---

## 🛡️ Configuração de Segurança
As ferramentas utilizam o token `SENTINELA_APIFY_API_TOKEN` definido no arquivo `.env_geral`. NUNCA exponha este token em logs de saída.

---
*Atualizado em: 24/04/2026 por Gemini CLI*
