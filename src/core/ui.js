import { state, setViewState, setNetworkView } from './state.js';
import { dataService, planService } from '../services/dataService.js';
import { authService } from '../services/authService.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        updateSidebarActive();
        renderKPIs();
        renderTopbar();
        renderSTN();

        const views = ['monitor', 'networks', 'dossie', 'map', 'directory', 'ads'];
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
        } else if (state.view === 'ads') {
            renderAds();
        } else if (state.view === 'map') {
            renderGeopolitica();
        } else if (state.view === 'directory') {
            renderDirectory();
        }

        if (window.lucide) lucide.createIcons();
        initSwipeGestures(); // Blindagem: garantindo listeners pós-render
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
                <div class="p-3 bg-blue-50 rounded-lg text-center cursor-pointer hover:bg-blue-100 transition-colors" onclick="window.generateTargetDossier('${a.username}')">
                    <span class="block text-[9px] font-bold text-blue-600 uppercase mb-1">Relatório</span>
                    <i data-lucide="file-down" class="w-3 h-3 m-auto text-blue-600"></i>
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

    // PAGINAÇÃO ESTRITA NO FRONTEND (Dopamine Flow)
    // Corta a lista para mostrar apenas a quantidade da página atual, evitando travamentos
    const maxItems = state.currentPage * 20;
    const paginatedList = list.slice(0, maxItems);

    if (!paginatedList.length) {
        container.innerHTML = `<div class="p-12 text-center opacity-30 text-xs font-mono tracking-widest uppercase">Nenhum sinal detectado</div>`;
        return;
    }

    let html = "";
    paginatedList.forEach((alerta, index) => {
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

    // Como o paginatedList contém TODOS os itens até a página atual,
    // sempre atualizamos o innerHTML completamente para evitar duplicação em re-renders
    container.innerHTML = html;
}

function buildPostCard(alerta) {
    const agressor = alerta.autor_username || 'anônimo';
    const targetId = alerta.candidato_id || 'alvo';
    const targetData = state.data.find(a => a.username === targetId) || { username: targetId, nome_completo: 'Alvo não mapeado' };
    
    const dateStr = new Date(alerta.data_coleta).toLocaleTimeString('pt-BR');
    const severity = alerta.severidade || 'INFO';
    const platLabel = 'IG';
    const platColor = 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500';
    
    const isLocked = !planService.canAccess('identities');
    const displayedUser = isLocked ? 'agressor_protegido' : `@${agressor.replace('@','')}`;
    
    const avatarAgressor = isLocked 
        ? 'https://ui-avatars.com/api/?name=?&background=334155&color=fff'
        : `https://unavatar.io/instagram/${agressor.replace('@','')}`;
        
    const avatarTarget = `https://unavatar.io/instagram/${targetId}`;
    
    return `
        <div class="post-card-container relative mb-6 rounded-3xl overflow-hidden bg-slate-900" data-alerta-id="${alerta.id}">
            <div class="absolute inset-y-0 right-0 w-1/3 flex items-center justify-end pr-8">
                <div class="flex flex-col items-center justify-center opacity-60 text-white">
                    <i data-lucide="archive" class="w-6 h-6 mb-1"></i>
                    <span class="text-[10px] font-black uppercase tracking-widest">Arquivar</span>
                </div>
            </div>

            <article class="post-card-surface animate-in ${isLocked ? 'is-locked' : ''} relative bg-white border border-slate-200 rounded-3xl p-6 shadow-sm z-10 w-full h-full transition-all hover:shadow-xl hover:-translate-y-1">
                <div class="absolute top-4 left-6 z-20">
                    <span class="px-3 py-1 bg-slate-900 text-white rounded-full text-[9px] font-black tracking-widest shadow-sm uppercase border border-slate-800">
                        Suspeito
                    </span>
                </div>

                <div class="post-header flex justify-between items-center gap-4 mb-6">
                    <div class="flex items-center gap-4 mt-2">
                        <div class="post-avatar relative">
                            <img src="${avatarAgressor}" alt="Suspeito" class="w-12 h-12 rounded-2xl ${isLocked ? 'blur-[4px] select-none pointer-events-none' : ''} object-cover border border-slate-100 shadow-sm" loading="lazy" onerror="this.src='https://ui-avatars.com/api/?name=${agressor}&background=random&color=fff'">
                            <div class="absolute -right-2 -bottom-2 bg-white rounded-full p-1.5 shadow-md border border-slate-50">
                                <i data-lucide="user" class="w-3 h-3 text-slate-500"></i>
                            </div>
                        </div>
                        
                        <div class="flex flex-col">
                            <div class="post-username text-[13px] font-black text-slate-900 ${isLocked ? 'blur-[6px] select-none pointer-events-none opacity-50' : ''}">${displayedUser}</div>
                            <div class="text-[10px] font-bold text-slate-400 flex items-center gap-1">
                                <i data-lucide="clock" class="w-2.5 h-2.5"></i> ${dateStr}
                            </div>
                        </div>
                    </div>

                    <div class="flex items-center gap-4 text-right">
                        <div class="flex flex-col items-end min-w-0 max-w-[120px]">
                            <div class="px-2 py-1 bg-blue-50 text-blue-800 rounded-lg text-[10px] font-black uppercase tracking-tighter truncate w-full">
                                @${targetId}
                            </div>
                            <div class="text-[9px] font-black text-slate-700 uppercase truncate w-full mt-1">${targetData.nome_completo || 'Alvo Monitorado'}</div>
                        </div>
                        <div class="w-12 h-12 rounded-2xl overflow-hidden border-2 border-slate-50 shadow-sm transition-transform group-hover:scale-110">
                            <img src="${avatarTarget}" alt="Alvo" class="w-full h-full object-cover" onerror="this.src='https://ui-avatars.com/api/?name=${targetId}&background=0D8ABC&color=fff'">
                        </div>
                    </div>
                </div>

                <div class="post-content mt-4 p-5 bg-slate-50 rounded-2xl text-[15px] leading-relaxed text-slate-800 font-medium border-l-8 border-blue-500 shadow-inner italic">
                    "${(alerta.texto_bruto && alerta.texto_bruto.trim()) || (alerta.text && alerta.text.trim()) || alerta.comentario || 'Conteúdo indisponível para esta perícia manual.'}"
                </div>
                
                ${isLocked ? `
                    <div class="mt-6 pt-5 border-t border-slate-100 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center border border-amber-100">
                                <i data-lucide="lock" class="w-4 h-4 text-amber-500"></i>
                            </div>
                            <div>
                                <span class="text-[10px] font-black text-slate-900 uppercase block leading-none">Dados Ocultos</span>
                                <span class="text-[8px] font-bold text-slate-400 uppercase tracking-tighter">Upgrade STN necessário</span>
                            </div>
                        </div>
                        <button class="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all shadow-xl shadow-slate-200" onclick="window.unlockIntel('${alerta.id}')">
                            Revelar Dados
                        </button>
                    </div>
                ` : `
                    <div class="flex gap-3 mt-6 pt-4 border-t border-slate-100">
                        <button class="flex-1 flex items-center justify-center gap-2 py-3 bg-slate-50 text-slate-600 hover:bg-blue-600 hover:text-white rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all shadow-sm" onclick="window.toggleTriage('${alerta.id}')">
                            <i data-lucide="scan-eye" class="w-4 h-4"></i> Analisar
                        </button>
                        <button class="flex-1 flex items-center justify-center gap-2 py-3 bg-slate-50 text-slate-600 hover:bg-red-600 hover:text-white rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all shadow-sm" onclick="window.markFalsePositive('${alerta.id}')">
                            <i data-lucide="x-circle" class="w-4 h-4"></i> Descartar
                        </button>
                        <div class="flex items-center gap-2 px-3 bg-red-50 rounded-2xl border border-red-100">
                            <span class="text-[10px] font-black text-red-600 uppercase tracking-tighter">${severity}</span>
                        </div>
                    </div>
                `}
            </article>
        </div>
    `;
}

window.unlockIntel = async (id) => {
    if (state.stn_tokens < 10) {
        alert("CRÉDITOS INSUFICIENTES! Adquira mais munição de dados para continuar a análise.");
        window.location.hash = 'pricing';
        return;
    }
    
    if (confirm("Gastar 10 STN para revelar a identidade do autor?")) {
        state.stn_tokens -= 10;
        alert("IDENTIDADE REVELADA! (Simulação)");
        renderAll();
    }
};

function renderMonitorImpacto(container) {
    if (!container || !state.data) return;
    
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
    
    let timeStr = "--:--";
    if (state.lastSyncAt) {
        const d = new Date(state.lastSyncAt);
        timeStr = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
    }

    const update = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    };
    
    const updateTime = (id) => update(id, timeStr);

    update('kpi-monitorados', s.total_monitorados);
    updateTime('kpi-time-monitorados');
    
    update('kpi-hate', s.total_alertas);
    updateTime('kpi-time-hate');
    
    update('kpi-total', s.total_amostra.toLocaleString());
    updateTime('kpi-time-total');
    
    update('kpi-res', s.resiliencia + '%');
    updateTime('kpi-time-res');
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
async function renderNetworkIntelligence() { 
    const container = document.getElementById('view-networks');
    if (!container) return;
    
    container.innerHTML = `
        <div class="p-12 text-center">
            <div class="skeleton w-16 h-16 rounded-2xl mx-auto mb-4 bg-slate-100"></div>
            <p class="text-slate-400 text-sm font-bold animate-pulse">Detectando redes coordenadas...</p>
        </div>`;
        
    try {
        const networks = await dataService.getNetworks();
        
        if (!networks || networks.length === 0) {
            container.innerHTML = `
                <div class="p-12 text-center bg-white border border-slate-200 rounded-xl animate-in mt-4 flex flex-col items-center justify-center" style="min-height: 60vh;">
                    <div class="w-16 h-16 bg-blue-50 text-blue-500 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
                        <i data-lucide="network" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-xl font-black text-slate-800 mb-2">Mapeamento de Redes Coordenadas</h3>
                    <p class="text-sm text-slate-500 max-w-md mx-auto mb-8">Nenhuma rede coordenada detectada no momento. O sistema continua monitorando os fluxos forenses.</p>
                </div>`;
            if (window.lucide) lucide.createIcons();
            return;
        }

        let html = `
        <div class="p-6 animate-in">
            <h2 class="text-2xl font-black text-slate-800 tracking-tighter mb-8">Redes Coordenadas Detectadas</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        `;
        
        networks.forEach(net => {
            const dateStr = new Date(net.created_at).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
            
            const isAtiva = net.status === 'ATIVA';
            const badgeClasses = isAtiva ? 'bg-red-50 text-red-600 border-red-100' : 'bg-amber-50 text-amber-600 border-amber-100';
            const stripeClass = isAtiva ? 'bg-red-500' : 'bg-amber-500';
            
            const keywords = (net.palavras_chave || []).slice(0, 10).map(k => 
                `<span class="inline-block px-2 py-1 bg-slate-100 border border-slate-200 rounded-lg text-[10px] font-bold text-slate-600 mr-1.5 mb-1.5 shadow-sm hover:bg-slate-200 transition-colors cursor-default">#${k}</span>`
            ).join('');
            
            html += `
            <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-lg transition-all relative overflow-hidden group">
                <div class="absolute top-0 left-0 w-1.5 h-full ${stripeClass}"></div>
                <div class="absolute top-4 right-6 opacity-5 group-hover:opacity-10 transition-opacity">
                    <i data-lucide="network" class="w-24 h-24 text-slate-900"></i>
                </div>
                
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-6">
                        <div>
                            <span class="px-2.5 py-1 ${badgeClasses} rounded-md text-[9px] font-black uppercase tracking-widest border shadow-sm">${net.status}</span>
                            <h3 class="text-lg font-black text-slate-800 mt-3 tracking-tight">${net.nome}</h3>
                        </div>
                        <div class="text-right flex flex-col items-end">
                            <div class="text-3xl font-black ${isAtiva ? 'text-red-500' : 'text-amber-500'} leading-none">${net.severidade}</div>
                            <div class="text-[8px] font-black text-slate-400 uppercase tracking-widest mt-1">Severidade</div>
                        </div>
                    </div>
                    
                    <div class="flex items-center gap-5 mb-6 p-4 bg-slate-50 rounded-2xl border border-slate-100">
                        <div class="flex items-center gap-2">
                            <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shadow-inner">
                                <i data-lucide="users" class="w-4 h-4"></i>
                            </div>
                            <div>
                                <div class="text-sm font-black text-slate-800 leading-none">${net.eventos_count}</div>
                                <div class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">Conexões</div>
                            </div>
                        </div>
                        
                        <div class="w-px h-8 bg-slate-200"></div>
                        
                        <div class="flex items-center gap-2">
                            <div class="w-8 h-8 rounded-full bg-slate-200 text-slate-500 flex items-center justify-center shadow-inner">
                                <i data-lucide="clock" class="w-4 h-4"></i>
                            </div>
                            <div>
                                <div class="text-xs font-bold text-slate-800 leading-none mt-0.5">${dateStr}</div>
                                <div class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1">Detecção</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-5 border-t border-slate-100">
                        <div class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-1">
                            <i data-lucide="hash" class="w-3 h-3"></i> Vetor Lexical Forense
                        </div>
                        <div class="flex flex-wrap">${keywords}</div>
                    </div>
                </div>
            </div>`;
        });
        
        html += `</div></div>`;
        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("Erro ao carregar redes:", e);
        container.innerHTML = `
            <div class="p-12 text-center">
                <div class="w-16 h-16 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <i data-lucide="alert-triangle" class="w-8 h-8"></i>
                </div>
                <h3 class="text-lg font-black text-slate-800 mb-2">Erro de Conexão</h3>
                <p class="text-sm text-slate-500">Falha ao buscar dados do motor de análise forense.</p>
            </div>`;
        if (window.lucide) lucide.createIcons();
    }
}

async function renderDossieGrid() { 
    const container = document.getElementById('view-dossie');
    if (!container) return;

    const config = state.currentReportConfig;
    const totalCost = state.reportOptions
        .filter(opt => config.selectedIds.includes(opt.id))
        .reduce((sum, opt) => sum + opt.cost, 0);

    container.innerHTML = `
        <div class="p-6">
            <div class="flex justify-between items-center mb-8">
                <h2 class="text-2xl font-black text-slate-800 tracking-tighter">Gerador de Inteligência</h2>
                <div class="px-4 py-2 bg-slate-900 text-white rounded-xl flex items-center gap-3 shadow-xl">
                    <i data-lucide="zap" class="w-4 h-4 text-yellow-400 fill-yellow-400"></i>
                    <span class="text-xs font-black uppercase tracking-widest" id="report-stn-balance">${state.stn_tokens} STN</span>
                </div>
            </div>

            <!-- FORMULÁRIO DE CUSTOMIZAÇÃO -->
            <div class="bg-white border border-slate-200 rounded-3xl p-6 mb-12 shadow-sm">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                        <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest mb-4">1. Selecionar Alvo</h3>
                        <select id="report-target-select" onchange="window.updateReportConfig('target', this.value)" class="w-full p-4 bg-slate-50 border-none rounded-2xl text-sm font-bold text-slate-700 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
                            <option value="">Selecione um perfil monitorado...</option>
                            ${(state.data || []).map(c => `<option value="${c.username}" ${config.target === c.username ? 'selected' : ''}>@${c.username} (${c.nome_completo || 'Identidade Pendente'})</option>`).join('')}
                        </select>
                        <p class="mt-3 text-[10px] text-slate-400 font-bold uppercase tracking-tight">O levantamento será processado pelo motor PASA v16.4</p>
                    </div>

                    <div>
                        <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest mb-4">2. Configurar Módulos</h3>
                        <div class="space-y-3">
                            ${state.reportOptions.map(opt => `
                                <label class="flex items-center justify-between p-4 ${config.selectedIds.includes(opt.id) ? 'bg-blue-50 border-blue-100' : 'bg-slate-50 border-transparent'} border rounded-2xl cursor-pointer hover:border-blue-200 transition-all group">
                                    <div class="flex items-center gap-3">
                                        <input type="checkbox" 
                                               ${opt.required ? 'disabled checked' : ''} 
                                               ${config.selectedIds.includes(opt.id) ? 'checked' : ''}
                                               onchange="window.toggleReportModule('${opt.id}')"
                                               class="w-5 h-5 rounded-lg border-slate-300 text-blue-600 focus:ring-blue-500">
                                        <span class="text-sm font-black text-slate-700">${opt.label}</span>
                                    </div>
                                    <span class="text-[10px] font-black ${config.selectedIds.includes(opt.id) ? 'text-blue-600' : 'text-slate-400'} uppercase">${opt.cost} STN</span>
                                </label>
                            `).join('')}
                        </div>

                        <div class="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between">
                            <div>
                                <span class="text-[10px] font-black text-slate-400 uppercase block tracking-widest">Custo do Levantamento</span>
                                <strong class="text-2xl font-black text-slate-900">${totalCost} STN</strong>
                            </div>
                            <button onclick="window.processReportGeneration()" 
                                    class="px-8 py-4 bg-blue-600 text-white rounded-2xl font-black uppercase tracking-widest shadow-xl shadow-blue-200 hover:bg-blue-700 transition-all flex items-center gap-3 ${!config.target ? 'opacity-50 cursor-not-allowed' : ''}">
                                <i data-lucide="wand-2" class="w-5 h-5"></i> Gerar Levantamento
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- LISTAGEM DE HISTÓRICO -->
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-lg font-black text-slate-800 tracking-tight">Repositório de Relatórios</h2>
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest" id="dossie-count-label">Buscando...</span>
            </div>
            <div id="dossie-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div class="p-8 text-center bg-white border border-slate-200 rounded-3xl col-span-full">
                    <div class="spinner m-auto mb-4"></div>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Acessando registros criptografados...</span>
                </div>
            </div>
        </div>
    `;

    try {
        const dossiers = await dataService.getDossiers();
        const listContainer = document.getElementById('dossie-list');
        const countLabel = document.getElementById('dossie-count-label');
        
        if (countLabel) countLabel.innerText = `${dossiers?.length || 0} REGISTROS`;

        if (!dossiers || dossiers.length === 0) {
            listContainer.innerHTML = `
                <div class="p-12 text-center bg-white border border-slate-200 rounded-3xl col-span-full">
                    <i data-lucide="file-warning" class="w-12 h-12 text-slate-200 m-auto mb-4"></i>
                    <p class="text-sm text-slate-400 font-bold uppercase tracking-tight">Nenhum relatório encontrado no repositório.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        listContainer.innerHTML = dossiers.map(d => `
            <div class="p-5 bg-white border border-slate-200 rounded-3xl hover:shadow-xl transition-all group relative overflow-hidden">
                <div class="absolute top-0 right-0 p-3">
                    <span class="px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full text-[8px] font-black uppercase tracking-tighter">${d.versao_pasa || 'v16.4'}</span>
                </div>
                
                <div class="flex items-center gap-4 mb-4">
                    <div class="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-inner">
                        <i data-lucide="file-text" class="w-6 h-6"></i>
                    </div>
                    <div class="min-w-0">
                        <h4 class="text-sm font-black text-slate-800 truncate leading-none mb-1">@${d.candidato_id}</h4>
                        <span class="text-[10px] text-slate-400 font-bold uppercase tracking-tight">${new Date(d.data_geracao).toLocaleDateString('pt-BR')}</span>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3 mb-6">
                    <div class="p-3 bg-slate-50 rounded-2xl border border-slate-100/50">
                        <span class="text-[9px] text-slate-400 block uppercase font-black tracking-widest mb-1">Amostra</span>
                        <strong class="text-base font-black text-slate-800">${d.total_comentarios}</strong>
                    </div>
                    <div class="p-3 bg-red-50 rounded-2xl border border-red-100/50">
                        <span class="text-[9px] text-red-400 block uppercase font-black tracking-widest mb-1">Hostis</span>
                        <strong class="text-base font-black text-red-600">${d.total_hate}</strong>
                    </div>
                </div>

                <div class="flex justify-between items-center pt-4 border-t border-slate-50">
                    <div class="flex flex-col">
                        <span class="text-[9px] text-slate-300 font-mono tracking-tighter uppercase">Integridade Selada</span>
                        <span class="text-[8px] text-slate-200 font-mono">${d.hash_integridade ? d.hash_integridade.substring(0, 16) : '---'}</span>
                    </div>
                    <a href="${d.arquivo_path}" target="_blank" class="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all shadow-lg">
                        <i data-lucide="download" class="w-3.5 h-3.5"></i> Abrir
                    </a>
                </div>
            </div>
        `).join('');
        
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Error rendering report grid:', e);
    }
}

window.updateReportConfig = (key, val) => {
    state.currentReportConfig[key] = val;
    renderDossieGrid();
};

window.toggleReportModule = (id) => {
    const ids = state.currentReportConfig.selectedIds;
    if (ids.includes(id)) {
        state.currentReportConfig.selectedIds = ids.filter(i => i !== id);
    } else {
        state.currentReportConfig.selectedIds.push(id);
    }
    renderDossieGrid();
};

window.processReportGeneration = async () => {
    const config = state.currentReportConfig;
    if (!config.target) {
        alert("SELECIONE UM ALVO PARA O LEVANTAMENTO.");
        return;
    }

    const totalCost = state.reportOptions
        .filter(opt => config.selectedIds.includes(opt.id))
        .reduce((sum, opt) => sum + opt.cost, 0);

    if (state.stn_tokens < totalCost) {
        alert(`CRÉDITOS INSUFICIENTES. Este levantamento custa ${totalCost} STN, você possui ${state.stn_tokens} STN.`);
        window.location.hash = 'pricing';
        return;
    }

    if (confirm(`Confirmar geração de relatório para @${config.target}? Custo: ${totalCost} STN.`)) {
        try {
            // Usa o postJson resiliente com os módulos selecionados
            await dataService.postJson('/dossiers/generate', { 
                candidato_id: config.target,
                modules: config.selectedIds 
            });
            
            state.stn_tokens -= totalCost;
            alert("PROCESSAMENTO INICIADO! O relatório aparecerá no repositório em breve.");
            
            state.currentReportConfig.target = null;
            state.currentReportConfig.selectedIds = ['base'];
            
            renderDossieGrid();
        } catch (e) {
            console.error(e);
            alert("Erro no motor estratégico. Tente novamente.");
        }
    }
};

async function renderGeopolitica() { 
    const container = document.getElementById('view-map');
    if (!container) return;

    container.innerHTML = `
        <div class="p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h2 class="text-2xl font-black text-slate-800 tracking-tighter">Geopolítica da Hostilidade</h2>
                    <p class="text-xs text-slate-400 font-bold uppercase tracking-tighter">Mapeamento situacional por Unidade Federativa</p>
                </div>
                <div class="flex gap-2">
                    <div class="px-4 py-2 bg-white border border-slate-200 rounded-xl flex items-center gap-2 shadow-sm">
                        <div class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        <span class="text-[10px] font-black uppercase tracking-widest text-slate-600">Dados em Tempo Real</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-8 shadow-sm relative overflow-hidden flex items-center justify-center" style="min-height: 600px;">
                    <div id="map-canvas" class="w-full max-w-lg h-full">
                        <!-- O SVG será injetado aqui pelo BrazilMap.js -->
                        <div class="flex flex-col items-center justify-center h-full opacity-20">
                            <i data-lucide="map" class="w-24 h-24 mb-4"></i>
                            <span class="text-xs font-mono uppercase tracking-[0.2em]">Desenhando Topologia...</span>
                        </div>
                    </div>
                    
                    <!-- TOOLTIP FLUTUANTE -->
                    <div id="map-tooltip" class="absolute pointer-events-none opacity-0 transition-opacity bg-slate-900 text-white p-3 rounded-xl shadow-2xl z-50 border border-slate-700"></div>
                </div>

                <div class="bg-slate-900 rounded-3xl p-6 shadow-2xl overflow-hidden flex flex-col">
                    <div class="flex items-center gap-2 mb-6">
                        <i data-lucide="list-ordered" class="w-4 h-4 text-blue-400"></i>
                        <h3 class="text-white font-black text-sm uppercase tracking-widest">Focos de Hostilidade</h3>
                    </div>
                    <div id="geo-ranking-list" class="space-y-3 overflow-y-auto custom-scrollbar pr-2 flex-1" style="max-height: 500px;">
                        <!-- Preenchido via API -->
                        <div class="animate-pulse space-y-4">
                            ${Array(6).fill(0).map(() => `<div class="h-16 bg-slate-800 rounded-2xl"></div>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    try {
        const geoData = await dataService.getGeoUF();
        const rankingList = document.getElementById('geo-ranking-list');
        const tooltip = document.getElementById('map-tooltip');
        
        // Converte para objeto para o componente de mapa
        const ufStats = geoData.reduce((acc, item) => {
            acc[item.uf] = { alvos: item.total_alvos, odio: item.total_hate, color: item.color };
            return acc;
        }, {});

        // Renderiza o mapa SVG
        renderBrazilMap('map-canvas', ufStats, (name, data, ufId) => {
            state.selectedUF = { id: ufId, name, ...data };
            window.debouncedRender();
        });

        // Preenche o Ranking Lateral
        if (rankingList) {
            const sorted = [...geoData].sort((a, b) => b.total_hate - a.total_hate);
            rankingList.innerHTML = sorted.map(item => `
                <div class="flex items-center justify-between p-4 bg-slate-800/40 border border-slate-800 rounded-2xl hover:bg-slate-800 hover:border-slate-700 transition-all cursor-pointer group" onclick="window.handleUFClick('${item.uf}', '${item.uf}')">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-white font-black text-sm border border-slate-700 group-hover:border-blue-500 transition-colors">${item.uf}</div>
                        <div class="min-w-0">
                            <span class="text-[9px] font-bold text-slate-500 uppercase block leading-none mb-1">${item.total_alvos} Alvos Ativos</span>
                            <strong class="text-white text-sm truncate block">${item.uf === 'BR' ? 'Brasil (Geral)' : 'Território ' + item.uf}</strong>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-[12px] font-black text-red-500 block leading-none">${item.total_hate} <span class="text-[8px] opacity-50">SINAIS</span></span>
                        <div class="w-16 h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden border border-slate-700">
                            <div class="h-full rounded-full" style="width: ${Math.min(100, (item.total_hate / (sorted[0].total_hate || 1)) * 100)}%; background: ${item.color}"></div>
                        </div>
                    </div>
                </div>
            `).join('') || '<p class="text-slate-600 text-center text-xs font-black uppercase py-8 opacity-30">Aguardando telemetria...</p>';
        }
        
        // Listener de Tooltip para o mapa
        const mapCanvas = document.getElementById('map-canvas');
        if (mapCanvas) {
            mapCanvas.addEventListener('mousemove', (e) => {
                const target = e.target.closest('.uf-path');
                if (target) {
                    const ufId = target.id.replace('uf-', '');
                    const data = ufStats[ufId];
                    if (data) {
                        tooltip.style.opacity = '1';
                        tooltip.style.left = (e.clientX + 20) + 'px';
                        tooltip.style.top = (e.clientY + 20) + 'px';
                        tooltip.innerHTML = `
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center font-black text-xs border border-slate-700">${ufId}</div>
                                <div>
                                    <div class="text-[10px] font-black uppercase text-slate-400 leading-none mb-1">Hostilidade Detectada</div>
                                    <div class="text-sm font-black text-white">${data.odio} Alertas</div>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    tooltip.style.opacity = '0';
                }
            });
            mapCanvas.addEventListener('mouseleave', () => tooltip.style.opacity = '0');
        }
        
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('[UI] Map render failed:', e);
    }
}

