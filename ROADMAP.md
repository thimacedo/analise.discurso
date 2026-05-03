# ROADMAP - Projeto Sentinela Democrática

## Visão Geral
Refatoração e padronização do sistema de workers e agentes para garantir consistência técnica, segurança e conformidade forense (PASA v16.4).

## Status Atual
- [x] Pesquisa técnica (Linguística Forense + Estratégia de Feed).
- [ ] Implementação do Validador MCP (`validator_mcp.py`).
- [ ] Criação e aplicação das System Instructions (SI) para os Workers.
- [ ] Atualização dos scripts de coleta e classificação.

## Próximos Passos
1. **Implementar Validador MCP:** Finalizar e colocar em produção o `validator_mcp.py`.
2. **Treinar Workers:** Atualizar as System Instructions de cada worker para incluir a chamada obrigatória ao `validate_worker_standard`.
3. **Refatoração Forense:** Ajustar os scripts de coleta para aplicar a lógica de severidade PASA e o cálculo de Relevância Diamond.
4. **Governança:** Registrar todas as mudanças no histórico de commits seguindo o padrão definido.

## Instruções de Execução
- Use `npx @wonderwhy-er/desktop-commander@latest` para interagir.
- Sempre verifique o `PWD` antes de rodar qualquer script em `E:\Projetos\sentinela-democratica`.
- Validar código via `validate_worker_standard` antes de qualquer commit.
