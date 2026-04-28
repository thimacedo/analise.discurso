import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas, fetchGlobalStats, fetchSyncToken } from '../services/apiService.js';
import { renderAll } from './ui.js';

let lastSyncToken = null;

async function init() {
    console.log('Sentinela Diamond v16.4.0 initializing...');

    window.addEventListener('hashchange', () => {
        setViewState(window.location.hash.substring(1) || 'monitor');
        renderAll();
    });

    window.navigate = (view) => {
        window.location.hash = view;
    };

    setViewState(window.location.hash.substring(1) || 'monitor');
    renderAll();

    await checkAndRefresh();
    setInterval(checkAndRefresh, 15000);

    if (window.lucide) lucide.createIcons();
}

async function checkAndRefresh() {
    try {
        const currentToken = await fetchSyncToken();

        if (currentToken !== lastSyncToken) {
            lastSyncToken = currentToken;
            await refreshData();
            return;
        }

        state.lastSyncAt = new Date().toISOString();
        renderAll();
    } catch (e) {
        state.error = 'Falha ao verificar novas entradas.';
        state.loading = false;
        renderAll();
        console.error('Sync check failure:', e);
    }
}

async function refreshData() {
    state.loading = true;
    state.error = null;
    renderAll();

    try {
        const [candidatos, alertas, stats] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(15),
            fetchGlobalStats()
        ]);

        state.data = candidatos || [];
        state.alertas = alertas || [];
        state.stats = {
            total: Number(stats?.total || 0),
            hate: Number(stats?.hate || 0)
        };
        state.lastSyncAt = new Date().toISOString();
        state.loading = false;
        state.error = null;
    } catch (e) {
        state.error = 'Nao foi possivel carregar os dados do monitoramento.';
        state.loading = false;
        console.error('Refresh failure:', e);
    }

    renderAll();
}

window.debouncedRender = renderAll;
window.forceRefresh = refreshData;

document.addEventListener('DOMContentLoaded', init);
