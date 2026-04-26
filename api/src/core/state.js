/**
 * Sentinela State Management
 * v15.5.20 - Indestructible Navigation
 */

export const state = {
    view: 'monitor',
    data: [],
    stats: {},
    alertas: [],
    currentModalUF: null,
    
    config: {
        version: '15.5.20',
        apiBase: window.location.hostname === 'localhost' ? 'http://localhost:8000/api/v1' : '/api/v1'
    }
};

/**
 * Troca de View com Sincronização de UI
 */
export function setViewState(v) {
    const view = v || 'monitor';
    console.log(`🛰️ Ativando módulo: ${view}`);
    
    state.view = view;
    
    // 1. Esconder todas as views e desativar menu
    document.querySelectorAll('.view-content').forEach(el => {
        el.classList.add('hidden');
        el.style.display = 'none';
    });
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    // 2. Ativar a view selecionada
    const targetView = document.getElementById(`view-${view}`);
    const targetNav = document.getElementById(`nav-${view}`);
    
    if (targetView) {
        targetView.classList.remove('hidden');
        targetView.style.display = 'block';
    }

    if (targetNav) {
        targetNav.classList.add('active');
    }
}

// Ouvinte de mudança de hash (Navegação via URL/Botões)
window.addEventListener('hashchange', () => {
    const view = window.location.hash.replace('#', '');
    setViewState(view);
    if(window.renderAll) window.renderAll();
});
