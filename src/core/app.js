// src/core/app.js
// SENTINELA | Diamond Edition - App Core v20.5.6 [STABLE]

import { state, setViewState } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll, renderFeed, toggleSkeleton } from './ui.js?v=20.5.6';

// Constants for API URLs and other configurations
const SENTINELA_CONFIG = {
    apiUrl: 'http://localhost:3000/api/v1' // Placeholder - assume this is dynamically set or configured elsewhere
};

let renderTimeout;
window.debouncedRender = () => {
    if (renderTimeout) cancelAnimationFrame(renderTimeout);
    renderTimeout = requestAnimationFrame(() => renderAll());
};

window.setDashboardFilter = (filter) => {
    state.dashboardFilter = filter;
    state.currentPage = 1;
    refreshData();
};

window.setDashboardSearch = (query) => {
    state.searchQuery = query;
    state.currentPage = 1;
    const clearBtn = document.getElementById('clear-search-btn');
    if (clearBtn) clearBtn.style.display = query ? 'block' : 'none';
    window.debouncedRender();
};

window.clearDashboardSearch = () => {
    const input = document.getElementById('dashboard-search-input');
    if (input) input.value = '';
    window.setDashboardSearch('');
};

// Função para sinalizar falso positivo (adicionar ao app.js)
window.markFalsePositive = async (commentId, cardElement) => {
  try {
    const response = await fetch(`${SENTINELA_CONFIG.apiUrl}/alerts/false-positive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: commentId })
    });
    if (response.ok) {
      console.log('[FP] Comentário sinalizado com sucesso.');
      if (cardElement) cardElement.style.display = 'none';
    } else {
      console.error('[FP] Erro ao sinalizar:', await response.json());
    }
  } catch (e) {
    console.error('[FP] Falha na requisição:', e);
  }
};

// Adiciona a função window.unlockIntel
window.unlockIntel = (alertId) => {
  console.log('[Intel] Solicitada auditoria para alerta:', alertId);
  // Exibe os detalhes do alerta
  const alerta = state.alertas.find(a => a.id === alertId);
  if (alerta) {
    alert(`Auditoria do Alerta:\n\nCategoria: ${alerta.categoria_ia}\nAlvo: @${alerta.alvo_username}\nTexto: "${alerta.texto_bruto}"\nHash: ${alerta.id}`);
  } else {
    alert('Detalhes do alerta não disponíveis.');
  }
};

// Adiciona a função window.setFiltroAlvo
window.setFiltroAlvo = (username) => {
  console.log('[Filtro] Definindo filtro para:', username);
  const input = document.getElementById('dashboard-search-input');
  if (input) {
    input.value = username;
    window.setDashboardSearch(username);
  }
};

// Confirma a existência e adiciona a função window.markFalsePositive se ausente
if (typeof window.markFalsePositive === 'undefined') {
    window.markFalsePositive = async (commentId, cardElement) => {
      try {
        const response = await fetch(`${SENTINELA_CONFIG.apiUrl}/alerts/false-positive`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: commentId })
        });
        if (response.ok) {
          console.log('[FP] Comentário sinalizado com sucesso.');
          if (cardElement) {
              const container = cardElement.closest('.post-card-container');
              if (container) container.style.display = 'none';
          }
        } else {
          const errorData = await response.json();
          console.error('[FP] Erro ao sinalizar:', errorData);
          alert(`Erro ao sinalizar falso positivo: ${errorData.message || response.statusText}`);
        }
      } catch (e) {
        console.error('[FP] Falha na requisição:', e);
        alert('Falha na requisição para sinalizar falso positivo. Verifique o console.');
      }
    };
}
};


async function loadMoreAlerts() {
    if (state.isLoading || state.currentPage >= 5) return;
    try {
        state.isLoading = true;
        toggleSkeleton(true);
        const nextPage = state.currentPage + 1;
        const newAlerts = await dataService.getAlerts(20, nextPage);
        if (Array.isArray(newAlerts) && newAlerts.length > 0) {
            state.alertas = [...state.alertas, ...newAlerts];
            state.currentPage = nextPage;
            renderFeed(newAlerts, 'feed-alertas', true);
        } else {
            state.currentPage = 999;
        }
    } catch (e) {
        console.error('[App] Scroll Error:', e);
    } finally {
        state.isLoading = false;
        toggleSkeleton(false);
    }
}

function initInfiniteScroll() {
    const sentinel = document.getElementById('scroll-sentinel');
    if (!sentinel) return;
    new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !state.isLoading && state.currentPage < 10) loadMoreAlerts();
    }, { threshold: 0.1 }).observe(sentinel);
}


async function init() {
    console.log('🌟 SENTINELA | Diamond Edition v20.5.6 [STABLE]');
    try {
        await authService.init();
        if (authService.isAuthenticated()) fcmService.init();
    } catch (e) {
        console.error('[App] Init Error:', e);
    }
    window.addEventListener('hashchange', () => setViewState(window.location.hash.substring(1) || 'monitor'));
    setViewState(window.location.hash.substring(1) || 'monitor');
    await refreshData();
    initInfiniteScroll();
    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    try {
        state.loading = true;
        toggleSkeleton(true);
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary().catch(() => ({})), // Retorna objeto vazio em caso de erro
            dataService.getTargets().catch(() => []),   // Retorna array vazio em caso de erro
            dataService.getAlerts(20, 1).catch(() => [])       // Retorna array vazio em caso de erro
        ]);

        state.data = targets;
        state.alertas = alerts;
        state.summary = summary;

        const now = new Date().toLocaleTimeString('pt-BR');
        const updateEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        
        updateEl('kpi-monitorados', state.summary?.total_monitorados ?? '---');
        updateEl('kpi-time-monitorados', 'agora');
        updateEl('kpi-hate', state.summary?.total_alertas ?? '---');
        updateEl('kpi-time-hate', 'agora');
        updateEl('kpi-total', state.summary?.total_amostra?.toLocaleString('pt-BR') ?? '---');
        updateEl('kpi-time-total', 'agora');
        updateEl('kpi-res', `${state.summary?.resiliencia ?? 0}%`);
        updateEl('kpi-time-res', 'agora');
        
        const chartMain = document.getElementById('chartMain');
        if (chartMain) {
            if (state.data.length > 0) {
                chartMain.innerHTML = [...state.data]
                    .sort((a, b) => (b?.prioridade_coleta || 0) - (a?.prioridade_coleta || 0))
                    .slice(0, 15)
                    .map(alvo => {
                        const score = alvo.prioridade_coleta || 0;
                        const color = score > 80 ? '#ef4444' : score > 60 ? '#f59e0b' : '#10b981';
                        return `
                        <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row p-3 rounded-xl border border-transparent hover:bg-white hover:shadow-sm cursor-pointer transition-all flex items-center gap-3">
                            <div class="monitor-avatar w-10 h-10 border-2 border-slate-100">
                                <img src="https://ui-avatars.com/api/?name=${alvo.username}&background=0D8ABC&color=fff" alt="${alvo.username}" loading="lazy" width="40" height="40">
                            </div>
                            <div class="flex-1">
                                <div class="flex justify-between items-center mb-1">
                                    <strong class="text-xs font-black text-slate-800">@${alvo.username}</strong>
                                    <span class="text-[9px] font-black px-1.5 py-0.5 rounded bg-red-50 text-red-500">${score}</span>
                                </div>
                                <div class="w-full bg-slate-100 h-1 rounded-full overflow-hidden"><div class="h-full" style="width:${Math.min(100, score)}%; background:${color}"></div></div>
                            </div>
                        </div>`;
                    }).join('');
            } else {
                chartMain.innerHTML = '<p class="text-xs text-slate-400">Nenhum alvo para exibir.</p>';
            }
        }

        state.currentPage = 1;
        state.loading = false;
        state.lastSyncAt = new Date().toISOString();
        
        if (state.userPlan === 'diamond' || state.userPlan === 'premium') {
            const adCards = document.querySelectorAll('.insight-card');
            adCards.forEach(card => {
                // Verifica se o card contém um anúncio AdSense ou texto indicativo
                if (card.innerText.includes('Publicidade Estratégica') || card.querySelector('.adsbygoogle')) {
                    card.style.display = 'none !important'; // Garante que o anúncio seja ocultado
                }
            });
        }

        renderAll(state.summary, state.data, state.alertas);
    } catch (e) {
        console.error('[App] Refresh Error:', e);
        state.loading = false;
        renderAll({}, [], []);
    }
}

document.addEventListener('DOMContentLoaded', init);
