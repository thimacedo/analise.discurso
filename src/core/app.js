import { state, setViewState } from './state.js';
import { dataService } from '../services/dataService.js';
import { renderAll } from './ui.js';

let lastSyncToken = null;

async function init() {
    console.log('SENTINELA | Diamond Edition v1.0 initializing...');

    window.addEventListener('hashchange', () => {
        setViewState(window.location.hash.substring(1) || 'monitor');
        renderAll();
    });

    window.navigate = (view) => {
        window.location.hash = view;
    };

    setViewState(window.location.hash.substring(1) || 'monitor');
    renderAll();

    await refreshData();
    setInterval(refreshData, window.SENTINELA_CONFIG?.refreshInterval || 60000);

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    state.loading = true;
    state.error = null;
    renderAll();

    try {
        const [summary, trends, pasa, geo] = await Promise.all([
            dataService.getSummary(),
            dataService.getTrends(30),
            dataService.getPasaBreakdown(),
            dataService.getGeoUF()
        ]);

        state.summary = summary;
        state.trends = trends;
        state.pasa = pasa;
        state.geo = geo;
        
        // Compatibilidade com UI atual (migração gradual)
        state.stats = {
            total: summary.total_amostra,
            hate: summary.total_alertas,
            resiliencia: summary.resiliencia
        };
        
        // Carregar alvos para triagem/dossie
        state.data = await dataService.getTargets();
        state.alertas = await dataService.getAlerts(20);

        state.lastSyncAt = new Date().toISOString();
        state.loading = false;
        state.error = null;
    } catch (e) {
        state.error = 'Não foi possível carregar os dados de inteligência.';
        state.loading = false;
        console.error('Refresh failure:', e);
    }

    renderAll();
}

window.debouncedRender = renderAll;
window.forceRefresh = refreshData;

document.addEventListener('DOMContentLoaded', init);

window.debouncedRender = renderAll;
window.forceRefresh = refreshData;

document.addEventListener('DOMContentLoaded', init);
