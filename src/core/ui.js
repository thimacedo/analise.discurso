/**
 * SENTINELA UI ENGINE v16.1.0
 * Summary Integration & Geopolitica Fix
 */
import { state } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        renderKPIs();
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderPredictiveTrends();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }
        if (window.lucide) lucide.createIcons();
    } catch (e) { console.error("Render Error:", e); }
}

async function renderKPIs() {
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    
    try {
        const res = await fetch(`/api/v1/summary?t=${Date.now()}`);
        const data = await res.json();
        
        set('kpi-monitorados', data.total_monitorados || 0);
        set('kpi-hate', (data.total_alertas || 0).toLocaleString());
        set('kpi-total', (data.total_amostra || 0).toLocaleString());
        set('kpi-res', `${data.resiliencia}%`);
    } catch {
        set('kpi-res', 'Ativo');
    }
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;
    const res = await fetch(`/api/v1/stats/top-alvos?t=${Date.now()}`);
    const data = await res.json();
    
    if (!data.length) {
        container.innerHTML = '<p style="text-align: center; padding: 100px 0; font-size: 10px; color: #475569; font-weight: 800; text-transform: uppercase;">Sincronizando...</p>';
        return;
    }
    container.innerHTML = data.map(alvo => `
        <div style="padding: 16px; margin-bottom: 12px; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px;">
            <div style="display: flex; justify-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 12px; font-weight: 800; color: white;">@${alvo.username}</span>
                <span style="font-size: 9px; font-weight: 900; color: #3b82f6;">${alvo.share_blindagem}%</span>
            </div>
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                <div style="height: 100%; background: #2563eb; width: ${alvo.share_blindagem}%"></div>
            </div>
        </div>`).join('');
}

async function renderGeopolitica() {
    const res = await fetch(`/api/v1/geopolitica?t=${Date.now()}`);
    const ufStats = await res.json();
    
    if (document.getElementById('svg-map-br')) {
        renderBrazilMap('svg-map-br', ufStats, (uf, data) => {
            document.getElementById('st-name').innerText = uf;
            document.getElementById('st-targets').innerText = data.alvos || 0;
            document.getElementById('st-hate').innerText = (data.alertas || 0).toLocaleString();
        });
    }
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `<div class="glass-card" style="padding: 20px;"><h4>@${t.username}</h4></div>`).join('');
}

function renderPredictiveTrends() { console.log("Predictive Active"); }
