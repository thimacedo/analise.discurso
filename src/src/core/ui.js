/**
 * SENTINELA UI ENGINE v15.11.0
 * Absolute Stability Edition
 */

import { state } from './state.js';

export function renderAll() {
    try {
        renderKPIs();
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        }
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Critical Render Failure:", e);
    }
}

function renderKPIs() {
    const total = state.data.length || 0;
    const hate = state.data.reduce((acc, curr) => acc + (curr.odio || 0), 0);
    
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', total);
    set('kpi-hate', hate.toLocaleString());
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;

    if (!state.data.length) {
        container.innerHTML = '<p class="text-[10px] text-slate-500 text-center py-20 font-black animate-pulse uppercase">Carregando Inteligência...</p>';
        return;
    }

    container.innerHTML = state.data.map(alvo => {
        const b = alvo.share_blindagem || 100;
        return `
            <div class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-black text-white">@${alvo.username}</span>
                    <span class="text-[10px] font-black text-emerald-500 font-mono">${b.toFixed(1)}% Blindagem</span>
                </div>
                <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div class="h-full bg-blue-600" style="width: ${b}%"></div>
                </div>
            </div>`;
    }).join('');
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if (!container) return;
    
    container.innerHTML = state.data.map(t => `
        <div class="glass-card p-6 flex flex-col justify-between h-full bg-slate-900/20">
            <h4 class="text-[10px] font-black text-white">@${t.username}</h4>
            <span class="text-[7px] text-blue-400 uppercase font-black">${t.estado || 'BR'}</span>
            <button class="mt-4 w-full py-2 bg-white/5 text-[9px] font-black uppercase rounded-lg border border-white/5">Detalhes</button>
        </div>
    `).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;
    container.innerHTML = '<p class="col-span-full text-center py-10 text-slate-600 font-black uppercase text-[9px] italic">Monitoramento Estável.</p>';
}
