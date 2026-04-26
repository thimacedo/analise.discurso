/**
 * Sentinela State Management
 * v15.5.0
 */

export const state = {
    view: 'monitor',
    data: [],
    stats: {},
    alertas: [],
    currentModalUF: null,
    
    // Configurações Globais
    config: {
        version: '15.5.0',
        apiBase: window.location.hostname === 'localhost' ? 'http://localhost:8000/api/v1' : '/api/v1'
    }
};

export function setViewState(v) {
    state.view = v;
    window.location.hash = v;
    
    document.querySelectorAll('.view-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    const targetView = document.getElementById(`view-${v}`);
    const targetNav = document.getElementById(`nav-${v}`);
    
    if(targetView) targetView.classList.remove('hidden');
    if(targetNav) targetNav.classList.add('active');
}
