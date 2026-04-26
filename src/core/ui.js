/**
 * SENTINELA UI ENGINE v15.6.9
 * Neighborhood Attack Detection & Network Analysis
 */

import { state } from './state.js';

export function renderAll() {
    try {
        renderKPIs();
        if (state.view === 'monitor') {
            renderFocusDossiers();
            renderAlerts();
            renderMonitorImpacto();
            renderPredictiveTrends();
            renderNeighborhood(); // Novo: Detecção de Redes
        } 
        else if (state.view === 'dossie') {
            renderDossieGrid();
        } 
        else if (state.view === 'map') {
            renderGeopolitica();
        }
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Render Error:", e);
    }
}

/**
 * RENDERIZA O MAPA DE VIZINHANÇA (Atores Transversais)
 */
async function renderNeighborhood() {
    const container = document.getElementById('predictive-trends'); // Reutilizamos a área lateral para inteligência
    if(!container) return;

    try {
        const response = await fetch('/api/v1/stats/neighborhood');
        const networks = await response.json();

        if(!networks || networks.length === 0) {
            // Se não houver redes detectadas, mantém a tendência preditiva original
            return;
        }

        const neighborhoodHtml = `
            <div class="space-y-6 mt-10">
                <div class="flex items-center gap-3 px-2">
                    <i data-lucide="share-2" class="w-4 h-4 text-amber-500"></i>
                    <h3 class="text-xs font-black text-white uppercase tracking-widest">Atores Transversais</h3>
                </div>
                ${networks.map(n => `
                    <div class="glass-card p-5 border-amber-500/10 bg-amber-500/[0.02] group relative overflow-hidden">
                        <div class="flex justify-between items-start mb-3">
                            <span class="text-[9px] font-black text-amber-500 uppercase tracking-widest">Rede Detectada</span>
                            <span class="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-[8px] font-bold rounded-full">${n.intensidade} Alvos</span>
                        </div>
                        <h4 class="text-[10px] font-black text-white mb-3">@${n.autor}</h4>
                        <div class="flex flex-wrap gap-1">
                            ${n.alvos.map(alvo => `<span class="text-[7px] text-slate-500 font-bold">@${alvo}</span>`).join('<span class="text-[7px] text-slate-700">&bull;</span>')}
                        </div>
                        <div class="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <i data-lucide="zap" class="w-16 h-16 text-amber-500"></i>
                        </div>
                    </div>
                `).join('')}
            </div>`;
            
        // Inserir após as tendências preditivas
        const trendsArea = document.getElementById('predictive-trends');
        if(trendsArea && !document.getElementById('neighborhood-block')) {
            const div = document.createElement('div');
            div.id = 'neighborhood-block';
            div.innerHTML = neighborhoodHtml;
            trendsArea.appendChild(div);
            if(window.lucide) lucide.createIcons();
        }
    } catch (e) {
        console.error("Neighborhood error:", e);
    }
}

// Funções base e auxiliares
function cleanName(target) {
    let name = (target.username || target.candidato_id || "Alvo").toString();
    name = name.split('\\').pop().split('/').pop().replace('raw_', '').replace('.json', '').replace('@', '');
    return name.toLowerCase().trim();
}

function imgHtml(username, className = "w-10 h-10 rounded-xl") {
    const clean = username.replace('@', '').trim();
    const primary = `https://cdn.statically.io/img/unavatar.io/instagram/${clean}`;
    const fallback = `https://ui-avatars.com/api/?name=${clean}&background=0f172a&color=3b82f6&bold=true`;
    return `<img src="${primary}" class="${className} border border-white/10 shadow-lg bg-slate-900" loading="lazy" onerror="this.onerror=null; this.src='${fallback}';">`;
}

