// src/core/app.js
import { renderSessionManager } from '../components/session-manager.js';

// 1. INICIALIZAÇÃO DO SUPABASE (Sem import, usando o objeto global do CDN)
const SUPABASE_URL = 'https://vhamejkldzxbeibqeqpk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY';

let supabaseClient;
try {
    if (SUPABASE_URL !== 'SUA_URL_DO_SUPABASE_AQUI' && window.supabase) {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log("✅ Supabase Client inicializado com sucesso via CDN.");
    } else {
        console.warn("⚠️ Credenciais do Supabase não configuradas ou CDN não carregou.");
    }
} catch (e) {
    console.error("❌ Erro crítico ao inicializar Supabase:", e);
}

// PASA v24.1: Integração do Motor de XP e Circuit Breaker no Cérebro Frontend
export async function initPasaDashboard() {
    // 1. Renderiza o Gerenciador de Sessões (Cookie Injector)
    renderSessionManager('session-manager-container');

    // 2. Busca o Status Unificado do Backend
    await fetchSystemStatus();

    // 3. Supabase Realtime para atualizar XP no vivo
    if (supabaseClient) {
        supabaseClient
          .channel('worker-ledger-changes')
          .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'worker_ledger' }, payload => {
            updateWorkerXPUI(payload.new);
          })
          .subscribe();
    }
}

async function fetchSystemStatus() {
    try {
        const response = await fetch('/api/v1/monitor/status');
        if (!response.ok) throw new Error('API Offline');
        
        const data = await response.json();

        // --- Atualização dos KPIs (A Alma do Dashboard) ---
        updateKPI('kpi-monitorados', (data.queue_health?.pending || 0) + (data.queue_health?.processing || 0));
        
        // Para "Alertas Hoje", somamos os critical_hits do ledger
        const totalAlerts = (data.worker_evolution || []).reduce((sum, w) => sum + (w.total_critical_hits || w.critical_hits || 0), 0);
        updateKPI('kpi-hate', totalAlerts);
        
        // "Amostra DB" - Total de runs executadas pelo ecossistema
        const totalRuns = (data.worker_evolution || []).reduce((sum, w) => sum + (w.total_runs || 0), 0);
        updateKPI('kpi-total', totalRuns);

        // "Resiliência" - Baseada no Circuit Breaker
        const resEl = document.getElementById('kpi-res');
        if (resEl) {
            if (data.queue_health?.circuit_breaker_tripped) {
                resEl.textContent = 'CRÍTICO';
                resEl.classList.remove('text-emerald-600');
                resEl.classList.add('text-red-600');
            } else {
                resEl.textContent = '100%';
                resEl.classList.remove('text-red-600');
                resEl.classList.add('text-emerald-600');
            }
        }

        // --- Renderização dos Módulos Visuais ---
        renderCircuitBreakerAlert(data.queue_health || { circuit_breaker_tripped: false });
        renderWorkerEvolution(data.worker_evolution || []);

    } catch (error) {
        console.error('[Sentinela] Falha ao buscar status do sistema:', error);
        const resEl = document.getElementById('kpi-res');
        if(resEl) {
            resEl.textContent = 'OFFLINE';
            resEl.classList.remove('text-emerald-600');
            resEl.classList.add('text-red-600');
        }
    }
}

function updateKPI(elementId, value) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = value;
        // Animação sutil de atualização
        el.classList.add('scale-110');
        setTimeout(() => el.classList.remove('scale-110'), 300);
    }
}

function renderCircuitBreakerAlert(queueHealth) {
    const container = document.getElementById('circuit-breaker-alert');
    if (!container) return;

    if (queueHealth.circuit_breaker_tripped) {
        container.innerHTML = `
            <div class="bg-red-50 border-l-4 border-red-500 text-red-700 p-3 rounded-r-lg shadow-sm flex items-start gap-3 animate-pulse">
                <i data-lucide="alert-octagon" class="w-5 h-5 flex-shrink-0 mt-0.5"></i>
                <div>
                    <p class="font-black text-xs uppercase">Circuit Breaker Ativado</p>
                    <p class="text-[10px] mt-1">Coleta pausada. Injete cookies para retomar.</p>
                </div>
            </div>
        `;
        // Força a exibição do painel de injeção de sessão
        const sessionContainer = document.getElementById('session-manager-container');
        if (sessionContainer) sessionContainer.classList.remove('hidden');
    } else {
        container.innerHTML = '';
        const sessionContainer = document.getElementById('session-manager-container');
        if (sessionContainer) sessionContainer.classList.add('hidden');
    }
    // Re-inicializa ícones Lucide após injeção de HTML
    if (window.lucide) lucide.createIcons();
}

