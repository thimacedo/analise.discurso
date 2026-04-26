/**
 * SENTINELA UI ENGINE v15.8.5
 * PERSISTENT STABILITY EDITION
 */

import { state } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        renderKPIs();
        
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
            renderLiveIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Critical Render Error:", e);
    }
}

async function apiGet(endpoint) {
    try {
        const r = await fetch(`/api/v1/${endpoint}`);
        return r.ok ? await r.json() : [];
    } catch { return []; }
}

/**
 * 🌍 RESTAURAÇÃO: Geopolítica UF
 */
export function renderGeopolitica() {
    const container = document.getElementById('view-map');
    if (!container) return;

    // Agregar estatísticas por UF do estado global
    const ufStats = {};
    state.data.forEach(t => {
        const uf = (t.estado || 'BR').toUpperCase();
        if(!ufStats[uf]) ufStats[uf] = { count: 0, hate: 0 };
        ufStats[uf].count++;
        ufStats[uf].hate += (t.comentarios_odio_count || 0);
    });

    // Chamar componente de Mapa
    if (document.getElementById('svg-map-br')) {
        renderBrazilMap('svg-map-br', ufStats);
    }

    // Configurar card lateral
    window.focusState = (uf) => {
        const info = ufStats[uf] || { count: 0, hate: 0 };
        const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
        set('st-name', uf);
        set('st-targets', info.count);
        set('st-hate', info.hate);
    };
}

/**
 * 📊 RESTAURAÇÃO: Monitor de Impacto v3.0
 */
async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;

    const data = await apiGet('stats/top-alvos');
    if (!data.length) {
        container.innerHTML = '<p class="text-[10px] text-slate-600 text-center py-20 font-black animate-pulse uppercase">Sincronizando Base...</p>';
        return;
    }

    container.innerHTML = data.map(alvo => {
        const b = alvo.share_blindagem || 100;
        return `
            <div onclick="window.openDetail('${alvo.username}')" class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2 cursor-pointer hover:bg-white/[0.05] transition-all">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-black text-white">@${alvo.username}</span>
                    <span class="text-[10px] font-black text-emerald-500 font-mono">${b.toFixed(1)}% Blindagem</span>
                </div>
                <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                    <div class="h-full bg-blue-600" style="width: ${b}%"></div>
                    <div class="h-full bg-red-600" style="width: ${100-b}%"></div>
                </div>
            </div>`;
    }).join('');
}

function renderKPIs() {
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    const hate = state.data.reduce((a, b) => a + (b.comentarios_odio_count || 0), 0);
    set('kpi-monitorados', state.data.length);
    set('kpi-hate', hate.toLocaleString());
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `
        <div class="glass-card p-6 flex flex-col gap-4">
            <h4 class="text-[10px] font-black text-white uppercase">@${t.username}</h4>
            <div class="flex justify-between items-end">
                <span class="text-[7px] text-slate-500 font-black">UF: ${t.estado || 'BR'}</span>
                <span class="text-[10px] text-blue-400 font-black">${t.comentarios_totais_count}</span>
            </div>
            <button onclick="window.openDetail('${t.username}')" class="w-full py-2.5 bg-white/5 text-[8px] font-black uppercase rounded-lg border border-white/5">Detalhar</button>
        </div>
    `).join('');
}

async function renderLiveIntelligence() {
    const container = document.getElementById('predictive-trends');
    if (!container) return;
    const logs = await apiGet('live-intelligence');
    if (!logs.length) return;
    const html = `<div class="space-y-4 mt-8" id="live-stream-box"><h3 class="text-[10px] font-black text-blue-400 uppercase tracking-widest px-2">IA Stream</h3>${logs.slice(0, 3).map(l => `<div class="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-[10px]"><div class="flex justify-between mb-1"><span class="font-black text-white">@${l.alvo}</span><span class="text-slate-600 font-mono">${l.timestamp}</span></div><p class="text-slate-400 italic">"${l.texto}"</p></div>`).join('')}</div>`;
    const el = document.getElementById('live-stream-box');
    if(el) el.outerHTML = html; else container.insertAdjacentHTML('afterbegin', html);
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas.length) return;
    container.innerHTML = state.alertas.slice(0, 4).map(a => `<div class="p-4 bg-white/[0.01] border border-white/5 rounded-2xl"><p class="text-[10px] font-black text-blue-400 mb-2 uppercase">@${a.candidato_id}</p><p class="text-[11px] text-slate-300 italic">"${a.texto_bruto || a.texto}"</p></div>`).join('');
}
