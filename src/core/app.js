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

        // Atualizar a Sidebar Dinamicamente
        const nowStr = new Date().toLocaleTimeString('pt-BR');
        
        const elMonitorados = document.getElementById('kpi-monitorados');
        if(elMonitorados) elMonitorados.textContent = state.summary.total_monitorados;
        const elTimeMonitorados = document.getElementById('kpi-time-monitorados');
        if(elTimeMonitorados) elTimeMonitorados.textContent = nowStr;

        const elHate = document.getElementById('kpi-hate');
        if(elHate) elHate.textContent = state.summary.total_alertas;
        const elTimeHate = document.getElementById('kpi-time-hate');
        if(elTimeHate) elTimeHate.textContent = nowStr;

        const elTotal = document.getElementById('kpi-total');
        if(elTotal) elTotal.textContent = state.summary.total_amostra.toLocaleString('pt-BR');
        const elTimeTotal = document.getElementById('kpi-time-total');
        if(elTimeTotal) elTimeTotal.textContent = nowStr;

        const elRes = document.getElementById('kpi-res');
        if(elRes) elRes.textContent = `${state.summary.resiliencia}%`;
        const elTimeRes = document.getElementById('kpi-time-res');
        if(elTimeRes) elTimeRes.textContent = nowStr;
        
        // Atualizar lista de Triagem na Sidebar
        const chartMain = document.getElementById('chartMain');
        if (chartMain && state.data.length > 0) {
            const topTargets = [...state.data]
                .sort((a, b) => (b.prioridade_coleta || 0) - (a.prioridade_coleta || 0))
                .slice(0, 15);
                
            chartMain.innerHTML = topTargets.map(alvo => {
                const priorityScore = alvo.prioridade_coleta || 0;
                const percent = Math.min(100, (priorityScore / 100) * 100);
                let color = '#10b981'; // green
                if(percent > 60) color = '#f59e0b'; // yellow
                if(percent > 80) color = '#ef4444'; // red
                
                return `
                <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row p-3 rounded-xl border border-transparent hover:bg-white hover:shadow-sm cursor-pointer transition-all flex items-center gap-3">
                    <div class="monitor-avatar w-10 h-10 border-2 border-slate-100">
                        <img src="https://ui-avatars.com/api/?name=${alvo.username}&background=0D8ABC&color=fff" alt="${alvo.username}" loading="lazy" width="40" height="40">
                    </div>
                    <div class="flex-1">
                        <div class="flex justify-between items-center mb-1">
                            <strong class="text-xs font-black text-slate-800">@${alvo.username}</strong>
                            <span class="text-[9px] font-black px-1.5 py-0.5 rounded bg-red-50 text-red-500">${priorityScore}</span>
                        </div>
                        <div class="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                            <div class="h-full" style="width:${percent}%; background:${color}"></div>
                        </div>
                    </div>
                </div>
                `;
            }).join('');
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