function renderDirectory() { 
    const container = document.getElementById('view-directory');
    if (!container) return;

    const query = state.directorySearchQuery?.toLowerCase() || '';
    const filtered = (state.data || []).filter(c => 
        (c.username && c.username.toLowerCase().includes(query)) || 
        (c.nome_completo && c.nome_completo.toLowerCase().includes(query))
    );

    container.innerHTML = `
        <div class="p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h2 class="text-2xl font-black text-slate-800">Diretório Global de Perfis</h2>
                    <p class="text-xs text-slate-500 font-bold uppercase tracking-tighter">${state.data?.length || 0} perfis monitorados no sistema</p>
                </div>
                <div class="relative w-full md:w-80">
                    <i data-lucide="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"></i>
                    <input type="text" 
                           id="directory-search-input" 
                           placeholder="Buscar handle ou nome..." 
                           class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                           value="${state.directorySearchQuery || ''}"
                           oninput="window.setDirectorySearch(this.value)">
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                ${filtered.map(c => {
                    const avatarUrl = c.avatar_url || `https://ui-avatars.com/api/?name=${c.username}&background=0D8ABC&color=fff`;
                    return `
                        <div class="p-4 bg-white border border-slate-200 rounded-2xl hover:shadow-xl transition-all group cursor-pointer" onclick="window.inspectTarget('${c.username}')">
                            <div class="flex items-center gap-3 mb-4">
                                <div class="w-12 h-12 rounded-full overflow-hidden border-2 border-slate-50 group-hover:border-blue-500 transition-colors shadow-sm">
                                    <img src="${avatarUrl}" alt="${c.username}" class="w-full h-full object-cover">
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h4 class="text-sm font-black text-slate-900 truncate">@${c.username}</h4>
                                    <span class="text-[11px] font-extrabold text-slate-600 truncate block leading-tight">${c.nome_completo || 'Identidade Pendente'}</span>
                                </div>
                                <div class="text-right">
                                    <span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-[8px] font-black">${c.estado || 'BR'}</span>
                                </div>
                            </div>
                            <div class="py-2">
                                <span class="text-[10px] font-black text-slate-800 uppercase block truncate">${c.nome_completo || 'Identidade Pendente'}</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2 py-3 border-t border-slate-50">
                                <div>
                                    <span class="text-[8px] text-slate-400 font-bold uppercase block">Seguidores</span>
                                    <strong class="text-xs font-black text-slate-800">${formatCompactNumber(c.seguidores || 0)}</strong>
                                </div>
                                <div class="text-right">
                                    <span class="text-[8px] text-slate-400 font-bold uppercase block">Risco PASA</span>
                                    <strong class="text-xs font-black" style="color:${c.color || 'var(--success)'}">${c.score_risco || 0}%</strong>
                                </div>
                            </div>
                            <button class="w-full mt-2 py-2.5 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest transition-all hover:bg-blue-600 shadow-lg shadow-slate-200 group-hover:shadow-blue-100">
                                Abrir Timeline
                            </button>
                        </div>
                    `;
                }).join('')}
                ${filtered.length === 0 ? '<div class="col-span-full py-12 text-center text-slate-400 text-xs font-mono uppercase opacity-50">Nenhum perfil corresponde à busca</div>' : ''}
            </div>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

