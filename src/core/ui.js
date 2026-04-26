/**
 * SENTINELA UI ENGINE v15.5.12
 * Zero Noise & High Integrity Edition
 */

import { state } from './state.js';

export function renderAll() {
    renderKPIs();
    renderFocusDossiers();
    renderAlerts();
    renderNativeImpactChart();
    if (window.lucide) lucide.createIcons();
}

/**
 * Limpeza agressiva de nomes de perfis
 */
function cleanName(target) {
    let name = target.username || "Alvo Oculto";
    // Remove caminhos, prefixos e extensões
    name = name.split('\\').pop().split('/').pop();
    name = name.replace('raw_', '').replace('.json', '').replace('@', '');
    return name.toLowerCase().trim();
}

function renderKPIs() {
    const total = state.data.length;
    const hate = state.data.reduce((acc, curr) => acc + (curr.comentarios_odio_count || 0), 0);
    const sample = state.data.reduce((acc, curr) => acc + (curr.comentarios_totais_count || 0), 0);
    const resiliencia = sample > 0 ? (100 - (hate / sample * 100)).toFixed(1) : "100.0";

    const set = (id, val) => {
        const el = document.getElementById(id);
        if(el) el.innerText = val;
    };
    
    set('kpi-monitorados', total);
    set('kpi-hate', hate.toLocaleString());
    set('kpi-total', sample.toLocaleString());
    set('kpi-res', `${resiliencia}%`);
}

function renderNativeImpactChart() {
    const container = document.getElementById('chartMain');
    if(!container || !state.data.length) return;

    const validData = state.data.filter(c => (c.comentarios_totais_count || 0) > 0);
    const top4BR = validData.filter(c => (c.estado || '').toUpperCase() === 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 4);
    const top4UF = validData.filter(c => (c.estado || '').toUpperCase() !== 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 4);

    const combined = [...top4BR, ...top4UF];

    container.innerHTML = combined.map(t => {
        const resM = 100 - (t.comentarios_odio_count / t.comentarios_totais_count * 100);
        const hatePercent = (t.comentarios_odio_count / t.comentarios_totais_count * 100);
        
        return `
            <div onclick="window.openDetail('${t.username}')" class="flex flex-col gap-2 p-3 bg-white/[0.02] border border-white/5 rounded-2xl hover:bg-white/[0.05] transition-all cursor-pointer group">
                <div class="flex justify-between items-center px-1">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-900 text-white group-hover:text-blue-400 transition-colors uppercase tracking-tight">@${cleanName(t)}</span>
                        <span class="px-1.5 py-0.5 bg-slate-800 text-[7px] font-black text-slate-500 rounded uppercase">${t.estado || 'BR'}</span>
                    </div>
                    <div class="text-right">
                        <span class="text-[8px] font-black ${resM < 70 ? 'text-red-500' : 'text-emerald-500'} uppercase font-mono">${resM.toFixed(1)}% Blindagem</span>
                    </div>
                </div>
                <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex shadow-inner">
                    <div class="h-full bg-blue-600" style="width: ${resM}%"></div>
                    <div class="h-full bg-red-600" style="width: ${hatePercent}%"></div>
                </div>
            </div>`;
    }).join('');
}