function renderWorkerEvolution(workers) {
    const container = document.getElementById('worker-xp-ranking');
    if (!container) return;

    if (!workers || workers.length === 0) {
        container.innerHTML = '<p class="text-[10px] text-slate-400">Nenhum worker ativo ainda.</p>';
        return;
    }

    container.innerHTML = workers.map(w => `
        <div class="flex justify-between items-center p-2 bg-slate-50 rounded-md border border-slate-100 hover:bg-slate-100 transition-colors">
            <div class="flex items-center gap-2">
                <span class="text-[10px] font-mono font-bold text-slate-600">${w.worker_id || w.worker_name}</span>
            </div>
            <div class="flex gap-3 items-center">
                <span class="text-[9px] font-black text-yellow-500 bg-yellow-50 px-1.5 py-0.5 rounded">Nv ${w.current_level || 1}</span>
                <span class="text-[9px] font-bold text-blue-600">${w.current_xp || 0} XP</span>
            </div>
        </div>
    `).join('');
}

function updateWorkerXPUI(workerData) {
    // Simplesmente re-busca o status para atualizar a UI
    fetchSystemStatus();
}

// 2. MAPEAMENTO VISUAL DO PASA v16.4
const PASA_THREAT_PROFILE = {
    'AMEACA': { color: 'bg-red-600', label: 'Ameaça', badge: 'bg-red-50 text-red-600' },
    'ODIO_IDENTITARIO': { color: 'bg-orange-500', label: 'Ódio Identitário', badge: 'bg-orange-50 text-orange-600' },
    'VIOLENCIA_GENERO': { color: 'bg-purple-500', label: 'Violência de Gênero', badge: 'bg-purple-50 text-purple-600' },
    'RIGOR_CRIMINAL': { color: 'bg-yellow-500', label: 'Rigor Criminal', badge: 'bg-yellow-50 text-yellow-700' },
    'INSULTO_AD_HOMINEM': { color: 'bg-amber-500', label: 'Ad Hominem', badge: 'bg-amber-50 text-amber-700' },
    'ATAQUE_INSTITUCIONAL': { color: 'bg-blue-500', label: 'Ataque Institucional', badge: 'bg-blue-50 text-blue-600' },
    'NEUTRO': { color: 'bg-slate-300', label: 'Neutro', badge: 'bg-slate-100 text-slate-500' }
};

// 3. FUNÇÕES DE RENDERIZAÇÃO
function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text || ''));
    return div.innerHTML;
}

function getTimeAgo(timestamp) {
    if (!timestamp) return '';
    const diffMins = Math.round((new Date() - new Date(timestamp)) / 60000);
    if (diffMins < 1) return 'agora';
    if (diffMins < 60) return `há ${diffMins} min`;
    if (diffMins < 1440) return `há ${Math.round(diffMins / 60)}h`;
    return `há ${Math.round(diffMins / 1440)}d`;
}

