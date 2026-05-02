import { state, setViewState, setNetworkView } from './state.js';
import { dataService, planService } from '../services/dataService.js';
import { authService } from '../services/authService.js';

export function renderAll() {
    try {
        updateSidebarActive();
        renderKPIs();
        renderTopbar();
        renderSTN();

        const views = ['monitor', 'networks', 'dossie', 'map', 'directory'];
        views.forEach((view) => {
            const el = document.getElementById(`view-${view}`);
            if (el) {
                el.classList.toggle('active-view', state.view === view);
            }
        });

        if (state.view === 'monitor') {
            renderMonitorLayout();
        } else if (state.view === 'networks') {
            renderNetworkIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        } else if (state.view === 'directory') {
            renderDirectory();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Render error:', e);
    }
}

function renderMonitorLayout() {
    const feedContainer = document.getElementById('feed-alertas');
    const priorityContainer = document.getElementById('chartMain');
    
    if (feedContainer) {
        if (state.selectedAlvo) {
            renderCandidateProfile(feedContainer);
        } else {
            renderOnboarding(feedContainer);
        }
        renderAlertasFeed(feedContainer);
    }
    if (priorityContainer) renderMonitorImpacto(priorityContainer);
}

function renderOnboarding(container) {
    container.innerHTML = `
        <div class="p-8 bg-white border-b border-slate-200 animate-in">
            <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Centro de Comando</span>
            <h3 class="text-xl font-extrabold mt-2 mb-4">Bem-vindo ao Sentinela</h3>
            <p class="text-sm text-slate-500 leading-relaxed max-w-md">
                Monitoramento forense em tempo real. Selecione um perfil na barra lateral de risco para detalhar as agressões.
            </p>
        </div>
    `;
}

function renderCandidateProfile(container) {
    const a = state.selectedAlvo;
    container.innerHTML = `
        <div class="p-6 bg-white border-b border-slate-200 animate-in">
            <div class="flex items-center gap-4 mb-6">
                <div class="w-16 h-16 rounded-2xl bg-blue-500 flex items-center justify-center text-white text-2xl font-black shadow-lg shadow-blue-200">${a.username.charAt(0).toUpperCase()}</div>
                <div>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">${a.estado || 'BR'} • ${a.partido || 'Sem Partido'}</span>
                    <h2 class="text-2xl font-black">@${a.username}</h2>
                </div>
                <button class="ml-auto p-2 hover:bg-slate-50 rounded-full transition-colors" onclick="window.setFiltroAlvo(null)"><i data-lucide="x" class="w-5 h-5 text-slate-400"></i></button>
            </div>
            <p class="text-sm text-slate-600 mb-6 leading-relaxed">${a.bio || 'Sem biografia disponível.'}</p>
            <div class="grid grid-cols-4 gap-4">
                <div class="p-3 bg-slate-50 rounded-xl">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase">Seguidores</span>
                    <strong class="text-sm font-black">${formatCompactNumber(a.seguidores || 0)}</strong>
                </div>
                <div class="p-3 bg-slate-50 rounded-xl">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase">Amostra</span>
                    <strong class="text-sm font-black">${a.comentarios_totales_count || 0}</strong>
                </div>
                <div class="p-3 bg-red-50 rounded-xl">
                    <span class="block text-[9px] font-bold text-red-400 uppercase">Alertas</span>
                    <strong class="text-sm font-black text-red-600">${a.comentarios_odio_count || 0}</strong>
                </div>
                <div class="p-3 bg-slate-50 rounded-xl">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase">Risco</span>
                    <strong class="text-sm font-black" style="color:${a.color || 'var(--danger)'}">${a.score_risco}%</strong>
                </div>
            </div>
        </div>
    `;
}

function renderAlertasFeed(container) {
    const list = state.selectedAlvo 
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.username)) 
        : state.alertas;

    if (!list.length) {
        container.innerHTML += `<div class="p-12 text-center opacity-30 text-xs font-mono tracking-widest uppercase">Nenhum sinal detectado</div>`;
        return;
    }

    const html = list.map((alerta) => buildPostCard(alerta)).join('');
    // Se for o render inicial do monitor, substitui. Se for append, o app.js trata.
    if (state.currentPage === 1 && !state.isLoading) {
        container.innerHTML += html;
    }
}

