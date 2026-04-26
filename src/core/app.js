import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.8.1 - Absolute Stability
 */

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    // 1. Definir View Inicial
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    // 2. Carregar Dados com Silêncio Operacional
    try {
        await refreshData();
    } catch (e) {
        console.error("FALHA INICIAL:", e);
    }
    
    // 3. Renderizar Componentes Fixos com Proteção
    if (document.getElementById('svg-map-br')) {
        try {
            renderBrazilMap('svg-map-br', {}); // Iniciar mapa vazio/neutro
        } catch (e) { console.warn("Erro ao iniciar mapa:", e); }
    }
    
    // 4. Exposição Global
    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };
    
    window.renderAll = renderAll;
    window.openDetail = (username) => {
        const modal = document.getElementById('checkout-modal');
        if(modal) modal.classList.remove('hidden');
    };

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    const [candidatos, alertas] = await Promise.all([
        fetchCandidatos().catch(() => []),
        fetchAlertas(15).catch(() => [])
    ]);
    
    state.data = Array.isArray(candidatos) ? candidatos : [];
    state.alertas = Array.isArray(alertas) ? alertas : [];
    
    renderAll();
}

document.addEventListener('DOMContentLoaded', init);
