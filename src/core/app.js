import { fetchCandidatos, fetchAlertas } from '../services/apiService.js';
import { renderBrazilMap } from '../components/BrazilMap.js';
import { renderDossieGrid } from '../components/Dossie.js';

let appState = {
    view: 'monitor',
    data: [],
    stats: {},
    classified: [],
    alertas: [],
    trends: []
};

window.navigate = function(v) {
    appState.view = v;
    window.location.hash = v;
    document.querySelectorAll('.view-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    const targetView = document.getElementById('view-' + v);
    const targetNav = document.getElementById('nav-' + v);
    
    if(targetView) targetView.classList.remove('hidden');
    if(targetNav) targetNav.classList.add('active');
    
    if(v === 'monitor') renderTimeline();
};

window.focusState = function(uf) {
    document.querySelectorAll('.state').forEach(s => s.classList.remove('active'));
    const stateEl = document.getElementById('state-' + uf);
    if(stateEl) stateEl.classList.add('active');
    
    const info = appState.stats[uf] || { count: 0, hate: 0 };
    document.getElementById('st-name').innerText = uf;
    document.getElementById('st-targets').innerText = info.count;
    document.getElementById('st-hate').innerText = info.hate;
};

window.refresh = async function() {
    console.log("Iniciando Sincronização v15.2...");
    try {
        let trendsData = [];
        try {
            const trRes = await fetch('/data/predictive_trends.json');
            if(trRes.ok) trendsData = await trRes.json();
        } catch(e) { console.warn("Predictive data not found"); }

        const [data, alertas] = await Promise.all([
            fetchCandidatos(),
            fetchAlertas(6)
        ]);
        
        appState.data = data;
        appState.alertas = alertas;
        appState.trends = trendsData;

        appState.classified = data.map(c => {
            let scenario = "Nacional";
            const u = (c.username || "").toLowerCase();
            const n = (c.nome_completo || "").toLowerCase();
            if (u.includes("vereador") || n.includes("vereador") || u.includes("parnamirim") || n.includes("natal")) {
                scenario = "Municipal";
            } else if (u.includes("rn") || u.includes("bezerra")) {
                scenario = "Estadual";
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

        appState.stats = stateStats;
        
        const elAlvos = document.getElementById('kpi-monitorados');
        const elTotal = document.getElementById('kpi-total');
        const elHate = document.getElementById('kpi-hate');
        const elRes = document.getElementById('kpi-res');
        
        if(elAlvos) elAlvos.innerText = data.length;
        if(elTotal) elTotal.innerText = globTotal.toLocaleString();
        if(elHate) elHate.innerText = globHate;
        if(elRes) elRes.innerText = (100 - (globHate/globTotal*100 || 0)).toFixed(1) + "%";

        renderRankings(appState.classified);
        renderAlerts(appState.alertas);
        renderTrends(appState.trends);
        renderDossieGrid('dossie-grid', data);
        renderBrazilMap('svg-map-br', stateStats);
        
        console.log("Sincronização Finalizada.");
    } catch(e) { 
        console.error("Critical Refresh Error:", e);
    }
};

function renderRankings(data) {
    const nac = data.filter(i => i.scenario === 'Nacional').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 5);
    const reg = data.filter(i => i.scenario === 'Municipal' || i.scenario === 'Estadual').sort((a,b) => b.comentarios_totais_count - a.comentarios_totais_count).slice(0, 5);
    
    const draw = (list, id) => {
        const container = document.getElementById(id);
        if(!container) return;
        const maxVal = list[0]?.comentarios_totais_count || 1;
        container.innerHTML = list.map(t => `
            <div class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-all cursor-pointer">
                <img src="https://unavatar.io/instagram/${t.username}" class="w-8 h-8 rounded-lg border border-white/10" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                <div class="flex-1">
                    <div class="flex justify-between text-[9px] font-bold text-slate-300">
                        <span class="truncate w-24">@${t.username}</span>
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
function renderTimeline() {
    const ctxEl = document.getElementById('chartMain');
    if(!ctxEl) return;
    const labels = ['18/04','19/04','20/04','21/04','22/04','23/04','Hoje'];
    const volumeData = [1200, 1900, 3100, 2800, 4200, 3800, 5100]; 
    const attackData = [80, 150, 420, 310, 580, 490, 720];

    if(mainChart) mainChart.destroy();
    const ctx = ctxEl.getContext('2d');
    mainChart = new Chart(ctx, {
        type: 'line',
        data: { 
            labels, 
            datasets: [
                { label: 'Volume', data: volumeData, borderColor: '#3b82f6', borderWidth: 3, tension: 0.4, fill: true, backgroundColor: 'rgba(59,130,246,0.05)', pointRadius: 4, pointBackgroundColor: '#3b82f6' },
                { label: 'Ataques', data: attackData, borderColor: '#ef4444', borderWidth: 2, borderDash: [5, 5], tension: 0.4, fill: false, pointRadius: 0 }
            ] 
        },
        options: { 
            responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, 
            scales: { 
                y: { grid: { color: 'rgba(255,255,255,0.02)' }, ticks: { color: '#475569', font: { size: 8 } } }, 
                x: { grid: { display: false }, ticks: { color: '#475569', font: { size: 8 } } } 
            } 
        }
    });
}

function renderAlerts(alertas) {
    const container = document.getElementById('feed-alertas');
    if(!container) return;
    if(!alertas || alertas.length === 0) {
        container.innerHTML = `<div class="col-span-full py-10 text-center text-slate-500 text-[10px] font-bold uppercase tracking-widest italic">Nenhum alerta crítico detectado nas últimas horas.</div>`;
        return;
    }
    container.innerHTML = alertas.map(a => `
        <div class="glass-card p-6 bg-red-500/[0.03] border-red-500/10 hover:bg-red-500/[0.06] transition-all group relative overflow-hidden">
            <div class="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity"><i data-lucide="alert-triangle" class="w-4 h-4 text-red-500"></i></div>
            <div class="flex items-center gap-3 mb-4">
                <img src="https://unavatar.io/instagram/${a.candidatos?.username}" class="w-6 h-6 rounded-full border border-red-500/20" onerror="this.src='https://ui-avatars.com/api/?name=${a.candidatos?.username}'">
                <div><span class="text-[9px] font-black text-white block">@${a.candidatos?.username}</span><span class="text-[7px] text-slate-500 uppercase font-bold tracking-tighter">${new Date(a.criado_em).toLocaleString('pt-BR')}</span></div>
            </div>
            <p class="text-[11px] text-slate-300 leading-relaxed italic border-l-2 border-red-500/30 pl-3 mb-4">"${a.texto_bruto}"</p>
            <div class="flex justify-between items-center">
                <span class="px-2 py-0.5 bg-red-500/10 text-red-400 rounded text-[7px] font-black uppercase border border-red-500/20">Ataque Detectado</span>
                <span class="text-[8px] font-bold text-slate-500">Confiança: 98%</span>
            </div>
        </div>`).join('');
    if(window.lucide) lucide.createIcons();
}

function renderTrends(trends) {
    const container = document.getElementById('predictive-trends');
    if(!container) return;
    container.innerHTML = (trends || []).map(t => `
        <div class="p-4 bg-blue-600/5 rounded-2xl border border-blue-500/10 flex items-center justify-between">
            <div class="flex items-center gap-3"><div class="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div><span class="text-[10px] font-black text-white uppercase">@${t.username}</span></div>
            <span class="text-[8px] font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded uppercase tracking-tighter">${t.status}</span>
        </div>`).join('') || '<p class="text-[9px] text-slate-500 italic text-center py-4">Sem anomalias preditivas detectadas.</p>';
}

window.openDetail = function(username) {
    const monitorado = appState.data.find(d => d.username === username);
    if(!monitorado) return;
    const modal = document.getElementById('detail-modal');
    const content = document.getElementById('detail-content');
    const resiliencia = monitorado.comentarios_totais_count > 0 ? (100 - (monitorado.comentarios_odio_count / monitorado.comentarios_totais_count * 100)) : 100;
    content.innerHTML = `
        <div class="flex items-center gap-8 mb-10">
            <img src="https://unavatar.io/instagram/${username}" class="w-32 h-32 rounded-3xl border-4 border-blue-600/20 shadow-2xl" onerror="this.src='https://ui-avatars.com/api/?name=${username}'">
            <div>
                <h2 class="text-4xl font-black text-white mb-2">@${username}</h2>
                <p class="text-lg text-blue-400 font-bold uppercase tracking-widest">${monitorado.nome_completo || 'Identidade Preservada'}</p>
                <div class="flex gap-3 mt-4">
                    <span class="px-3 py-1 bg-white/5 rounded-full text-[10px] font-bold text-slate-400 border border-white/10 uppercase">${monitorado.cargo || 'Monitorado'}</span>
                    <span class="px-3 py-1 bg-blue-600/10 rounded-full text-[10px] font-bold text-blue-400 border border-blue-500/20 uppercase">${monitorado.estado || 'BR'}</span>
                </div>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-6 mb-10">
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1">Total Comentários</span>
                <div class="text-2xl font-black text-white">${(monitorado.comentarios_totais_count || 0).toLocaleString()}</div>
            </div>
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1 text-red-500">Alertas de Ódio</span>
                <div class="text-2xl font-black text-red-500">${monitorado.comentarios_odio_count || 0}</div>
            </div>
            <div class="p-6 bg-white/5 rounded-3xl border border-white/5 text-center">
                <span class="text-[10px] text-slate-500 font-bold uppercase block mb-1 text-emerald-400">Resiliência</span>
                <div class="text-2xl font-black text-emerald-400">${resiliencia.toFixed(1)}%</div>
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