function renderFocusDossiers() {
    const validData = state.data.filter(i => (i.comentarios_totais_count || 0) > 0);
    const topNac = validData.filter(i => (i.estado || '').toUpperCase() === 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];
    const topReg = validData.filter(i => (i.estado || '').toUpperCase() !== 'BR').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count)[0];

    const renderCard = (target, containerId) => {
        const el = document.getElementById(containerId);
        if(!el || !target) return;
        const resM = (target.comentarios_totais_count || 0) > 0 ? (100 - (target.comentarios_odio_count / target.comentarios_totais_count * 100)).toFixed(1) : "100.0";
        el.innerHTML = `
            <div onclick="window.openDetail('${target.username}')" class="cursor-pointer group h-full flex flex-col justify-between">
                <div class="flex items-center gap-4">
                    <div class="relative">
                        <img src="https://unavatar.io/instagram/${cleanName(target)}" class="w-12 h-12 rounded-xl border-2 border-white/10 group-hover:border-blue-500/50 transition-all shadow-xl" onerror="this.src='https://ui-avatars.com/api/?name=${target.username}'">
                        <span class="absolute -bottom-1 -right-1 px-1.5 py-0.5 bg-blue-600 text-[7px] font-black text-white rounded-md border border-[#020617] uppercase">${target.estado || 'BR'}</span>
                    </div>
                    <div class="text-left min-w-0">
                        <h4 class="text-[10px] font-900 text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors truncate">@${cleanName(target)}</h4>
                        <p class="text-[8px] text-slate-500 font-bold uppercase truncate">${target.cargo || 'Monitorado'}</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3 mt-4">
                    <div class="p-3 bg-white/[0.03] border border-white/5 rounded-xl text-left">
                        <span class="text-[7px] text-slate-500 font-black uppercase block mb-1">Impacto</span>
                        <div class="text-[10px] font-black text-white font-mono">${(target.comentarios_totais_count || 0).toLocaleString()}</div>
                    </div>
                    <div class="p-3 bg-white/[0.03] border border-white/5 rounded-xl text-left">
                        <span class="text-[7px] text-slate-500 font-black uppercase block mb-1">Resiliência</span>
                        <div class="text-[10px] font-black ${resM < 70 ? 'text-red-500' : 'text-emerald-500'} font-mono">${resM}%</div>
                    </div>
                </div>
            </div>`;
    };
    renderCard(topNac, 'dossie-top-nac');
    renderCard(topReg, 'dossie-top-reg');
}

/**
 * FEED DE ALERTAS - RIGOR SEMÂNTICO MÁXIMO
 */
function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas) return;
    
    // Blacklist para evitar falsos positivos ridículos (aplausos e elogios)
    const blacklist = ["👏", "top", "parabéns", "show", "muito bem", "parabens", "bravo", "lula la", "sou lula"];

    const eliteAlerts = state.alertas.filter(a => {
        const text = (a.texto_bruto || a.texto || "").toLowerCase();
        
        // 1. Deve ser marcado como ódio no banco
        if (a.is_hate !== true) return false;
        
        // 2. Não pode ser apenas emoji de aplauso ou frase da blacklist se for curto
        if (text.length < 20 && blacklist.some(word => text.includes(word))) return false;

        return true;
    }).slice(0, 8); // Apenas os 8 últimos REAIS

    if(eliteAlerts.length === 0) {
        container.innerHTML = '<div class="col-span-full py-10 text-center text-slate-600 font-black uppercase text-[9px] tracking-widest italic border border-dashed border-white/5 rounded-3xl">Monitoramento Estável: Nenhuma ameaça crítica nas últimas horas.</div>';
        return;
    }

    container.innerHTML = eliteAlerts.map(a => {
        const categoria = a.categoria_ia ? a.categoria_ia.replace('[GROQ-LLAMA-70B] ', '') : 'CRÍTICA';
        return `
        <div class="glass-card p-6 bg-red-600/[0.01] border-red-500/10 hover:border-red-500/30 transition-all group relative">
            <div class="flex items-center gap-3 mb-4">
                <img src="https://unavatar.io/instagram/${cleanName({username: a.candidato_id})}" class="w-8 h-8 rounded-lg border border-red-500/20" onerror="this.src='https://ui-avatars.com/api/?name=${a.candidato_id}'">
                <div>
                    <span class="text-[10px] font-black text-white block">@${cleanName({username: a.candidato_id})}</span>
                    <span class="text-[7px] text-slate-500 font-bold uppercase">${new Date(a.data_coleta).toLocaleString('pt-BR')}</span>
                </div>
            </div>
            <p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-red-500/20 pl-3">"${a.texto_bruto || a.texto}"</p>
            <div class="mt-4 flex justify-between items-center">
                <span class="text-[7px] font-black bg-red-500/10 text-red-400 px-2 py-0.5 rounded border border-red-500/20 uppercase tracking-widest">${categoria}</span>
                <span class="text-[8px] font-black text-slate-700 tracking-tighter">PROTOCOLO PASA</span>
            </div>
        </div>`;
    }).join('');
}
