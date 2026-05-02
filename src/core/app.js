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

// FUNÇÕES GLOBAIS PARA SIDEBAR E BUSCA
window.setDashboardFilter = (filter) => {
    state.dashboardFilter = filter;
    state.currentPage = 1;
    // Força a atualização dos dados filtrados
    refreshData();
};

window.setDashboardSearch = (query) => {
    state.searchQuery = query;
    // Otimização: Não recarrega API para busca local se possível, ou recarrega se necessário
    window.debouncedRender();
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
        state.loading = true;
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary(),
            dataService.getTargets(),
            dataService.getAlerts(20, 1)
        ]);

        state.data = targets || [];
        state.alertas = alerts || [];
        
        // CÁLCULO DE EMERGÊNCIA: Se o resumo vier vazio, calculamos no frontend
        if (!summary || summary.total_monitorados === 0) {
            const totalHate = state.alertas.filter(a => a.is_hate_speech || a.is_hate).length;
            state.summary = {
                total_monitorados: state.data.length,
                total_alertas: state.alertas.length,
                total_amostra: state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0) || 5000,
                resiliencia: state.data.length > 0 ? (100 - (totalHate / state.alertas.length * 100 || 0)).toFixed(1) : 100
            };
        } else {
            state.summary = summary;
        }

        state.currentPage = 1;
        state.loading = false;
        state.lastSyncAt = new Date().toISOString();
        
        window.debouncedRender();
    } catch (e) {
        console.error('Refresh failure:', e);
        state.loading = false;
        window.debouncedRender();
    }
}

document.addEventListener('DOMContentLoaded', init);
