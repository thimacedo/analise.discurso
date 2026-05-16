/**
 * PASA v47.1 - State Manager: Memória Central da Sala de Situação
 * Guarda o estado da aplicação. O app.js manda os dados aqui.
 */

export const State = {
    comments: [],
    systemStatus: null,
    profilerStream: [],
    workers: [],
    currentFilter: 'all',
    searchTerm: ''
};
