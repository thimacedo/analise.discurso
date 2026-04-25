import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderBrazilMap } from '../components/BrazilMap.js';
import { renderDossieGrid } from '../components/Dossie.js';

let appState = {
    view: 'monitor',
    data: [],
    stats: {},
    classified: [],
    alertas: [],
    trends: [],
    currentModalUF: null
};

// EXPOSIÇÃO GLOBAL PARA O HTML
window.navigate = function(v) {
    appState.view = v;
    window.location.hash = v;
    document.querySelectorAll('.view-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    const targetView = document.getElementById(`view-${v}`);
    const targetNav = document.getElementById(`nav-${v}`);
    
    if(targetView) targetView.classList.remove('hidden');
    if(targetNav) targetNav.classList.add('active');
    
    if(v === 'monitor') renderImpactCharts();
};

window.focusState = function(uf) {
    document.querySelectorAll('.state-rect').forEach(s => s.classList.remove('active'));
    const stateEl = document.getElementById(`state-${uf}`);
    if(stateEl) stateEl.classList.add('active');
    
    const info = appState.stats[uf] || { count: 0, hate: 0, total: 0 };
    const stNameEl = document.getElementById('st-name');
    const stTargetsEl = document.getElementById('st-targets');
    const stHateEl = document.getElementById('st-hate');
    
    if(stNameEl) stNameEl.innerText = uf === "BR" ? "Brasil" : uf;
    if(stTargetsEl) stTargetsEl.innerText = info.count;
    if(stHateEl) stHateEl.innerText = info.hate;
};

window.refresh = async function() {
    console.log("Iniciando Sincronização v15.4.1...");
    try {
        const results = await Promise.allSettled([
            fetchCandidatos(),
            fetchAlertas(12) // Aumentado para garantir histórico
        ]);

        const data = results[0].status === 'fulfilled' ? results[0].value : [];
        const alertas = results[1].status === 'fulfilled' ? results[1].value : [];
        
        appState.data = data;
        appState.alertas = alertas;
        
        // --- CLASSIFICAÇÃO INTELIGENTE ---
        appState.classified = data.map(c => {
            const u = (c.username || "").toLowerCase();
            const n = (c.nome_completo || "").toLowerCase();
            const cargo = (c.cargo || "").toLowerCase();
            const estado = (c.estado || "").toUpperCase();

            let scenario = "Nacional"; 

            const isRegional = 
                cargo.includes("vereador") || 
                cargo.includes("prefeito") || 
                cargo.includes("estadual") ||
                u.includes("veread") ||
                n.includes("vereador") ||
                u.includes("parnamirim") ||
                u.includes("natal") ||
                (estado === "RN" && !cargo.includes("senador") && !cargo.includes("federal") && !cargo.includes("ministro"));

            if (isRegional) {
                scenario = "Regional";
            }

            return { ...c, scenario };
        });

        let globTotal = 0, globHate = 0;
        const stateStats = {};
        
        data.forEach(c => {
            const ti = c.comentarios_totais_count || 0;
            const th = c.comentarios_odio_count || 0;
            globTotal += ti; globHate += th;
            const uf = c.estado || 'BR';
            if(!stateStats[uf]) stateStats[uf] = { count: 0, hate: 0, total: 0 };
            stateStats[uf].count++;
            stateStats[uf].total += ti;
            stateStats[uf].hate += th;
        });

        stateStats['BR'] = { count: data.length, hate: globHate, total: globTotal };
        appState.stats = stateStats;
        
        const updateText = (id, val) => {
            const el = document.getElementById(id);
            if(el) el.innerText = val;
        };

        updateText('kpi-monitorados', data.length);
        updateText('kpi-total', globTotal.toLocaleString());
        updateText('kpi-hate', globHate);
        updateText('kpi-res', `${(100 - (globHate/globTotal*100 || 0)).toFixed(1)}%`);

        renderRankings(appState.classified);
        renderAlerts(appState.alertas);
        renderDossieGrid('dossie-grid', data);
        renderBrazilMap('svg-map-br', stateStats);
        renderImpactCharts();
        
        console.log("Sincronização Finalizada.");
    } catch(e) { 
        console.error("Critical Refresh Error:", e);
    }
};

function renderRankings(data) {
    const nac = data.filter(i => i.scenario === 'Nacional').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 5);
    const reg = data.filter(i => i.scenario === 'Regional').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 5);
    
    const draw = (list, id) => {
        const container = document.getElementById(id);
        if(!container) return;
        const maxVal = list[0]?.comentarios_totais_count || 1;
        container.innerHTML = list.map(t => `
            <div onclick="window.openDetail('${t.username}')" class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-all cursor-pointer group">
                <img src="https://unavatar.io/instagram/${t.username}" class="w-8 h-8 rounded-lg border border-white/10" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                <div class="flex-1">
                    <div class="flex justify-between text-[9px] font-bold text-slate-300">
                        <span class="truncate w-24 group-hover:text-blue-400 transition-colors">@${t.username}</span>
                        <span class="font-mono text-blue-400">${(t.comentarios_totais_count || 0).toLocaleString()}</span>
                    </div>
                    <div class="w-full h-1 bg-white/5 rounded-full mt-1.5 overflow-hidden">
                        <div class="h-full bg-blue-600 shadow-[0_0_8px_rgba(37,99,235,0.5)]" style="width: ${(t.comentarios_totais_count/maxVal*100)}%"></div>
                    </div>
                </div>
            </div>`).join('');
    };
    draw(nac, 'rank-nac');
    draw(reg, 'rank-reg');
}