window.setDirectorySearch = (val) => {
    state.directorySearchQuery = val;
    window.debouncedRender();
};
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

window.generateTargetDossier = async (username) => {
    if (state.stn_tokens < 50) {
        alert("CRÉDITOS INSUFICIENTES (Mínimo: 50 STN). Adquira mais créditos para gerar o levantamento.");
        window.location.hash = 'pricing';
        return;
    }

    if (confirm(`Deseja gastar 50 STN para gerar um Relatório Detalhado de @${username}?`)) {
        try {
            // Usa o postJson resiliente
            const result = await dataService.postJson('/dossiers/generate', { candidato_id: username });
            
            alert("RELATÓRIO GERADO COM SUCESSO! Você será redirecionado para o repositório.");
            state.stn_tokens -= 50;
            window.location.hash = 'dossie';
            renderAll();
        } catch (e) {
            console.error(e);
            alert("Erro no motor de inteligência. Tente novamente.");
        }
    }
};

window.markFalsePositive = async (id) => {
    try {
        await dataService.markFalsePositive(id);
        
        // Remove do estado local para feedback imediato
        state.alertas = state.alertas.filter(a => a.id !== id);
        
        // Se estiver no feed principal, remove o elemento com animação
        const el = document.querySelector(`[data-alerta-id="${id}"]`);
        if (el) {
            el.style.opacity = '0';
            el.style.transform = 'scale(0.9)';
            setTimeout(() => {
                el.remove();
                if (state.alertas.length === 0) window.debouncedRender();
            }, 300);
        }
    } catch (e) {
        alert("Falha ao descartar sinal. Tente novamente.");
    }
};

