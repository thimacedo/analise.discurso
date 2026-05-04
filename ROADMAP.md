# ROADMAP - Projeto Sentinela Democrática (Diamond Edition)

## Visão Geral
Monitoramento situacional de alto desempenho para as Eleições 2026. Foco em detecção de ódio, redes coordenadas e transparência democrática (PASA v16.4).

## Status Atual (v20.5.9)
- [x] **Conectividade Vercel**: Resolvido conflito de portas e priorizado caminho relativo `/api/v1`.
- [x] **KPIs 24h**: Dashboard operando com janela móvel adaptativa (48h fallback).
- [x] **Refatoração Implacável**: Backend e DataService limpos de 'AI Slop' e otimizados para performance.
- [x] **Segurança RLS**: Blindagem consolidada com papéis (anon/auth) e Grants explícitos.
- [x] **STN-008: Alertas Preditivos**: Motor de análise de séries temporais concluído (v20.5.7).
- [x] **STN-009: Exportação Executiva**: Geração de dossiês PDF com gráficos automáticos (v20.5.8).
- [x] **STN-010: Multi-Tenancy**: Infraestrutura de isolamento por organização e membros (v20.5.9).
- [x] **Arquitetura de Workers**: Workers modulares baseados em contratos (Diamond Protocol).
- [x] **STN-012: Motor de Inteligência de Alvos**: Varredura automática de pesquisas PDF e priorização.

## Em Planejamento e Refatoração (Reabertos)
- [ ] **STN-001: Repositório de Relatórios Estratégicos** (Inoperante/Dados inconsistentes)
- [ ] **STN-003: Meta Ad Library** (Painel e integração sem dados reais/incompletos)
- [ ] **STN-005: Diretório Global** (Busca e métricas inoperantes)
- [ ] **STN-006: Geopolítica UF** (Mapa e ranking inoperantes)
- [ ] **STN-007: Refatoração AIService** (Cascata falhando/incompleta)

## Próximos Passos (Evolução Contínua)
1. **Interface de Gestão de Organização**: UI para convite de membros e troca de contexto.
2. **App Mobile Native**: Interface em Compose Multiplatform para alertas em tempo real.
3. **Módulo de Resposta Rápida**: Sugestão de contra-narrativas via IA.


## Instruções de Execução
- Priorizar arquitetura 'Local-First' com fallback para Nuvem.
- Validar conformidade PASA em todas as mudanças de classificação.
- Manter o `STATE.md` atualizado após cada ciclo de entrega.
