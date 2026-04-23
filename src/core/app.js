import { fetchCandidatos } from '../services/apiService.js';
import { renderBrazilMap } from '../components/BrazilMap.js';
import { renderDossieGrid } from '../components/Dossie.js';

let appState = {
    view: 'monitor',
    data: [],
    stats: {}
};

window.navigate = function(v) {
    appState.view = v;
    window.location.hash = v;
    document.querySelectorAll('.view-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`view-${v}`).classList.remove('hidden');
    document.getElementById(`nav-${v}`).classList.add('active');
    if(v === 'monitor') renderTimeline();
};

window.focusState = function(uf) {
    document.querySelectorAll('.state').forEach(s => s.classList.remove('active'));
    document.getElementById(`state-${uf}`).classList.add('active');
    const info = appState.stats[uf] || { count: 0, hate: 0 };
    document.getElementById('st-name').innerText = uf;
    document.getElementById('st-targets').innerText = info.count;
    document.getElementById('st-hate').innerText = info.hate;
};

export async function refresh() {
    try {
        const data = await fetchCandidatos();
        appState.data = data;
        
        let globTotal = 0, globHate = 0;
        const stateStats = {};
        
        data.forEach(c => {
            const ti = c.comentarios_totais_count || 0;
            const th = c.comentarios_odio_count || 0;
            globTotal += ti; globHate += th;
            if(c.estado) {
                if(!stateStats[c.estado]) stateStats[c.estado] = { count: 0, hate: 0, total: 0 };
                stateStats[c.estado].count++;
                stateStats[c.estado].total += ti;
                stateStats[c.estado].hate += th;
            }
        });

        appState.stats = stateStats;
        updateKPIs(data.length, globTotal, globHate);
        renderRankings(data);
        renderDossieGrid('dossie-grid', data);
        renderBrazilMap('svg-map-br', stateStats);
    } catch(e) { console.error("App Refresh Error:", e); }
}

function updateKPIs(alvos, total, hate) {
    document.getElementById('kpi-alvos').innerText = alvos;
    document.getElementById('kpi-total').innerText = total.toLocaleString();
    document.getElementById('kpi-hate').innerText = hate;
    document.getElementById('kpi-res').innerText = `${(100 - (hate/total*100 || 0)).toFixed(1)}%`;
}

function renderRankings(data) {
    const nac = data.filter(i => !i.estado || i.estado === 'DF').slice(0, 4);
    const reg = data.filter(i => i.estado && i.estado !== 'DF').slice(0, 4);
    const draw = (list, id) => {
        document.getElementById(id).innerHTML = list.map(t => `
            <div class="flex items-center gap-3">
                <img src="https://unavatar.io/instagram/${t.username}" class="w-8 h-8 rounded-lg" onerror="this.src='https://ui-avatars.com/api/?name=${t.username}'">
                <div class="flex-1"><div class="flex justify-between text-[9px] font-bold"><span>@${t.username}</span><span>${t.comentarios_totais_count}</span></div>
                <div class="w-full h-1 bg-white/5 rounded-full mt-1"><div class="h-full bg-blue-600" style="width: ${t.comentarios_totais_count/(list[0].comentarios_totais_count||1)*100}%"></div></div></div>
            </div>`).join('');
    };
    draw(nac, 'rank-nac'); draw(reg, 'rank-reg');
}

function renderTimeline() {
    const ctx = document.getElementById('chartMain').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: { labels: ['17/04','18/04','19/04','20/04','21/04','22/04','23/04'], datasets: [{ label: 'V', data: [150, 220, 180, 290, 310, 240, 380], borderColor: '#3b82f6', tension: 0.4, fill: true, backgroundColor: 'rgba(59,130,246,0.02)', pointRadius: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { display: false }, x: { grid: { display: false }, ticks: { color: '#475569', font: { size: 8 } } } } }
    });
}

window.onload = () => {
    navigate(window.location.hash.substring(1) || 'monitor');
    refresh();
};
