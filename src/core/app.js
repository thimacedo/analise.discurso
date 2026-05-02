import { state, setViewState, setNetworkView } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll } from './ui.js';

let lastSyncToken = null;

// ... (restante dos window exposure)

async function init() {
    console.log('SENTINELA | Diamond Edition v19.7 initializing (Identity-First)...');

    // 1. Inicializa Autenticação Real
    try {
        await authService.init();
        state.stn_tokens = authService.user?.stn_tokens || 0;
        console.log(`[App] Auth initialized. Plan: ${authService.getPlan()} | Tokens: ${state.stn_tokens}`);
        
        // 2. Inicializa Notificações Push se autenticado
        if (authService.isAuthenticated()) {
            fcmService.init();
        }
    } catch (e) {
        console.error('[App] Auth failure:', e);
    }


    window.addEventListener('hashchange', () => {
        const view = window.location.hash.substring(1) || 'monitor';
        setViewState(view);
        renderAll();
    });

    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
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

document.addEventListener('DOMContentLoaded', init);