function renderSparkline(data) {
    if(!data || !data.length) return '';
    const max = Math.max(...data, 1);
    const width = 100, height = 30;
    const points = data.map((v, i) => `${(i * (width / (data.length - 1)))} , ${height - (v / max * height)}`).join(' ');
    return `<svg viewBox="0 0 ${width} ${height}" class="w-full h-8 overflow-visible"><polyline fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" points="${points}" /><circle cx="${width}" cy="${height - (data[data.length-1] / max * height)}" r="2" fill="#ef4444" /></svg>`;
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid'); if(!container) return;
    const search = document.getElementById('dossie-search')?.value.toLowerCase() || "";
    let filtered = state.data.filter(t => cleanName(t).includes(search) || (t.nome_completo && t.nome_completo.toLowerCase().includes(search)) || (t.estado && t.estado.toLowerCase().includes(search)));
    const federais = filtered.filter(t => (t.estado || '').toUpperCase() === 'BR');
    const regionais = filtered.filter(t => (t.estado || '').toUpperCase() !== 'BR');
    const renderBatch = (list, title) => {
        if(!list.length) return '';
        return `<div class="col-span-full mt-10 mb-6 flex items-center gap-4"><h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">${title}</h3><div class="h-px bg-white/5 flex-1"></div></div>${list.map(t => {
            const resM = (t.comentarios_totais_count || 0) > 0 ? (100 - (t.comentarios_odio_count / t.comentarios_totais_count * 100)).toFixed(1) : "100.0";
            return `<div class="glass-card p-6 border-white/5 hover:border-blue-500/30 transition-all flex flex-col justify-between h-full bg-slate-900/20 group"><div class="flex items-center gap-4 mb-6">${imgHtml(cleanName(t), "w-12 h-12 rounded-xl")}<div class="min-w-0"><h4 class="text-[11px] font-black text-white truncate">@${cleanName(t)}</h4><span class="text-[7px] text-blue-400 uppercase font-black tracking-widest">${t.estado || 'BR'}</span></div></div><div class="mb-6 px-1">${renderSparkline(t.timeline || [])}</div><div class="mb-8"><div class="flex flex-wrap gap-1.5">${(t.idioleto || []).map(word => `<span class="px-2 py-0.5 bg-white/5 text-slate-500 text-[8px] font-bold rounded-md border border-white/5 uppercase">${word}</span>`).join('')}</div></div><div class="space-y-3"><div class="flex justify-between items-end"><span class="text-[8px] text-slate-500 font-black uppercase tracking-widest">Resili&ecirc;ncia</span><span class="text-[10px] font-black ${resM < 70 ? 'text-red-500' : 'text-emerald-500'} font-mono">${resM}%</span></div><div class="w-full h-1 bg-white/5 rounded-full overflow-hidden"><div class="h-full ${resM < 70 ? 'bg-red-600' : 'bg-blue-600'}" style="width: ${resM}%"></div></div></div><button onclick="window.openDetail('${t.username}')" class="mt-8 w-full py-3 bg-white/5 hover:bg-blue-600/20 text-blue-400 text-[9px] font-black border border-white/5 rounded-xl transition-all uppercase">Dossi&ecirc; Completo</button></div>`;
        }).join('')}`;
    };
    container.innerHTML = renderBatch(federais, 'Cen&aacute;rio Nacional') + renderBatch(regionais, 'Cen&aacute;rio Regional');
}

function renderMonitorImpacto() {
    const container = document.getElementById('chartMain'); if(!container) return;
    const topAlvos = [...state.data].filter(c => (c.comentarios_totais_count || 0) > 0).sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 10);
    container.innerHTML = topAlvos.map(alvo => {
        const total = alvo.comentarios_totais_count || 0;
        const blindagem = total > 0 ? (100 - (alvo.comentarios_odio_count / total * 100)) : 100;
        return `<div onclick="window.openDetail('${alvo.username}')" class="flex flex-col gap-3 p-4 bg-slate-800/40 border border-slate-700/50 rounded-xl hover:bg-slate-800 transition-all cursor-pointer group"><div class="flex justify-between items-center"><div class="flex items-center gap-3">${imgHtml(cleanName(alvo), "w-7 h-7 rounded-md")}<span class="text-sm font-bold text-slate-200 group-hover:text-blue-400">@${cleanName(alvo)}</span></div><div class="text-right"><span class="text-[10px] font-black ${blindagem < 70 ? 'text-rose-500' : 'text-emerald-400'} font-mono">${blindagem.toFixed(1)}%</span></div></div><div class="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden flex"><div class="h-full bg-blue-600" style="width: ${blindagem}%"></div><div class="h-full bg-red-600" style="width: ${100-blindagem}%"></div></div></div>`;
    }).join('');
}

function renderKPIs() {
    const total = state.data.length;
    const hate = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    const sample = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0);
    const res = sample > 0 ? (100 - (hate / sample * 100)).toFixed(1) : "100.0";
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', total); set('kpi-hate', hate.toLocaleString()); set('kpi-total', sample.toLocaleString()); set('kpi-res', `${res}%`);
}

