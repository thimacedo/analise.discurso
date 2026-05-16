/**
 * PASA v47.1 - App Orchestrator: O Maestro da Sala de Situação
 * Busca dados -> Manda pro State -> Manda State pro UI.
 * Zero lógica de DOM aqui.
 */
import { State } from './state.js';
import { UI } from './ui.js';
import { initAuth, getCurrentUserEmail } from './auth.js';
import { renderSessionManager } from '../components/session-manager.js';

const SUPABASE_URL = window.SUPABASE_URL;
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY;

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    renderSessionManager('session-manager-container');
    fetchAllData();
    setupFilters();
    setupSearch();
});

async function fetchAllData() {
    await Promise.all([fetchComments(), fetchProfilerStream()]);
}

async function fetchComments() {
    if (!SUPABASE_URL) return;
    try {
        const res = await fetch(`${SUPABASE_URL}/rest/v1/comentarios?select=id,autor_username,texto_limpo,data_coleta,is_hate,categoria_ia,direcao_odio,confianca_ia,processado_ia,candidato_id,ccf_density,ccf_sync,ccf_performativity&order=data_coleta.desc&limit=100`, {
            headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
        });
        State.comments = await res.json();
        applyFiltersAndRender();
    } catch (e) { console.error(e); }
}

async function fetchProfilerStream() {
    try {
        const res = await fetch(`/docs/kpis.json?t=${Date.now()}`);
        const kpis = await res.json();
        document.getElementById('kpi-targets').textContent = kpis.targets || 0;
        document.getElementById('kpi-hate').textContent = kpis.alerts || 0;
        document.getElementById('kpi-total').textContent = kpis.db_sample || 0;

        const streamRes = await fetch(`/docs/profiler_stream.json?t=${Date.now()}`);
        State.profilerStream = await streamRes.json();
        UI.renderProfilerStream(State.profilerStream.slice().reverse());
    } catch (e) { console.error(e); }
}

function applyFiltersAndRender() {
    let filtered = State.comments;
    if (State.currentFilter === 'hate') filtered = filtered.filter(c => c.is_hate === true);
    if (State.currentFilter === 'critical') filtered = filtered.filter(c => c.is_hate === true && c.confianca_ia >= 0.8);
    
    if (State.searchTerm) {
        const term = State.searchTerm.toLowerCase();
        filtered = filtered.filter(c => (c.texto_limpo || '').toLowerCase().includes(term) || (c.autor_username || '').toLowerCase().includes(term));
    }
    
    UI.renderFeed(filtered);
}

function setupFilters() {
    window.setDashboardFilter = (filter) => {
        State.currentFilter = filter;
        applyFiltersAndRender();
        document.querySelectorAll('#btn-filter-all, #btn-filter-hate, #btn-filter-critical').forEach(b => b.classList.remove('active'));
        document.getElementById(`btn-filter-${filter}`)?.classList.add('active');
    };
}

function setupSearch() {
    const input = document.getElementById('dashboard-search-input');
    if(input) {
        input.addEventListener('keyup', (e) => {
            State.searchTerm = e.target.value;
            applyFiltersAndRender();
        });
    }
}

window.auditComment = async (commentId, rotulo) => {
    const res = await fetch('/api/v1/audit/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment_id: commentId, rotulo_correto: rotulo, validado_por: getCurrentUserEmail() })
    });
    if (res.ok) { fetchComments(); } // Refresh
};
