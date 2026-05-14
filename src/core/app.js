// src/core/app.js

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
