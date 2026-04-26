import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.11.0 - Absolute Stability
 */

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    await refreshData();
    
    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };
    
    window.renderAll = renderAll;

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    const [candidatos, alertas] = await Promise.all([
        fetchCandidatos(),
        fetchAlertas(15)
    ]);
    
    state.data = Array.isArray(candidatos) ? candidatos : [];
    state.alertas = Array.isArray(alertas) ? alertas : [];
    
    renderAll();
}

document.addEventListener('DOMContentLoaded', init);
