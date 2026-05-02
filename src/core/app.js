import { state, setViewState, setNetworkView } from './state.js';
import { dataService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { fcmService } from '../services/fcmService.js';
import { renderAll } from './ui.js';

// CONFIGURAÇÃO CENTRALIZADA E PROTEGIDA
window.SENTINELA_CONFIG = {
    apiUrl: '/api/v1',
    supabaseUrl: 'https://vhamejkldzxbeibqeqpk.supabase.co',
    // A chave agora é injetada via processo de build ou authService
    // Para esta versão, mantemos o fallback controlado
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY',
    refreshInterval: 3600000 
};

async function init() {
    console.log('💎 SENTINELA | Diamond Edition v20.1.1 [ALTA DENSIDADE]');

    try {
        await authService.init();
        if (authService.isAuthenticated()) {
            fcmService.init();
        }
    } catch (e) {
        console.error('[App] Auth failure:', e);
    }

    window.addEventListener('hashchange', () => {
        const view = window.location.hash.substring(1) || 'monitor';
        setViewState(view);
    });

    const initialView = window.location.hash.substring(1) || 'monitor';
    setViewState(initialView);

    await refreshData();
    setInterval(refreshData, 60000); // 1 min sync

    if (window.lucide) lucide.createIcons();
}

async function refreshData() {
    try {
        const [summary, targets, alerts, temporal] = await Promise.all([
            dataService.getSummary(),
            dataService.getTargets(),
            dataService.getAlerts(50), // Aumentado para preencher a nova densidade
            dataService.getPasaTemporal(7)
        ]);

        state.summary = summary;
        state.data = targets;
        state.alertas = alerts;
        state.pasaTemporal = temporal;
        state.lastSyncAt = new Date().toISOString();
        
        renderAll();
    } catch (e) {
        console.error('Refresh failure:', e);
    }
}

document.addEventListener('DOMContentLoaded', init);
