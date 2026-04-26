import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';

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
    console.log("🔄 Sincronizando dados com o servidor...");
    try {
        const [candidatos, alertas] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(12)
        ]);
        
        state.data = candidatos;
        state.alertas = alertas;
        
        // Disparar Renderização de todos os componentes
        renderAll();
        
        console.log("✅ Dados sincronizados e interface atualizada.");
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
