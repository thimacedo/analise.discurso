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
        if (state.currentPage === 1) {
            feedContainer.innerHTML = '';
            if (state.selectedAlvo) {
                renderCandidateProfile(feedContainer);
            } else {
                renderOnboarding(feedContainer);
            }
        }
        renderAlertasFeed(feedContainer);
    }
    if (priorityContainer) renderMonitorImpacto(priorityContainer);
}

function renderOnboarding(container) {
    container.innerHTML = `
        <div class="p-8 bg-white border border-slate-200 rounded-xl mb-4 animate-in">
            <span class="text-[10px] font-black uppercase tracking-widest text-blue-500">Inteligência Estratégica</span>
            <h3 class="text-xl font-extrabold mt-2 mb-4">Monitoramento Diamond</h3>
            <p class="text-sm text-slate-500 leading-relaxed">
                Bem-vindo ao Sentinela v20.2. Analisando fluxos de desinformação e hostilidade em tempo real. Selecione um alvo para iniciar a perícia.
            </p>
        </div>
    `;
}

function renderCandidateProfile(container) {
    const a = state.selectedAlvo;
    const avatarUrl = a.avatar_url || `https://ui-avatars.com/api/?name=${a.username}&background=0D8ABC&color=fff`;
    
    container.innerHTML = `
        <div class="p-6 bg-white border border-slate-200 rounded-xl mb-6 animate-in">
            <div class="flex items-center gap-4 mb-6">
                <div class="monitor-avatar w-16 h-16 shadow-xl shadow-blue-100">
                    <img src="${avatarUrl}" alt="${a.username}">
                </div>
                <div>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">${a.estado || 'BR'} • ${a.partido || 'Sem Partido'}</span>
                    <h2 class="text-2xl font-black">@${a.username}</h2>
                </div>
                <button class="ml-auto p-2 hover:bg-slate-50 rounded-full transition-colors" onclick="window.setFiltroAlvo(null)"><i data-lucide="x" class="w-5 h-5 text-slate-400"></i></button>
            </div>
            <div class="grid grid-cols-4 gap-3">
                <div class="p-3 bg-slate-50 rounded-lg text-center">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase mb-1">Seguidores</span>
                    <strong class="text-xs font-black">${formatCompactNumber(a.seguidores || 0)}</strong>
                </div>
                <div class="p-3 bg-slate-50 rounded-lg text-center">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase mb-1">Alertas</span>
                    <strong class="text-xs font-black text-red-600">${a.comentarios_odio_count || 0}</strong>
                </div>
                <div class="p-3 bg-slate-50 rounded-lg text-center">
                    <span class="block text-[9px] font-bold text-slate-400 uppercase mb-1">Risco</span>
                    <strong class="text-xs font-black" style="color:${a.color || 'var(--danger)'}">${a.score_risco}%</strong>
                </div>
                <div class="p-3 bg-blue-50 rounded-lg text-center cursor-pointer hover:bg-blue-100 transition-colors" onclick="window.inspectTarget('${a.username}')">
                    <span class="block text-[9px] font-bold text-blue-600 uppercase mb-1">Dossiê</span>
                    <i data-lucide="external-link" class="w-3 h-3 m-auto text-blue-600"></i>
                </div>
            </div>
        </div>
    `;
}

function renderAlertasFeed(container) {
    const list = state.selectedAlvo 
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.username)) 
        : state.alertas;

    if (!list.length && state.currentPage === 1) {
        container.innerHTML += `<div class="p-12 text-center opacity-30 text-xs font-mono tracking-widest uppercase">Nenhum sinal detectado</div>`;
        return;
    }

    const html = list.map((alerta) => buildPostCard(alerta)).join('');
    if (state.currentPage === 1) {
        container.insertAdjacentHTML('beforeend', html);
    }
}

function buildPostCard(alerta) {
    const agressor = alerta.autor_username || 'anônimo';
    const target = alerta.candidato_id || 'alvo';
    const dateStr = new Date(alerta.data_coleta).toLocaleTimeString('pt-BR');
    const severity = alerta.severidade || 'INFO';
    const plataforma = (alerta.plataforma || 'instagram').toLowerCase();
    
    // LOGICA DE MONETIZAÇÃO: Se não for PRO, borra o agressor
    const isLocked = !planService.canAccess('identities');
    const displayedUser = isLocked ? 'agressor_protegido' : `@${agressor.replace('@','')}`;
    const avatarUrl = isLocked 
        ? 'https://ui-avatars.com/api/?name=?&background=334155&color=fff'
        : `https://ui-avatars.com/api/?name=${agressor}&background=random&color=fff&size=64`;
    
    return `
        <article class="post-card animate-in ${isLocked ? 'is-locked' : ''}">
            <div class="post-header">
                <div class="post-avatar">
                    <img src="${avatarUrl}" alt="Avatar" class="${isLocked ? 'blur-[4px]' : ''}">
                </div>
                <div class="post-user-info">
                    <div class="post-username ${isLocked ? 'blur-[5px] select-none' : ''}">${displayedUser}</div>
                    <div class="post-meta">➔ @${target} • ${dateStr}</div>
                </div>
                <span class="severity-pill is-${severity.toLowerCase()}">${severity}</span>
            </div>
            <div class="post-content">
                "${alerta.texto_bruto || 'Sem conteúdo'}"
            </div>
            
            ${isLocked ? `
                <div class="mt-4 p-4 bg-slate-900 border border-cyan-900/30 rounded-xl flex items-center justify-between shadow-inner">
                    <div>
                        <span class="block text-[10px] font-black text-cyan-400 uppercase tracking-widest">Ruptura Necessária</span>
                        <p class="text-[11px] text-slate-400">Alvo com blindagem ativa. Requer pulso de varredura.</p>
                    </div>
                    <button class="bg-cyan-600 text-white px-4 py-2 rounded-lg text-[10px] font-black shadow-lg shadow-cyan-900/20 hover:bg-cyan-500 transition-all uppercase tracking-tighter" onclick="window.unlockIntel('${alerta.id}')">
                        Injetar Carga
                    </button>
                </div>
            ` : `
                <div class="flex gap-6 mt-4 pt-3 border-t border-slate-50">
                    <button class="action-btn" onclick="window.toggleTriage('${alerta.id}')"><i data-lucide="shield-alert" class="w-4 h-4"></i> Analisar</button>
                    <button class="action-btn" onclick="window.markFalsePositive('${alerta.id}')"><i data-lucide="thumbs-down" class="w-4 h-4"></i> Falso</button>
                    <button class="action-btn ml-auto"><i data-lucide="share-2" class="w-4 h-4"></i></button>
                </div>
            `}
        </article>
    `;
}

