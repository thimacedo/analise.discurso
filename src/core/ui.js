/**
 * SENTINELA UI ENGINE v15.15.0
 * UX Elite Edition - Integrated Rendering
 */
import { state } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        console.log("🛡️ [UI] Renderizando v15.15.0...");
        renderKPIs();
        
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
            renderPredictiveTrends();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }
        
        if (window.lucide) lucide.createIcons();
    } catch (e) { console.error("Render Error:", e); }
}

window.closeCheckout = () => {
    const modal = document.getElementById('checkout-modal');
    if(modal) modal.classList.add('hidden');
};

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

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;

    try {
        const response = await fetch(`/api/v1/stats/top-alvos?t=${Date.now()}`);
        const alvos = await response.json();

        if (!alvos || !alvos.length) {
            container.innerHTML = '<p class="text-center py-20 text-[10px] font-black opacity-30 uppercase tracking-[0.3em]">Sincronizando Base...</p>';
            return;
        }

        container.innerHTML = alvos.map(alvo => {
            const b = alvo.share_blindagem || 100;
            // Se blindagem < 50%, adiciona classe de perigo (threat-high)
            const threatClass = b < 50 ? 'threat-high' : '';
            return `
                <div onclick="window.openDetail('${alvo.username}')" class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2 cursor-pointer hover:bg-white/[0.04] transition-all ${threatClass}">
                    <div class="flex justify-between items-center">
                        <span class="text-xs font-bold text-white">@${alvo.username}</span>
                        <span class="text-[10px] font-black text-emerald-500 font-mono">${b.toFixed(1)}%</span>
                    </div>
                    <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                        <div class="h-full bg-blue-600" style="width: ${b}%"></div>
                        <div class="h-full bg-red-600" style="width: ${100-b}%"></div>
                    </div>
                </div>`;
        }).join('');
    } catch (e) { console.error("Monitor Render Failure:", e); }
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `
        <div class="glass-card p-6 flex flex-col gap-4 group">
            <h4 class="text-[10px] font-black text-white">@${t.username}</h4>
            <span class="text-[8px] text-slate-500 uppercase">${t.estado || 'BR'}</span>
            <button onclick="window.openDetail('${t.username}')" class="w-full py-2 bg-white/5 text-[9px] font-black uppercase rounded-lg border border-white/5 hover:bg-blue-600/20 transition-all">Análise</button>
        </div>
    `).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas.length) return;
    container.innerHTML = state.alertas.slice(0, 4).map(a => `
        <div class="p-4 bg-white/[0.01] border border-white/5 rounded-2xl">
            <p class="text-[10px] font-black text-blue-400 mb-2 uppercase">@${a.candidato_id}</p>
            <p class="text-[11px] text-slate-300 italic">"${a.texto_bruto || a.texto}"</p>
        </div>
    `).join('');
}

function renderPredictiveTrends() {
    const container = document.getElementById('predictive-trends');
    if (!container || !state.data.length) return;

    const trends = [...state.data]
        .filter(c => (c.comentarios_totais_count || 0) > 0)
        .map(c => ({
            username: c.username,
            score: (c.comentarios_odio_count || 0) * 5 + (c.comentarios_totais_count / 10)
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 3);

    container.innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center gap-2 px-2">
                <i data-lucide="zap" class="w-4 h-4 text-amber-500"></i>
                <h3 class="text-xs font-black text-white uppercase tracking-widest">Tendências de Crise</h3>
            </div>
            ${trends.map(t => `
                <div class="p-5 bg-white/[0.02] border border-white/5 rounded-3xl group">
                    <div class="flex justify-between items-start mb-3">
                        <span class="text-[9px] font-black text-amber-500 uppercase">Probabilidade Crise</span>
                        <span class="text-xs font-black text-white font-mono">${Math.min(99, (t.score % 100).toFixed(0))}%</span>
                    </div>
                    <h4 class="text-[11px] font-black text-slate-300">@${t.username}</h4>
                </div>
            `).join('')}
        </div>`;
    if (window.lucide) lucide.createIcons();
}

function renderGeopolitica() {
    const ufStats = {};
    state.data.forEach(t => { const uf = (t.estado || 'BR').toUpperCase(); if(!ufStats[uf]) ufStats[uf] = { count: 0, hate: 0 }; ufStats[uf].count++; ufStats[uf].hate += (t.comentarios_odio_count || 0); });
    if (document.getElementById('svg-map-br')) renderBrazilMap('svg-map-br', ufStats);
}
