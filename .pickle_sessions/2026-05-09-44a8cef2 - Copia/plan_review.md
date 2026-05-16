# Plan Review: Milestone v20.6 (Estabilização + Purga de Workers)

**Status**: ✅ APPROVED
**Reviewed**: 2026-05-09 18:45

## 1. Structural Integrity
- [x] **Atomic Phases**: As fases estão bem divididas. A inclusão da Fase 5 (Ruthless Refactor) adiciona um valor imenso de manutenção a longo prazo.
- [x] **Worktree Safe**: A limpeza de workers deve ser feita com cautela para não quebrar dependências na API.

*Architect Comments*: A purga de workers (Fase 5) é essencial para reduzir a carga cognitiva do projeto. Recomendo fazer um backup ou commit antes de deletar arquivos físicos.

## 2. Specificity & Clarity
- [x] **File-Level Detail**: Todos os arquivos e diretórios foram mapeados.
- [x] **No "Magic"**: O plano de consolidação exige um inventário prévio (Fase 5, Passo 1), o que é uma abordagem segura.

*Architect Comments*: O passo de "Inventário de Zombies" é o mais crítico. Não delete nada que não tenha certeza absoluta de que é inútil.

## 3. Verification & Safety
- [x] **Automated Tests**: Precisamos garantir que a purga não quebre o boot da API.
- [x] **Manual Steps**: A validação manual após a purga deve incluir um reinício completo do backend.

*Architect Comments*: Adicione um teste de fumaça (smoke test) após a Fase 5: `python api/index.py` deve rodar sem erros de importação.

## 4. Architectural Risks
- **Risco de Dependência**: Alguns workers podem ser importados dinamicamente. O inventário deve ser rigoroso.
- **Risco de Cache**: A Fase 3 (Cache Busting) ajuda a garantir que o cliente não tente chamar workers/endpoints que foram deletados.

## 5. Recommendations
- Utilize o comando `grep` para procurar referências aos nomes dos arquivos de workers antes de deletá-los.
- Mantenha o `BaseWorker` como a interface única para qualquer processo de background remanescente.

---
**Final Verdict**: "This plan is solid. The Ruthless Refactor addition is excellent. Proceed to implementation."
