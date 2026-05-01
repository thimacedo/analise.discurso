# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.8.5 (Headless Dominance)
- **Data da última atualização:** 01/05/2026
- **Status:** Operacional e Estabilizado. Scraper headless operando em alta performance.

## ✅ O que está funcionando
- **Autenticação Multi-Cookie:** Injeção de `sessionid`, `ds_user_id`, `csrftoken` e `ig_did` via Playwright para bypass total de login.
- **Extração Resiliente (DOM 2026):** Novo extrator de seguidores e posts baseado em seletores ultra-abrangentes e scroll proativo.
- **Filtro de Ruído Forense:** Blacklist integrada no scraper para ignorar links de sistema (meta, help, privacy) e capturar apenas discurso real.
- **Arquitetura Diamond:** Núcleo assíncrono em `core/db.py` e `core/ai_service.py` validado sob carga.
- **Pipeline Completa:** Coleta -> Classificação PASA v16.4 -> Clustering -> Dossiê PDF -> Alerta WhatsApp.

## 🛠 Mudanças Técnicas (Sessão 01/05)
1. **ElectionMonitor:** Corrigido bug de `AttributeError` e `TypeError` (await em chamadas síncronas do Supabase).
2. **InstagramHeadless:** Migração total de extração via `window._sharedData` (obsoleto) para análise direta de DOM com seletores de fallback.
3. **TargetManager:** Ajustado para integrar nativamente com o ciclo de monitoramento eleitoral externo.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] Instaloader Simples:** Frequentemente bloqueado ou detectando perfis públicos como "privados".
- **[DESCARTADO] wait_until="networkidle":** Removido por causar timeouts infinitos no Instagram 2026; substituído por `commit` + `sleep` estratégico.
- **[DESCARTADO] Seletores Fixos de Classe:** Substituídos por busca de atributos (`href`, `title`) para maior durabilidade contra mudanças de CSS.

## 🐛 Bugs Atuais / Bloqueios
- **Alvos Genéricos:** Nomes como "Lula" ou "Bolsonaro" sem o sufixo oficial falham na busca; necessário normalização contínua na fila.
