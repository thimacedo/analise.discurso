/**
 * SENTINELA UI ENGINE v15.11.9
 */
import { state } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        renderKPIs();
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }
        if (window.lucide) lucide.createIcons();
    } catch (e) { console.error("Render Error:", e); }
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;
    const response = await fetch('/api/v1/stats/top-alvos');
    const alvos = await response.json();
    if (!alvos || !alvos.length) {
        container.innerHTML = '<p class="text-center py-20 text-[10px] uppercase font-black opacity-50">Sincronizando Base...</p>';
        return;
    }
    container.innerHTML = alvos.map(alvo => {
        const b = alvo.share_blindagem || 100;
        return `<div onclick="window.openDetail('${alvo.username}')" class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2 cursor-pointer hover:bg-white/[0.04] transition-all"><div class="flex justify-between items-center"><span class="text-xs font-bold text-white">@${alvo.username}</span><span class="text-[10px] font-black text-emerald-500 font-mono">${b.toFixed(1)}% Blindagem</span></div><div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex"><div class="h-full bg-blue-600" style="width: ${b}%"></div><div class="h-full bg-red-600" style="width: ${100-b}%"></div></div></div>`;
    }).join('');
}

function renderKPIs() {
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', state.data.length || '---');
    const hate = state.data.reduce((a, b) => a + (b.comentarios_odio_count || 0), 0);
    set('kpi-hate', hate.toLocaleString());
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `<div class="glass-card p-6 flex flex-col gap-4 group"><h4 class="text-[10px] font-black text-white">@${t.username}</h4><button onclick="window.openDetail('${t.username}')" class="w-full py-2 bg-white/5 text-[9px] font-black uppercase rounded-lg border border-white/5">Detalhar</button></div>`).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas.length) return;
    container.innerHTML = state.alertas.slice(0, 4).map(a => `<div class="p-4 bg-white/[0.01] border border-white/5 rounded-2xl"><p class="text-[10px] font-black text-blue-400 mb-2 uppercase">@${a.candidato_id}</p><p class="text-[11px] text-slate-300 italic">"${a.texto_bruto || a.texto}"</p></div>`).join('');
}

function renderGeopolitica() {
    const ufStats = {};
    state.data.forEach(t => { const uf = (t.estado || 'BR').toUpperCase(); if(!ufStats[uf]) ufStats[uf] = { count: 0, hate: 0 }; ufStats[uf].count++; ufStats[uf].hate += (t.comentarios_odio_count || 0); });
    if (document.getElementById('svg-map-br')) renderBrazilMap('svg-map-br', ufStats);
}
