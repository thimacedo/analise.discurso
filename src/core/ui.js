/**
 * SENTINELA UI ENGINE v16.0.0
 * Unified API & UX Diamond Edition
 */
import { state } from './state.js';

export function renderAll() {
    try {
        renderKPIs();
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
            renderPredictiveTrends();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        }
        if (window.lucide) lucide.createIcons();
    } catch (e) { console.error("Render Error:", e); }
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;

    try {
        const response = await fetch(`/api/v1/stats/top-alvos?t=${Date.now()}`);
        const alvos = await response.json();

        if (!alvos || !alvos.length) {
            container.innerHTML = '<p style="text-align: center; padding: 100px 0; font-size: 10px; color: #475569; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3em;">Sincronizando Base...</p>';
            return;
        }

        container.innerHTML = alvos.map(alvo => {
            const b = alvo.share_blindagem || 100;
            const isDanger = b < 50;
            return `
                <div onclick="window.openDetail('${alvo.username}')" class="glass-card" style="padding: 16px; margin-bottom: 12px; cursor: pointer; border-left: 4px solid ${isDanger ? '#ef4444' : '#10b981'};">
                    <div style="display: flex; justify-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 800; color: white;">@${alvo.username}</span>
                        <span style="font-size: 10px; font-weight: 900; color: ${isDanger ? '#f87171' : '#34d399'}; margin-left: auto;">${b.toFixed(1)}%</span>
                    </div>
                    <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; display: flex;">
                        <div style="height: 100%; background: #2563eb; width: ${b}%"></div>
                        <div style="height: 100%; background: #ef4444; width: ${100-b}%"></div>
                    </div>
                </div>`;
        }).join('');
    } catch (e) { console.error("Monitor Render Failure:", e); }
}

function renderKPIs() {
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    const totalAlvos = state.data.length || 0;
    const totalAlertas = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    const totalAmostra = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0);
    const resiliencia = totalAmostra > 0 ? (100 - (totalAlertas / totalAmostra * 100)).toFixed(1) : "100.0";

    set('kpi-monitorados', totalAlvos);
    set('kpi-hate', totalAlertas.toLocaleString());
    set('kpi-total', totalAmostra.toLocaleString());
    set('kpi-res', `${resiliencia}%`);
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `
        <div class="glass-card" style="padding: 24px; text-align: center;">
            <h4 style="font-size: 14px; font-weight: 800; color: white; margin-bottom: 4px;">@${t.username}</h4>
            <span style="font-size: 9px; color: #3b82f6; font-weight: 800; text-transform: uppercase;">${t.estado || 'BR'}</span>
            <button onclick="window.openDetail('${t.username}')" style="margin-top: 16px; width: 100%; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); color: white; font-size: 10px; font-weight: 800; border-radius: 8px; cursor: pointer;">Dossiê</button>
        </div>
    `).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas.length) return;
    container.innerHTML = state.alertas.slice(0, 4).map(a => `
        <div class="glass-card" style="padding: 16px; border-left: 2px solid #ef4444;">
            <p style="font-size: 9px; font-weight: 900; color: #3b82f6; text-transform: uppercase; margin-bottom: 4px;">@${a.alvo}</p>
            <p style="font-size: 11px; color: #94a3b8; font-style: italic; line-height: 1.4;">"${a.texto}"</p>
        </div>
    `).join('');
}

function renderPredictiveTrends() {
    console.log("Predictive Engine Operational.");
}
