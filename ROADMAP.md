# ROADMAP - Projeto Sentinela Democrática (Diamond Edition)

## Visão Geral
Monitoramento situacional de alto desempenho para as Eleições 2026. Foco em detecção de ódio, redes coordenadas e transparência democrática (PASA v16.4).

## Status Atual (v20.5.4)
- [x] **Conectividade Vercel**: Resolvido conflito de portas e priorizado caminho relativo `/api/v1`.
- [x] **KPIs 24h**: Dashboard operando com janela móvel de 24 horas (Alvos, Alertas, Amostra).
- [x] **Refatoração Implacável**: Backend e DataService limpos de 'AI Slop' e otimizados para performance.
- [x] **Persistência de Dossiês**: Infraestrutura STN-001 concluída e testada.
- [ ] **Segurança RLS**: Script de blindagem pronto, aguardando execução no DB.

## Próximos Passos (Backlog Ativo)
1. **STN-005: Diretório Global de Perfis**: Implementar visualização e busca para os 343+ candidatos mapeados.
2. **STN-006: Geopolítica UF**: Integração do mapa vetorial D3.js com dados reais de hostilidade por estado.
3. **STN-007: Refatoração AIService**: Consolidar lógica de cascata (Gemini/Groq/Ollama) e reduzir latência de inferência.
4. **STN-003: Meta Ad Library**: Finalizar painel visual para anúncios detectados.

## Instruções de Execução
- Priorizar arquitetura 'Local-First' com fallback para Nuvem.
- Validar conformidade PASA em todas as mudanças de classificação.
- Manter o `STATE.md` atualizado após cada ciclo de entrega.
