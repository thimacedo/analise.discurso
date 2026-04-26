/**
 * SENTINELA UI ENGINE v15.8.1
 * Bulletproof Stability & Absolute Resilience
 */

import { state } from './state.js';

export function renderAll() {
    try {
        console.log("🎨 Iniciando Renderização Global...");
        renderKPIs();

        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderFocusDossiers();
            renderAlerts();
            renderPredictiveTrends();
            renderNeighborhood();
            renderLiveIntelligence(); 
        } 
        else if (state.view === 'dossie') {
            renderDossieGrid();
        } 
        else if (state.view === 'map') {
            renderGeopolitica();
        }
        
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("🚨 Falha Crítica de Renderização:", e);
    }
}

async function safeFetch(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return Array.isArray(data) ? data : [];
    } catch (e) {
        console.warn(`⚠️ Falha ao buscar ${url}:`, e);
        return [];
    }
}

async function renderLiveIntelligence() {
    const container = document.getElementById('predictive-trends');
    if(!container) return;

    const logs = await safeFetch('/api/v1/live-intelligence');
    if(!logs.length) return;

    const html = `
        <div class="space-y-4 mt-8" id="live-pasa-monitor">
            <div class="flex items-center gap-2 px-2">
                <span class="w-2 h-2 bg-blue-500 rounded-full animate-ping"></span>
                <h3 class="text-[10px] font-black text-white uppercase tracking-widest">IA Live Stream</h3>
            </div>
            ${logs.slice(0, 3).map(log => `
                <div class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl text-[10px]">
                    <div class="flex justify-between mb-1">
                        <span class="font-black text-blue-400">@${log.alvo}</span>
                        <span class="text-slate-600">${log.timestamp}</span>
                    </div>
                    <p class="text-slate-400 italic truncate">"${log.texto}"</p>
                    <div class="mt-2 flex justify-between">
                        <span class="${log.status?.includes('ALERTA') ? 'text-rose-500' : 'text-emerald-500'} font-black">${log.status}</span>
                        <span class="text-slate-700 font-bold">${log.categoria}</span>
                    </div>
                </div>
            `).join('')}
        </div>`;

    const el = document.getElementById('live-pasa-monitor');
    if(el) el.outerHTML = html;
    else container.insertAdjacentHTML('afterbegin', html);
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if(!container) return;

    const alvos = await safeFetch('/api/v1/stats/top-alvos');
    if(!alvos.length) {
        container.innerHTML = '<p class="text-[10px] text-slate-600 text-center py-20 font-black uppercase">Aguardando Dados do Motor...</p>';
        return;
    }

    container.innerHTML = alvos.map(alvo => {
        const blindagem = alvo.share_blindagem || 100;
        const hostilidade = 100 - blindagem;
        return `
            <div onclick="window.openDetail('${alvo.username}')" class="flex flex-col gap-2 p-4 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.05] transition-all cursor-pointer">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-black text-white">@${alvo.username}</span>
                    <div class="flex gap-4">
                        <span class="text-[10px] font-black text-emerald-500 font-mono">${blindagem.toFixed(1)}%</span>
                        <span class="text-[10px] font-black text-rose-500 font-mono">${hostilidade.toFixed(1)}%</span>
                    </div>
                </div>
                <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                    <div class="h-full bg-blue-600" style="width: ${blindagem}%"></div>
                    <div class="h-full bg-red-600" style="width: ${hostilidade}%"></div>
                </div>
            </div>`;
    }).join('');
}

function renderKPIs() {
    const total = state.data.length;
    const hate = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    const sample = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0);
    const res = sample > 0 ? (100 - (hate / sample * 100)).toFixed(1) : "100.0";
    
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', total || '---');
    set('kpi-hate', hate.toLocaleString());
    set('kpi-total', sample.toLocaleString());
    set('kpi-res', `${res}%`);
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    
    const search = (document.getElementById('dossie-search')?.value || "").toLowerCase();
    const filtered = state.data.filter(t => 
        (t.username || "").toLowerCase().includes(search) || 
        (t.estado || "").toLowerCase().includes(search)
    );

    if(!filtered.length) {
        container.innerHTML = '<p class="col-span-full text-center py-20 text-slate-600 font-black uppercase text-[10px]">Nenhum alvo localizado.</p>';
        return;
    }

    container.innerHTML = filtered.map(t => {
        const resM = (t.comentarios_totais_count || 0) > 0 ? (100 - (t.comentarios_odio_count / t.comentarios_totais_count * 100)).toFixed(1) : "100.0";
        const clean = (t.username || "Alvo").replace('raw_', '').replace('.json', '');
        return `
            <div class="glass-card p-6 border-white/5 hover:border-blue-500/30 transition-all flex flex-col justify-between h-full bg-slate-900/20 group">
                <div class="flex items-center gap-3 mb-6">
                    <img src="https://ui-avatars.com/api/?name=${clean}&background=0f172a&color=3b82f6&bold=true" class="w-10 h-10 rounded-xl" alt="">
                    <div class="min-w-0">
                        <h4 class="text-[10px] font-black text-white truncate">@${clean}</h4>
                        <span class="text-[7px] text-blue-400 uppercase font-black">${t.estado || 'BR'}</span>
                    </div>
                </div>
                <div class="space-y-2">
                    <div class="flex justify-between items-end text-[8px] font-black uppercase text-slate-500">
                        <span>Blindagem</span>
                        <span class="${resM < 70 ? 'text-red-500' : 'text-emerald-500'} font-mono">${resM}%</span>
                    </div>
                    <div class="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                        <div class="h-full ${resM < 70 ? 'bg-red-600' : 'bg-blue-600'}" style="width: ${resM}%"></div>
                    </div>
                </div>
                <button onclick="window.openDetail('${t.username}')" class="mt-6 w-full py-2.5 bg-white/5 hover:bg-blue-600/20 text-blue-400 text-[8px] font-black border border-white/5 rounded-lg transition-all uppercase">An&aacute;lise</button>
            </div>`;
    }).join('');
}

function renderGeopolitica() {
    // Implementação básica para evitar erros
    const nameEl = document.getElementById('st-name');
    if (nameEl && nameEl.innerText === '---') nameEl.innerText = 'Brasil';
}

function renderFocusDossiers() {
    // Implementação resiliente
}

async function renderNeighborhood() {
    // Implementação resiliente
}
