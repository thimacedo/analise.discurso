/**
 * PASA v47.3 - App Orchestrator: Central Application Coordinator
 * Manages application lifecycle, state updates, and side effects
 */
import { State, stateMutations, selectors } from './state.js';
import { UI } from './ui.js';
import { initAuth, getCurrentUserEmail } from './auth.js';
import { renderSessionManager } from '../components/session-manager.js';
import { renderSessionsView } from '../components/session-table.js';
import { dataService } from '../services/dataService.js';

// Configuration
const SUPABASE_URL = window.SENTINELA_CONFIG?.supabaseUrl;
const SUPABASE_ANON_KEY = window.SENTINELA_CONFIG?.supabaseKey;

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    rightSidebar: document.getElementById('right-sidebar'),
    sidebarToggle: document.getElementById('sidebar-toggle'),
    rightSidebarToggle: document.getElementById('right-sidebar-toggle'),
    feedContainer: document.getElementById('feed-alertas'),
    scrollSentinel: document.getElementById('scroll-sentinel'),
    profilerStream: document.getElementById('profiler-stream-feed'),
    workerXpRanking: document.getElementById('worker-xp-ranking'),
    kpiTargets: document.getElementById('kpi-targets'),
    kpiHate: document.getElementById('kpi-hate'),
    kpiTotal: document.getElementById('kpi-total'),
    kpiRes: document.getElementById('kpi-res'),
    dashboardSearch: document.getElementById('dashboard-search'),
    clearSearchBtn: document.getElementById('clear-search-btn')
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initializeEventListeners();
    loadInitialData();
    setupInfiniteScroll();
});

// Initialize core functionality
async function loadInitialData() {
    try {
        // Set loading states
        stateMutations.setLoading(State, 'comments', true);
        stateMutations.setLoading(State, 'workers', true);
        stateMutations.setLoading(State, 'profiler', true);
        stateMutations.setLoading(State, 'kpis', true);
        stateMutations.setLoading(State, 'sessions', true);
        
        // Initial partial render
        renderApplication();

        // Fetch all data in parallel
        await Promise.allSettled([
            fetchComments(),
            fetchWorkersTelemetry(),
            fetchProfilerData(),
            fetchKPIs(),
            fetchSessions()
        ]);
        
        // Final render after data load
        renderApplication();
    } catch (error) {
        stateMutations.setError(State, error);
        renderApplication();
    } finally {
        // Clear loading states
        stateMutations.setLoading(State, 'comments', false);
        stateMutations.setLoading(State, 'workers', false);
        stateMutations.setLoading(State, 'profiler', false);
        stateMutations.setLoading(State, 'kpis', false);
        stateMutations.setLoading(State, 'sessions', false);
    }
}

