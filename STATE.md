# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 20.5.0 (Intelligence Optimization)
- **Data da última atualização:** 02/05/2026
- **Status:** Operacional. Scraper resiliente e analytics temporal funcional.

## ✅ O que está funcionando
- **Scraper Resiliente (NEW):** Implementada a classe `IdentityManager` que gerencia a rotação de contas de coleta e detecta automaticamente sinais de Shadowban, garantindo fluxo contínuo de dados.
- **Analytics Temporal (NEW):** Novo gráfico de barras empilhadas no Dashboard mostrando a evolução dia a dia das categorias PASA, facilitando a identificação de ondas de ataque.
- **Módulo de Grafos SVG:** Visualização de clusters de ataque com tooltips e zoom.
- **IA Local via Ollama:** Processamento descentralizado via Qwen 2.5 3B.
- **Firebase Push Notifications:** Alertas em tempo real.

## 🛠 Mudanças Técnicas (Sessão 02/05)
1. **InstagramHeadlessScraper:** Refatorado para modo de rotação, consultando a tabela `scraping_accounts` para cada ciclo de coleta.
2. **API Analytics:** Criado endpoint `/api/v1/analytics/pasa-temporal` com agregação por data e categoria forense.
3. **Frontend UI:** Adicionado componente D3.js para renderização de séries temporais empilhadas no painel de monitoramento.
4. **Versão 20.5.0:** Sistema otimizado para escala e inteligência de longo prazo.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] Conta Única:** Abordagem de credenciais fixas no .env abandonada em favor do pool dinâmico no DB.
- **[DESCARTADO] Gráfico de Linha Simples:** Substituído por Barras Empilhadas para visualizar a composição qualitativa do ódio no tempo.

## 🐛 Bugs Atuais / Bloqueios
- **Nenhum bloqueio crítico.** Próximo foco: Robustez da prova pericial (Screenshots automáticos).
