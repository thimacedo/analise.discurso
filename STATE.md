# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 20.1.0 (Diamond Push)
- **Data da última atualização:** 02/05/2026
- **Status:** Operacional. Notificações Push nativas e Normalização de Alvos robusta.

## ✅ O que está funcionando
- **Firebase Push Notifications (NEW):** Migração total dos alertas de WhatsApp para Push nativo via FCM. Backend integrado e Frontend Service Worker operacional.
- **Normalizador Inteligente (NEW):** Bug de alvos genéricos corrigido com `TargetNormalizer` + `FALLBACK_MAP`. Suporte a Unicode (limpeza de acentos) e de-duplicação.
- **Ambiente Virtual Blindado:** `.venv` recriado com Python 3.12 e todas as dependências core (pandas, spacy, networkx, fpdf2) validadas via Smoke Test.
- **Meta Ad Library:** Motor de scraping Playwright integrado ao orquestrador.
- **Arquitetura Diamond:** Núcleo assíncrono validado e estável.

## 🛠 Mudanças Técnicas (v20.1)
1. **API v1 Config:** Novo endpoint `/api/v1/config/firebase` para chaves públicas.
2. **Orquestrador:** Saneado de referências ao CallMeBot; agora utiliza `FirebaseAlerter` nativamente.
3. **Frontend:** `app.js` restaurado integralmente com suporte a `fcmService.init()`.
4. **NLP:** Inclusão de `spacy` (pt_core_news_sm) e `nltk` no pipeline de processamento de texto.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] CallMeBot WhatsApp:** Removido por instabilidade e latência; substituído por Firebase.
- **[DESCARTADO] Instaloader Simples:** Frequentemente bloqueado pela infraestrutura do Instagram 2026.
- **[DESCARTADO] Python 3.14 (Beta):** Incompatível com algumas bibliotecas core; revertido para 3.12 estável.

## 🐛 Bugs Atuais / Bloqueios
- **Cota de API (Cloud):** Erros 429 intermitentes no Gemini 3 Flash Preview; mitigado via retry com backoff ou switch manual para local.
- **Próximo Foco:** Polimento visual (v20.2 - Diamond Theme).
