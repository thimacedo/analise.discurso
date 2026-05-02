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
    dossieGrouping: 'agressoes',
    dossieSearch: '',
    stn_tokens: 0,
    loading: true,
    isLoading: false, // Controle de load do scroll infinito
    currentPage: 1,   // Página atual do feed
    error: null,
    lastSyncAt: null
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