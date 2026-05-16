/**
 * PASA v40 - Frontend Engine: Integração completa com Backend Forense e Monitor de Ameaças
 */
import { initAuth, getCurrentUserEmail } from './auth.js';
import { renderSessionManager } from '../components/session-manager.js';
import { renderWorkersView } from './workers_view.js';
import { dataService } from '../services/dataService.js';

// Configurações Supabase (Injetadas pelo Vite ou window)
const SUPABASE_URL = window.SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY;

let allComments = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initAuth();
    setupRouting();
});

export async function initDashboard() {
    renderSessionManager('session-manager-container');
    await fetchSystemStatus();
    await fetchComments();
    setupFilters();
    setupSearch();
}

// --- ROUTING ---

function setupRouting() {
    const handleRoute = () => {
        const hash = window.location.hash.replace('#', '') || 'monitor';
        
        // Atualizar Sidebar
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.toggle('active', el.id === `nav-${hash}`);
        });

        // Atualizar Visibilidade das Views
        document.querySelectorAll('.view-content').forEach(el => {
            el.classList.toggle('active-view', el.id === `view-${hash}`);
        });

        // Trigger Renderizadores Específicos
        switch(hash) {
            case 'monitor':
                renderFeed();
                break;
            case 'networks':
                renderNetworks();
                break;
            case 'directory':
                renderDirectory();
                break;
            case 'dossie':
                renderDossie();
                break;
            case 'ads':
                renderAds();
                break;
            case 'workers':
                renderWorkersView();
                break;
        }

        if (window.lucide) lucide.createIcons();
    };

    window.addEventListener('hashchange', handleRoute);
    handleRoute(); // Initial route
}

