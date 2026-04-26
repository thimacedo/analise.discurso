/**
 * SENTINELA — Documentação de Arquitetura v15.5 (PROTECTED)
 * 
 * Este documento estabelece os padrões de imutabilidade para o núcleo do sistema.
 * 
 * 1. Camada de Dados (Frozen):
 *    - Supabase (PostgreSQL) como Fonte Única da Verdade (SSOT).
 *    - Todas as IDs de candidatos devem ser unificadas e limpas (sem resíduos técnicos).
 * 
 * 2. Motor de Inteligência (Frozen):
 *    - Protocolo PASA v15.5 injetado via System Instructions.
 *    - Filtro de Hostilidade Universal no apiService.js: busca is_hate=true.
 *    - Filtro Semântico na UI: Bloqueio de Blacklist de Elogios (👏, Parabéns).
 * 
 * 3. Design System (Frozen):
 *    - Estética Stealth Profissional: #020617 base.
 *    - Gráficos Nativos: Renderização via DOM API para fidelidade visual absoluta.
 *    - Tipografia: Plus Jakarta Sans 11px (Hierarchy Scale: 8px to 14px).
 * 
 * 4. Proteção contra Regressão:
 *    - NENHUM AGENTE deve modificar src/core/ui.js ou src/core/state.js sem validar 
 *      os filtros periciais estabelecidos na versão 15.5.11.
 */