// Data fetching functions
async function fetchComments() {
    if (!SUPABASE_URL) return;
    
    try {
        const timestamp = Date.now();
        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/comentarios?` +
            `select=id,id_externo,autor_username,texto_limpo,texto_bruto,data_coleta,data_publicacao,is_hate,categoria_ia,direcao_odio,confianca_ia,processado_ia,candidato_id,plataforma,ccf_density,ccf_sync,ccf_performativity&` +
            `order=data_coleta.desc&limit=100&t=${timestamp}`, {
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const comments = await response.json();
        stateMutations.setComments(State, comments);
    } catch (error) {
        console.error('Failed to fetch comments:', error);
        stateMutations.setError(State, error);
    }
}

async function fetchWorkersTelemetry() {
    try {
        const response = await fetch('/api/v1/workers/telemetry');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        stateMutations.setWorkers(State, data.workers || []);
        stateMutations.setKpis(State, {
            workersHealthy: data.healthy_workers,
            workersTotal: data.total_workers
        });
    } catch (error) {
        console.error('Failed to fetch workers telemetry:', error);
    }
}

async function fetchProfilerData() {
    try {
        // Fetch KPIs
        const kpiResponse = await fetch(`/docs/kpis.json?t=${Date.now()}`);
        if (kpiResponse.ok) {
            const kpis = await kpiResponse.json();
            stateMutations.setKpis(State, {
                targets: kpis.targets || 0,
                hate: kpis.alerts || 0,
                total: kpis.db_sample || 0,
                resiliencia: kpis.db_sample > 0 ? 
                    ((kpis.db_sample - kpis.alerts) / kpis.db_sample * 100).toFixed(1) : 
                    100
            });
        }
        
        // Fetch profiler stream
        const streamResponse = await fetch(`/docs/profiler_stream.json?t=${Date.now()}`);
        if (streamResponse.ok) {
            const stream = await streamResponse.json();
            stateMutations.setProfilerStream(State, stream.slice().reverse());
        }
    } catch (error) {
        console.error('Failed to fetch profiler data:', error);
    }
}

async function fetchKPIs() {
    try {
        const response = await fetch('/api/v1/monitor/status');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        // Update KPIs from monitor endpoint
        stateMutations.setKpis(State, {
            queueHealth: data.queue_health || {}
        });
    } catch (error) {
        console.error('Failed to fetch KPIs:', error);
    }
}

async function fetchSessions() {
    try {
        const sessions = await dataService.getSessions();
        stateMutations.setSessions(State, sessions || []);
    } catch (error) {
        console.error('Failed to fetch sessions:', error);
    }
}

// Event listeners
function initializeEventListeners() {
    // Sidebar toggle
    if (elements.sidebarToggle) {
        elements.sidebarToggle.addEventListener('click', () => {
            stateMutations.setSidebarCollapsed(State, !State.sidebarCollapsed);
            renderApplication();
        });
    }
    
    // Right sidebar toggle
    if (elements.rightSidebarToggle) {
        elements.rightSidebarToggle.addEventListener('click', () => {
            stateMutations.setRightSidebarCollapsed(State, !State.rightSidebarCollapsed);
            renderApplication();
        });
    }
    
    // Search functionality
    if (elements.dashboardSearch) {
        let searchTimeout = null;
        elements.dashboardSearch.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                stateMutations.setSearchTerm(State, e.target.value);
                stateMutations.updatePagination(State, { page: 1, limit: 20, hasMore: true });
                renderApplication();
            }, 300); // 300ms debounce
        });
    }
    
    // Clear search
    if (elements.clearSearchBtn) {
        elements.clearSearchBtn.addEventListener('click', () => {
            elements.dashboardSearch.value = '';
            stateMutations.setSearchTerm(State, '');
            stateMutations.updatePagination(State, { page: 1, limit: 20, hasMore: true });
            renderApplication();
        });
    }
    
    // Filter buttons
    window.setDashboardFilter = (filter) => {
        stateMutations.setFilter(State, filter);
        stateMutations.updatePagination(State, { page: 1, limit: 20, hasMore: true });
        renderApplication();
        
        // Update active filter button
        document.querySelectorAll('.filter-btn')
            .forEach(btn => btn.classList.remove('active'));
        
        const activeBtn = document.getElementById(`btn-filter-${filter}`);
        if (activeBtn) activeBtn.classList.add('active');
    };
    
    // Audit comment
    window.auditComment = async (commentId, rotulo) => {
        try {
            const response = await fetch('/api/v1/audit/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    comment_id: commentId,
                    rotulo_correto: rotulo,
                    validado_por: getCurrentUserEmail()
                })
            });
            
            if (!response.ok) throw new Error('Audit failed');
            
            // Refresh comments
            await fetchComments();
            renderApplication();
        } catch (error) {
            console.error('Audit comment failed:', error);
            alert('Falha ao validar comentário. Tente novamente.');
        }
    };
    
    // Window hash change (for navigation)
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.replace('#', '') || 'monitor';
        stateMutations.setView(State, hash);
        renderApplication();
    });
    
    // Initial hash load
    if (!window.location.hash) {
        window.history.replaceState(null, '', '#monitor');
    }
}

// Infinite scroll setup
function setupInfiniteScroll() {
    if (!elements.feedContainer || !elements.scrollSentinel) return;
    
    const observer = new IntersectionObserver(
        async (entries) => {
            if (entries[0].isIntersecting && 
                !State.isLoading.comments && 
                State.view === 'monitor' && 
                selectors.hasMoreComments(State)) {
                
                stateMutations.updatePagination(State, {
                    page: State.pagination.page + 1,
                    limit: State.pagination.limit,
                    hasMore: selectors.hasMoreComments(State)
                });
                
                renderApplication();
            }
        },
        {
            rootMargin: '200px',
            threshold: 0.1
        }
    );
    
    observer.observe(elements.scrollSentinel);
}

// Main render function
function renderApplication() {
    // Handle errors
    if (State.error) {
        renderErrorState();
        return;
    }
    
    // Update sidebar states
    updateSidebarStates();
    
    // Update right sidebar states
    updateRightSidebarStates();
    
    // Render view based on current state
    const viewContainer = document.querySelectorAll('.view-content');
    viewContainer.forEach(el => el.classList.remove('active-view'));
    
    const currentView = document.getElementById(`view-${State.view}`);
    if (currentView) currentView.classList.add('active-view');

    // Update Nav Active State
    document.querySelectorAll('.nav-item').forEach(el => {
        if (el.getAttribute('href') === `#${State.view}`) {
            el.setAttribute('aria-current', 'page');
        } else {
            el.removeAttribute('aria-current');
        }
    });
    
    switch (State.view) {
        case 'monitor':
            renderMonitorView();
            break;
        case 'workers':
            import('../components/workers-dashboard.js').then(m => m.renderWorkersView());
            break;
        case 'sessions':
            renderSessionsView();
            break;
        // Other views handled by their containers
    }
    
    // Render UI components
    UI.renderKPIs(State.kpis);
    UI.renderProfilerStream(State.profilerStream);
    UI.renderWorkerXpRanking(State.workers);
    
    // Render Session Manager in header
    renderSessionManager('session-manager-container');
    
    // Render icons
    if (window.lucide) lucide.createIcons();
}

