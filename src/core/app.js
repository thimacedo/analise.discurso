import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.6.6 - Performance & INP Optimization
 */

// Helper para evitar sobrecarga de processamento (Debounce)
let renderTimeout;
function debouncedRender() {
    clearTimeout(renderTimeout);
    renderTimeout = setTimeout(() => {
        renderAll();
    }, 300);
}

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    await refreshData();
    
    if (document.getElementById('svg-map-br')) {
        renderBrazilMap('svg-map-br');
    }
    
    // Exposição Global Otimizada
    window.navigate = (view) => {
        setViewState(view);
        renderAll(); // Renderização imediata na troca de aba
    };
    
    window.debouncedRender = debouncedRender;
    window.refresh = refreshData;
    window.renderAll = renderAll;
    
    window.openDetail = (username) => {
        console.log(`🔍 Solicitação de Dossiê: @${username}`);
        const modal = document.getElementById('checkout-modal');
        if(modal) modal.classList.remove('hidden');
    };

    lucide.createIcons();
}

async function refreshData() {
    try {
        const [candidatos, alertas] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(15)
        ]);
        state.data = candidatos;
        state.alertas = alertas;
        renderAll();
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
