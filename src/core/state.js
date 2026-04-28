export const state = {
    view: 'monitor',
    data: [],
    alertas: [],
    stats: {
        total: 0,
        hate: 0
    },
    selectedUF: null,
    selectedAlvo: null,
    dossieGrouping: 'agressoes',
    dossieSearch: '',
    loading: true,
    error: null,
    lastSyncAt: null
};

export function setViewState(view) {
    state.view = view;
    window.location.hash = view;
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
