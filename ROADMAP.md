# ROADMAP - Projeto Sentinela Democrática (Diamond Edition)

## Visão Geral
Monitoramento situacional de alto desempenho para as Eleições 2026. Foco em detecção de ódio, redes coordenadas e transparência democrática (PASA v16.4).

## Status Atual (v20.5.9)
- [x] **Conectividade Vercel**: Resolvido conflito de portas e priorizado caminho relativo `/api/v1`.
- [x] **KPIs 24h**: Dashboard operando com janela móvel adaptativa (48h fallback).
- [x] **Refatoração Implacável**: Backend e DataService limpos de 'AI Slop' e otimizados para performance.
- [x] **Persistência de Dossiês**: Infraestrutura STN-001 concluída e testada.
- [x] **Segurança RLS**: Blindagem consolidada com papéis (anon/auth) e Grants explícitos.
- [x] **STN-005: Diretório Global**: Interface premium de perfis com busca e métricas integradas.
- [x] **STN-006: Geopolítica UF**: Mapa vetorial interativo com ranking de hostilidade por estado.
- [x] **STN-007: Refatoração AIService**: Cascata de IA resiliente (Gemini/Groq/Ollama) com latência zero.
- [x] **STN-003: Meta Ad Library**: Painel visual de anúncios detectados integrado ao motor PASA.
- [x] **STN-008: Alertas Preditivos**: Motor de análise de séries temporais concluído (v20.5.7).
- [x] **STN-009: Exportação Executiva**: Geração de dossiês PDF com gráficos automáticos (v20.5.8).
- [x] **STN-010: Multi-Tenancy**: Infraestrutura de isolamento por organização e membros (v20.5.9).

## Próximos Passos (Evolução Contínua)
1. **Interface de Gestão de Organização**: UI para convite de membros e troca de contexto.
2. **App Mobile Native**: Interface em Compose Multiplatform para alertas em tempo real.
3. **Módulo de Resposta Rápida**: Sugestão de contra-narrativas via IA.


## Instruções de Execução
- Priorizar arquitetura 'Local-First' com fallback para Nuvem.
- Validar conformidade PASA em todas as mudanças de classificação.
- Manter o `STATE.md` atualizado após cada ciclo de entrega.
