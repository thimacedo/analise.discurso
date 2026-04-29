import { state, setViewState } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { renderAll } from './ui.js';

let lastSyncToken = null;

async function init() {
    console.log('SENTINELA | Diamond Edition v19.5 initializing (Identity-First)...');

    // 1. Inicializa Autenticação Real
    try {
        await authService.init();
        console.log(`[App] Auth initialized. Plan: ${authService.getPlan()}`);
    } catch (e) {
        console.error('[App] Auth failure:', e);
    }

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
    // Atualiza a cada 60 segundos
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
        const [targets, alerts, networks] = await Promise.all([
            dataService.getTargets(),
            dataService.getAlerts(20),
            dataService.getNetworks()
        ]);

        state.data = targets;
        state.alertas = alerts;
        state.networks = networks;

        state.lastSyncAt = new Date().toISOString();
        state.loading = false;
        state.error = null;
        
        // Atualiza texto de sincronização na UI
        const syncEl = document.getElementById('status-sync');
        if (syncEl) syncEl.innerText = `Sincronizado: ${new Date().toLocaleTimeString('pt-BR')}`;

    } catch (e) {
        state.error = 'Não foi possível carregar os dados de inteligência.';
        state.loading = false;
        console.error('Refresh failure:', e);
    }

    renderAll();
}

// Global exposure for UI interactions
window.debouncedRender = renderAll;
window.forceRefresh = refreshData;

document.addEventListener('DOMContentLoaded', init);