// View rendering functions
function renderMonitorView() {
    if (!elements.feedContainer) return;

    const comments = selectors.paginatedComments(State);
    
    if (State.isLoading.comments && State.comments.length === 0) {
        elements.feedContainer.innerHTML = renderLoadingSkeleton(3);
        return;
    }
    
    if (comments.length === 0) {
        elements.feedContainer.innerHTML = renderEmptyState();
        return;
    }
    
    elements.feedContainer.innerHTML = comments.map(renderCommentCard).join('');
    
    // Show loading sentinel if more data available
    if (selectors.hasMoreComments(State)) {
        elements.scrollSentinel.style.display = 'block';
    } else {
        elements.scrollSentinel.style.display = 'none';
    }
}

function renderCommentCard(comment) {
    // MAPEAMENTO CORRIGIDO PARA O SCHEMA REAL DO BANCO
    const text = comment.texto_bruto || comment.texto_limpo || 'Sem texto';
    const timestamp = comment.data_publicacao || comment.data_coleta;
    const category = comment.processado_ia ? (comment.categoria_ia || 'NEUTRO') : 'NAO_PROCESSADO';

    const confidence = comment.confianca_ia ? (comment.confianca_ia * 100).toFixed(1) : 0;
    const confidenceClass = 
        confidence >= 80 ? 'text-success-600' :
        confidence >= 50 ? 'text-warning-600' :
        'text-danger-600';
    
    let borderColor = 'border-base-200';
    let badgeClass = 'bg-base-100 text-base-500';
    let badgeText = category === 'NAO_PROCESSADO' ? 'Pendente' : 'Processado';
    let quoteClass = 'bg-base-50 border-base-200 text-base-700';
    let iconColor = 'text-base-400';
    
    if (comment.is_hate === true && comment.categoria_ia) {
        borderColor = 'border-danger-500';
        iconColor = 'text-danger-500';
        
        const categoryMap = {
            'ODIO_IDENTITARIO': { bg: 'bg-primary-50 text-primary-600', txt: 'Ódio Identitário' },
            'VIOLENCIA_GENERO': { bg: 'bg-success-50 text-success-600', txt: 'Violência de Gênero' },
            'AMEACA': { bg: 'bg-danger-50 text-danger-600', txt: 'Ameaça Física/Morte' },
            'INSULTO_AD_HOMINEM': { bg: 'bg-warning-50 text-warning-600', txt: 'Insulto Ad Hominem' },
            'ATAQUE_INSTITUCIONAL': { bg: 'bg-info-50 text-info-600', txt: 'Ataque Institucional' },
            'RIGOR_CRIMINAL': { bg: 'bg-warning-50 text-warning-600', txt: 'Rigor Criminal' }
        };
        
        const cat = categoryMap[comment.categoria_ia] || {
            bg: 'bg-danger-50 text-danger-600',
            txt: 'Indício de Risco'
        };
        
        badgeClass = cat.bg;
        badgeText = `${cat.txt} ${comment.direcao_odio ? '→ ' + comment.direcao_odio : ''}`;
        quoteClass = 'bg-danger-50 border-danger-200 text-danger-900';
    } else if (comment.processado_ia === true) {
        borderColor = 'border-success-400';
        badgeClass = 'bg-success-50 text-success-600';
        badgeText = 'Seguro';
        quoteClass = 'bg-success-50 border-success-400 text-success-800';
        iconColor = 'text-success-500';
    }
    
    return `
        <div class="post-card hover:shadow-lg transition-shadow duration-200">
            <div class="flex">
                <div class="w-1 ${borderColor} flex-shrink-0"></div>
                <div class="flex-1 p-5">
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-base-100 flex items-center justify-center text-xs font-bold text-base-500 overflow-hidden">
                                <img src="/assets/sentinela_small.webp" class="w-full h-full object-cover">
                            </div>
                            <div>
                                <span class="text-sm font-bold text-base-800"> @${comment.autor_username || 'Anônimo'}</span>
                                <span class="text-xs font-bold ${badgeClass} px-2 py-0.5 rounded-full uppercase tracking-wider">
                                    ${badgeText}
                                </span>
                            </div>
                        </div>
                        <div class="text-right">
                            <span class="text-xs font-mono text-base-400 block">
                                ${timeAgo(timestamp)}
                            </span>
                            <span class="text-xs font-bold ${confidenceClass} block">
                                Conf: ${confidence}%
                            </span>
                        </div>
                    </div>
                    <div class="${quoteClass} border-l-2 rounded-r-lg p-4 mb-4">
                        <p class="text-sm italic leading-relaxed">"${text}"</p>
                    </div>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <span class="flex items-center gap-1 text-xs font-bold uppercase ${iconColor}">
                                <i data-lucide="shield-alert" class="w-3 h-3"></i> 
                                ${comment.categoria_ia || 'N/A'}
                            </span>
                            <span class="flex items-center gap-1 text-xs font-bold text-base-400 uppercase">
                                <i data-lucide="share-2" class="w-3 h-3"></i> 
                                ${(comment.candidato_id || 'IG')}
                            </span>
                        </div>
                        ${comment.is_hate === true ? `
                            <div class="flex gap-2">
                                <button onclick="window.auditComment('${comment.id}', 'not_hate')" 
                                        class="btn btn-sm btn-outline text-xs h-8 px-2">
                                    Falso Positivo
                                </button>
                                <button onclick="window.auditComment('${comment.id}', 'hate')" 
                                        class="btn btn-sm btn-primary text-xs h-8 px-2">
                                    Padrão Ouro
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderLoadingSkeleton(count) {
    return Array(count).fill(0).map(() => `
        <div class="post-card p-5 space-y-4">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full skeleton"></div>
                <div class="flex-1 space-y-2">
                    <div class="h-3 w-24 skeleton"></div>
                    <div class="h-2 w-32 skeleton"></div>
                </div>
            </div>
            <div class="h-16 w-full skeleton rounded-lg"></div>
            <div class="h-4 w-1/3 skeleton"></div>
        </div>
    `).join('');
}

function renderEmptyState() {
    return `
        <div class="text-center py-12">
            <i data-lucide="alert-circle" class="w-12 h-12 text-base-400 mx-auto mb-4"></i>
            <p class="text-base-500 text-lg">Nenhum registro encontrado</p>
            <p class="text-base-400 text-sm mt-2">Ajuste os filtros ou aguarde novas coletas.</p>
        </div>
    `;
}

function renderErrorState() {
    if (!elements.feedContainer) return;
    elements.feedContainer.innerHTML = `
        <div class="text-center py-12">
            <i data-lucide="alert-triangle" class="w-12 h-12 text-danger-500 mx-auto mb-4"></i>
            <p class="text-base-500 text-lg">Erro ao carregar dados</p>
            <p class="text-base-400 text-sm mt-2">${State.error?.message || 'Erro desconhecido'}</p>
            <button onclick="window.location.reload()" class="btn btn-primary mt-4">Recarregar</button>
        </div>
    `;
}

// Helper functions
function timeAgo(dateString) {
    if (!dateString) return 'agora';
    const diff = Math.floor((new Date() - new Date(dateString)) / 60000);
    if (diff < 1) return 'agora';
    if (diff < 60) return `${diff}m`;
    if (diff < 1440) return `${Math.floor(diff/60)}h`;
    return `${Math.floor(diff/1440)}d`;
}

function updateSidebarStates() {
    if (!elements.sidebar) return;
    if (State.sidebarCollapsed) {
        elements.sidebar.classList.add('sidebar-collapsed');
    } else {
        elements.sidebar.classList.remove('sidebar-collapsed');
    }
}

function updateRightSidebarStates() {
    if (!elements.rightSidebar) return;
    if (State.rightSidebarCollapsed) {
        elements.rightSidebar.classList.add('sidebar-collapsed');
    } else {
        elements.rightSidebar.classList.remove('sidebar-collapsed');
    }
}

// Handle window resize for responsive breakpoints
window.addEventListener('resize', () => {
    const width = window.innerWidth;
    if (width < 640) {
        stateMutations.setSidebarCollapsed(State, true);
        stateMutations.setRightSidebarCollapsed(State, true);
    } else if (width < 1024) {
        stateMutations.setSidebarCollapsed(State, true);
        stateMutations.setRightSidebarCollapsed(State, false);
    } else {
        stateMutations.setSidebarCollapsed(State, false);
        stateMutations.setRightSidebarCollapsed(State, false);
    }
    renderApplication();
});
