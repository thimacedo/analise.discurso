# ROADMAP - Sentinela Democrática

## ✅ Concluído (Milestone v20.6 - Estabilização e Resiliência)
- [x] **Frontend Null-Safety**: Garantir resiliência contra falhas de API (evitar White Screens).
    - [x] Frontend: Add null-safety for 'summary' property (d5e6f7g8-01)
    - [x] Frontend: Add null-safety for 'targets' property (d5e6f7g8-02)
    - [x] Frontend: Add null-safety for 'alerts' property (d5e6f7g8-03)
- [x] **Otimização de Memória (OOM Prevention)**: Paginação estrita (limite de 20 itens) no carregamento inicial.
    - [x] DataService: Implement initial fetch limit of 20 items (h9i0j1k2-01)
    - [x] Frontend: Implement infinite scroll mechanism for data loading (h9i0j1k2-02)
- [x] **Estratégia de Cache Busting**: Versionamento de ES Modules e headers HTTP `no-cache`.
    - [x] Frontend: Add query string versioning to JS files in index.html (p7q8r9s0-01)
- [x] **Resiliência de Scraping**: Fallbacks de Regex para extração de texto em falhas de seletores DOM.
    - [x] Add Regex Fallback for Scraper Selectors (t1u2v3w4)
- [x] **Purga de Workers (Ruthless Refactor)**: Consolidação de serviços redundantes e remoção de referências a workers obsoletos (STN-006).
    - [x] Consolidate Redundant Workers and Remove Obsolete References (b9c0d1e2)
- [x] **Gatilhos de IA Removidos do Frontend**: Otimização sugerida pelo usuário para evitar travamentos de UI.

## Em Andamento (Milestone v20.7 - Enterprise Ready)
- [ ] **Zombie Process Killer**: Script para limpar portas 8000/8080 antes do boot de dev.
    - [ ] Create Script to Kill Zombie Processes on Dev Ports (x5y6z7a8)
- [ ] **Otimização de Performance (Panorama)**: Redução drástica do tempo de carregamento da tela inicial (STN-007).
- [ ] **Correção de Monetização**: IDs reais do AdSense e Stripe Production IDs.
    - [ ] Monetization: Correct Stripe Price ID configuration (l3m4n5o6-01)
    - [ ] Monetization: Correct AdSense ID configuration (l3m4n5o6-02)

## Próximos Passos (Épicos)
- [ ] **Épico Sentinela Enterprise**: Upgrade de Arquitetura e UI/UX.
  - [ ] CI/CD Quality Gates (Ruff, Black, ESLint, GitHub Actions).
  - [ ] Filas Assíncronas e DLQ (Integração com Redis/RabbitMQ).
  - [ ] Refatoração do Front-end com Vite (Cache Busting).
  - [ ] Implementação de Dark Mode Nativo (Tailwind).
  - [ ] UI de Skeleton Screens & Empty States.
  - [ ] UX de Progressive Disclosure (Resumo PASA).
  - [ ] Navegação por Atalhos de Teclado (Hotkeys).
