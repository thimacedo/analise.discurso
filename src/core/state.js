export const state = {
    view: 'monitor',
    data: [],
    alertas: [],
    networks: { nodes: [], links: [] },
    networkView: 'clusters',
    stats: {
        total: 0,
        hate: 0,
        resiliencia: 100.0
    },
    summary: null,
    trends: [],
    pasa: [],
    geo: [],
    selectedUF: null,
    selectedAlvo: null,
    filterHateOnly: false,
    dashboardSearch: '',
    directorySearchQuery: '',
    dossieGrouping: 'agressoes',
    dossieSearch: '',
    stn_tokens: 50,   // Amostra grátis de munição forense
    userPlan: 'free', // Começa no Free pra forçar o gasto
    reportOptions: [
        { id: 'base', label: 'Sumário Executivo', cost: 10, required: true },
        { id: 'networks', label: 'Mapeamento de Redes', cost: 20 },
        { id: 'sentiment', label: 'Análise de Sentimento Profunda', cost: 15 },
        { id: 'history', label: 'Histórico Completo (30 dias)', cost: 15 },
        { id: 'export', label: 'Exportação PDF Premium', cost: 10 }
    ],
    currentReportConfig: {
        target: null,
        selectedIds: ['base']
    },
    loading: true,
    isLoading: false, // Controle de load do scroll infinito
    currentPage: 1,   // Página atual do feed
    error: null,
    lastSyncAt: null,
    organizations: [],
    currentOrganizationId: localStorage.getItem('sentinela_org_id') || null
};

export function setViewState(view) {
    state.view = view;
    window.location.hash = view;
    if (window.debouncedRender) window.debouncedRender();
}

export function setNetworkView(view) {
    state.networkView = view;
    if (window.debouncedRender) window.debouncedRender();
}

export function setDossieGrouping(grouping) {
    state.dossieGrouping = grouping;
    if (window.debouncedRender) window.debouncedRender();
}

export function setDossieSearch(query) {
    state.dossieSearch = (query || '').trim().toLowerCase();
    if (window.debouncedRender) window.debouncedRender();
}