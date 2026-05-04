# ROADMAP - Projeto Sentinela Democrática (Diamond Edition)

## Visão Geral
Monitoramento situacional de alto desempenho para as Eleições 2026. Foco em detecção de ódio, redes coordenadas e transparência democrática (PASA v16.4).

## Status Atual (v20.5.6)
- [x] **Conectividade Vercel**: Resolvido conflito de portas e priorizado caminho relativo `/api/v1`.
- [x] **KPIs 24h**: Dashboard operando com janela móvel adaptativa (48h fallback).
- [x] **Refatoração Implacável**: Backend e DataService limpos de 'AI Slop' e otimizados para performance.
- [x] **Persistência de Dossiês**: Infraestrutura STN-001 concluída e testada.
- [x] **Segurança RLS**: Blindagem consolidada com papéis (anon/auth) e Grants explícitos.
- [x] **STN-005: Diretório Global**: Interface premium de perfis com busca e métricas integradas.
- [x] **STN-006: Geopolítica UF**: Mapa vetorial interativo com ranking de hostilidade por estado.
- [x] **STN-007: Refatoração AIService**: Cascata de IA resiliente (Gemini/Groq/Ollama) com latência zero.
- [x] **STN-003: Meta Ad Library**: Painel visual de anúncios detectados integrado ao motor PASA.

## Próximos Passos (Evolução Contínua)
1. **Alertas Preditivos**: Uso de séries temporais para prever picos de hostilidade.
2. **Exportação Executiva**: Geração de relatórios PDF com gráficos D3.js embarcados.
3. **Multi-Tenancy**: Sistema de sub-organizações para gestão de campanhas independentes.


## Instruções de Execução
- Priorizar arquitetura 'Local-First' com fallback para Nuvem.
- Validar conformidade PASA em todas as mudanças de classificação.
- Manter o `STATE.md` atualizado após cada ciclo de entrega.
