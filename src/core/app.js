import { state, setViewState } from './state.js';
import { SENTINELA_CONFIG } from '../config.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll, initInfiniteScroll, initSwipeGestures } from './ui.js';

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
    state.currentPage = 1; // Reseta para a página 1 ao pesquisar
    
    const clearBtn = document.getElementById('clear-search-btn');
    if (clearBtn) {
        clearBtn.style.display = query ? 'block' : 'none';
    }
    
    // Otimização: Não recarrega API para busca local se possível, ou recarrega se necessário
    window.debouncedRender();
};

window.clearDashboardSearch = () => {
    const input = document.getElementById('dashboard-search-input');
    if (input) input.value = '';
    window.setDashboardSearch('');
};

async function init() {
    console.log('🌟 SENTINELA | Diamond Edition v20.5.6 [STABLE]');

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
    
    // Inicia o observador de rolagem infinita e gestos de Swipe
    initInfiniteScroll();
    initSwipeGestures();

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    try {
        state.loading = true;
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary(),
            dataService.getTargets(),
            // Puxa 200 itens para garantir que a busca local tenha massa de dados suficiente
            dataService.getAlerts(200, 1)
        ]);

        state.data = targets || [];
        state.alertas = alerts || [];
        
        // PRIORIDADE: Dados reais da API. FALLBACK: Estado local limpo.
        if (summary && !summary.error) {
            state.summary = summary;
        } else {
            // Fallback robusto se a API falhar
            const totalHate = state.alertas.length;
            const totalAmostra = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0) || 1000;
            state.summary = {
                total_monitorados: state.data.length,
                total_alertas: totalHate,
                total_amostra: totalAmostra,
                resiliencia: totalAmostra > 0 ? ((totalAmostra - totalHate) / totalAmostra * 100).toFixed(1) : 100
            };
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
