/**
 * SENTINELA UI ENGINE v15.6.1
 * Independent Forensic Edition - High Fidelity UI
 */

import { state } from './state.js';

export function renderAll() {
    try {
        renderKPIs();
        renderFocusDossiers();
        renderAlerts();
        renderMonitorImpacto(); // Novo: Design v3.0 (Portado do React)
        renderPredictiveTrends();
        renderDossieGrid(); // Dossiê com Agrupamentos
        renderGeopolitica();
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Render Error:", e);
    }
}

function cleanName(target) {
    let name = (target.username || target.candidato_id || "Alvo").toString();
    name = name.split('\\').pop().split('/').pop();
    name = name.replace('raw_', '').replace('.json', '').replace('@', '');
    return name.toLowerCase().trim();
}

/**
 * MONITOR DE IMPACTO & HOSTILIDADE v3.0 (Nativo)
 * Portado do componente React fornecido
 */
function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if(!container) return;

    // Simular o fetch do componente React usando o estado global sincronizado
    // Ou buscar diretamente da nova rota da API se preferir
    const topAlvos = [...state.data]
        .filter(c => (c.comentarios_totais_count || 0) > 0)
        .sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)
        .slice(0, 10);

    container.innerHTML = topAlvos.map(alvo => {
        const total = alvo.comentarios_totais_count || 0;
        const odio = alvo.comentarios_odio_count || 0;
        const blindagem = total > 0 ? (100 - (odio / total * 100)) : 100;
        const hostilidade = 100 - blindagem;

        return `
            <div onclick="window.openDetail('${alvo.username}')" 
                 class="flex flex-col gap-3 p-4 bg-slate-800/40 border border-slate-700/50 rounded-xl hover:bg-slate-800 hover:border-slate-600 transition-all duration-300 cursor-pointer group">
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-3">
                        <span class="text-sm font-bold text-slate-200 group-hover:text-blue-400 transition-colors tracking-tight">
                            @${cleanName(alvo)}
                        </span>
                        <span class="px-2 py-0.5 bg-slate-700 text-[10px] font-bold text-slate-300 rounded uppercase tracking-wider">
                            ${alvo.estado || 'BR'}
                        </span>
                    </div>
                    <div class="flex items-center gap-4 text-right">
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-medium text-slate-500 uppercase tracking-wider mb-0.5">Proteção</span>
                            <span class="text-xs font-bold text-emerald-400 font-mono">${blindagem.toFixed(1)}%</span>
                        </div>
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-medium text-slate-500 uppercase tracking-wider mb-0.5">Risco</span>
                            <span class="text-xs font-bold text-rose-500 font-mono">${hostilidade.toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                <div class="w-full h-2 bg-slate-900 rounded-full overflow-hidden flex">
                    <div class="h-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-700 ease-out" style="width: ${blindagem}%"></div>
                    <div class="h-full bg-gradient-to-r from-rose-500 to-red-600 transition-all duration-700 ease-out" style="width: ${hostilidade}%"></div>
                </div>
            </div>`;
    }).join('');
}

/**
 * DOSSIÊ DE ALVOS v2.2 - AGRUPAMENTOS DINÂMICOS
 */
function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    
    const search = document.getElementById('dossie-search')?.value.toLowerCase() || "";
    let filtered = state.data.filter(t => 
        cleanName(t).includes(search) || 
        (t.nome_completo && t.nome_completo.toLowerCase().includes(search)) ||
        (t.estado && t.estado.toLowerCase().includes(search))
    );

    // Agrupamento Visual por "Relevância de Cenário"
    const federais = filtered.filter(t => (t.estado || '').toUpperCase() === 'BR');
    const regionais = filtered.filter(t => (t.estado || '').toUpperCase() !== 'BR');

    const renderBatch = (list, title) => {
        if(!list.length) return '';
        return `
            <div class="col-span-full mt-8 mb-4 flex items-center gap-4">
                <h3 class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] whitespace-nowrap">${title}</h3>
                <div class="h-px bg-white/5 w-full"></div>
            </div>
            ${list.map(t => {
                const resM = (t.comentarios_totais_count || 0) > 0 ? (100 - (t.comentarios_odio_count / t.comentarios_totais_count * 100)).toFixed(1) : "100.0";
                return `
                <div class="glass-card p-6 border-white/5 hover:border-blue-500/30 transition-all group flex flex-col justify-between h-full bg-slate-900/20">
                    <div class="flex items-center gap-3 mb-6">
                        <img src="https://unavatar.io/instagram/${cleanName(t)}" class="w-12 h-12 rounded-xl border border-white/10 group-hover:scale-105 transition-transform" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                        <div class="min-w-0">
                            <h4 class="text-[10px] font-black text-white truncate">@${cleanName(t)}</h4>
                            <span class="text-[7px] text-blue-400 uppercase font-black tracking-widest">${t.estado || 'BR'}</span>
                        </div>
                    </div>
                    <div class="space-y-3">
                        <div class="flex justify-between items-end">
                            <span class="text-[8px] text-slate-500 font-black uppercase">Resiliência</span>
                            <span class="text-[10px] font-black ${resM < 70 ? 'text-red-500' : 'text-emerald-500'} font-mono">${resM}%</span>
                        </div>
                        <div class="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                            <div class="h-full ${resM < 70 ? 'bg-red-600 shadow-[0_0_8px_#ef4444]' : 'bg-blue-600'}" style="width: ${resM}%"></div>
                        </div>
                    </div>
                    <button onclick="window.openDetail('${t.username}')" class="mt-6 w-full py-2.5 bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white text-[8px] font-black border border-blue-600/20 rounded-xl transition-all uppercase tracking-widest">Dossiê Detalhado</button>
                </div>`;
            }).join('')}`;
    };

    container.innerHTML = renderBatch(federais, 'Cenário Nacional') + renderBatch(regionais, 'Cenário Regional (UFs)');
}

