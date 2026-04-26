import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.5.17 - Total Integration
 */

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    // 1. Restaurar navegação por hash
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    // 2. Iniciar Sincronização de Dados
    await refreshData();
    
    // 3. Inicializar Mapa (Geopolítica)
    if (document.getElementById('svg-map-br')) {
        renderBrazilMap('svg-map-br');
    }
    
    // 4. Expor Eventos Globais
    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };
    window.refresh = refreshData;
    window.renderAll = renderAll;
    
    // Lógica de Detalhes (Modal ou View)
    window.openDetail = (username) => {
        console.log(`🔍 Abrindo dossiê detalhado: @${username}`);
        // Por enquanto, apenas log e alerta. Podemos expandir para um modal real.
        alert(`Dossiê Detalhado de @${username} disponível na versão Premium.`);
    };

    lucide.createIcons();
}

async function refreshData() {
    console.log("🔄 Sincronizando com Supabase...");
    try {
        const [candidatos, alertas] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(15)
        ]);
        
        state.data = candidatos;
        state.alertas = alertas;
        
        renderAll();
        console.log("✅ Sistema sincronizado.");
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