window.forceRefresh = () => window.location.reload();

async function renderAds() {
    const container = document.getElementById('view-ads');
    if (!container) return;

    container.innerHTML = `
        <div class="p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h2 class="text-2xl font-black text-slate-800 tracking-tighter">Meta Ad Library</h2>
                    <p class="text-xs text-slate-400 font-bold uppercase tracking-tighter">Monitoramento de anúncios pagos detectados</p>
                </div>
                <div class="flex gap-2">
                    <div class="px-4 py-2 bg-blue-50 text-blue-700 rounded-xl flex items-center gap-2 shadow-sm">
                        <i data-lucide="megaphone" class="w-4 h-4"></i>
                        <span class="text-[10px] font-black uppercase tracking-widest">Rastreamento Ativo</span>
                    </div>
                </div>
            </div>

            <div id="ads-list" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                <div class="p-12 text-center bg-white border border-slate-200 rounded-3xl col-span-full">
                    <div class="spinner m-auto mb-4"></div>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Varrendo Biblioteca de Anúncios...</span>
                </div>
            </div>
        </div>
    `;

    try {
        const ads = await dataService.getAds();
        const listContainer = document.getElementById('ads-list');
        
        if (!ads || ads.length === 0) {
            listContainer.innerHTML = `
                <div class="p-12 text-center bg-white border border-slate-200 rounded-3xl col-span-full">
                    <i data-lucide="info" class="w-12 h-12 text-slate-200 m-auto mb-4"></i>
                    <p class="text-sm text-slate-400 font-bold uppercase tracking-tight">Nenhum anúncio suspeito detectado nesta janela.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        listContainer.innerHTML = ads.map(ad => `
            <div class="p-5 bg-white border border-slate-200 rounded-3xl hover:shadow-xl transition-all group flex flex-col h-full">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg">
                            <i data-lucide="facebook" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h4 class="text-sm font-black text-slate-800 leading-none mb-1">${ad.page_name || 'Página Oculta'}</h4>
                            <span class="text-[10px] text-blue-600 font-black uppercase tracking-tighter">@${ad.candidato_id}</span>
                        </div>
                    </div>
                    <span class="px-2 py-1 ${ad.status === 'Active' ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'} rounded-lg text-[8px] font-black uppercase tracking-widest">${ad.status || 'OFF'}</span>
                </div>

                <div class="flex-1">
                    <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100 mb-4 italic text-sm text-slate-700 leading-relaxed min-h-[100px]">
                        "${ad.creative_body ? ad.creative_body.substring(0, 200) + '...' : 'Sem conteúdo textual.'}"
                    </div>
                </div>

                <div class="space-y-3 pt-4 border-t border-slate-50">
                    <div class="flex justify-between items-center">
                        <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Investimento</span>
                        <strong class="text-xs font-black text-slate-800">${ad.spend_range || 'N/A'}</strong>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Pago por</span>
                        <span class="text-[9px] font-bold text-slate-600 truncate max-w-[120px]">${ad.paid_by || 'Privado'}</span>
                    </div>
                    <a href="${ad.ad_url}" target="_blank" class="w-full mt-2 py-3 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all flex items-center justify-center gap-2 shadow-lg">
                        <i data-lucide="external-link" class="w-3.5 h-3.5"></i> Ver na Biblioteca
                    </a>
                </div>
            </div>
        `).join('');
        
        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Error rendering ads grid:', e);
    }
}
window.setNetworkView = (view) => { state.networkView = view; state.view = 'networks'; renderAll(); };

// --- GESTOS DE SWIPE (Tinder do Ódio) ---
export function initSwipeGestures() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;

    let startX = 0;
    let currentX = 0;
    let activeSurface = null;
    let isDragging = false;

    const startDrag = (x, target) => {
        const surface = target.closest('.post-card-surface');
        if (!surface) return;
        activeSurface = surface;
        startX = x;
        isDragging = true;
        activeSurface.style.transition = 'none'; 
    };

    const moveDrag = (x) => {
        if (!isDragging || !activeSurface) return;
        currentX = x - startX;
        if (currentX < 0) { // Permitir apenas arraste para a esquerda (descarte)
            activeSurface.style.transform = `translateX(${currentX}px)`;
        }
    };

    const endDrag = () => {
        if (!isDragging || !activeSurface) return;
        isDragging = false;
        activeSurface.style.transition = 'transform 0.2s ease-out';
        
        if (currentX < -100) { // Limiar de descarte (100px)
            const alertaId = activeSurface.closest('.post-card-container').dataset.alertaId;
            activeSurface.style.transform = `translateX(-120%)`; // Desliza pra fora da tela
            
            // Aguarda animação e despacha o falso positivo
            setTimeout(() => {
                if (window.markFalsePositive) window.markFalsePositive(alertaId);
            }, 200);
        } else {
            // Volta para a posição original
            activeSurface.style.transform = `translateX(0px)`;
        }
        activeSurface = null;
        currentX = 0;
    };

    // Suporte a Touch (Mobile)
    container.addEventListener('touchstart', (e) => startDrag(e.touches[0].clientX, e.target), {passive: true});
    container.addEventListener('touchmove', (e) => moveDrag(e.touches[0].clientX), {passive: true});
    container.addEventListener('touchend', endDrag);

    // Suporte a Mouse (Desktop)
    container.addEventListener('mousedown', (e) => startDrag(e.clientX, e.target));
    container.addEventListener('mousemove', (e) => moveDrag(e.clientX));
    container.addEventListener('mouseup', endDrag);
    container.addEventListener('mouseleave', endDrag);
}

