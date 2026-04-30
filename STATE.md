# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.7.4 (Frontend Restore & Hybrid Auth Locked)

- **Data da última atualização:** 29/04/2026
- **Status:** Scrapy desacoplado da IA, Fila Dinâmica ativa, Lote Seguro (Capping) operacional.

## ✅ O que está funcionando

- **Fila Dinâmica (Scrapy):** O spider busca alvos diretamente do Supabase, priorizando novos perfis (last_scraped_at NULL).
- **Lote Seguro (IA Capping):** Classificação processa apenas 100 comentários por ciclo, evitando gargalos temporais.

- **API Proxy (FastAPI):** Centraliza requisições com segurança. Sem exposição de chaves no Frontend.
- **Persistência Forense (PASA):** Orquestrador grava `is_hate`, `categoria_ia` (Float) e metadados diretamente no Supabase.
- **Blindagem PASA v16.4:** Falsos positivos mitigados. Críticas políticas classificadas como NEUTRO.
- **Monetização (STN):** Stripe Checkout e Webhooks operacionais. RPC atômica de créditos ativa no banco.
- **Frontend (Diamond UI):** Dashboard dinâmico consumindo dados do Proxy.
- **Resiliência IA:** Backoff Exponencial implementado no `qwen_classifier.py` para Rate Limits (429).
- **Alertas WhatsApp:** Resumo executivo enviado ao final de cada ciclo de mineração via CallMeBot.
- **Monitoramento Inteligente (TargetManager):** Filtro em memória que evita raspagens redundantes. Perfis atualizados nas últimas 48h são ignorados pelo Scrapy.
- **CI/CD Corrigido:** Removido arquivo inválido `.github/workflows/render.yaml` que continha segredos expostos. Implementado workflow real em `.github/workflows/render_deploy.yml`.
- **Frontend Restaurado (Arquitetura Híbrida):** SDK Supabase reintegrado apenas para Auth (Login/Sessão). Todos os dados sensíveis agora trafegam exclusivamente via Proxy FastAPI. Exposição global de funções críticas corrigida.

## 🚫 Abordagens Descartadas

- **[DESCARTADO] SDK Supabase no Frontend:** Risco de segurança. Tudo passa pelo Proxy.
- **[DESCARTADO] Alertas via Discord/Telegram:** WhatsApp é o canal oficial do sistema. Discord removido por preferência do operador.
- **[DESCARTADO] PayPal Manual:** Escalabilidade zero. Substituído por Stripe Webhooks.

## 🐛 Bugs Atuais / Bloqueios

- Nenhum bloqueio crítico. Sistema em voo de cruzeiro.
