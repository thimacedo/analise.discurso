import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.5.0
 */

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    // Restaurar navegação por hash
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    // Iniciar Sincronização
    await refreshData();
    
    // Eventos Globais
    window.navigate = setViewState;
    window.refresh = refreshData;
    
    lucide.createIcons();
}

async function refreshData() {
    try {
        const [candidatos, alertas] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(12)
        ]);
        
        state.data = candidatos;
        state.alertas = alertas;
        
        updateKPIs();
        // Disparar renderizações (implementadas no ui.js)
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

function updateKPIs() {
    const total = state.data.length;
    const hate = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    
    const set = (id, val) => {
        const el = document.getElementById(id);
        if(el) el.innerText = val;
    };
    
    set('kpi-monitorados', total);
    set('kpi-hate', hate);
}

document.addEventListener('DOMContentLoaded', init);