async function renderNetworks() {
    const container = document.getElementById('networks-container');
    if (!container) return;
    container.innerHTML = `
        <div class="p-12 text-center">
            <i data-lucide="share-2" class="w-12 h-12 text-blue-500 m-auto mb-4 opacity-20"></i>
            <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-2">Mapeamento de Clusters</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase">Analisando conexões coordenadas entre perfis suspeitos...</p>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

async function renderDirectory() {
    const container = document.getElementById('directory-container');
    if (!container) return;
    container.innerHTML = `
        <div class="p-12 text-center">
            <i data-lucide="users" class="w-12 h-12 text-slate-300 m-auto mb-4"></i>
            <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-2">Diretório de Perfis</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase">Base de dados consolidada de alvos e agressores.</p>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

async function renderDossie() {
    const container = document.getElementById('dossie-container');
    if (!container) return;
    container.innerHTML = `
        <div class="p-12 text-center">
            <i data-lucide="fingerprint" class="w-12 h-12 text-slate-300 m-auto mb-4"></i>
            <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-2">Central de Relatórios</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase">Geração de dossiês automatizados para fins informacionais.</p>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

async function renderAds() {
    const container = document.getElementById('ads-list');
    if (!container) return;
    container.innerHTML = `
        <div class="p-12 text-center col-span-full">
            <i data-lucide="megaphone" class="w-12 h-12 text-slate-300 m-auto mb-4"></i>
            <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-2">Monitor de Anúncios</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase">Integração com Meta Ad Library para rastreio de impulsionamento.</p>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

// --- DATA FETCHING ---

async function fetchSystemStatus() {
    try {
        const res = await fetch('/api/v1/monitor/status');
        if (!res.ok) {
            // Fallback se a API de monitor falhar, tentamos o stream local
            await fetchProfilerStream();
            return;
        }
        const data = await res.json();
        renderKPIs(data);
        renderCircuitBreaker(data.queue_health || { circuit_breaker_tripped: false });
        renderWorkerEvolution(data.worker_evolution || []);
        
        // PASA v40: Prioridade para o stream de ameaças
        await fetchProfilerStream();
    } catch (e) {
        console.error('Status fetch error:', e);
        await fetchProfilerStream();
    }
}

async function fetchProfilerStream() {
    try {
        // PASA v40: Busca do JSON gerado pelo servidor local (via Git push)
        const timestamp = new Date().getTime();
        
        // Busca KPIs consolidados
        const kpiRes = await fetch(`/docs/kpis.json?t=${timestamp}`);
        if (kpiRes.ok) {
            const kpis = await kpiRes.json();
            updateKPI('kpi-targets', kpis.targets || 0);
            updateKPI('kpi-hate', kpis.alerts || 0);
            updateKPI('kpi-total', kpis.db_sample || 0);
            
            const resEl = document.getElementById('kpi-res');
            if (resEl) {
                // Cálculo de resiliência simples
                const resValue = kpis.db_sample > 0 ? (((kpis.db_sample - kpis.alerts) / kpis.db_sample) * 100).toFixed(1) : 100;
                resEl.textContent = `${resValue}%`;
                resEl.className = resValue < 80 ? 'text-lg font-black text-red-600' : 'text-lg font-black text-emerald-600';
            }
        }

        // Busca Stream de Ameaças
        const streamRes = await fetch(`/docs/profiler_stream.json?t=${timestamp}`);
        if (streamRes.ok) {
            const stream = await streamRes.json();
            renderProfilerStream(stream);
        }
    } catch (e) {
        console.warn('Profiler stream offline:', e);
    }
}

async function fetchComments() {
    if (!SUPABASE_URL) return;
    try {
        // PASA v45: Injeção Cirúrgica - Buscando métricas CCF e Direção de Risco
        const timestamp = new Date().getTime();
        const res = await fetch(`${SUPABASE_URL}/rest/v1/comentarios?select=id,autor_username,texto_limpo,data_coleta,is_hate,categoria_ia,direcao_odio,confianca_ia,processado_ia,candidato_id,ccf_density,ccf_sync,ccf_performativity&order=data_coleta.desc&limit=100&t=${timestamp}`, {
            headers: { 
                'apikey': SUPABASE_ANON_KEY, 
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        allComments = await res.json();
        renderFeed();
    } catch (e) {
        console.error('Comments fetch error:', e);
    }
}

// --- RENDERING ---

function renderFeed() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;

    let filtered = allComments;
    if (currentFilter === 'hate') filtered = allComments.filter(c => c.is_hate === true);
    if (currentFilter === 'critical') filtered = allComments.filter(c => c.is_hate === true && c.confianca_ia >= 0.8);

    container.innerHTML = filtered.map(c => renderThreatCard(c)).join('');
    if (window.lucide) lucide.createIcons();
}

function renderThreatCard(c) {
    let borderColor = 'bg-slate-300', badgeColor = 'bg-slate-100 text-slate-500', badgeText = 'Pendente', quoteStyle = 'bg-slate-50 border-slate-300 text-slate-700', iconColor = 'text-slate-400';
    
    if (c.is_hate === true && c.categoria_ia) {
        borderColor = 'bg-red-500'; iconColor = 'text-red-500';
        const catMap = {
            'ODIO_IDENTITARIO': { bg: 'bg-purple-100 text-purple-600', txt: `Ódio Identitário ${c.direcao_odio ? '→ ' + c.direcao_odio : ''}`, q: 'bg-purple-50 border-purple-400 text-purple-800' },
            'VIOLENCIA_GENERO': { bg: 'bg-pink-100 text-pink-600', txt: `Violência de Gênero ${c.direcao_odio ? '→ ' + c.direcao_odio : ''}`, q: 'bg-pink-50 border-pink-400 text-pink-800' },
            'AMEACA': { bg: 'bg-red-100 text-red-700', txt: 'Ameaça Física/Morte', q: 'bg-red-100 border-red-500 text-red-900' },
            'INSULTO_AD_HOMINEM': { bg: 'bg-rose-100 text-rose-600', txt: 'Insulto Ad Hominem', q: 'bg-rose-50 border-rose-400 text-rose-800' },
            'ATAQUE_INSTITUCIONAL': { bg: 'bg-cyan-100 text-cyan-700', txt: `Ataque Institucional ${c.direcao_odio ? '→ ' + c.direcao_odio : ''}`, q: 'bg-cyan-50 border-cyan-400 text-cyan-800' },
            'RIGOR_CRIMINAL': { bg: 'bg-amber-100 text-amber-700', txt: 'Rigor Criminal (Sem Prova)', q: 'bg-amber-50 border-amber-400 text-amber-800' }
        };
        const cat = catMap[c.categoria_ia] || { bg: 'bg-red-100 text-red-600', txt: 'Indício de Risco', q: 'bg-red-50 border-red-400 text-red-800' };
        badgeColor = cat.bg; badgeText = cat.txt; quoteStyle = cat.q;
    } else if (c.processado_ia === true) {
        borderColor = 'bg-emerald-400'; badgeColor = 'bg-emerald-100 text-emerald-600'; badgeText = 'Seguro'; quoteStyle = 'bg-emerald-50 border-emerald-300 text-emerald-800'; iconColor = 'text-emerald-500';
    }

    const cleanText = (c.texto_limpo || '').replace(/&nbsp;/g, ' ').trim();
    const cleanAuthor = (c.autor_username || 'Anônimo').split('\n')[0];

    // PASA v45: Cálculo e Exibição do CCF no Card
    const confidence = c.confianca_ia ? (c.confianca_ia * 100).toFixed(1) : 0;
    const confidenceColor = confidence >= 80 ? 'text-green-600' : confidence >= 50 ? 'text-yellow-600' : 'text-red-600';
    
    const ccfBreakdown = c.is_hate ? `
        <div class="flex gap-3 text-[9px] font-mono text-slate-500 mt-1">
            <span title="Densidade Léxica">Den: ${(c.ccf_density * 100).toFixed(0)}%</span>
            <span title="Sincronização/Bot">Sync: ${(c.ccf_sync * 100).toFixed(0)}%</span>
            <span title="Performatividade">Perf: ${(c.ccf_performativity * 100).toFixed(0)}%</span>
        </div>
    ` : '';

    return `
        <div class="threat-card bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all overflow-hidden group">
            <div class="flex">
                <div class="w-1 ${borderColor} flex-shrink-0 transition-colors"></div>
                <div class="flex-1 p-4">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 overflow-hidden">
                                <img src="/assets/sentinela_small.webp" class="w-full h-full object-cover" onerror="this.style.display='none'">
                            </div>
                            <div>
                                <span class="text-sm font-bold text-slate-800"> @${cleanAuthor}</span>
                                <span class="text-[10px] ml-2 font-bold ${badgeColor} px-2 py-0.5 rounded-full uppercase tracking-wider">${badgeText}</span>
                            </div>
                        </div>
                        <div class="text-right">
                            <span class="text-[10px] font-mono text-slate-400 block">${timeAgo(c.data_coleta)}</span>
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
                                <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase">
                                    <i data-lucide="share-2" class="w-3 h-3"></i> ${(c.candidato_id || 'IG').substring(0,10)}
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
}

function renderKPIs(data) {
    if (data.queue_health) {
        updateKPI('kpi-monitorados', data.queue_health.pending + data.queue_health.processing);
    }
    // PASA v46: Atualiza ranking de alvos com alerta de shadowban
    renderHotTargets();
}

async function renderHotTargets() {
    try {
        // PASA v46: Busca alvos de maior relevância e checa shadowban
        const res = await fetch(`${SUPABASE_URL}/rest/v1/candidatos?select=username,nota_relevancia,shadowban_suspect&order=nota_relevancia.desc&limit=10`, {
            headers: { 
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
            }
        });
        const targets = await res.json();
        
        // Procuramos o container de ranking (chartMain no ui.js legado ou criamos um novo se necessário)
        const container = document.getElementById('chartMain') || document.getElementById('profiler-stream-feed');
        if (!container) return;

        // Se estivermos injetando no topo do profiler_stream_feed para visibilidade imediata
        const rankingHtml = `
            <div class="mb-4 pb-4 border-b border-slate-100">
                <h4 class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-3">Ranking de Relevância</h4>
                <div class="space-y-2">
                    ${targets.map(t => {
                        const density = t.nota_relevancia || 0;
                        const color = density > 40 ? 'bg-red-500' : density > 20 ? 'bg-orange-500' : 'bg-blue-500';
                        const shadowbanIcon = t.shadowban_suspect ? '<span title="Possível Shadowban" class="text-red-500 animate-pulse">👁️‍🗨️</span>' : '';
                        
                        return `
                            <div class="flex items-center justify-between">
                                <span class="text-[10px] font-bold text-slate-700">@${t.username} ${shadowbanIcon}</span>
                                <div class="flex items-center gap-2">
                                    <span class="text-[9px] font-black text-slate-400">${density}%</span>
                                    <div class="w-12 bg-slate-100 rounded-full h-1">
                                        <div class="${color} h-1 rounded-full" style="width: ${Math.min(density, 100)}%"></div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        // Para não sobrescrever o stream, podemos injetar no início
        if (container.id === 'profiler-stream-feed') {
            const existingRanking = container.querySelector('.ranking-area');
            if (existingRanking) {
                existingRanking.innerHTML = rankingHtml;
            } else {
                const div = document.createElement('div');
                div.className = 'ranking-area';
                div.innerHTML = rankingHtml;
                container.prepend(div);
            }
        }
    } catch(e) { console.error('Error rendering hot targets:', e); }
}

function renderProfilerStream(stream) {
    const container = document.getElementById('profiler-stream-feed');
    if (!container) return;
    
    if (!stream || stream.length === 0) {
        container.innerHTML = '<p class="text-[10px] text-slate-400 text-center">Aguardando dados da mineração...</p>';
        return;
    }

    // Inverte para mostrar os mais recentes primeiro
    const reversedStream = stream.slice().reverse();
    container.innerHTML = reversedStream.map(item => {
        const color = item.density > 40 ? 'text-red-600 bg-red-50' : item.density > 10 ? 'text-orange-600 bg-orange-50' : 'text-slate-700 bg-white';
        const barColor = item.density > 40 ? 'bg-red-500' : item.density > 10 ? 'bg-orange-500' : 'bg-emerald-500';
        return `
            <div class="flex items-center gap-2 p-2 rounded border border-slate-100 ${color} transition-all">
                <div class="flex-1">
                    <p class="text-[10px] font-bold truncate">@${item.user}</p>
                    <div class="w-full bg-slate-200 rounded-full h-1 mt-1">
                        <div class="${barColor} h-1 rounded-full" style="width: ${Math.min(item.density, 100)}%"></div>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-xs font-black">${item.density}%</p>
                    <p class="text-[8px] text-slate-500">${item.hate}/${item.total}</p>
                </div>
            </div>
        `;
    }).join('');
}

function renderWorkerEvolution(workers) {
    const container = document.getElementById('worker-xp-ranking');
    if (!container || !workers || workers.length === 0) return;
    container.innerHTML = workers.map(w => `
        <div class="flex justify-between items-center p-2 bg-slate-50 rounded-md border border-slate-100">
            <span class="text-[10px] font-mono font-bold text-slate-600">${w.worker_id}</span>
            <div class="flex gap-2 items-center">
                <span class="text-[9px] font-black text-yellow-500 bg-yellow-50 px-1.5 py-0.5 rounded">Nv ${w.current_level}</span>
                <span class="text-[9px] font-bold text-blue-600">${w.current_xp} XP</span>
            </div>
        </div>
    `).join('');
}

// --- UTILITIES & EVENTS ---

function updateKPI(id, value) { const el = document.getElementById(id); if (el) el.textContent = value; }

function timeAgo(dateString) {
    if (!dateString) return 'agora';
    const diff = Math.floor((new Date() - new Date(dateString)) / 60000);
    if (diff < 1) return 'agora'; if (diff < 60) return `${diff}m`; return `${Math.floor(diff/60)}h`;
}

function setupFilters() {
    window.setDashboardFilter = (filter) => {
        currentFilter = filter;
        document.querySelectorAll('#btn-filter-all, #btn-filter-hate, #btn-filter-critical').forEach(b => b.classList.remove('active'));
        document.getElementById(`btn-filter-${filter}`)?.classList.add('active');
        renderFeed();
    };
}

function setupSearch() {
    const input = document.getElementById('dashboard-search-input');
    if(input) {
        input.addEventListener('keyup', (e) => {
            const term = e.target.value.toLowerCase();
            if(!term) { fetchComments(); return; }
            const filtered = allComments.filter(c => (c.texto_limpo || '').toLowerCase().includes(term) || (c.autor_username || '').toLowerCase().includes(term));
            renderFeedWithData(filtered);
        });
    }
}

function renderFeedWithData(data) {
    const container = document.getElementById('feed-alertas');
    if (!container) return;
    container.innerHTML = data.map(c => renderThreatCard(c)).join('');
    if (window.lucide) lucide.createIcons();
}

window.auditComment = async (commentId, rotulo) => {
    const res = await fetch('/api/v1/audit/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment_id: commentId, rotulo_correto: rotulo, validado_por: getCurrentUserEmail() })
    });
    if (res.ok) { alert('Auditado! Padrão Ouro atualizado.'); fetchComments(); }
};