// Funções de apoio
function renderKPIs() {
    const total = state.data.length;
    const hate = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    const sample = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0);
    const res = sample > 0 ? (100 - (hate / sample * 100)).toFixed(1) : "100.0";
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', total); set('kpi-hate', hate.toLocaleString()); set('kpi-total', sample.toLocaleString()); set('kpi-res', `${res}%`);
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

function renderFocusDossiers() {
    const valid = state.data.filter(i => (i.comentarios_totais_count || 0) > 0);
    const topNac = valid.filter(i => (i.estado || '').toUpperCase() === 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];
    const topReg = valid.filter(i => (i.estado || '').toUpperCase() !== 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];
    const render = (target, id) => {
        const el = document.getElementById(id); if(!el || !target) return;
        const res = (target.comentarios_totais_count || 0) > 0 ? (100 - (target.comentarios_odio_count / target.comentarios_totais_count * 100)).toFixed(1) : "100.0";
        el.innerHTML = `<div onclick="window.openDetail('${target.username}')" class="cursor-pointer group"><div class="flex items-center gap-4 mb-6"><div class="relative"><img src="https://unavatar.io/instagram/${cleanName(target)}" class="w-12 h-12 rounded-xl border border-white/10 group-hover:border-blue-500/50 transition-all"><span class="absolute -bottom-1 -right-1 px-1.5 py-0.5 bg-blue-600 text-[7px] font-black text-white rounded uppercase">${target.estado || 'BR'}</span></div><div class="text-left min-w-0"><h4 class="text-[10px] font-900 text-white group-hover:text-blue-400 truncate">@${cleanName(target)}</h4><p class="text-[8px] text-slate-500 font-bold uppercase truncate">${target.cargo || 'Monitorado'}</p></div></div><div class="grid grid-cols-2 gap-3"><div class="p-3 bg-white/5 border border-white/5 rounded-xl text-left"><span class="text-[7px] text-slate-500 uppercase block mb-1">Impacto</span><div class="text-xs font-black text-white">${(target.comentarios_totais_count || 0).toLocaleString()}</div></div><div class="p-3 bg-white/5 border border-white/5 rounded-xl text-left"><span class="text-[7px] text-slate-500 uppercase block mb-1">Resiliência</span><div class="text-xs font-black ${res < 70 ? 'text-red-500' : 'text-emerald-500'}">${res}%</div></div></div></div>`;
    };
    render(topNac, 'dossie-top-nac'); render(topReg, 'dossie-top-reg');
}

function renderPredictiveTrends() {
    const container = document.getElementById('predictive-trends'); if(!container || !state.data.length) return;
    const trends = state.data.filter(c => (c.comentarios_totais_count || 0) > 0).map(c => ({ ...c, calor: (c.comentarios_odio_count || 0) * 2 + (c.comentarios_totais_count / 10) })).sort((a,b) => b.calor - a.calor).slice(0, 3);
    container.innerHTML = trends.map(t => {
        const risk = t.comentarios_odio_count > 10 || (t.comentarios_odio_count / t.comentarios_totais_count > 0.2);
        return `<div class="glass-card p-5 border-white/5 group"><div class="flex items-center gap-3 mb-3"><div class="w-2 h-2 rounded-full ${risk ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-blue-500 animate-pulse'}"></div><span class="text-[9px] font-black text-slate-400 uppercase">${risk ? 'Risco de Crise' : 'Tendência'}</span></div><h4 class="text-xs font-black text-white mb-2 truncate">@${cleanName(t)}</h4><div class="mt-4 pt-4 border-t border-white/5 flex justify-between items-center"><span class="text-[8px] font-bold text-slate-600 uppercase">Probabilidade</span><span class="text-[10px] font-black ${risk ? 'text-red-400' : 'text-blue-400'} font-mono">${(t.calor % 100).toFixed(0)}%</span></div></div>`;
    }).join('');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas'); if(!container || !state.alertas) return;
    const blacklist = ["👏", "top", "parabéns", "show", "muito bem", "parabens", "bravo"];
    const elite = state.alertas.filter(a => a.is_hate === true && !blacklist.some(word => (a.texto_bruto || "").toLowerCase().includes(word))).slice(0, 8);
    if(elite.length === 0) { container.innerHTML = '<p class="col-span-full text-center py-10 text-slate-600 font-black uppercase text-[9px] italic">Monitoramento Estável.</p>'; return; }
    container.innerHTML = elite.map(a => `<div class="glass-card p-6 bg-red-600/[0.01] border-red-500/10 hover:border-red-500/30 transition-all group relative"><div class="flex items-center gap-3 mb-4"><img src="https://unavatar.io/instagram/${cleanName({candidato_id: a.candidato_id})}" class="w-8 h-8 rounded-lg border border-red-500/20" onerror="this.src='https://ui-avatars.com/api/?name=${a.candidato_id}'"><div><span class="text-[10px] font-black text-white block">@${cleanName({candidato_id: a.candidato_id})}</span><span class="text-[7px] text-slate-500 font-bold uppercase">${new Date(a.data_coleta).toLocaleString('pt-BR')}</span></div></div><p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-red-500/20 pl-3">"${a.texto_bruto || a.texto}"</p><div class="mt-4 flex justify-between items-center"><span class="text-[7px] font-black bg-red-500/10 text-red-400 px-2 py-0.5 rounded border border-red-500/20 uppercase tracking-widest">${(a.categoria_ia || "ALERTA").replace("[GROQ-LLAMA-70B] ", "")}</span><span class="text-[8px] font-black text-slate-700 tracking-tighter uppercase">PASA v15.6</span></div></div>`).join('');
}
