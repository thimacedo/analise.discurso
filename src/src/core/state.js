/**
 * Sentinela State Management
 * v15.11.0 - Persistent & Immutable
 */

export const state = {
    view: 'monitor',
    data: [],
    stats: {},
    alertas: [],
    
    config: {
        version: '15.11.0',
        apiBase: '/api/v1'
    }
};

export function setViewState(v) {
    const view = v || 'monitor';
    state.view = view;
    
    document.querySelectorAll('.view-content').forEach(el => {
        el.classList.add('hidden');
        el.style.display = 'none';
    });
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    const targetView = document.getElementById(`view-${view}`);
    const targetNav = document.getElementById(`nav-${view}`);
    
    if (targetView) {
        targetView.classList.remove('hidden');
        targetView.style.display = 'block';
    }
    if (targetNav) targetNav.classList.add('active');
}

window.addEventListener('hashchange', () => {
    const view = window.location.hash.replace('#', '');
    setViewState(view);
    if(window.renderAll) window.renderAll();
});