function renderFocusDossiers() {
    const valid = state.data.filter(i => (i.comentarios_totais_count || 0) > 0);
    const topNac = valid.filter(i => (i.estado || '').toUpperCase() === 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];
    const topReg = valid.filter(i => (i.estado || '').toUpperCase() !== 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];
    const render = (target, id) => {
        const el = document.getElementById(id); if(!el || !target) return;
        const res = (target.comentarios_totais_count || 0) > 0 ? (100 - (target.comentarios_odio_count / target.comentarios_totais_count * 100)).toFixed(1) : "100.0";
        el.innerHTML = `<div onclick="window.openDetail('${target.username}')" class="cursor-pointer group"><div class="flex items-center gap-4 mb-6"><div class="relative">${imgHtml(cleanName(target), "w-16 h-16 rounded-2xl border-2 border-white/10 shadow-2xl")}<span class="absolute -bottom-1 -right-1 px-1.5 py-0.5 bg-blue-600 text-[7px] font-black text-white rounded uppercase shadow-lg border border-[#020617]">${target.estado || 'BR'}</span></div><div class="text-left min-w-0"><h4 class="text-[11px] font-900 text-white group-hover:text-blue-400 truncate">@${cleanName(target)}</h4><p class="text-[8px] text-slate-500 font-bold uppercase truncate">${target.cargo || 'Monitorado'}</p></div></div><div class="grid grid-cols-2 gap-3"><div class="p-3 bg-white/5 border border-white/5 rounded-xl text-left"><span class="text-[7px] text-slate-500 uppercase block mb-1">Impacto</span><div class="text-xs font-black text-white">${(target.comentarios_totais_count || 0).toLocaleString()}</div></div><div class="p-3 bg-white/5 border border-white/5 rounded-xl text-left"><span class="text-[7px] text-slate-500 uppercase block mb-1">Resili&ecirc;ncia</span><div class="text-xs font-black ${res < 70 ? 'text-red-500' : 'text-emerald-500'}">${res}%</div></div></div></div>`;
    };
    render(topNac, 'dossie-top-nac'); render(topReg, 'dossie-top-reg');
}

function renderGeopolitica() {
    const states = {};
    state.data.forEach(t => {
        const uf = (t.estado || 'BR').toUpperCase();
        if(!states[uf]) states[uf] = { targets: 0, alerts: 0 };
        states[uf].targets += 1; states[uf].alerts += (t.comentarios_odio_count || 0);
    });
    window.updateMapCard = (uf) => {
        const info = states[uf.toUpperCase()] || { targets: 0, alerts: 0 };
        const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
        set('st-name', uf.toUpperCase()); set('st-targets', info.targets); set('st-hate', info.alerts);
    };
}

function renderPredictiveTrends() {
    const container = document.getElementById('predictive-trends'); if(!container || !state.data.length) return;
    const trends = state.data.filter(c => (c.comentarios_totais_count || 0) > 0).map(c => ({ ...c, calor: (c.comentarios_odio_count || 0) * 2 + (c.comentarios_totais_count / 10) })).sort((a,b) => b.calor - a.calor).slice(0, 3);
    container.innerHTML = trends.map(t => {
        const risk = t.comentarios_odio_count > 10 || (t.comentarios_odio_count / t.comentarios_totais_count > 0.2);
        return `<div class="glass-card p-5 border-white/5 group"><div class="flex items-center gap-3 mb-3"><div class="w-2 h-2 rounded-full ${risk ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-blue-500 animate-pulse'}"></div><span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">${risk ? 'Crise' : 'Est&aacute;vel'}</span></div><h4 class="text-xs font-black text-white truncate">@${cleanName(t)}</h4><div class="mt-4 pt-4 border-t border-white/5 flex justify-between items-center"><span class="text-[8px] font-bold text-slate-600 uppercase">Probabilidade</span><span class="text-[10px] font-black ${risk ? 'text-red-400' : 'text-blue-400'} font-mono">${(t.calor % 100).toFixed(0)}%</span></div></div>`;
    }).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas'); if(!container || !state.alertas) return;
    const blacklist = ["👏", "top", "parabéns", "show", "muito bem", "parabens", "bravo"];
    const elite = state.alertas.filter(a => a.is_hate === true && !blacklist.some(word => (a.texto_bruto || "").toLowerCase().includes(word))).slice(0, 8);
    if(elite.length === 0) { container.innerHTML = '<p class="col-span-full text-center py-10 text-slate-600 font-black uppercase text-[9px] italic">Monitoramento Est&aacute;vel.</p>'; return; }
    container.innerHTML = elite.map(a => `<div class="glass-card p-6 bg-red-600/[0.01] border-red-500/10 hover:border-red-500/30 transition-all group relative"><div class="flex items-center gap-3 mb-4">${imgHtml(cleanName({username: a.candidato_id}), "w-8 h-8 rounded-lg")}<div><span class="text-[10px] font-black text-white block">@${cleanName({username: a.candidato_id})}</span><span class="text-[7px] text-slate-500 font-bold uppercase">${new Date(a.data_coleta).toLocaleString('pt-BR')}</span></div></div><p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-red-500/20 pl-3">"${a.texto_bruto || a.texto}"</p></div>`).join('');
}