function buildPostCard(alerta) {
    const agressor = alerta.autor_username || 'anônimo';
    const target = alerta.candidato_id || 'alvo';
    const dateStr = new Date(alerta.data_coleta).toLocaleTimeString('pt-BR');
    const severity = alerta.severidade || 'INFO';
    const plataforma = (alerta.plataforma || 'instagram').toLowerCase();
    
    return `
        <article class="post-card animate-in">
            <div class="post-header">
                <div class="post-avatar">${agressor.substring(0,2).toUpperCase()}</div>
                <div class="post-user-info">
                    <div class="post-username">@${agressor.replace('@','')}</div>
                    <div class="post-meta">➔ @${target} • ${dateStr}</div>
                </div>
                <div class="flex items-center gap-2">
                    <span class="px-1.5 py-0.5 rounded bg-slate-100 text-[9px] font-bold text-slate-500">${plataforma.toUpperCase()}</span>
                    <div class="w-2 h-2 rounded-full is-${severity.toLowerCase()}" style="background:${severity === 'CRÍTICO' ? 'var(--danger)' : 'var(--accent)'}; box-shadow: 0 0 6px rgba(0,0,0,0.1)"></div>
                </div>
            </div>
            <div class="post-content">"${alerta.texto_bruto || 'Sem conteúdo'}"</div>
            <div class="flex gap-6 mt-3 pt-3 border-t border-slate-50">
                <button class="action-btn text-slate-400 hover:text-blue-500" onclick="window.toggleTriage('${alerta.id}')"><i data-lucide="shield-alert" class="w-4 h-4"></i> <span class="text-[10px]">Analisar</span></button>
                <button class="action-btn text-slate-400 hover:text-red-500" onclick="window.markFalsePositive('${alerta.id}')"><i data-lucide="thumbs-down" class="w-4 h-4"></i> <span class="text-[10px]">Falso Positivo</span></button>
            </div>
            <div id="triage-actions-${alerta.id}" class="mt-3 p-3 bg-slate-50 rounded-lg text-[10px] hidden font-mono">
                <strong class="text-slate-400">Classificação IA:</strong> ${String(alerta.categoria_ia || 'NEUTRO').replace(/_/g, ' ')}<br>
                <strong class="text-slate-400">Confiança:</strong> ${(alerta.confianza_ia * 100).toFixed(1)}%
            </div>
        </article>
    `;
}

function renderMonitorImpacto(container) {
    if (!container) return;
    container.innerHTML = state.data.map((alvo, index) => {
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        return `
            <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''} p-3 rounded-xl border border-transparent hover:bg-slate-50 cursor-pointer transition-all">
                <div class="flex justify-between items-center mb-2">
                    <strong class="text-sm font-black text-slate-800">@${alvo.username}</strong>
                    <span class="text-[10px] font-black px-2 py-0.5 rounded-full bg-red-100 text-red-600">${alvo.comentarios_odio_count}</span>
                </div>
                <div class="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                    <div class="h-full" style="width:${alvo.score_risco}%; background:${alvo.color || 'var(--danger)'}"></div>
                </div>
                <div class="flex justify-between mt-2 text-[9px] font-bold text-slate-400 uppercase tracking-tighter">
                    <span>Risco: ${alvo.score_risco}%</span>
                    <span>Prio ${index + 1}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderKPIs() {
    if (!state.summary) return;
    const s = state.summary;
    const update = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    };
    update('kpi-monitorados', s.total_monitorados);
    update('kpi-hate', s.total_alertas);
    update('kpi-total', s.total_amostra.toLocaleString());
    update('kpi-res', s.resiliencia + '%');
}

function renderSTN() {
    const el = document.getElementById('stn-balance');
    if (el) el.innerText = `${state.stn_tokens} STN`;
}

function updateSidebarActive() {
    document.querySelectorAll('.nav-item').forEach(nav => {
        const href = nav.getAttribute('href').substring(1);
        nav.classList.toggle('active', state.view === href);
    });
}

function formatCompactNumber(number) {
    if (number < 1000) return number;
    if (number < 1000000) return (number / 1000).toFixed(1) + 'K';
    return (number / 1000000).toFixed(1) + 'M';
}

// --- ROLAGEM INFINITA ---
export function initInfiniteScroll() {
    const sentinel = document.getElementById('scroll-sentinel');
    if (!sentinel) return;

    const observer = new IntersectionObserver(async (entries) => {
        if (entries[0].isIntersecting && !state.isLoading && state.view === 'monitor') {
            state.isLoading = true;
            const spinner = document.getElementById('loading-spinner');
            if (spinner) spinner.style.display = 'flex';
            
            try {
                const nextPage = state.currentPage + 1;
                const newAlertas = await dataService.getAlerts(20, nextPage);
                
                if (newAlertas && newAlertas.length > 0) {
                    state.currentPage = nextPage;
                    state.alertas = [...state.alertas, ...newAlertas];
                    const feed = document.getElementById('feed-alertas');
                    if (feed) feed.insertAdjacentHTML('beforeend', newAlertas.map(alerta => buildPostCard(alerta)).join(''));
                }
            } catch (e) {
                console.error('[InfiniteScroll] Error:', e);
            } finally {
                state.isLoading = false;
                if (spinner) spinner.style.display = 'none';
                if (window.lucide) lucide.createIcons();
            }
        }
    }, { rootMargin: '400px' });

    observer.observe(sentinel);
}

// Placeholder functions for other views
function renderNetworkIntelligence() { console.log('Network view active'); }
function renderDossieGrid() { console.log('Dossie view active'); }
function renderGeopolitica() { console.log('Map view active'); }
function renderDirectory() { console.log('Directory view active'); }
function renderPasaTemporalChart() { console.log('Chart view active'); }

window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find(item => item.username === id) : null;
    state.currentPage = 1; // Reseta scroll ao mudar alvo
    renderAll();
};

window.toggleTriage = (id) => {
    const el = document.getElementById(`triage-actions-${id}`);
    if (el) el.classList.toggle('hidden');
};

window.setViewState = setViewState;
window.setNetworkView = setNetworkView;
window.renderAll = renderAll;
