import { state, setViewState } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll, initInfiniteScroll } from './ui.js';

// CONFIGURAÇÃO CENTRALIZADA
window.SENTINELA_CONFIG = {
    apiUrl: '/api/v1',
    supabaseUrl: 'https://vhamejkldzxbeibqeqpk.supabase.co',
    refreshInterval: 3600000 
};

// DEBOUNCED RENDER PARA PERFORMANCE
let renderTimeout;
window.debouncedRender = () => {
    if (renderTimeout) cancelAnimationFrame(renderTimeout);
    renderTimeout = requestAnimationFrame(() => {
        renderAll();
    });
};

async function init() {
    console.log('🌟 SENTINELA | Diamond Edition v20.2.0 [SOCIAL CLEAN]');

    try {
        await authService.init();
        if (authService.isAuthenticated()) {
            fcmService.init();
        }
    } catch (e) {
        console.error('[App] Auth failure:', e);
    }

    window.addEventListener('hashchange', () => {
        const view = window.location.hash.substring(1) || 'monitor';
        setViewState(view);
    });

    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);

    await refreshData();
    
    // Inicia o observador de rolagem infinita
    initInfiniteScroll();

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    try {
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary(),
            dataService.getTargets(),
            dataService.getAlerts(20, 1) // Primeira página
        ]);

        state.summary = summary;
        state.data = targets;
        state.alertas = alerts;
        state.currentPage = 1;
        state.loading = false; // Desativa loading após carregar
        state.lastSyncAt = new Date().toISOString();
        
        window.debouncedRender();
    } catch (e) {
        console.error('Refresh failure:', e);
    }
}

document.addEventListener('DOMContentLoaded', init);
