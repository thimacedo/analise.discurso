/**
 * SENTINELA UI ENGINE v15.11.10
 * Total Intelligence & Predictive Recovery
 */
import { state } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        console.log("🛡️ [SENTINELA] Renderizando v15.11.10...");
        renderKPIs();
        
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
            renderPredictiveTrends(); // RESTAURADO
            renderLiveIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }
        
        if (window.lucide) lucide.createIcons();
    } catch (e) { console.error("Critical Render Failure:", e); }
}

async function apiGet(endpoint) {
    try {
        const r = await fetch(`/api/v1/${endpoint}?t=${Date.now()}`);
        return r.ok ? await r.json() : [];
    } catch { return []; }
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

async function renderPredictiveTrends() {
    const container = document.getElementById('predictive-trends');
    if (!container || !state.data.length) return;

    // Lógica Preditiva: Identifica alvos com aceleração de ataques
    const trends = [...state.data]
        .filter(c => (c.comentarios_totais_count || 0) > 0)
        .map(c => ({
            ...c,
            score: (c.comentarios_odio_count || 0) * 5 + (c.comentarios_totais_count / 10)
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 3);

    const html = `
        <div class="space-y-4 mt-6" id="predictive-content">
            <div class="flex items-center gap-2 px-2">
                <i data-lucide="zap" class="w-4 h-4 text-amber-500"></i>
                <h3 class="text-xs font-black text-white uppercase tracking-widest">Tend&ecirc;ncias de Crise</h3>
            </div>
            ${trends.map(t => `
                <div class="p-5 bg-white/[0.02] border border-white/5 rounded-3xl relative overflow-hidden group">
                    <div class="flex justify-between items-start mb-3">
                        <span class="text-[9px] font-black text-amber-500 uppercase">Probabilidade Crise</span>
                        <span class="text-xs font-black text-white font-mono">${Math.min(99, (t.score % 100).toFixed(0))}%</span>
                    </div>
                    <h4 class="text-[11px] font-black text-slate-300">@${t.username}</h4>
                    <div class="mt-4 w-full h-1 bg-white/5 rounded-full overflow-hidden">
                        <div class="h-full bg-amber-500 shadow-[0_0_10px_#f59e0b]" style="width: ${Math.min(100, t.score)}%"></div>
                    </div>
                </div>
            `).join('')}
        </div>`;

    const existing = document.getElementById('predictive-content');
    if(existing) existing.outerHTML = html;
    else container.insertAdjacentHTML('beforeend', html);
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;
    const data = await apiGet('stats/top-alvos');
    if (!data.length) {
        container.innerHTML = '<p class="text-center py-20 text-[10px] font-black opacity-30 uppercase tracking-[0.3em]">Sincronizando Base...</p>';
        return;
    }
    container.innerHTML = data.map(alvo => {
        const b = alvo.share_blindagem || 100;
        return `<div onclick="window.openDetail('${alvo.username}')" class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2 cursor-pointer hover:bg-white/[0.04] transition-all"><div class="flex justify-between items-center"><span class="text-xs font-bold text-white">@${alvo.username}</span><span class="text-[10px] font-black text-emerald-500 font-mono">${b.toFixed(1)}%</span></div><div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex"><div class="h-full bg-blue-600" style="width: ${b}%"></div><div class="h-full bg-red-600" style="width: ${100-b}%"></div></div></div>`;
    }).join('');
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `
        <div class="glass-card p-6 flex flex-col justify-between h-full bg-slate-900/20 group">
            <h4 class="text-[10px] font-black text-white">@${t.username}</h4>
            <span class="text-[7px] text-blue-400 font-black uppercase mb-4">${t.estado || 'BR'}</span>
            <button onclick="window.openDetail('${t.username}')" class="w-full py-2.5 bg-white/5 text-[9px] font-black uppercase rounded-xl border border-white/5 hover:bg-blue-600/20 transition-all">Dossi&ecirc;</button>
        </div>
    `).join('');
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

async function renderLiveIntelligence() {
    const container = document.getElementById('predictive-trends');
    if (!container) return;
    const logs = await apiGet('live-intelligence');
    if (!logs.length) return;
    const html = `<div class="space-y-4 mt-8" id="live-stream-box"><h3 class="text-[10px] font-black text-blue-400 uppercase tracking-widest px-2">IA Stream</h3>${logs.slice(0, 3).map(l => `<div class="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-[10px]"><div class="flex justify-between mb-1"><span class="font-black text-white">@${l.alvo}</span><span class="text-slate-600 font-mono">${l.timestamp}</span></div><p class="text-slate-400 italic">"${l.texto}"</p></div>`).join('')}</div>`;
    const el = document.getElementById('live-stream-box');
    if(el) el.outerHTML = html; else container.insertAdjacentHTML('afterbegin', html);
}
