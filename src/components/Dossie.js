export function renderDossieGrid(containerId, data) {
    const grid = document.getElementById(containerId);
    grid.innerHTML = data.map(t => {
        const total = t.comentarios_totais_count || 0;
        const hate = t.comentarios_odio_count || 0;
        const perc = total > 0 ? (100 - (hate/total*100)) : 100;
        
        return `
        <div class="glass-card p-6 bg-white/[0.02] border-white/5 hover:border-blue-500/30 transition-all">
            <div class="flex justify-between items-start mb-6">
                <img src="https://unavatar.io/instagram/${t.username}" class="profile-thumb" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                <span class="text-[8px] px-2 py-1 rounded bg-blue-500/10 text-blue-400 font-black uppercase">${t.estado || 'BR'}</span>
            </div>
            <h4 class="text-sm font-black mb-1 truncate">@${t.username}</h4>
            <p class="text-[9px] text-slate-500 uppercase font-bold mb-4">${t.cargo || 'Monitorado'}</p>
            <div class="spectrum-bar mb-2"><div class="spectrum-segment seg-neutro" style="width: ${perc}%"></div><div class="spectrum-segment seg-ataque" style="width: ${100-perc}%"></div></div>
            <div class="flex justify-between text-[8px] font-bold uppercase"><span class="text-slate-500">Resiliência</span><span class="text-blue-400">${perc.toFixed(1)}%</span></div>
        </div>`;
    }).join('');
}
