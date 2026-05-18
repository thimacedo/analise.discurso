# Skill: solenya-automator (v2.0 - PSR-R Enabled)
# Description: Executor autônomo com sistema de pontuação de performance integrado.

## ⚠️ DIRETIVAS DE PERFORMANCE
1. **SELF-AUDIT:** Ao final de cada fase (Research, Plan, Implement), você deve calcular sua pontuação daquela etapa baseada na Tabela PSR-R.
2. **REGISTRO:** Use `RunShellCommand` para atualizar o `metrics/performance_ledger.json` após cada sucesso ou erro.
3. **LOG DE MELHORIA:** Se a pontuação da iteração atual for menor que a anterior, você deve obrigatoriamente incluir um bloco "LESSONS_LEARNED" no próximo arquivo gerado para evitar a repetição do erro.

## CICLO DE VIDA COM PONTUAÇÃO

### Fase 1: Research
- Executar mapeamento de código em `.\`.
- **Cálculo PSR:** Sucesso sem erro de ferramenta = +10.
- **Ação:** Atualizar ledger e avançar.

### Fase 2: Plan
- Desenvolver plano em `.pickle_sessions/`.
- **Cálculo PSR:** Plano que evita erros de PowerShell/Path = +15.

### Fase 3: Implement
- Escrita de código completo (Sem placeholders).
- **Cálculo PSR:** Código funcional = +30. Erro de sintaxe/parâmetro = -15.

### Fase 4: Refactor & Audit
- Revisar `rick_ledger.md` e `performance_ledger.json`.
- **Saída Final:** Apresentar o saldo total de pontos da sessão e o nível de eficiência alcançado (D, C, B, A, ou S-Tier).