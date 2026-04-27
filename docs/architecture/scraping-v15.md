# 🛰️ Processo de Raspagem Diamond (v15.18+)

## 1. Arquitetura de Carga (Load Balancing)
O sistema NAO utiliza uma unica API. Ele distribui os 242 alvos entre 3 provedores RapidAPI em modo Round-Robin:
- **Scraper-New**: instagram-scrapper-new.p.rapidapi.com
- **Bulk-Scraper**: instagram-public-bulk-scraper.p.rapidapi.com
- **Scraper-20251**: instagram-scraper-20251.p.rapidapi.com

## 2. Mecanismo de Resiliencia (Circuit Breaker)
Cada API e monitorada em tempo real. Se uma API retornar 3 falhas consecutivas (Rate Limit ou Erro 500), ela e isolada por 15 minutos (Cooldown). O fluxo continua automaticamente com as APIs restantes.

## 3. Fluxo de Execucao Assincrono
- **Concorrencia**: Maximo de 6 alvos simultaneos (2 por API).
- **Delay**: Pausa de 5 segundos entre lotes para polidez de rede.
- **Tipagem**: O `candidato_id` deve ser sempre o ID numerico (Integer) do Supabase, nunca o username.

## 4. Padrao de Evidencia PASA
Todo registro salvo na tabela `comentarios` deve conter obrigatoriamente:
- `id_externo`: ID original da rede social (String).
- `fonte_coleta`: Nome da API que gerou o dado (rastreabilidade).
- `raw_metadata`: JSON bruto da resposta da API (para auditoria forense).
- `url_post`: Link direto da evidencia.

## 🚫 PROCESSOS DEPRECADOS (PROIBIDO USAR)
1. **ScrapeGraphAI para Redes Sociais**: Lento e caro para este volume. Usar apenas para sites de noticias/blogs.
2. **Raspagem Sequencial (for loop)**: Proibido devido ao tempo de execucao de 50min+. Usar sempre `asyncio`.
3. **NLP ao Voo**: Nao processar sentimentos/categorias durante a raspagem. O coletor deve ser "burro" e rapido; a inteligencia (Llama 3.1) roda em um worker separado.
