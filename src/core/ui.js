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
            
            // Exibir Skeleton enquanto carrega
            if (state.alertas.length === 0 && state.loading) {
                feedContainer.innerHTML = Array(3).fill(0).map(() => `
                    <div class="post-card">
                        <div class="flex items-center gap-3 mb-4">
                            <div class="skeleton w-10 h-10 rounded-full"></div>
                            <div class="flex-1 space-y-2">
                                <div class="skeleton h-3 w-24 rounded"></div>
                                <div class="skeleton h-2 w-32 rounded"></div>
                            </div>
                        </div>
                        <div class="skeleton h-4 w-full rounded mb-2"></div>
                        <div class="skeleton h-4 w-3/4 rounded"></div>
                    </div>
                `).join('');
                return;
            }

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
                    <img src="${avatarUrl}" alt="${a.username}" width="64" height="64">
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
    let list = state.selectedAlvo 
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.username)) 
        : state.alertas;

    // APLICAR FILTROS DE SIDEBAR
    if (state.dashboardFilter) {
        if (state.dashboardFilter === 'hate') {
            list = list.filter(a => a.is_hate_speech || a.is_hate || ['ODIO_IDENTITARIO', 'VIOLENCIA_GENERO', 'AMEACA'].includes(a.category));
        } else if (state.dashboardFilter === 'critical') {
            list = list.filter(a => a.severidade === 'CRÍTICA' || a.severidade === 'ALTA' || (a.score_risco && a.score_risco > 70));
        }
    }

    // APLICAR BUSCA GLOBAL
    if (state.searchQuery && state.searchQuery.trim() !== '') {
        const q = state.searchQuery.toLowerCase();
        list = list.filter(a => 
            (a.texto_bruto && a.texto_bruto.toLowerCase().includes(q)) || 
            (a.autor_username && a.autor_username.toLowerCase().includes(q)) ||
            (a.candidato_id && a.candidato_id.toLowerCase().includes(q))
        );
    }

    // ALGORITMO DE REDE SOCIAL: Se não houver filtro ativo e nem busca, mistura agressivamente
    if (!state.selectedAlvo && (!state.dashboardFilter || state.dashboardFilter === 'all') && !state.searchQuery) {
        // Shuffle determinístico por data mas com diversidade de alvos
        list = [...list].sort(() => Math.random() - 0.5);
    }

    if (!list.length && state.currentPage === 1) {
        container.innerHTML = `<div class="p-12 text-center opacity-30 text-xs font-mono tracking-widest uppercase">Nenhum sinal detectado</div>`;
        return;
    }

    let html = "";
    list.forEach((alerta, index) => {
        html += buildPostCard(alerta);
        
        // MONETIZAÇÃO ADSENSE: Injetar anúncio a cada 5 posts
        if ((index + 1) % 5 === 0) {
            html += `
                <div class="ad-slot bg-slate-50 border-y border-slate-100 p-6 mb-4 text-center overflow-hidden">
                    <span class="text-[8px] text-slate-400 block mb-3 font-bold uppercase tracking-widest">Informativo Patrocinado</span>
                    <!-- ADSENSE FEED UNIT -->
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-format="fluid"
                         data-ad-layout-key="-fb+5w+4e-db+86"
                         data-ad-client="ca-pub-1827611269042960"
                         data-ad-slot="FEED_UNIT_V20"></ins>
                    <script>(window.adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            `;
        }
    });

    if (state.currentPage === 1) {
        container.innerHTML = html;
    } else {
        container.insertAdjacentHTML('beforeend', html);
    }
}

