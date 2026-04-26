export function renderDossieGrid(containerId, data) {
    const grid = document.getElementById(containerId);
    if(!grid) return;
    
    grid.innerHTML = data.map(t => {
        const total = t.comentarios_totais_count || 0;
        const hate = t.comentarios_odio_count || 0;
        const perc = total > 0 ? (100 - (hate/total*100)) : 100;
        
        return `
        <div onclick="window.openDetail('${t.username}')" class="glass-card p-6 bg-white/[0.02] border-white/5 hover:border-blue-500/50 hover:bg-white/[0.05] transition-all cursor-pointer group">
            <div class="flex justify-between items-start mb-6">
                <div class="relative">
                    <img src="https://unavatar.io/instagram/${t.username}" class="profile-thumb border-2 border-transparent group-hover:border-blue-500/50 transition-all" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                    <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-[#020617] rounded-full"></div>
                </div>
                <span class="text-[8px] px-2 py-1 rounded bg-blue-500/10 text-blue-400 font-black uppercase border border-blue-500/20">${t.estado || 'BR'}</span>
            </div>
            <h4 class="text-sm font-black mb-1 truncate text-white group-hover:text-blue-400 transition-colors">@${t.username}</h4>
            <p class="text-[9px] text-slate-500 uppercase font-bold mb-4 tracking-widest">${t.cargo || 'Monitorado'}</p>
            
            <div class="space-y-3">
                <div class="spectrum-bar"><div class="spectrum-segment seg-neutro" style="width: ${perc}%"></div><div class="spectrum-segment seg-ataque" style="width: ${100-perc}%"></div></div>
                <div class="flex justify-between text-[8px] font-bold uppercase tracking-tighter">
                    <span class="text-slate-500">Resiliência Digital</span>
                    <span class="text-blue-400 font-mono">${perc.toFixed(1)}%</span>
                </div>
            </div>

            <div class="mt-6 pt-4 border-t border-white/5 flex justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-[9px] font-black text-blue-500 uppercase tracking-widest flex items-center gap-1">Ver Diagnóstico Completo <i data-lucide="chevron-right" class="w-3 h-3"></i></span>
            </div>
        </div>`;
    }).join('');
    
    if(window.lucide) lucide.createIcons();
}
