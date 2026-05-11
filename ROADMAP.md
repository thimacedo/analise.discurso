# ROADMAP - Sentinela Democrática

## 🛠️ Em Andamento (Milestone v20.6/v20.7 - Restauração e Estabilização)
- [ ] **Resiliência do Frontend (Null-Safety)**: Garantir resiliência contra falhas de API.
    - [ ] **[STN-001]** Frontend: Add null-safety para 'summary', 'targets' e 'alerts'.
- [ ] **Otimização de Memória (OOM Prevention)**: Paginação estrita e Infinite Scroll.
    - [ ] **[STN-002]** DataService: Implementar fetch limit de 20 itens.
    - [ ] **[STN-002.1]** Frontend: Validar mecanismo de infinite scroll.
- [ ] **Estratégia de Cache e Monetização**: Versionamento e IDs reais.
    - [ ] **[STN-003]** Cache Busting: Headers Vercel e versionamento JS.
    - [ ] **[STN-004]** Monetização: IDs reais do AdSense (Slot 1779104226) e Stripe.
- [ ] **Infra Local**:
    - [ ] **[STN-X01]** Zombie Process Killer: Script para limpar portas 8000/8080.

## ✅ Concluído
- [x] **UX/UI**: Bordas vermelhas em alertas críticos e Skeleton Loading com `animate-pulse`.
- [x] **MARKETING**: Anúncios AdSense ocultos para usuários Diamond.
- [x] **VIRALIDADE**: Rodapé cinza profissional adicionado aos PDFs gerados.
- [x] **Sistema Central de Recompensas e Quality Gate**: Validação de workers e sistema de ledger de performance.
- [x] **Gatilhos de IA Removidos do Frontend**: Otimização para evitar travamentos de UI.
- [x] **Estrutura Base Diamond**: Dashboard, KPIs e Monitoramento.
- [x] **Scraper**: Implementar Fallback de Regex robusto.
- [x] **Purga**: Centralizar orquestração no `orquestrador.py` e remover obsoletos.
- [x] **Blindagem de Raspagem**: Implementado Proxy Rotativo e Stealth Mode (inclui fallback de regex, delays aleatórios, tratamento de erros).
- [x] **Geração Assíncrona de Dossiês**: Endpoint `/api/v1/dossiers/generate` agora enfileira a tarefa no Supabase.
- [x] **Sistema de Sessão de Trabalho**: Implementada rotina diária automatizada com sleep de 30 minutos.

## 🗺️ Roadmap Futuro (Épicos)
- [ ] **Épico: Escalonamento de Conexões (Vercel Edge Caching & Redis)**: Implementar cache de 60s no frontend para desafogar as conexões simultâneas no Supabase.
- [ ] **Épico: Message Brokers para Workers**: Transitar a inserção direta de dados para um sistema de filas (RabbitMQ ou Celery) consumidas pelo Validador de Recompensas.
- [ ] **Épico: Proxy Rotativo Residencial**: Orquestrar rotação dinâmica de proxies no `core/orquestrador.py` para evitar bans da Meta/Instagram.
- [ ] **Épico Sentinela Enterprise**: Upgrade de Arquitetura.
  - [ ] CI/CD Quality Gates (GitHub Actions).
  - [ ] Dashboard de Receita em Tempo Real.
  - [ ] Gestão de pool dinâmico de proxies.
