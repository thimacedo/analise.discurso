import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

/**
 * Orquestrador Principal do Sentinela
 * v15.5.18 - Resilient Integration
 */

async function init() {
    console.log(`🛡️ Sentinela Core ${state.config.version} Initializing...`);
    
    // 1. Restaurar navegação por hash
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    
    // 2. Iniciar Sincronização de Dados
    await refreshData();
    
    // 3. Expor Eventos Globais
    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };
    window.refresh = refreshData;
    window.renderAll = renderAll;
    
    // Lógica de Mapa (Interatividade)
    window.focusState = (uf) => {
        if(window.updateMapCard) window.updateMapCard(uf);
    };

    window.openDetail = (username) => {
        console.log(`🔍 Abrindo dossiê detalhado: @${username}`);
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
        
        // 4. Renderização Completa
        renderAll();
        
        // 5. Atualizar Mapa com dados reais
        if (document.getElementById('svg-map-br')) {
            const stats = {};
            candidatos.forEach(t => {
                const uf = (t.estado || 'BR').toUpperCase();
                if(!stats[uf]) stats[uf] = { count: 0, hate: 0 };
                stats[uf].count += 1;
                stats[uf].hate += (t.comentarios_odio_count || 0);
            });
            renderBrazilMap('svg-map-br', stats);
        }

        console.log("✅ Sistema sincronizado e visualizado.");
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
