import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

async function init() {
    console.log(`🛡️ Sentinela Core v15.14.1 Initializing...`);
    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);
    await refreshData();
    if (document.getElementById('svg-map-br')) {
        renderBrazilMap('svg-map-br', {});
    }
    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };
    window.renderAll = renderAll;
    window.debouncedRender = () => {
        clearTimeout(window.rt);
        window.rt = setTimeout(renderAll, 300);
    };
    window.openDetail = (username) => {
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
        state.data = candidatos || [];
        state.alertas = alertas || [];
        renderAll();
    } catch (e) {
        console.error("Sync Error:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