function buildPostCard(alerta) {
    const agressor = alerta.autor_username || 'anônimo';
    const targetId = alerta.candidato_id || 'alvo';
    const targetData = state.data.find(a => a.username === targetId) || { username: targetId };
    
    const dateStr = new Date(alerta.data_coleta).toLocaleTimeString('pt-BR');
    const severity = alerta.severidade || 'INFO';
    const plataforma = (alerta.plataforma || 'instagram').toLowerCase();
    const platLabel = plataforma === 'youtube' ? 'YT' : 'IG';
    const platColor = plataforma === 'youtube' ? 'bg-red-500' : 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500';
    
    // LOGICA DE MONETIZAÇÃO: Se não for PRO, borra o agressor
    const isLocked = !planService.canAccess('identities');
    const displayedUser = isLocked ? 'agressor_protegido' : `@${agressor.replace('@','')}`;
    
    const avatarAgressor = isLocked 
        ? 'https://ui-avatars.com/api/?name=?&background=334155&color=fff'
        : `https://ui-avatars.com/api/?name=${agressor}&background=random&color=fff&size=64`;
        
    const avatarTarget = targetData.avatar_url || `https://ui-avatars.com/api/?name=${targetId}&background=0D8ABC&color=fff`;
    
    return `
        <article class="post-card animate-in ${isLocked ? 'is-locked' : ''} relative mb-4">
            <div class="absolute top-3 left-1/2 -translate-x-1/2 z-20">
                <span class="px-2 py-0.5 ${platColor} text-white rounded-full text-[7px] font-black tracking-tighter shadow-sm opacity-80">
                    ${platLabel}
                </span>
            </div>

            <div class="post-header items-start">
                <div class="flex items-center gap-2">
                    <div class="post-avatar relative">
                        <img src="${avatarAgressor}" alt="Agressor" class="w-8 h-8 rounded-full ${isLocked ? 'blur-[4px]' : ''}" loading="lazy">
                        <div class="absolute -right-1 -bottom-1 bg-white rounded-full p-0.5 shadow-sm">
                            <i data-lucide="zap" class="w-2.5 h-2.5 text-yellow-500 fill-yellow-500"></i>
                        </div>
                    </div>
                    
                    <div class="flex flex-col">
                        <div class="post-username text-[11px] font-bold ${isLocked ? 'blur-[5px] select-none' : ''}">${displayedUser}</div>
                        <div class="text-[9px] text-slate-400">${dateStr}</div>
                    </div>
                </div>

                <div class="flex-1 flex justify-center items-center px-2">
                    <div class="h-px bg-slate-50 flex-1 relative">
                         <i data-lucide="chevron-right" class="absolute right-0 -top-[7px] w-3 h-3 text-slate-100"></i>
                    </div>
                </div>

                <div class="flex items-center gap-2 text-right">
                    <div class="flex flex-col items-end">
                        <div class="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-[9px] font-black uppercase tracking-tighter">
                            @${targetId}
                        </div>
                        <div class="text-[8px] font-bold text-slate-300 uppercase">${targetData.partido || 'ALVO'}</div>
                    </div>
                    <div class="w-8 h-8 rounded-full overflow-hidden border border-slate-100 shadow-sm">
                        <img src="${avatarTarget}" alt="Alvo" class="w-full h-full object-cover">
                    </div>
                </div>
            </div>

            <div class="post-content mt-3 text-[12px] leading-relaxed text-slate-600 font-medium italic">
                "${alerta.texto_bruto || 'Sem conteúdo'}"
            </div>
            
            ${isLocked ? `
                <div class="mt-4 pt-3 border-t border-slate-50 flex items-center justify-between opacity-80 hover:opacity-100 transition-opacity">
                    <div class="flex items-center gap-2">
                        <i data-lucide="lock" class="w-3 h-3 text-slate-300"></i>
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Identidade sob sigilo</span>
                    </div>
                    <button class="text-[10px] font-black text-blue-500 hover:text-blue-600 transition-colors uppercase tracking-widest flex items-center gap-1" onclick="window.unlockIntel('${alerta.id}')">
                        Desbloquear <i data-lucide="chevron-right" class="w-3 h-3"></i>
                    </button>
                </div>
            ` : `
                <div class="flex gap-4 mt-4 pt-2 border-t border-slate-50">
                    <button class="flex items-center gap-1.5 text-[9px] font-bold text-slate-300 hover:text-blue-500 transition-colors" onclick="window.toggleTriage('${alerta.id}')"><i data-lucide="shield-alert" class="w-3 h-3"></i> Periciar</button>
                    <button class="flex items-center gap-1.5 text-[9px] font-bold text-slate-300 hover:text-red-500 transition-colors" onclick="window.markFalsePositive('${alerta.id}')"><i data-lucide="thumbs-down" class="w-3 h-3"></i> Descartar</button>
                    <div class="ml-auto flex items-center gap-2">
                        <span class="px-1.5 py-0.5 bg-slate-50 text-slate-400 rounded text-[8px] font-bold uppercase">${severity}</span>
                        <button class="p-1 text-slate-200 hover:text-slate-400"><i data-lucide="share-2" class="w-3 h-3"></i></button>
                    </div>
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
    if (!container || !state.data) return;
    
    // Otimização de DOM: Renderizar apenas os Top 15 alvos com maior volume de alertas
    const topAlvos = [...state.data]
        .sort((a, b) => (b.comentarios_odio_count || 0) - (a.comentarios_odio_count || 0))
        .slice(0, 15);

    container.innerHTML = topAlvos.map((alvo, index) => {
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        const avatarUrl = alvo.avatar_url || `https://ui-avatars.com/api/?name=${alvo.username}&background=0D8ABC&color=fff`;
        
        return `
            <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''} p-3 rounded-xl border border-transparent hover:bg-white hover:shadow-sm cursor-pointer transition-all flex items-center gap-3">
                <div class="monitor-avatar w-10 h-10 border-2 ${isActive ? 'border-blue-500' : 'border-slate-100'}">
                    <img src="${avatarUrl}" alt="${alvo.username}" loading="lazy" width="40" height="40">
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
    try {
        const navItems = document.querySelectorAll('.nav-item');
        if (!navItems) return;
        
        navItems.forEach(nav => {
            const href = nav.getAttribute('href');
            if (href && href.startsWith('#')) {
                const view = href.substring(1);
                nav.classList.toggle('active', state.view === view);
            } else {
                // Para botões sem href (filtros), usamos o ID ou a lógica de estado
                const navId = nav.getAttribute('id');
                if (navId && state.dashboardFilter) {
                    nav.classList.toggle('active', navId.includes(state.dashboardFilter));
                }
            }
        });
    } catch (err) {
        console.warn('[UI] Sidebar update skipped:', err.message);
    }
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

// Outras views básicas e Gated
function renderNetworkIntelligence() { 
    document.getElementById('view-networks').innerHTML = `
        <div class="p-12 text-center bg-white border border-slate-200 rounded-xl animate-in mt-4 flex flex-col items-center justify-center" style="min-height: 60vh;">
            <div class="w-16 h-16 bg-blue-50 text-blue-500 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
                <i data-lucide="network" class="w-8 h-8"></i>
            </div>
            <h3 class="text-xl font-black text-slate-800 mb-2">Mapeamento de Redes Coordenadas</h3>
            <p class="text-sm text-slate-500 max-w-md mx-auto mb-8">Esta funcionalidade requer calibração dos motores de processamento em grafo para gerar os clusters visuais. Módulo operando em background.</p>
            <button class="px-6 py-3 bg-slate-900 text-white rounded-lg text-[11px] font-black uppercase tracking-widest shadow-lg shadow-slate-900/20 opacity-50 cursor-not-allowed">
                Processamento Pendente
            </button>
        </div>`; 
}

function renderDossieGrid() { 
    document.getElementById('view-dossie').innerHTML = `
        <div class="p-12 text-center bg-white border border-slate-200 rounded-xl animate-in mt-4 flex flex-col items-center justify-center" style="min-height: 60vh;">
            <div class="w-16 h-16 bg-slate-50 text-slate-400 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
                <i data-lucide="fingerprint" class="w-8 h-8"></i>
            </div>
            <h3 class="text-xl font-black text-slate-800 mb-2">Repositório de Dossiês Forenses</h3>
            <p class="text-sm text-slate-500 max-w-md mx-auto mb-8">O acesso ao banco de PDF gerados (PASA v16.4) é restrito a administradores com verificação TOTP ativa. Solicite a chave de montagem.</p>
            <button class="px-6 py-3 bg-blue-600 text-white rounded-lg text-[11px] font-black uppercase tracking-widest shadow-lg shadow-blue-600/20 hover:bg-blue-700 transition-colors">
                Verificar Chave Local
            </button>
        </div>`; 
}

function renderGeopolitica() { 
    document.getElementById('view-map').innerHTML = `
        <div class="p-12 text-center bg-slate-950 border border-cyan-900/30 rounded-xl animate-in mt-4 flex flex-col items-center justify-center overflow-hidden relative" style="min-height: 60vh;">
            <div class="absolute inset-0 bg-gradient-to-tr from-cyan-900/10 to-blue-900/10"></div>
            <div class="w-16 h-16 bg-cyan-900/30 text-cyan-400 rounded-full flex items-center justify-center mb-6 border border-cyan-500/20 relative z-10">
                <i data-lucide="globe" class="w-8 h-8"></i>
            </div>
            <h3 class="text-xl font-black text-white mb-2 relative z-10">Geopolítica UF - Mapa Integrado</h3>
            <p class="text-sm text-cyan-200/60 max-w-md mx-auto mb-8 relative z-10">Conexão com servidor D3.js não estabelecida. O mapeamento vetorial requer download de topologia de estado.</p>
            <div class="h-2 w-48 bg-slate-900 rounded-full overflow-hidden relative z-10">
                <div class="h-full bg-cyan-500 w-1/3 animate-pulse"></div>
            </div>
        </div>`; 
}

function renderDirectory() { 
    document.getElementById('view-directory').innerHTML = `
        <div class="p-12 text-center bg-white border border-slate-200 rounded-xl animate-in mt-4 flex flex-col items-center justify-center" style="min-height: 60vh;">
            <div class="w-16 h-16 bg-slate-50 text-slate-400 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
                <i data-lucide="users" class="w-8 h-8"></i>
            </div>
            <h3 class="text-xl font-black text-slate-800 mb-2">Diretório Global de Perfis</h3>
            <p class="text-sm text-slate-500 max-w-md mx-auto mb-8">Mais de ${state.data?.length || '1000'} perfis mapeados no Supabase. O diretório expandido requer tokenização STN para exibição.</p>
        </div>`; 
}
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
