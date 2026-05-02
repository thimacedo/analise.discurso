import { state, setViewState, setNetworkView } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll } from './ui.js';

let lastSyncToken = null;

// Global exposure for UI interactions (Exposed immediately)
window.debouncedRender = renderAll;

window.forceRefresh = async () => {
    console.log("Sincronizando dados via Proxy...");
    await refreshData();
};

window.navigate = (view) => {
    window.location.hash = view;
};

window.setNetworkView = (view) => {
    const subNav = document.getElementById('sub-networks');
    if (subNav) subNav.style.display = 'flex';
    setNetworkView(view);
};

// Toggle manual triage visibility
window.toggleTriage = (commentId) => {
    const el = document.getElementById(`triage-actions-${commentId}`);
    if (el) el.style.display = el.style.display === 'none' ? 'flex' : 'none';
};

// Handle manual false positive marking
window.markFalsePositive = async (id) => {
    if (!confirm("Confirmar que este comentário NÃO é discurso de ódio? (Isso treinará a IA)")) return;

    try {
        const response = await fetch(`${window.SENTINELA_CONFIG.apiUrl}/alerts/false-positive`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        if (response.ok) {
            // Remove do estado local e re-renderiza
            state.alertas = state.alertas.filter(a => a.id !== id);
            // Atualiza contadores do alvo se houver
            if (state.selectedAlvo) {
                state.selectedAlvo.comentarios_odio_count = Math.max(0, state.selectedAlvo.comentarios_odio_count - 1);
            }
            renderAll();
        } else {
            alert("Erro ao processar triagem manual.");
        }
    } catch (e) {
        console.error("Triage error:", e);
    }
};

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
        const [summary, trends, pasa, geo, temporal] = await Promise.all([
            dataService.getSummary(),
            dataService.getTrends(30),
            dataService.getPasaBreakdown(),
            dataService.getGeoUF(),
            dataService.getPasaTemporal(7)
        ]);

        state.summary = summary;
        state.trends = trends;
        state.pasa = pasa;
        state.geo = geo;
        state.pasaTemporal = temporal;

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
