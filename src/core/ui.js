/**
 * PASA v47.1 - UI Manager: O Construtor Visual
 * Responsabilidade única: Transformar dados do State em HTML.
 * Proteção Jurídica: NENHUMA menção a "forense", "prova" ou "evidência".
 */

const MTAD_COLORS = {
    ODIO_IDENTITARIO: { bg: 'bg-purple-100 text-purple-600', txt: 'Ódio Identitário', q: 'bg-purple-50 border-purple-400 text-purple-800' },
    VIOLENCIA_GENERO: { bg: 'bg-pink-100 text-pink-600', txt: 'Violência de Gênero', q: 'bg-pink-50 border-pink-400 text-pink-800' },
    AMEACA: { bg: 'bg-red-100 text-red-700', txt: 'Ameaça Física/Morte', q: 'bg-red-100 border-red-500 text-red-900' },
    INSULTO_AD_HOMINEM: { bg: 'bg-rose-100 text-rose-600', txt: 'Insulto Ad Hominem', q: 'bg-rose-50 border-rose-400 text-rose-800' },
    ATAQUE_INSTITUCIONAL: { bg: 'bg-cyan-100 text-cyan-700', txt: 'Ataque Institucional', q: 'bg-cyan-50 border-cyan-400 text-cyan-800' },
    RIGOR_CRIMINAL: { bg: 'bg-amber-100 text-amber-700', txt: 'Rigor Criminal', q: 'bg-amber-50 border-amber-400 text-amber-800' }
};

export const UI = {
    renderFeed(comments) {
        const container = document.getElementById('feed-alertas');
        if (!container) return;
        container.innerHTML = comments.map(c => UI.buildThreatCard(c)).join('');
        if (window.lucide) lucide.createIcons();
    },

    buildThreatCard(c) {
        let borderColor = 'bg-slate-300', badgeColor = 'bg-slate-100 text-slate-500', badgeText = 'Pendente', quoteStyle = 'bg-slate-50 border-slate-300 text-slate-700', iconColor = 'text-slate-400';
        
        if (c.is_hate === true && c.categoria_ia) {
            borderColor = 'bg-red-500'; iconColor = 'text-red-500';
            const cat = MTAD_COLORS[c.categoria_ia] || { bg: 'bg-red-100 text-red-600', txt: 'Indício de Risco', q: 'bg-red-50 border-red-400 text-red-800' };
            badgeColor = cat.bg; 
            badgeText = `${cat.txt} ${c.direcao_odio ? '→ ' + c.direcao_odio : ''}`; 
            quoteStyle = cat.q;
        } else if (c.processado_ia === true) {
            borderColor = 'bg-emerald-400'; badgeColor = 'bg-emerald-100 text-emerald-600'; badgeText = 'Seguro'; quoteStyle = 'bg-emerald-50 border-emerald-300 text-emerald-800'; iconColor = 'text-emerald-500';
        }

        const cleanText = (c.texto_limpo || '').replace(/&nbsp;/g, ' ').trim();
        const cleanAuthor = (c.autor_username || 'Anônimo').split('\n')[0];
        const confidence = c.confianca_ia ? (c.confianca_ia * 100).toFixed(1) : 0;
        const confidenceColor = confidence >= 80 ? 'text-green-600' : confidence >= 50 ? 'text-yellow-600' : 'text-red-600';
        
        const ccfBreakdown = c.is_hate ? `
            <div class="flex gap-3 text-[9px] font-mono text-slate-500 mt-1">
                <span title="Densidade Léxica">Den: ${(c.ccf_density * 100).toFixed(0)}%</span>
                <span title="Sincronização">Sync: ${(c.ccf_sync * 100).toFixed(0)}%</span>
                <span title="Performatividade">Perf: ${(c.ccf_performativity * 100).toFixed(0)}%</span>
            </div>
        ` : '';

        return `
            <div class="threat-card bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all overflow-hidden group">
                <div class="flex">
                    <div class="w-1 ${borderColor} flex-shrink-0"></div>
                    <div class="flex-1 p-4">
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 overflow-hidden">
                                    <img src="/assets/sentinela_small.webp" class="w-full h-full object-cover" onerror="this.style.display='none'">
                                </div>
                                <div>
                                    <span class="text-sm font-bold text-slate-800">@${cleanAuthor}</span>
                                    <span class="text-[10px] ml-2 font-bold ${badgeColor} px-2 py-0.5 rounded-full uppercase tracking-wider">${badgeText}</span>
                                </div>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-mono text-slate-400 block">${UI.timeAgo(c.data_coleta)}</span>
                                <span class="text-[9px] font-bold ${confidenceColor} block">Conf: ${confidence}%</span>
                            </div>
                        </div>
                        <div class="${quoteStyle} border-l-2 rounded-r-lg p-3 mb-3">
                            <p class="text-sm italic leading-relaxed">"${cleanText}"</p>
                        </div>
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="flex items-center gap-4">
                                    <span class="flex items-center gap-1 text-[10px] font-bold uppercase ${iconColor}">
                                        <i data-lucide="shield-alert" class="w-3 h-3"></i> ${c.categoria_ia || 'N/A'}
                                    </span>
                                </div>
                                ${ccfBreakdown}
                            </div>
                            ${c.is_hate === true ? `
                            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button onclick="window.auditComment('${c.id}', 'not_hate')" class="text-[9px] bg-emerald-500 hover:bg-emerald-600 text-white px-2 py-1 rounded font-bold">Falso Positivo</button>
                                <button onclick="window.auditComment('${c.id}', 'hate')" class="text-[9px] bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded font-bold">Padrão Ouro</button>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    renderProfilerStream(stream) {
        const container = document.getElementById('profiler-stream-feed');
        if (!container) return;
        container.innerHTML = stream.map(item => {
            const color = item.density > 40 ? 'text-red-600 bg-red-50' : item.density > 10 ? 'text-orange-600 bg-orange-50' : 'text-slate-700 bg-white';
            const barColor = item.density > 40 ? 'bg-red-500' : item.density > 10 ? 'bg-orange-500' : 'bg-emerald-500';
            return `<div class="flex items-center gap-2 p-2 rounded border border-slate-100 ${color}"><div class="flex-1"><p class="text-[10px] font-bold truncate">@${item.user}</p><div class="w-full bg-slate-200 rounded-full h-1 mt-1"><div class="${barColor} h-1 rounded-full" style="width: ${Math.min(item.density, 100)}%"></div></div></div><div class="text-right"><p class="text-xs font-black">${item.density}%</p><p class="text-[8px] text-slate-500">${item.hate}/${item.total}</p></div></div>`;
        }).join('');
    },

    timeAgo(dateString) {
        if (!dateString) return 'agora';
        const diff = Math.floor((new Date() - new Date(dateString)) / 60000);
        if (diff < 1) return 'agora'; if (diff < 60) return `${diff}m`; return `${Math.floor(diff/60)}h`;
    }
};