function renderThreatCard(alertData) {
    const profile = PASA_THREAT_PROFILE[alertData.category] || PASA_THREAT_PROFILE['NEUTRO'];
    const severityClass = alertData.is_critical ? 'border-red-500' : 'border-slate-200';
    const timeAgo = getTimeAgo(alertData.timestamp);

    // ==========================================
    // DEFESA EM PROFUNDIDADE: FILTRO DE RUÍDO FRONTEND
    // ==========================================
    const UI_NOISE_PATTERNS = [
        /^upload de contatos/i,
        /^não usuários/i,
        /^há \d+ (hora|min|dia)/i,
        /^e outros \d+$/i,
    ];
    
    let safeCommentText = alertData.text || '';
    const isNoise = UI_NOISE_PATTERNS.some(p => p.test(safeCommentText));
    if (isNoise) {
        console.warn("🚫 Ruído de UI filtrado no frontend:", safeCommentText);
        return ''; // Não renderiza o card se for ruído
    }

    return `
        <div class="threat-card bg-white rounded-xl border ${severityClass} shadow-sm hover:shadow-md transition-all overflow-hidden group">
            <div class="flex">
                <div class="w-1 ${profile.color} flex-shrink-0"></div>
                <div class="flex-1 p-4">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 overflow-hidden">
                                <img src="${alertData.target_avatar_url || './assets/sentinela_small.webp'}" class="w-full h-full object-cover" onerror="this.style.display='none'">
                            </div>
                            <div>
                                <span class="text-sm font-bold text-slate-800">@${alertData.target_profile || 'Desconhecido'}</span>
                                <span class="text-[10px] ml-2 font-bold ${profile.badge} px-2 py-0.5 rounded-full uppercase tracking-wider">${profile.label}</span>
                            </div>
                        </div>
                        <span class="text-[10px] font-mono text-slate-400">${timeAgo}</span>
                    </div>
                    <div class="bg-slate-50 border-l-2 border-slate-300 rounded-r-lg p-3 mb-3">
                        <p class="text-sm text-slate-700 italic leading-relaxed">"${escapeHtml(alertData.text)}"</p>
                    </div>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase"><i data-lucide="shield-alert" class="w-3 h-3"></i> ${profile.label}</span>
                            <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase"><i data-lucide="share-2" class="w-3 h-3"></i> ${alertData.source || 'IG'}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
}

function renderHotTargets(targets) {
    const container = document.getElementById('chartMain');
    if (!container) return;
    container.innerHTML = '';

    if (targets.length === 0) {
        container.innerHTML = '<p class="text-center text-slate-300 text-[10px] py-4 uppercase">Sem alvos críticos</p>';
        return;
    }

    targets.slice(0, 5).forEach((target, index) => {
        const riskPercent = Math.min(100, Math.round((target.threat_count / target.max_threats) * 100));
        const riskColor = riskPercent > 75 ? 'bg-red-500' : riskPercent > 40 ? 'bg-orange-400' : 'bg-slate-300';

        container.innerHTML += `
            <div class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors group cursor-pointer">
                <div class="flex items-center gap-2">
                    <div class="w-6 h-6 rounded-full bg-red-50 flex items-center justify-center text-[9px] font-bold text-red-500 border border-red-100">${index + 1}</div>
                    <span class="text-xs font-bold text-slate-700 group-hover:text-slate-900">@${target.profile}</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-16 bg-slate-100 rounded-full h-1.5">
                        <div class="${riskColor} h-1.5 rounded-full" style="width: ${riskPercent}%"></div>
                    </div>
                    <span class="text-[9px] font-mono text-slate-400">${riskPercent}%</span>
                </div>
            </div>`;
    });
}

// 4. FUNÇÃO PRINCIPAL DE CARGA DO BANCO
async function loadSentinelaDashboard() {
    const feedContainer = document.getElementById('feed-alertas');
    const skeleton = document.getElementById('skeleton-container');
    
    if(!feedContainer) return;

    if (!supabaseClient) {
        console.error("❌ Supabase não inicializado. Verifique as credenciais.");
        feedContainer.innerHTML = '<p class="text-center text-red-400 text-sm py-8">Erro: Credenciais do Banco não configuradas no app.js.</p>';
        if(skeleton) skeleton.style.display = 'none';
        return;
    }

    try {
        console.log("🔍 Buscando alertas reais no Supabase (tabela comentarios)...");
        
        // A. BUSCAR ALERTAS REAIS
        const { data: alerts, error: alertError } = await supabaseClient
            .from('comentarios') // MUDOU AQUI
            .select('*')
            .order('data_publicacao', { ascending: false }) // MUDOU AQUI
            .limit(20);

        if (alertError) {
            console.error("❌ Erro do Supabase:", alertError.message);
            throw alertError;
        }

        console.log(`✅ ${alerts ? alerts.length : 0} alertas encontrados.`, alerts);

        feedContainer.innerHTML = '';
        if (alerts && alerts.length > 0) {
            alerts.forEach(alert => {
                // MAPEAMENTO DOS NOVOS CAMPOS PARA O CARD COM FALLBACKS DEFENSIVOS
                const mappedAlert = {
                    id: alert.id_externo || alert.id || 'unknown',
                    target_profile: alert.candidato_id || 'Desconhecido',
                    text: alert.texto_bruto || 'Sem texto',
                    category: alert.categoria_ia || 'NEUTRO',
                    is_critical: alert.is_hate || false,
                    source: alert.plataforma || 'IG',
                    timestamp: alert.data_publicacao || new Date().toISOString(),
                    target_avatar_url: "./assets/sentinela_small.webp"
                };
                feedContainer.innerHTML += renderThreatCard(mappedAlert);
            });
        } else {
            feedContainer.innerHTML = '<p class="text-center text-slate-400 text-sm py-8">Nenhum alerta encontrado no banco.</p>';
        }

        // B. CALCULAR ALVOS CRÍTICOS (Agora baseado na tabela comentarios)
        const { data: targetsData, error: targetsError } = await supabaseClient
            .from('comentarios') // MUDOU AQUI
            .select('candidato_id, categoria_ia') // MUDOU AQUI
            .not('categoria_ia', 'eq', 'NEUTRO');

        if (targetsError) throw targetsError;

        const profileCounts = {};
        targetsData.forEach(curr => {
            if (curr.categoria_ia !== 'NEUTRO' && curr.candidato_id) {
                profileCounts[curr.candidato_id] = (profileCounts[curr.candidato_id] || 0) + 1;
            }
        });

        const targetsArray = Object.entries(profileCounts).map(([profile, count]) => ({ profile, threat_count: count }));
        targetsArray.sort((a, b) => b.threat_count - a.threat_count);
        const maxThreats = targetsArray.length > 0 ? targetsArray[0].threat_count : 1;
        const finalTargets = targetsArray.map(t => ({ ...t, max_threats: maxThreats }));

        renderHotTargets(finalTargets);

        // C. ATUALIZAR KPIs
        document.getElementById('kpi-monitorados').innerText = new Set(alerts.map(a => a.candidato_id)).size; // MUDOU AQUI
        document.getElementById('kpi-hate').innerText = alerts.filter(a => a.is_hate).length; // MUDOU AQUI
        document.getElementById('kpi-total').innerText = alerts.length;
        document.getElementById('kpi-res').innerText = '99.8%';

    } catch (err) {
        console.error("❌ Falha geral:", err);
        feedContainer.innerHTML = '<p class="text-center text-red-500 text-sm py-8">Erro ao buscar dados. Verifique o Console (F12).</p>';
    } finally {
        if(skeleton) skeleton.style.display = 'none';
        if (window.lucide) lucide.createIcons();
    }
}

// 5. NAVEGAÇÃO SPA (Single Page Application)
// ==========================================
// ROUTER - Controlador de Navegação da Sidebar
// ==========================================
function setupSidebarNavigation() {
    const navItems = document.querySelectorAll('.side-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault(); // Impede o comportamento padrão do link

            // 1. Remove a classe 'active' de todos os itens do menu
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // 2. Adiciona 'active' ao item clicado
            item.classList.add('active');

            // 3. Determina qual seção mostrar baseado no href ou id
            const targetId = item.getAttribute('href')?.replace('#', 'view-') || item.id.replace('nav-', 'view-');
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                // Esconde todas as seções
                document.querySelectorAll('.view-content').forEach(section => {
                    section.classList.remove('active-view');
                    // Garante que a seção ocupe espaço apenas quando ativa
                    section.style.display = 'none';
                });

                // Mostra a seção alvo
                targetSection.classList.add('active-view');
                targetSection.style.display = 'block';

                // 4. Atualiza a URL
                const hash = item.getAttribute('href') || `#${item.id.replace('nav-', '')}`;
                history.pushState(null, '', hash);
            }
        });
    });

    // Lida com o botão "Voltar" do navegador
    window.addEventListener('popstate', () => {
        const hash = location.hash || '#monitor';
        const activeLink = document.querySelector(`.side-nav .nav-item[href="${hash}"]`);
        if (activeLink) activeLink.click();
    });
}

// 6. INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', () => {
    // Inicializa as funcionalidades PASA v24 (XP, Sessions, CB)
    initPasaDashboard();

    // Inicializa os dados do Dashboard
    loadSentinelaDashboard();

    // Inicializa a navegação da Sidebar
    setupSidebarNavigation();

    // Carrega a view correta baseada na URL inicial (ex: se abrir #networks)
    const initialHash = location.hash || '#monitor';
    const initialLink = document.querySelector(`.side-nav .nav-item[href="${initialHash}"]`);
    
    if (initialLink) {
        initialLink.click();
    } else {
        // Fallback para o monitor se a URL tiver um hash inválido
        const monitorNav = document.getElementById('nav-monitor') || document.querySelector('.side-nav .nav-item[href="#monitor"]');
        if (monitorNav) monitorNav.click();
    }
});