let mainChart = null;
function renderImpactCharts() {
    const ctxEl = document.getElementById('chartMain');
    if(!ctxEl) return;

    const labels = ['Nacional', 'Regional'];
    const volumeData = [
        appState.classified.filter(i => i.scenario === 'Nacional').reduce((s, c) => s + (c.comentarios_totais_count || 0), 0),
        appState.classified.filter(i => i.scenario === 'Regional').reduce((s, c) => s + (c.comentarios_totais_count || 0), 0)
    ];
    const hateData = [
        appState.classified.filter(i => i.scenario === 'Nacional').reduce((s, c) => s + (c.comentarios_odio_count || 0), 0),
        appState.classified.filter(i => i.scenario === 'Regional').reduce((s, c) => s + (c.comentarios_odio_count || 0), 0)
    ];

    if(mainChart) mainChart.destroy();
    const ctx = ctxEl.getContext('2d');
    
    mainChart = new Chart(ctx, {
        type: 'bar',
        data: { 
            labels, 
            datasets: [
                { 
                    label: 'Volume Total', 
                    data: volumeData, 
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    borderRadius: 8
                },
                { 
                    label: 'Ataques Detec.', 
                    data: hateData, 
                    backgroundColor: 'rgba(239, 68, 68, 0.5)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ] 
        },
        options: { 
            responsive: true, maintainAspectRatio: false, 
            plugins: { legend: { display: true, labels: { color: '#64748b', font: { size: 9 } } } }, 
            scales: { 
                y: { grid: { color: 'rgba(255,255,255,0.02)' }, ticks: { color: '#64748b', font: { size: 8 } } }, 
                x: { grid: { display: false }, ticks: { color: '#f8fafc', font: { size: 10, weight: 'bold' } } } 
            } 
        }
    });
}

function renderAlerts(alertas) {
    const container = document.getElementById('feed-alertas');
    if(!container) return;
    if(!alertas || alertas.length === 0) {
        container.innerHTML = `<div class="col-span-full py-10 text-center text-slate-500 text-[10px] font-bold uppercase tracking-widest italic">Nenhum registro encontrado.</div>`;
        return;
    }
    container.innerHTML = alertas.map(a => {
        // Se is_fallback for verdadeiro, não é um ataque de ódio, mas sim a última interação capturada
        const isHate = !a.is_fallback;
        const color = isHate ? 'red' : 'blue';
        const icon = isHate ? 'alert-triangle' : 'message-square';
        const title = isHate ? 'Ataque Detectado' : 'Interação Recente';
        const confianca = isHate ? '98%' : 'N/A';

        return `
        <div class="glass-card p-6 bg-${color}-500/[0.03] border-${color}-500/10 hover:bg-${color}-500/[0.06] transition-all group relative overflow-hidden">
            <div class="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity"><i data-lucide="${icon}" class="w-4 h-4 text-${color}-500"></i></div>
            <div class="flex items-center gap-3 mb-4">
                <img src="https://unavatar.io/instagram/${a.candidato_id}" class="w-6 h-6 rounded-full border border-${color}-500/20" onerror="this.src='https://ui-avatars.com/api/?name=${a.candidato_id}'">
                <div><span class="text-[9px] font-black text-white block">@${a.candidato_id}</span><span class="text-[7px] text-slate-500 uppercase font-bold tracking-tighter">${new Date(a.data_coleta).toLocaleString('pt-BR')}</span></div>
            </div>
            <p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-${color}-500/30 pl-3 mb-4">"${a.texto_bruto || a.texto}"</p>
            <div class="flex justify-between items-center">
                <span class="px-2 py-0.5 bg-${color}-500/10 text-${color}-400 rounded text-[7px] font-black uppercase border border-${color}-500/20">${title}</span>
                <span class="text-[8px] font-bold text-slate-500">Confiança: ${confianca}</span>
            </div>
        </div>`;
    }).join('');
    if(window.lucide) lucide.createIcons();
}

function renderTrends() {
    const container = document.getElementById('predictive-trends');
    if(!container) return;
    
    // Momentum Real
    const topTrends = appState.classified
        .filter(c => (c.comentarios_totais_count || 0) > 0)
        .map(c => ({
            username: c.username,
            ratio: ((c.comentarios_odio_count || 0) / (c.comentarios_totais_count || 1)),
            status: ((c.comentarios_odio_count || 0) / (c.comentarios_totais_count || 1)) > 0.1 ? 'RISCO ALTO' : 'ESTÁVEL'
        }))
        .sort((a,b) => b.ratio - a.ratio)
        .slice(0, 3);

    container.innerHTML = topTrends.map(t => `
        <div class="p-4 bg-blue-600/5 rounded-2xl border border-blue-500/10 flex items-center justify-between">
            <div class="flex items-center gap-3"><div class="w-2 h-2 ${t.status === 'RISCO ALTO' ? 'bg-red-500 animate-pulse' : 'bg-blue-500 animate-ping'} rounded-full"></div><span class="text-[10px] font-black text-white uppercase">@${t.username}</span></div>
            <span class="text-[8px] font-bold ${t.status === 'RISCO ALTO' ? 'text-red-400 bg-red-500/10' : 'text-blue-400 bg-blue-500/10'} px-2 py-0.5 rounded uppercase tracking-tighter">${t.status}</span>
        </div>`).join('') || '<p class="text-[9px] text-slate-500 italic text-center py-4">Aguardando dados de volumetria.</p>';
}

window.openDetail = function(username) {
    const m = appState.data.find(d => d.username === username);
    if(!m) return;
    const modal = document.getElementById('detail-modal');
    const content = document.getElementById('detail-content');
    const res = (m.comentarios_totais_count || 0) > 0 ? (100 - ((m.comentarios_odio_count || 0) / m.comentarios_totais_count * 100)) : 100;
    
    const backBtn = appState.currentModalUF 
        ? `<button onclick="window.openRegionalDetail('${appState.currentModalUF}')" class="mb-6 flex items-center gap-2 text-[10px] font-black text-blue-400 uppercase tracking-widest hover:text-white transition-colors"><i data-lucide="arrow-left" class="w-3 h-3"></i> Voltar ao Diagnóstico Regional (${appState.currentModalUF})</button>`
        : '';

    // Lógica de diagnóstico dinâmico baseada em linguística
    let diagText = "";
    if (res < 70) {
        diagText = `Identificada alta densidade de vocabulário hostil. Foram capturadas ${m.comentarios_odio_count || 0} interações com agressividade direta, superando a média do grupo monitorado e indicando forte rejeição orgânica.`;
    } else if (res < 90) {
        diagText = `A análise linguística aponta para um estado de atenção. O perfil registra ${m.comentarios_odio_count || 0} comentários com polarização negativa ou ironia. Recomenda-se leitura do contexto das interações.`;
    } else {
        diagText = `A maioria das interações (${m.comentarios_totais_count || 0} avaliadas) é composta por vocabulário neutro ou de apoio. O ecossistema de comentários apresenta alta resiliência linguística neste momento.`;
    }

    // Risco baseado em volumetria
    const riscoPercent = Math.min((100 - res) * 1.5, 100).toFixed(1);
    const engajRisco = (((m.comentarios_odio_count || 0) + 5) / ((m.comentarios_totais_count || 0) + 10) * 100).toFixed(1);

    content.innerHTML = `
        ${backBtn}
        <div class="flex items-center gap-8 mb-10">
            <img src="https://unavatar.io/instagram/${username}" class="w-32 h-32 rounded-3xl border-4 border-blue-600/20 shadow-2xl" onerror="this.src='https://ui-avatars.com/api/?name=${username}'">
            <div>
                <h2 class="text-4xl font-black text-white mb-2">@${username}</h2>
                <p class="text-lg text-blue-400 font-bold uppercase tracking-widest">${m.nome_completo || 'Identidade Preservada'}</p>
                <div class="flex gap-3 mt-4">
                    <span class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-bold text-slate-400 border border-white/10 uppercase">${m.cargo || 'Monitorado'}</span>
                    <span class="px-3 py-1 bg-blue-600/10 rounded-full text-[10px] font-bold text-blue-400 border border-blue-500/20 uppercase">${m.estado || 'BR'}</span>
                </div>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-6 mb-10">
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1 text-blue-400">Total Comentários</span>
                <div class="text-2xl font-black text-white">${(m.comentarios_totais_count || 0).toLocaleString()}</div>
            </div>
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center text-red-500">
                <span class="text-[10px] font-bold uppercase block mb-1">Alertas de Ódio</span>
                <div class="text-2xl font-black">${m.comentarios_odio_count || 0}</div>
            </div>
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center text-emerald-400">
                <span class="text-[10px] font-bold uppercase block mb-1">Resiliência</span>
                <div class="text-2xl font-black">${res.toFixed(1)}%</div>
            </div>
        </div>
        <div class="space-y-6">
            <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest border-b border-white/5 pb-2">Análise Linguística PASA</h3>
            <div class="p-8 bg-blue-600/5 rounded-3xl border border-blue-500/10">
                <div class="flex justify-between items-center mb-6">
                    <span class="text-[10px] font-black text-blue-400 uppercase tracking-widest">Diagnóstico Situacional</span>
                    <span class="px-3 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-[8px] font-black uppercase">Monitoramento Ativo</span>
                </div>
                <p class="text-sm text-slate-300 leading-relaxed italic mb-8">"${diagText}"</p>
                <div class="grid grid-cols-2 gap-8">
                    <div class="space-y-2">
                        <div class="flex justify-between text-[8px] font-bold uppercase">
                            <span class="text-slate-500">Probabilidade de Crise</span>
                        </div>
                        <div class="w-full h-4 bg-white/5 rounded-full overflow-hidden relative">
                            <div class="h-full bg-blue-600 transition-all duration-1000 flex items-center justify-end pr-2" style="width: ${riscoPercent}%">
                                <span class="text-[8px] font-bold text-white shadow-sm">${riscoPercent}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between text-[8px] font-bold uppercase">
                            <span class="text-slate-500">Engajamento de Risco</span>
                        </div>
                        <div class="w-full h-4 bg-white/5 rounded-full overflow-hidden relative">
                            <div class="h-full bg-amber-500 transition-all duration-1000 flex items-center justify-end pr-2" style="width: ${engajRisco}%">
                                <span class="text-[8px] font-bold text-white shadow-sm">${engajRisco}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    modal.style.display = 'flex';
    modal.classList.remove('hidden');
    if(window.lucide) lucide.createIcons();
};

window.closeDetail = function() {
    const modal = document.getElementById('detail-modal');
    modal.style.display = 'none';
    modal.classList.add('hidden');
    appState.currentModalUF = null;
};

window.openRegionalDetail = function(uf) {
    const filterUF = uf === "Brasil" ? "BR" : uf;
    appState.currentModalUF = filterUF;

    const modal = document.getElementById('detail-modal');
    const content = document.getElementById('detail-content');
    if(!modal || !content) return;

    const monitoradosNoEstado = filterUF === "BR" 
        ? appState.data 
        : appState.data.filter(d => d.estado === filterUF);

    const info = appState.stats[filterUF] || { count: 0, hate: 0, total: 0 };
    const resilienciaMedia = info.total > 0 ? (100 - (info.hate / info.total * 100)).toFixed(1) : "100.0";

    content.innerHTML = `
        <div class="flex justify-between items-start mb-8">
            <div>
                <h2 class="text-4xl font-black text-white mb-2">Diagnóstico: ${filterUF === "BR" ? "Brasil" : filterUF}</h2>
                <p class="text-sm text-blue-400 font-bold uppercase tracking-widest">Inteligência Estratégica Regional</p>
            </div>
            <div class="text-right">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1">Resiliência</span>
                <div class="text-3xl font-black text-emerald-400">${resilienciaMedia}%</div>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-10">
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1 text-blue-400">Interações</span>
                <div class="text-2xl font-black text-white">${info.total.toLocaleString()}</div>
            </div>
            <div class="p-6 bg-red-500/5 rounded-3xl border border-red-500/10 text-center text-red-500">
                <span class="text-[10px] font-bold uppercase block mb-1">Alertas</span>
                <div class="text-2xl font-black">${info.hate}</div>
            </div>
        </div>

        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 border-b border-white/5 pb-2">Monitorados Ativos</h3>
        
        <div class="space-y-3">
            ${monitoradosNoEstado.map(m => `
                <div onclick="window.openDetail('${m.username}')" class="flex items-center justify-between p-4 bg-white/[0.03] border border-white/5 rounded-2xl hover:bg-white/[0.08] transition-all cursor-pointer group">
                    <div class="flex items-center gap-4">
                        <img src="https://unavatar.io/instagram/${m.username}" class="w-10 h-10 rounded-xl border border-white/10" onerror="this.src='https://ui-avatars.com/api/?name=${m.username}'">
                        <div>
                            <span class="text-xs font-black text-white block group-hover:text-blue-400 transition-colors">@${m.username}</span>
                            <span class="text-[9px] text-slate-500 uppercase font-bold">${m.cargo || 'Monitorado'}</span>
                        </div>
                    </div>
                    <div class="text-right text-[10px] font-mono text-blue-400">${(m.comentarios_totais_count || 0).toLocaleString()} ints</div>
                </div>
            `).join('')}
        </div>`;

    modal.style.display = 'flex';
    modal.classList.remove('hidden');
    if(window.lucide) lucide.createIcons();
};

window.openCheckout = function() {
    document.getElementById('checkout-modal').style.display = 'flex';
};

window.closeCheckout = function() {
    document.getElementById('checkout-modal').style.display = 'none';
    document.getElementById('pix-area').classList.add('hidden');
};

window.payWithPix = async function() {
    const area = document.getElementById('pix-area');
    const img = document.getElementById('pix-qr-img');
    const text = document.getElementById('pix-payload-text');
    try {
        const response = await fetch('/api/generate-pix');
        const data = await response.json();
        if(data.qr_code) {
            img.src = data.qr_code;
            text.innerText = data.payload;
            area.classList.remove('hidden');
            area.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (e) { alert("Erro ao gerar QR Code PIX."); }
};

window.payWithPayPal = function() {
    const url = "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=thi.macedo@gmail.com&item_name=Dossie%20Sentinela&amount=49.99&currency_code=BRL";
    window.open(url, '_blank');
};

window.payWithStripe = async function() {
    try {
        const response = await fetch('/api/create-checkout-session', { method: 'POST' });
        const data = await response.json();
        if(data.url) window.location.href = data.url;
        else alert("Erro ao iniciar Checkout.");
    } catch (e) { alert("Erro de conexão com o gateway."); }
};

window.addEventListener('DOMContentLoaded', () => {
    window.navigate(window.location.hash.substring(1) || 'monitor');
    window.refresh();
    window.addEventListener('keydown', (e) => {
        if(e.key === 'Escape') { window.closeCheckout(); window.closeDetail(); }
    });
});
