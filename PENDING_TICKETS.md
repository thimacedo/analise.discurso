# 🚩 Tickets Pendentes - Sentinela Democrática
Este documento centraliza as tarefas pendentes das sessões anteriores e as novas prioridades de restauração (v20.6/v20.7).

## 1. 🛡️ Resiliência e UI (Prioridade Máxima)
- [ ] **[STN-UI-01]** Ressuscitar CSS (Hotfix Tailwind/CDN).
- [ ] **[STN-UI-02]** Corrigir Ciclo de Vida de Ícones Lucide (setTimeout 50ms).
- [ ] **[STN-001]** Implementar Null-Safety completo no frontend (summary, targets, alerts).

## 2. 🚀 Performance e Memória (P0)
- [ ] **[STN-002]** OOM Prevention: Paginação de 20 itens no DataService e Infinite Scroll.
- [ ] **[STN-007]** Otimização de SQL Query para carregamento instantâneo do Panorama.

## 3. 💰 Monetização e Integrações (P1)
- [ ] **[STN-004]** Configuração de IDs Reais: AdSense (Slot 1779104226) e Stripe Production IDs.

## 4. ⚙️ Infraestrutura e Manutenção (P1)
- [ ] **[STN-003]** Estratégia de Cache Busting (Query string v20.6.0 e headers Vercel).
- [ ] **[STN-006]** Purga de Workers: Deletar obsoletos e centralizar no `orquestrador.py`.
- [ ] **[STN-X01]** Zombie Process Killer: Script para limpar portas 8000/8080.

## 5. ⛏️ Extração e IA (P2)
- [ ] **[STN-005]** Robustez de Scraping: Implementar Fallback de Regex para seletores CSS instáveis.
- [ ] **[STN-IA-01]** Testes automatizados para expressões regulares de extração.

## 6. 🗺️ Roadmap Futuro
- [ ] Validação de escala para > 10.000 alertas.
- [ ] Dashboard de Receita em Tempo Real (Diamond Panel).
- [ ] Gestão de pool dinâmico de proxies rotativos.
- [ ] Webhooks endpoints para Stripe.
- [ ] Integração de Telemetria e Observabilidade.
