# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 20.1.0 (Diamond Push)
- **Data da última atualização:** 02/05/2026
- **Status:** Operacional. Notificações Push nativas e Normalização de Alvos robusta.

## ✅ O que está funcionando
- **Firebase Push Notifications (NEW):** Migração total dos alertas de WhatsApp para Push nativo via FCM.
- **Normalizador Inteligente (NEW):** Bug de alvos genéricos corrigido com fallback map e priorização por popularidade (seguidores).
- **Service Worker Push:** `firebase-messaging-sw.js` integrado para notificações em background.
- **Meta Ad Library:** Motor de scraping Playwright integrado ao orquestrador.
- **Re-perícia Automática:** Ciclo de atualização de alvos integrado ao pipeline principal.
- **Arquitetura Diamond:** Núcleo assíncrono validado e estável.

## 🛠 Mudanças Técnicas (Sessão 02/05)
1. **API v1 Config:** Novo endpoint `/api/v1/config/firebase` para fornecer chaves públicas ao frontend.
2. **Orquestrador:** Substituída a dependência `core.whatsapp_alerter` por `core.firebase_alerter`.
3. **Frontend Services:** Criado `fcmService.js` e integrado ao ciclo de vida do `app.js`.
4. **TargetNormalizer:** Implementada limpeza agressiva de strings e mapeamento manual de figuras públicas críticas.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] Instaloader Simples:** Frequentemente bloqueado.
- **[DESCARTADO] CallMeBot WhatsApp:** Removido por instabilidade e latência; substituído por Firebase.
- **[DESCARTADO] Seletores Fixos de Classe:** Substituídos por atributos de DOM estáveis.

## 🐛 Bugs Atuais / Bloqueios
- **Nenhum bloqueio crítico detectado.** Próximo foco: Polimento do Tema CSS Diamond.
