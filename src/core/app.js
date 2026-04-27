import { state, setViewState } from './state.js';
import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderAll } from './ui.js';

/**
 * SENTINELA CORE v15.15.0
 * UX Elite Edition - Flow & Robustness
 */

async function init() {
    console.log(`🛡️ Sentinela UX Edition v15.15.0 Initializing...`);
    
    setViewState(window.location.hash.substring(1) || 'monitor');
    await refreshData();

    // Micro-interações Globais: Fechar Modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') window.closeCheckout();
    });

    // Fechar Modal clicando fora (Overlay)
    document.getElementById('checkout-modal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) window.closeCheckout();
    });

    window.navigate = (view) => {
        setViewState(view);
        renderAll();
    };

    window.openDetail = (username) => {
        const modal = document.getElementById('checkout-modal');
        if(modal) {
            modal.classList.remove('hidden');
            modal.querySelector('a, button')?.focus(); // Focus Trap Básico
        }
    };

    window.debouncedRender = () => {
        clearTimeout(window.rt);
        // Feedback Visual de Sincronização
        document.querySelectorAll('.glass-card').forEach(c => c.classList.add('is-syncing'));
        window.rt = setTimeout(() => {
            renderAll();
            document.querySelectorAll('.glass-card').forEach(c => c.classList.remove('is-syncing'));
        }, 300);
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
        console.error("Sync Failure:", e);
    }
}

document.addEventListener('DOMContentLoaded', init);