window.unlockIntel = async (id) => {
    if (state.stn_tokens < 10) {
        alert("MUNIÇÃO INSUFICIENTE! Adquira mais tokens STN para continuar a perícia.");
        window.location.hash = 'pricing';
        return;
    }
    
    if (confirm("Gastar 10 STN para revelar a identidade do agressor?")) {
        // Aqui entraria a chamada de API real
        state.stn_tokens -= 10;
        alert("IDENTIDADE REVELADA! (Simulação)");
        renderAll();
    }
};

function renderMonitorImpacto(container) {
    if (!container) return;
    container.innerHTML = state.data.map((alvo, index) => {
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        const avatarUrl = alvo.avatar_url || `https://ui-avatars.com/api/?name=${alvo.username}&background=0D8ABC&color=fff`;
        
        return `
            <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''} p-3 rounded-xl border border-transparent hover:bg-white hover:shadow-sm cursor-pointer transition-all flex items-center gap-3">
                <div class="monitor-avatar w-10 h-10 border-2 ${isActive ? 'border-blue-500' : 'border-slate-100'}">
                    <img src="${avatarUrl}" alt="${alvo.username}">
                </div>
                <div class="flex-1">
                    <div class="flex justify-between items-center mb-1">
                        <strong class="text-xs font-black text-slate-800">@${alvo.username}</strong>
                        <span class="text-[9px] font-black px-1.5 py-0.5 rounded bg-red-50 text-red-500">${alvo.comentarios_odio_count}</span>
                    </div>
                    <div class="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                        <div class="h-full" style="width:${alvo.score_risco}%; background:${alvo.color || 'var(--danger)'}"></div>
                    </div>
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
    const mainContainer = document.querySelector('.main-feed-container');
    const sentinel = document.getElementById('scroll-sentinel');
    if (!sentinel || !mainContainer) return;

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
                    if (feed) {
                        const html = newAlertas.map(alerta => buildPostCard(alerta)).join('');
                        feed.insertAdjacentHTML('beforeend', html);
                    }
                }
            } catch (e) {
                console.error('[InfiniteScroll] Error:', e);
            } finally {
                state.isLoading = false;
                if (spinner) spinner.style.display = 'none';
                if (window.lucide) lucide.createIcons();
            }
        }
    }, { root: mainContainer, rootMargin: '400px' });

    observer.observe(sentinel);
}

// Outras views básicas para não quebrar o dashboard
function renderNetworkIntelligence() { document.getElementById('view-networks').innerHTML = '<div class="p-8 text-center text-slate-400">Mapeamento de Redes Coordenadas v20.2</div>'; }
function renderDossieGrid() { document.getElementById('view-dossie').innerHTML = '<div class="p-8 text-center text-slate-400">Repositório de Dossiês Forenses</div>'; }
function renderGeopolitica() { document.getElementById('view-map').innerHTML = '<div class="p-8 text-center text-slate-400">Geopolítica UF - Mapa Integrado</div>'; }
function renderDirectory() { document.getElementById('view-directory').innerHTML = '<div class="p-8 text-center text-slate-400">Diretório Global de Perfis</div>'; }
function renderPasaTemporalChart() { /* Implementação futura D3 */ }
function renderTopbar() { /* Implementação futura */ }

window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find(item => item.username === id) : null;
    state.currentPage = 1;
    state.alertas = []; // Limpa feed para recarregar
    refreshAndRender();
};

async function refreshAndRender() {
    const alerts = await dataService.getAlerts(20, 1);
    state.alertas = alerts;
    renderAll();
}

window.toggleTriage = (id) => {
    const el = document.getElementById(`triage-actions-${id}`);
    if (el) el.classList.toggle('hidden');
};

window.inspectTarget = (username) => {
    const alvo = state.data.find(item => item.username === username);
    if (alvo) {
        state.selectedAlvo = alvo;
        state.view = 'monitor';
        window.location.hash = 'monitor';
        refreshAndRender();
    }
};

window.forceRefresh = () => window.location.reload();
window.setNetworkView = (view) => { state.networkView = view; state.view = 'networks'; renderAll(); };
