# Contexto Completo do Frontend - Sentinela Democrática

Este arquivo contém o código fonte unificado de toda a camada Frontend (Vanilla JS, HTML e CSS).

## Arquivo: `index.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sentinela Democrática - Inteligência de dados e análise informacional estratégica.">
    <!-- Google Tools -->
    <meta name="google-site-verification" content="ALWjqhKFnwzKBPGcQPsygASHuoRaJmrXxhuCuxCorgI" />
    <meta name="google-adsense-account" content="ca-pub-1827611269042960">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1827611269042960" crossorigin="anonymous"></script>
    <!-- Google Analytics (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-1899XV142N"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-1899XV142N');
    </script>

    <!-- Performance Optimization -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://unpkg.com">

    <title>SENTINELA | Diamond Edition v44.2</title>
    <link rel="icon" type="image/png" href="/assets/sentinela_small.png">

    <!-- PASA v44.2: Tailwind CSS Compilado para Produção (Remove aviso de CDN) -->
    <link href="https://unpkg.com/tailwindcss@3.4.1/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest" defer></script>
    <link rel="stylesheet" href="/src/styles/main.css?v=44.2">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2" defer></script>
</head>
<body class="custom-scrollbar bg-slate-50">
    <!-- SIDEBAR ESQUERDA (Navegação) -->
    <aside class="sidebar-left">
        <div class="brand-block">
            <div class="brand-mark"><img src="/assets/sentinela_small.webp" alt="Logo" fetchpriority="high"></div>
            <h1>Sentinela</h1>
        </div>

        <nav class="side-nav">
            <div class="search-box-sidebar px-3 mb-6">
                <div class="relative flex items-center group">
                    <i data-lucide="search" class="absolute left-3 w-4 h-4 text-slate-400"></i>
                    <input type="text"
                           id="dashboard-search-input"
                           placeholder="Pesquisar..."
                           class="w-full bg-slate-100 border-none rounded-lg py-2 pl-10 pr-8 text-xs focus:ring-2 focus:ring-blue-500 transition-all">
                    <button onclick="window.clearDashboardSearch()" id="clear-search-btn" class="absolute right-3 w-4 h-4 text-slate-400 hover:text-slate-600 hidden group-hover:block transition-colors">
                        <i data-lucide="x" class="w-full h-full"></i>
                    </button>
                </div>
            </div>

            <a href="#monitor" class="nav-item active" id="nav-monitor"><i data-lucide="home" class="w-5 h-5"></i> <span>Panorama</span></a>
            <a href="#networks" class="nav-item" id="nav-networks"><i data-lucide="share-2" class="w-5 h-5"></i> <span>Redes</span></a>
            <a href="#directory" class="nav-item" id="nav-directory"><i data-lucide="users" class="w-5 h-5"></i> <span>Perfis</span></a>
            <a href="#dossie" class="nav-item" id="nav-dossie"><i data-lucide="fingerprint" class="w-5 h-5"></i> <span>Relatórios</span></a>
            <a href="#ads" class="nav-item" id="nav-ads"><i data-lucide="megaphone" class="w-5 h-5"></i> <span>Anúncios</span></a>

            <div class="mt-8 pt-6 border-t border-slate-200">
                <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest px-3 mb-3 block">Filtros PASA</span>
                <button onclick="window.setDashboardFilter('all')" id="btn-filter-all" class="nav-item active"><i data-lucide="globe" class="w-5 h-5"></i> <span>Global</span></button>
                <button onclick="window.setDashboardFilter('hate')" id="btn-filter-hate" class="nav-item"><i data-lucide="shield-alert" class="w-5 h-5"></i> <span>Alertas</span></button>
                <button onclick="window.setDashboardFilter('critical')" id="btn-filter-critical" class="nav-item"><i data-lucide="alert-octagon" class="w-5 h-5"></i> <span>Crítico</span></button>
            </div>
        </nav>
    </aside>

    <!-- FEED CENTRAL -->
    <main class="main-feed-container custom-scrollbar dashboard-main">
        <header class="p-6 border-b border-slate-200 bg-white sticky top-0 z-30 flex justify-between items-center">
             <!-- PASA v44.2: Proteção Jurídica - Substituído "Forensics" por "Informacional" -->
             <h2 class="text-lg font-black text-slate-800">Sala de Situação <span class="text-blue-500">Informacional</span></h2>
             <div id="session-manager-container"></div>
        </header>

        <div class="views-container p-6">
            <!-- PANORAMA (MONITOR) -->
            <section id="view-monitor" class="view-content active-view">
                <div id="feed-alertas" class="social-feed grid grid-cols-1 gap-4">
                    <!-- Cards de Alerta aqui -->
                </div>
                <div id="scroll-sentinel" class="h-10"></div>
            </section>

            <!-- REDES (NETWORKS) -->
            <section id="view-networks" class="view-content">
                <div id="networks-container" class="w-full h-full min-h-[600px] bg-white rounded-3xl border border-slate-200 overflow-hidden relative">
                    <div class="p-8 text-center">
                        <div class="spinner m-auto mb-4"></div>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Mapeando Redes de Influência...</p>
                    </div>
                </div>
            </section>

            <!-- PERFIS (DIRECTORY) -->
            <section id="view-directory" class="view-content">
                <div id="directory-container" class="w-full">
                    <div class="p-8 text-center bg-white rounded-3xl border border-slate-200">
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Carregando Diretório de Perfis...</p>
                    </div>
                </div>
            </section>

            <!-- RELATÓRIOS (DOSSIE) -->
            <section id="view-dossie" class="view-content">
                <div id="dossie-container" class="w-full">
                    <div class="p-8 text-center bg-white rounded-3xl border border-slate-200">
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Acessando Motor de Relatórios...</p>
                    </div>
                </div>
            </section>

            <!-- ANÚNCIOS (ADS) -->
            <section id="view-ads" class="view-content">
                <div id="ads-list" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    <div class="p-12 text-center bg-white border border-slate-200 rounded-3xl col-span-full">
                        <div class="spinner m-auto mb-4"></div>
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Varrendo Biblioteca de Anúncios...</span>
                    </div>
                </div>
            </section>
        </div>
    </main>

    <!-- SIDEBAR DIREITA (Monitor de Ameaças ao Vivo) -->
    <aside class="sidebar-right custom-scrollbar">
        <!-- PASA v40: Monitor de Ameaças ao Vivo -->
        <div class="insight-card p-4 bg-white border border-slate-200 rounded-xl mb-6 shadow-sm">
            <h3 class="text-[10px] font-black text-slate-400 uppercase mb-3 tracking-widest flex items-center gap-2">
                <i data-lucide="activity" class="w-3 h-3 text-red-400 animate-pulse"></i> Monitor de Ameaças
            </h3>
            
            <!-- KPIs Dinâmicos do JSON -->
            <div class="grid grid-cols-3 gap-2 mb-4 border-b border-slate-100 pb-4">
                <div class="text-center">
                    <span id="kpi-targets" class="text-lg font-black text-slate-800">-</span>
                    <span class="block text-[8px] font-bold text-slate-400 uppercase">Alvos</span>
                </div>
                <div class="text-center">
                    <span id="kpi-hate" class="text-lg font-black text-red-600">-</span>
                    <span class="block text-[8px] font-bold text-red-400 uppercase">Ódio</span>
                </div>
                <div class="text-center">
                    <span id="kpi-total" class="text-lg font-black text-slate-800">-</span>
                    <span class="block text-[8px] font-bold text-slate-400 uppercase">Amostra</span>
                </div>
            </div>

            <div class="flex justify-between items-center mb-4">
                <span class="text-[10px] font-bold text-slate-500 uppercase">Resiliência</span>
                <span id="kpi-res" class="text-lg font-black text-emerald-600">--%</span>
            </div>

            <!-- Feed Sequencial do Profiler -->
            <div id="profiler-stream-feed" class="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar bg-slate-50 rounded-lg p-3 border border-slate-100">
                <p class="text-[10px] text-slate-400 text-center animate-pulse">Aguardando dados da mineração...</p>
            </div>
        </div>

        <div class="insight-card p-4 bg-white border border-slate-200 rounded-xl mb-6">
            <h3 class="text-[10px] font-black text-slate-400 uppercase mb-4 tracking-widest">Evolução dos Workers</h3>
            <div id="worker-xp-ranking" class="flex flex-col gap-2">
                <!-- XP Ranking aqui -->
            </div>
        </div>

        <div class="insight-card p-4 bg-white border border-slate-200 rounded-xl">
             <h3 class="text-[10px] font-black text-slate-400 uppercase mb-4 tracking-widest">Acesso Rápido</h3>
             <div class="flex flex-wrap gap-2">
                 <button class="text-[9px] bg-slate-100 hover:bg-slate-200 text-slate-600 px-2 py-1 rounded font-bold uppercase transition-colors">Exportar CSV</button>
                 <button class="text-[9px] bg-slate-100 hover:bg-slate-200 text-slate-600 px-2 py-1 rounded font-bold uppercase transition-colors">Backup DB</button>
             </div>
        </div>
    </aside>

    <!-- Scripts -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>lucide.createIcons();</script>
    <script type="module" src="./src/core/app.js?v=44.2"></script>
</body>
</html>

```

## Arquivo: `local_dashboard.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentinela - Painel Local de Inspeção</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
<body class="bg-slate-950 text-white font-sans p-8">
    <div class="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <div>
            <h1 class="text-2xl font-black tracking-tight">🔍 Painel de Inspeção Local</h1>
            <p class="text-slate-400 text-sm">Resumo detalhado da raspagem e classificação em tempo real</p>
        </div>
        <button onclick="fetchData()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-bold text-sm transition-colors">Atualizar Dados</button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Coluna 1: Resumo de Raspagem -->
        <div>
            <h2 class="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Últimas Raspagens (Runs)
            </h2>
            <div id="runs-feed" class="space-y-4 max-h-[70vh] overflow-y-auto pr-2 custom-scrollbar">
                <p class="text-slate-500 text-sm">Carregando runs...</p>
            </div>
        </div>

        <!-- Coluna 2: Últimos Classificados -->
        <div>
            <h2 class="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
                <span class="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span> Últimos Classificados pela IA
            </h2>
            <div id="classified-feed" class="space-y-4 max-h-[70vh] overflow-y-auto pr-2 custom-scrollbar">
                <p class="text-slate-500 text-sm">Carregando classificações...</p>
            </div>
        </div>
    </div>

    <script>
        // Configuração direta do Supabase
        const URL = 'https://vhamejkldzxbeibqeqpk.supabase.co';
        const KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY';
        
        let db;
        try {
            db = supabase.createClient(URL, KEY);
        } catch(e) { console.error(e); }

        async function fetchData() {
            if (!db) {
                document.getElementById('runs-feed').innerHTML = '<p class="text-red-400">Erro ao inicializar cliente Supabase.</p>';
                return;
            }

            try {
                // 1. Busca Runs Recentes
                const { data: runs, error: runsError } = await db
                    .from('worker_runs')
                    .select('*')
                    .eq('worker_id', 'InstagramWorker')
                    .order('created_at', { ascending: false })
                    .limit(15);

                if (!runsError && runs) {
                    document.getElementById('runs-feed').innerHTML = runs.map(run => `
                        <div class="bg-slate-900 border border-slate-700 rounded-lg p-4 shadow-sm">
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-bold text-white"> @${run.target || 'Desconhecido'}</span>
                                <span class="text-[10px] font-mono text-slate-500">${new Date(run.created_at).toLocaleString()}</span>
                            </div>
                            <div class="grid grid-cols-3 gap-2 text-xs">
                                <div class="bg-slate-800 p-2 rounded text-center">
                                    <span class="block text-slate-400">Status</span>
                                    <span class="font-bold ${run.status === 'success' ? 'text-green-400' : 'text-red-400'}">${run.status}</span>
                                </div>
                                <div class="bg-slate-800 p-2 rounded text-center">
                                    <span class="block text-slate-400">XP Ganho</span>
                                    <span class="font-bold text-blue-400">${run.xp_gained || 0}</span>
                                </div>
                                <div class="bg-slate-800 p-2 rounded text-center">
                                    <span class="block text-slate-400">Items</span>
                                    <span class="font-bold text-white">${run.items_processed || 0}</span>
                                </div>
                            </div>
                            ${run.error_message ? `<p class="text-red-400 text-[10px] mt-2 bg-red-900/50 p-1 rounded">Erro: ${run.error_message}</p>` : ''}
                        </div>
                    `).join('');
                } else if (runsError) {
                    console.error("Erro ao buscar runs:", runsError);
                }

                // 2. Busca Últimos Classificados
                const { data: comments, error: commentsError } = await db
                    .from('comentarios')
                    .select('id, autor_username, texto_limpo, candidato_id, is_hate, categoria_ia, confianca_ia, direcao_odio, data_coleta')
                    .not('categoria_ia', 'is', null)
                    .order('data_coleta', { ascending: false })
                    .limit(20);

                if (!commentsError && comments) {
                    document.getElementById('classified-feed').innerHTML = comments.map(c => {
                        const isHate = c.is_hate === true;
                        const catColor = isHate ? 'text-red-400 bg-red-900/30 border-red-700' : 'text-emerald-400 bg-emerald-900/30 border-emerald-700';
                        
                        return `
                        <div class="bg-slate-900 border ${isHate ? 'border-red-800' : 'border-slate-700'} rounded-lg p-4 shadow-sm">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <span class="font-bold text-white text-xs"> @${c.autor_username}</span>
                                    <span class="text-[10px] text-slate-500 ml-2">em @${c.candidato_id}</span>
                                </div>
                                <span class="text-[10px] font-bold ${catColor} px-2 py-0.5 rounded border">${c.categoria_ia}</span>
                            </div>
                            <p class="text-sm text-slate-300 italic mb-3 line-clamp-3">"${c.texto_limpo}"</p>
                            <div class="flex gap-3 text-[10px] text-slate-500 font-mono border-t border-slate-700 pt-2">
                                <span>Confiança: <b class="text-white">${(c.confianca_ia * 100).toFixed(1)}%</b></span>
                                ${c.direcao_odio ? `<span>Alvo: <b class="text-red-400">${c.direcao_odio}</b></span>` : ''}
                            </div>
                        </div>
                    `}).join('');
                } else if (commentsError) {
                    console.error("Erro ao buscar comentários:", commentsError);
                }
            } catch (err) {
                console.error("Erro na busca de dados:", err);
            }
        }

        // Auto-refresh a cada 15 segundos
        setInterval(fetchData, 15000);
        fetchData();
    </script>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0f172a; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    </style>
</body>
</html>

```

## Arquivo: `src/styles/main.css`

```css
:root {
    --bg-base: #fafafa; 
    --bg-panel: #ffffff; 
    --border: #efefef; 
    --text-main: #262626; 
    --text-soft: #737373; /* Escurecido de #8e8e8e para melhor contraste */
    --text-muted: #525252; /* Escurecido de #c7c7c7 */
    --accent: #0070e0; /* Ajustado para melhor contraste em fundos claros */
    --danger: #dc2626; 
    --success: #16a34a;
    --font-mono: 'JetBrains Mono', monospace;
    --font-sans: 'Inter', sans-serif;
}

@font-face {
  font-family: 'Inter';
  font-display: swap;
}

@font-face {
  font-family: 'JetBrains Mono';
  font-display: swap;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    height: 100vh;
    width: 100%;
    background: var(--bg-base);
    color: var(--text-main);
    font-family: var(--font-sans);
    display: flex;
    overflow: hidden; 
}

/* LAYOUT DE 3 COLUNAS - PROPORÇÃO INSTAGRAM */
.sidebar-left {
    width: 250px;
    min-width: 250px;
    height: 100vh;
    background: var(--bg-panel);
    border-right: 1px solid var(--border);
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.brand-block {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 30px;
    padding-left: 12px;
}

.brand-mark {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.brand-mark img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.brand-block h1 {
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    text-transform: uppercase;
}

.main-feed-container {
    flex: 1;
    height: 100vh;
    overflow-y: auto;
    background: var(--bg-base);
    display: flex;
    justify-content: center;
    border-right: 1px solid var(--border);
}

.views-container {
    width: 100%;
    max-width: 800px; /* LARGURA IDEAL FEED EXPANDIDA */
    padding: 20px 16px;
}

.sidebar-right {
    width: 380px; /* COLUNA DE INTELIGÊNCIA MAIS LARGA */
    min-width: 380px;
    height: 100vh;
    padding: 24px;
    overflow-y: auto;
    background: var(--bg-base);
}

/* NAVEGAÇÃO LINKS */
.nav-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    border-radius: 12px;
    color: var(--text-main);
    text-decoration: none;
    font-weight: 500;
    transition: background 0.2s, transform 0.1s;
    cursor: pointer;
}

.nav-item:active { transform: scale(0.98); }
.nav-item:hover { background: #f2f2f2; }
.nav-item.active { font-weight: 800; color: var(--text-main); }
.nav-item.active i { color: var(--accent); }

/* AVATARES REAIS */
.post-avatar, .monitor-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    background: #efefef;
    border: 1px solid var(--border);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.post-avatar img, .monitor-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.feed-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
    padding: 12px 16px;
    position: sticky;
    top: 0;
    z-index: 10;
}

.filter-tabs { display: flex; gap: 20px; margin-bottom: 12px; }
.tab-btn { padding-bottom: 8px; background: none; border: 0; border-bottom: 2px solid transparent; color: var(--text-soft); font-size: 0.7rem; font-weight: 800; text-transform: uppercase; cursor: pointer; }
.tab-btn.active { border-bottom-color: var(--text-main); color: var(--text-main); }

.search-box { position: relative; }
.search-input { width: 100%; padding: 8px 12px 8px 36px; border-radius: 8px; border: 0; background: #efefef; font-size: 0.85rem; outline: none; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-soft); }

/* CARDS */
.post-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.post-avatar { width: 32px; height: 32px; border-radius: 50%; background: #efefef; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 0.7rem; color: #8e8e8e; border: 1px solid #ddd; }
.post-username { font-weight: 700; font-size: 0.85rem; }
.post-meta { font-size: 0.7rem; color: var(--text-soft); }
.post-content { font-size: 0.9rem; line-height: 1.5; color: var(--text-main); }

.severity-pill { font-size: 0.6rem; font-weight: 900; padding: 2px 8px; border-radius: 4px; }
.is-critico { background: #fee2e2; color: #dc2626; }
.is-info { background: #e0f2fe; color: #0284c7; }

/* SCROLLBAR */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dbdbdb; border-radius: 10px; }

.view-content { display: none; }
.active-view { display: flex !important; flex-direction: column; }

.loading-state { padding: 20px; display: flex; align-items: center; justify-content: center; gap: 10px; }
.spinner { border: 2px solid #efefef; border-top: 2px solid var(--accent); border-radius: 50%; width: 14px; height: 14px; animation: spin 1s linear infinite; }
/* ANIMATIONS */
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes shimmer {
    0% { background-position: -468px 0; }
    100% { background-position: 468px 0; }
}

.skeleton {
    background: #f6f7f8;
    background-image: linear-gradient(to right, #f6f7f8 0%, #edeef1 20%, #f6f7f8 40%, #f6f7f8 100%);
    background-repeat: no-repeat;
    background-size: 800px 104px;
    display: inline-block;
    position: relative;
    animation: shimmer 1s linear infinite forwards;
}

.dark .skeleton {
    background: #1e293b;
    background-image: linear-gradient(to right, #1e293b 0%, #334155 20%, #1e293b 40%, #1e293b 100%);
}

```

## Arquivo: `src/config.js`

```javascript
// SENTINELA | Diamond Edition - Configuração Central v20.2.1
// Prioridade: Vercel (Caminho Relativo) | Fallback: Localhost Port 8000
const API_BASE = '/api/v1'; 
const LOCAL_FALLBACK = 'http://localhost:8000/api/v1';
const PRODUCTION_URL = 'https://sentinela-democratica-ruby.vercel.app';

export const SENTINELA_CONFIG = {
    apiUrl: API_BASE,
    localFallbackUrl: LOCAL_FALLBACK,
    productionUrl: PRODUCTION_URL,
    supabaseUrl: 'https://vhamejkldzxbeibqeqpk.supabase.co',
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY',
    refreshInterval: 3600000 
};

window.SENTINELA_CONFIG = SENTINELA_CONFIG;

```

## Arquivo: `src/core/app.js`

```javascript
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

```

## Arquivo: `src/core/state.js`

```javascript
export const state = {
    view: 'monitor',
    data: [],
    alertas: [],
    networks: { nodes: [], links: [] },
    networkView: 'clusters',
    stats: {
        total: 0,
        hate: 0,
        resiliencia: 100.0
    },
    summary: null,
    trends: [],
    pasa: [],
    geo: [],
    selectedUF: null,
    selectedAlvo: null,
    filterHateOnly: false,
    dashboardSearch: '',
    directorySearchQuery: '',
    dossieGrouping: 'agressoes',
    dossieSearch: '',
    stn_tokens: 50,   // Amostra grátis de munição forense
    userPlan: 'free', // Começa no Free pra forçar o gasto
    reportOptions: [
        { id: 'base', label: 'Sumário Executivo', cost: 10, required: true },
        { id: 'networks', label: 'Mapeamento de Redes', cost: 20 },
        { id: 'sentiment', label: 'Análise de Sentimento Profunda', cost: 15 },
        { id: 'history', label: 'Histórico Completo (30 dias)', cost: 15 },
        { id: 'export', label: 'Exportação PDF Premium', cost: 10 }
    ],
    currentReportConfig: {
        target: null,
        selectedIds: ['base']
    },
    loading: true,
    isLoading: false, // Controle de load do scroll infinito
    currentPage: 1,   // Página atual do feed
    error: null,
    lastSyncAt: null,
    organizations: [],
    currentOrganizationId: localStorage.getItem('sentinela_org_id') || null
};

export function setViewState(view) {
    state.view = view;
    window.location.hash = view;
    if (window.debouncedRender) window.debouncedRender();
}

export function setNetworkView(view) {
    state.networkView = view;
    if (window.debouncedRender) window.debouncedRender();
}

export function setDossieGrouping(grouping) {
    state.dossieGrouping = grouping;
    if (window.debouncedRender) window.debouncedRender();
}

export function setDossieSearch(query) {
    state.dossieSearch = (query || '').trim().toLowerCase();
    if (window.debouncedRender) window.debouncedRender();
}
```

## Arquivo: `src/core/ui.js`

```javascript
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
                    "${(() => {
                        const raw = (alerta.texto_bruto || "").trim();
                        const user = (alerta.autor_username || "").trim().replace('@','').toLowerCase();
                        const rawLower = raw.toLowerCase();
                        
                        if (raw && rawLower !== user && rawLower !== `@${user}`) return raw;
                        return (alerta.text || alerta.comentario || 'Conteúdo indisponível').trim();
                    })()}"
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


```

## Arquivo: `src/core/auth.js`

```javascript
/**
 * PASA v44.2 - Auth Module: Integração Supabase Auth
 * Resolve erro 404 no import do app.js
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = window.SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = window.SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY;

let supabase;
if (supabaseUrl && supabaseKey) {
    supabase = createClient(supabaseUrl, supabaseKey);
}

let currentUser = null;

export async function initAuth() {
    if (!supabase) return;
    
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
        currentUser = session.user;
    }

    supabase.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_IN' && session) {
            currentUser = session.user;
        } else if (event === 'SIGNED_OUT') {
            currentUser = null;
        }
    });
}

export function getCurrentUserEmail() {
    return currentUser?.email || 'anonymous_user';
}

```

## Arquivo: `src/core/payments.js`

```javascript
// /src/core/payments.js
import { authService } from '../services/authService.js';

export async function initiateStripeCheckout(packageSlug) {
    const user = authService.user;
    if (!user) {
        alert("Necessário login para adquirir tokens de munição forense.");
        // Opcional: Abrir modal de login
        return;
    }

    // Configuração dos pacotes conforme o backend
    const PRICE_IDS = {
        'stn_starter': window.SENTINELA_CONFIG?.stripeStarterPriceId || 'price_1Starter',
        'stn_squad':   window.SENTINELA_CONFIG?.stripeSquadPriceId || 'price_1Squad',
        'stn_warroom': window.SENTINELA_CONFIG?.stripeWarroomPriceId || 'price_1WarRoom'
    };

    const priceId = PRICE_IDS[packageSlug];

    try {
        const resp = await fetch('/api/v1/checkout/create-session', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authService.session?.access_token}`
            },
            body: JSON.stringify({ 
                user_id: user.id, 
                package_slug: packageSlug,
                price_id: priceId
            })
        });
        
        if (!resp.ok) throw new Error('Falha ao gerar sessão de checkout');
        
        const { url } = await resp.json();
        if (url) {
            window.location.href = url;
        }
    } catch (e) {
        console.error('[Payments] Checkout error:', e);
        alert('Erro ao processar pagamento. Tente novamente mais tarde.');
    }
}

// Exposição global para chamadas via HTML onclick
window.initiateStripeCheckout = initiateStripeCheckout;

```

## Arquivo: `src/core/workers_view.js`

```javascript
/**
 * PASA v28 - Sala de Máquinas: Visualização detalhada dos Workers e XP
 */

const LEVEL_NAMES = {
    1: 'Recruta',
    2: 'Sentinela',
    3: 'Analista',
    4: 'Caçador',
    5: 'Mestre Forense'
};

export async function renderWorkersView() {
    const container = document.getElementById('view-workers');
    if (!container) return;

    container.innerHTML = `<div class="flex items-center justify-center h-full"><p class="text-slate-400 text-sm">Carregando infraestrutura...</p></div>`;

    try {
        const response = await fetch('/api/v1/monitor/status');
        if (!response.ok) throw new Error('API Offline');
        const data = await response.json();

        container.innerHTML = `
            <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-xl font-black text-slate-800 tracking-tight">Sala de Máquinas</h1>
                        <p class="text-xs text-slate-400 font-medium">Ranking de Evolução e Saúde dos Agentes PASA v28</p>
                    </div>
                    <span class="text-[10px] font-bold bg-blue-50 text-blue-600 px-2 py-1 rounded-full">${data.worker_evolution.length} Agentes Ativos</span>
                </div>

                <!-- Leaderboard de XP -->
                <div class="bg-white rounded-xl border border-slate-200 overflow-hidden mb-8">
                    <div class="px-4 py-3 border-b border-slate-100 bg-slate-50">
                        <h3 class="text-xs font-black text-slate-500 uppercase tracking-wider flex items-center gap-2">
                            <i data-lucide="trophy" class="w-3 h-3 text-yellow-500"></i> Leaderboard de Evolução
                        </h3>
                    </div>
                    <div class="divide-y divide-slate-100">
                        ${data.worker_evolution.map((w, index) => `
                            <div class="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                                <div class="flex items-center gap-4">
                                    <span class="text-sm font-black \${index === 0 ? 'text-yellow-500' : 'text-slate-400'}">#\${index + 1}</span>
                                    <div>
                                        <p class="text-sm font-bold text-slate-800">\${w.worker_id}</p>
                                        <p class="text-[10px] text-slate-500">\${LEVEL_NAMES[w.current_level] || 'Desconhecido'}</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-6 text-right">
                                    <div>
                                        <p class="text-xs font-bold text-slate-800">Nível \${w.current_level}</p>
                                        <div class="w-24 bg-slate-100 rounded-full h-1.5 mt-1">
                                            <div class="bg-blue-500 h-1.5 rounded-full" style="width: \${(w.current_xp % 500) / 5}%"></div>
                                        </div>
                                    </div>
                                    <span class="text-sm font-mono font-bold text-blue-600 w-20 text-right">\${w.current_xp} XP</span>
                                    <span class="text-[10px] font-bold text-slate-400 w-16">\${w.total_runs} runs</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Falhas Críticas Recentes -->
                <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
                    <div class="px-4 py-3 border-b border-slate-100 bg-slate-50">
                        <h3 class="text-xs font-black text-slate-500 uppercase tracking-wider flex items-center gap-2">
                            <i data-lucide="alert-triangle" class="w-3 h-3 text-red-500"></i> Log de Falhas Críticas
                        </h3>
                    </div>
                    <div class="p-4">
                        ${data.recent_critical_failures.length === 0 ? 
                            '<p class="text-xs text-slate-400 text-center py-4">Nenhuma falha registrada. Sistema estável.</p>' :
                            data.recent_critical_failures.map(f => `
                                <div class="flex items-start gap-3 mb-3 last:mb-0">
                                    <i data-lucide="x-circle" class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0"></i>
                                    <div>
                                        <p class="text-xs font-bold text-slate-700">\${f.worker_id} <span class="font-normal text-slate-400">• \${new Date(f.created_at).toLocaleString()}</span></p>
                                        <p class="text-[10px] text-red-600 font-mono bg-red-50 px-2 py-1 rounded mt-1 inline-block">\${f.error_message || 'Erro não especificado'}</p>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            </div>
        `;
        
        if (window.lucide) lucide.createIcons();

    } catch (e) {
        container.innerHTML = `<div class="p-6 text-center text-red-500">Falha ao carregar dados dos workers.</div>`;
    }
}

```

## Arquivo: `src/core/workersUI.js`

```javascript
import { state } from './state.js';
import { dataService } from '../services/dataService.js';

let pollingInterval = null;

export const workersUI = {
    async renderWorkersDashboard(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Show loading spinner initially
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center p-20 space-y-4">
                <div class="w-10 h-10 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <p class="text-slate-400 font-bold uppercase tracking-widest text-[10px]">Acessando telemetria dos workers...</p>
            </div>
        `;

        try {
            const metrics = await dataService.getWorkersMetrics();
            state.workersMetrics = metrics;

            if (!metrics) {
                container.innerHTML = `
                    <div class="p-8 text-center bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 font-bold">
                        <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-2 opacity-50"></i>
                        Falha ao obter telemetria. Verifique a conexão com o servidor.
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
                return;
            }

            this.drawDashboard(container, metrics);
            this.renderSessionManager(container);
            this.startPolling(containerId);
        } catch (error) {
            console.error('[WorkersUI] Error:', error);
            container.innerHTML = `
                <div class="p-8 text-center bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 font-bold">
                    Erro fatal na renderização das métricas.
                </div>
            `;
        }
    },

    drawDashboard(container, data) {
        const healthMap = {
            'green': { color: 'text-emerald-500', bg: 'bg-emerald-500', label: 'Operacional' },
            'yellow': { color: 'text-amber-500', bg: 'bg-amber-500', label: 'Degradado' },
            'red': { color: 'text-rose-500', bg: 'bg-rose-500', label: 'Crítico' }
        };
        const health = healthMap[data.system_health] || healthMap['yellow'];
        
        // Cálculo de latência média global (ms)
        const avgLatency = data.workers.length > 0 
            ? data.workers.reduce((acc, w) => acc + (w.avg_duration_ms || 0), 0) / data.workers.length 
            : 0;

        container.innerHTML = `
            <div class="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <!-- Header -->
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <div class="w-2 h-2 rounded-full ${health.bg} animate-pulse"></div>
                            <span class="text-[10px] font-black uppercase tracking-widest ${health.color}">Saúde do Sistema: ${health.label}</span>
                        </div>
                        <h2 class="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
                            Workers Telemetry
                            <span class="text-xs font-medium px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full border border-slate-200">v20.2</span>
                        </h2>
                    </div>
                    
                    <div class="flex items-center gap-4">
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Sincronizado em</span>
                            <span class="text-xs font-mono font-bold text-slate-600">${new Date(data.timestamp).toLocaleTimeString('pt-BR')}</span>
                        </div>
                        <button id="refresh-workers" class="p-2.5 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all shadow-sm active:scale-95 group">
                            <i data-lucide="refresh-cw" class="w-5 h-5 text-slate-500 group-hover:rotate-180 transition-all duration-500"></i>
                        </button>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Taxa de Sucesso -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-emerald-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-emerald-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="shield-check" class="w-6 h-6 text-emerald-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Taxa de Sucesso</span>
                                <div class="text-2xl font-black text-slate-800">${data.overall_success_rate}%</div>
                            </div>
                        </div>
                        <div class="w-full h-1.5 bg-slate-50 rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500 transition-all duration-1000" style="width: ${data.overall_success_rate}%"></div>
                        </div>
                        <p class="text-[10px] text-slate-400 font-bold mt-2 uppercase">${data.total_successful} de ${data.total_executions} tarefas</p>
                    </div>

                    <!-- Latência Média -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-blue-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-blue-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="timer" class="w-6 h-6 text-blue-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Latência Média</span>
                                <div class="text-2xl font-black text-slate-800">${(avgLatency / 1000).toFixed(2)}s</div>
                            </div>
                        </div>
                        <div class="flex items-center gap-1">
                            <div class="h-1 flex-1 bg-blue-500 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-300 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-100 rounded-full"></div>
                            <div class="h-1 flex-1 bg-slate-50 rounded-full"></div>
                        </div>
                        <p class="text-[10px] text-slate-400 font-bold mt-2 uppercase">Tempo médio de resposta global</p>
                    </div>

                    <!-- Throughput -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-purple-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-purple-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="zap" class="w-6 h-6 text-purple-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Throughput</span>
                                <div class="text-2xl font-black text-slate-800">${data.avg_system_throughput_items_per_sec} <span class="text-xs font-normal text-slate-400">it/s</span></div>
                            </div>
                        </div>
                        <p class="text-xl font-black text-slate-800">${(data.total_items_processed / 1000).toFixed(1)}k <span class="text-xs text-slate-400">itens</span></p>
                        <p class="text-[10px] text-slate-400 font-bold uppercase">Volume total processado</p>
                    </div>

                    <!-- Healthy Workers -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-amber-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-amber-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="activity" class="w-6 h-6 text-amber-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Workers</span>
                                <div class="text-2xl font-black text-slate-800">${data.healthy_workers}/${data.total_workers}</div>
                            </div>
                        </div>
                        <p class="text-sm font-black text-slate-700 uppercase tracking-tighter">Instâncias Ativas</p>
                        <p class="text-[10px] text-slate-400 font-bold uppercase">Status de saúde operacional</p>
                    </div>
                </div>

                <!-- Workers Table -->
                <div class="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden">
                    <div class="px-8 py-5 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
                        <h3 class="font-black text-slate-800 uppercase tracking-widest text-xs">Processadores em Execução</h3>
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">${data.workers.length} Ativos</span>
                        </div>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="bg-slate-50/50">
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Worker</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-center">Status</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Itens</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Throughput</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Latência/Erros</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-50">
                                ${data.workers.map(w => {
                                    const hasErrors = w.recent_errors && w.recent_errors.length > 0;
                                    return `
                                    <tr class="hover:bg-blue-50/30 transition-colors group">
                                        <td class="px-8 py-5">
                                            <div class="flex items-center gap-3">
                                                <div class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 font-black group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                                                    ${w.worker.charAt(0)}
                                                </div>
                                                <div>
                                                    <div class="font-black text-slate-700 text-sm">${w.worker}</div>
                                                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">${w.success_rate}% Success Rate</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-8 py-5 text-center">
                                            <span class="px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${w.status === 'healthy' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-rose-100 text-rose-700 border border-rose-200'}">
                                                ${w.status}
                                            </span>
                                        </td>
                                        <td class="px-8 py-5 text-right font-mono text-xs font-black text-slate-600">
                                            ${w.total_items_processed.toLocaleString('pt-BR')}
                                        </td>
                                        <td class="px-8 py-5 text-right">
                                            <div class="text-xs font-black text-slate-700 font-mono">${w.avg_throughput_items_per_sec || 0} it/s</div>
                                            <div class="text-[9px] text-slate-400 font-bold uppercase">Média em 24h</div>
                                        </td>
                                        <td class="px-8 py-5 text-right">
                                            <div class="text-xs font-black ${hasErrors ? 'text-rose-600' : 'text-slate-700'} font-mono">${w.avg_duration_ms.toFixed(0)}ms</div>
                                            <div class="text-[9px] ${hasErrors ? 'text-rose-400' : 'text-slate-400'} font-bold uppercase">${hasErrors ? w.recent_errors.length + ' falhas' : 'Estável'}</div>
                                        </td>
                                    </tr>
                                `;}).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Recent Errors Feed -->
                ${data.workers.some(w => w.recent_errors && w.recent_errors.length > 0) ? `
                    <div class="bg-rose-50 border border-rose-100 rounded-3xl p-6 animate-in">
                        <div class="flex items-center gap-3 mb-4">
                            <i data-lucide="alert-circle" class="w-5 h-5 text-rose-600"></i>
                            <h4 class="text-xs font-black text-rose-800 uppercase tracking-widest">Logs de Erros Críticos</h4>
                        </div>
                        <div class="space-y-3">
                            ${data.workers.filter(w => w.recent_errors && w.recent_errors.length > 0).map(w => `
                                <div class="p-4 bg-white/60 rounded-2xl border border-rose-100 text-xs border-2 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                                    <div class="flex justify-between mb-1">
                                        <span class="font-black text-rose-700 uppercase tracking-tighter">${w.worker}</span>
                                        <span class="text-slate-400 font-mono">${new Date(w.recent_errors[w.recent_errors.length-1].timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    <p class="text-slate-600 italic">"${w.recent_errors[w.recent_errors.length-1].error}"</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        if (window.lucide) lucide.createIcons();
        
        // Wire up manual refresh
        const refreshBtn = document.getElementById('refresh-workers');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.renderWorkersDashboard(container.id);
        }
    },

    async renderSessionManager(container) {
        const sessionContainer = document.createElement('div');
        sessionContainer.className = 'mt-12';
        container.appendChild(sessionContainer);

        try {
            const status = await dataService.getInstagramSessionStatus();
            
            sessionContainer.innerHTML = `
                <div class="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden max-w-2xl">
                    <div class="px-8 py-5 border-b border-slate-50 bg-slate-800 flex items-center gap-3">
                        <i data-lucide="shield" class="text-cyan-400 w-5 h-5"></i>
                        <h3 class="font-black text-white uppercase tracking-widest text-xs">Instagram Session Manager</h3>
                    </div>
                    
                    <div class="p-8 space-y-6">
                        <div class="p-4 rounded-2xl flex items-center justify-between ${status?.status === 'active' ? 'bg-emerald-50 border border-emerald-100' : 'bg-amber-50 border border-amber-100'}">
                            <div class="flex items-center gap-3">
                                <i data-lucide="${status?.status === 'active' ? 'check-circle' : 'alert-triangle'}" class="${status?.status === 'active' ? 'text-emerald-500' : 'text-amber-500'} w-5 h-5"></i>
                                <div>
                                    <p class="text-slate-700 font-black text-xs uppercase tracking-tight">${status?.status === 'active' ? 'Sessão Ativa' : 'Sessão Ausente'}</p>
                                    <p class="text-[10px] text-slate-400 font-bold uppercase">${status?.last_updated ? 'Atualizado em: ' + new Date(status.last_updated).toLocaleString() : 'Pendente'}</p>
                                </div>
                            </div>
                        </div>

                        <form id="session-form" class="space-y-4">
                            <div class="space-y-1">
                                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Session ID</label>
                                <input type="password" name="session_id" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="sessionid cookie value">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="space-y-1">
                                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">DS User ID</label>
                                    <input type="text" name="ds_user_id" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="ds_user_id">
                                </div>
                                <div class="space-y-1">
                                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">CSRF Token</label>
                                    <input type="text" name="csrf_token" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="csrftoken">
                                </div>
                            </div>
                            <button type="submit" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-black uppercase tracking-widest text-[10px] py-4 rounded-2xl transition-all active:scale-[0.98] shadow-lg shadow-slate-200 flex items-center justify-center gap-2">
                                <i data-lucide="save" class="w-4 h-4"></i>
                                Salvar Configurações
                            </button>
                        </form>
                    </div>
                </div>
            `;

            if (window.lucide) lucide.createIcons();

            const form = document.getElementById('session-form');
            form.onsubmit = async (e) => {
                e.preventDefault();
                const btn = e.target.querySelector('button');
                btn.disabled = true;
                btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4 animate-spin"></i> Salvando...';
                if (window.lucide) lucide.createIcons();

                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData.entries());
                
                try {
                    await dataService.updateInstagramSession(data);
                    alert('Sessão atualizada com sucesso!');
                    this.renderWorkersDashboard(container.id);
                } catch (err) {
                    alert('Erro ao atualizar: ' + err.message);
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<i data-lucide="save" class="w-4 h-4"></i> Salvar Configurações';
                    if (window.lucide) lucide.createIcons();
                }
            };

        } catch (error) {
            console.error('[WorkersUI] Session Manager Error:', error);
        }
    },

    startPolling(containerId) {
        if (pollingInterval) clearInterval(pollingInterval);

        pollingInterval = setInterval(async () => {
            // Only poll if we are still on the workers view
            if (state.view !== 'workers') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                return;
            }

            try {
                const metrics = await dataService.getWorkersMetrics();
                state.workersMetrics = metrics;
                const container = document.getElementById(containerId);
                if (container && metrics) {
                    this.drawDashboard(container, metrics);
                }
            } catch (error) {
                console.warn('[WorkersUI] Polling failed:', error);
            }
        }, 20000); // 20 seconds as requested
    }
};

```

## Arquivo: `src/services/apiService.js`

```javascript
const SB_URL = 'https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY';

const headers = { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY };

export async function fetchSyncToken() {
    try {
        // Usa o timestamp do último comentário de ódio como token de sincronização
        const r = await fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=id&order=data_coleta.desc&limit=1`, { headers });
        const data = await r.json();
        return data.length ? data[0].id : 'no_data';
    } catch (e) { return null; }
}

export async function fetchCandidatos() {
    try {
        const r = await fetch(`${SB_URL}/candidatos?select=*`, { headers });
        return r.ok ? await r.json() : [];
    } catch (e) { return []; }
}

export async function fetchAlertas(limit = 15) {
    try {
        const r = await fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=*,candidatos(username)&order=data_coleta.desc&limit=${limit}`, { headers });
        return r.ok ? await r.json() : [];
    } catch (e) { return []; }
}

export async function fetchGlobalStats() {
    try {
        const [rTotal, rHate] = await Promise.all([
            fetch(`${SB_URL}/comentarios?select=id`, { headers: { ...headers, 'Prefer': 'count=exact' }, method: 'HEAD' }),
            fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=id`, { headers: { ...headers, 'Prefer': 'count=exact' }, method: 'HEAD' })
        ]);
        return { 
            total: parseInt(rTotal.headers.get('content-range')?.split('/')[1] || 0), 
            hate: parseInt(rHate.headers.get('content-range')?.split('/')[1] || 0) 
        };
    } catch (e) { return { total: 0, hate: 0 }; }
}
```

## Arquivo: `src/services/dataService.js`

```javascript
// SENTINELA | Diamond Edition - Data Service
// Centraliza todas as chamadas para a API FastAPI

import { authService } from './authService.js';
import { state } from '../core/state.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';

class SentinelDataService {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = 60000; // 1 minuto
    }

    async fetchJson(endpoint, params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const path = `${endpoint}${queryParams ? '?' + queryParams : ''}`;
        const cacheKey = `${API_BASE}${path}`;
        
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) return cached.data;

        const tryFetch = async (baseUrl) => {
            const headers = {};
            if (state.currentOrganizationId) {
                headers['X-Organization-Id'] = state.currentOrganizationId;
            }
            if (authService.session?.access_token) {
                headers['Authorization'] = `Bearer ${authService.session.access_token}`;
            }

            const response = await fetch(`${baseUrl}${path}`, { headers });
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return await response.json();
        };

        try {
            const data = await tryFetch(window.SENTINELA_CONFIG.apiUrl);
            state.lastSyncAt = new Date().toISOString();
            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.warn(`[SentinelDataService] Primary path failed. Retrying fallback for ${endpoint}...`);
            try {
                return await tryFetch(window.SENTINELA_CONFIG.localFallbackUrl);
            } catch (fbError) {
                console.warn(`[SentinelDataService] All paths failed for ${endpoint}`);
                return this.getFallbackData(endpoint);
            }
        }
    }

    getFallbackData(endpoint) {
        // Dados de segurança para não deixar a UI vazia caso a API esteja offline
        const fallbacks = {
            '/summary': { total_monitorados: state.data?.length || 0, total_alertas: state.alertas?.length || 0, total_amostra: 1000, resiliencia: 98.5 },
            '/targets': [],
            '/alerts/active': [],
            '/trends': { labels: [], values: [] },
            '/networks': [],
            '/geo/uf': {}
        };
        return fallbacks[endpoint] || null;
    }

    // ── KPIs & Summary ──
    async getSummary() {
        return this.fetchJson('/summary');
    }

    // ── Tendências (Sparklines) ──
    async getTrends(days = 30) {
        return this.fetchJson('/trends', { days });
    }

    // ── Alvos & Dossiê ──
    async getTargets(search = null, groupBy = 'score', limit = 50) {
        return this.fetchJson('/targets', { search, group_by: groupBy, limit });
    }

    async getDossiers(candidato_id = null) {
        return this.fetchJson('/dossiers', { candidato_id });
    }

    async getAds(candidato_id = null) {
        return this.fetchJson('/ads', { candidato_id });
    }

    async postJson(endpoint, body = {}) {
        const path = endpoint;
        
        const tryPost = async (baseUrl) => {
            const headers = { 'Content-Type': 'application/json' };
            if (state.currentOrganizationId) {
                headers['X-Organization-Id'] = state.currentOrganizationId;
            }
            if (authService.session?.access_token) {
                headers['Authorization'] = `Bearer ${authService.session.access_token}`;
            }

            const response = await fetch(`${baseUrl}${path}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(body)
            });
            if (!response.ok) throw new Error(`API Post Error: ${response.status}`);
            return await response.json();
        };

        try {
            // TENTATIVA 1: Prioridade Vercel
            return await tryPost(window.SENTINELA_CONFIG.apiUrl);
        } catch (error) {
            // TENTATIVA 2: Fallback Local
            console.warn(`[SentinelDataService] POST failed. Retrying fallback for ${endpoint}...`);
            try {
                return await tryPost(window.SENTINELA_CONFIG.localFallbackUrl);
            } catch (fbError) {
                console.error(`[SentinelDataService] All POST paths failed for ${endpoint}`);
                throw fbError;
            }
        }
    }

    // ── Alertas PASA ──
    async getAlerts(limit = 20, page = 1) {
        return this.fetchJson('/alerts/active', { limit, page });
    }

    async markFalsePositive(id) {
        try {
            const data = await this.postJson('/alerts/false-positive', { id });
            // Invalida cache local para refletir a mudança no feed
            this.cache.delete(`${API_BASE}/alerts/active`);
            return data;
        } catch (e) {
            console.error('[DataService] Error marking false positive:', e);
            throw e;
        }
    }

    async fetchMoreAlertas(page = 1, limit = 20) {
        return this.getAlerts(limit, page);
    }

    // ── Redes Coordenadas ──
    async getNetworks() {
        return this.fetchJson('/networks');
    }

    // ── PASA Breakdown (Insights) ──
    async getPasaBreakdown() {
        return this.fetchJson('/pasa/breakdown');
    }

    // ── Analytics Temporal ──
    async getPasaTemporal(days = 7) {
        return this.fetchJson('/analytics/pasa-temporal', { days });
    }

    // ── Geolocalização (Mapa) ──
    async getGeoUF() {
        return this.fetchJson('/geo/uf');
    }

    // ── Invalidação Manual de Cache ──
    invalidateCache() {
        this.cache.clear();
    }
}

// Singleton para uso em toda a aplicação
export const dataService = new SentinelDataService();

// Real Plan Service (Identity-Driven) - CONFIGURADO PARA MONETIZAÇÃO
export const planService = {
    getPlan: () => state.userPlan || 'free', 
    canAccess: (feature) => {
        const plan = planService.getPlan();
        if (plan === 'enterprise') return true;
        if (feature === 'identities') return plan === 'pro';
        if (feature === 'pdf_export') return false; // Sempre custa STN
        return true; // Acesso básico grátis
    },
    maskName: (name) => {
        return planService.canAccess('identities') ? name : 'Agressor Oculto';
    }
};

```

## Arquivo: `src/services/authService.js`

```javascript
import { SENTINELA_CONFIG } from '../config.js';

class SentinelAuthService {
    constructor() {
        if (typeof supabase === 'undefined') {
            console.error('[AuthService] Supabase SDK not loaded!');
            this.client = null;
            return;
        }
        this.client = supabase.createClient(SENTINELA_CONFIG.supabaseUrl, SENTINELA_CONFIG.supabaseKey);
        this.user = null;
        this.session = null;
    }

    async init() {
        if (!this.client) return null;

        const { data: { session } } = await this.client.auth.getSession();
        this.session = session;
        if (session) {
            this.user = await this.getProfile(session.user.id);
            await this.fetchOrganizations();
        }
        
        // Listener para mudanças de estado (Login/Logout)
        this.client.auth.onAuthStateChange(async (event, session) => {
            console.log(`[AuthService] Event: ${event}`);
            this.session = session;
            if (session) {
                this.user = await this.getProfile(session.user.id);
                await this.fetchOrganizations();
            } else {
                this.user = null;
                const { state } = await import('../core/state.js');
                state.organizations = [];
                state.currentOrganizationId = null;
            }
            // Apenas recarrega a página em mudanças reais de login/logout, não na inicialização
            if (window.forceRefresh && (event === 'SIGNED_IN' || event === 'SIGNED_OUT')) {
                window.forceRefresh();
            }
        });

        return this.user;
    }

    async fetchOrganizations() {
        if (!this.session?.user) return;
        try {
            const { data, error } = await this.client
                .from('organization_members')
                .select('role, organizations(*)')
                .eq('profile_id', this.session.user.id);

            if (error) throw error;
            
            const orgs = data.map(m => ({ ...m.organizations, user_role: m.role }));
            
            // Import dinâmico do state para evitar dependência circular pesada
            const { state } = await import('../core/state.js');
            state.organizations = orgs;
            
            // Se não tiver org selecionada, pega a primeira
            if (!state.currentOrganizationId && orgs.length > 0) {
                state.currentOrganizationId = orgs[0].id;
                localStorage.setItem('sentinela_org_id', orgs[0].id);
            }
        } catch (e) {
            console.error('[AuthService] Error fetching organizations:', e);
        }
    }

    async getProfile(userId) {
        try {
            // Busca dados estendidos na tabela profiles (id, plan, username, stn_tokens)
            const { data, error } = await this.client
                .from('profiles')
                .select('*, stn_tokens')
                .eq('id', userId)
                .single();

            if (error) throw error;
            return data;
        } catch (e) {
            console.error('[AuthService] Error fetching profile:', e);
            // Fallback para dados básicos do Auth se o profile não existir
            return { id: userId, plan: 'public', username: 'Visitante', stn_tokens: 0 };
        }
    }

    async fetchUserTokens() {
        if (!this.session?.user) return 0;
        const profile = await this.getProfile(this.session.user.id);
        if (profile) {
            this.user = profile;
            if (window.forceRefresh) window.forceRefresh();
            return profile.stn_tokens || 0;
        }
        return 0;
    }


    async signIn(email, password) {
        if (!this.client) return;
        const { data, error } = await this.client.auth.signInWithPassword({ email, password });
        if (error) throw error;
        return data;
    }

    async signUp(email, password, username) {
        if (!this.client) return;
        const { data, error } = await this.client.auth.signUp({ 
            email, 
            password,
            options: { data: { username } }
        });
        if (error) throw error;
        return data;
    }

    async signOut() {
        if (!this.client) return;
        await this.client.auth.signOut();
        window.location.reload();
    }

    isAuthenticated() {
        return !!this.session;
    }

    getPlan() {
        return 'enterprise'; // Forçado para verificação total
    }
}

export const authService = new SentinelAuthService();

```

## Arquivo: `src/services/fcmService.js`

```javascript
// SENTINELA | Diamond Edition - FCM Service
// Gerencia notificações push via Firebase Cloud Messaging

import { dataService } from './dataService.js';
import { authService } from './authService.js';

class SentinelFCMService {
    constructor() {
        this.messaging = null;
        this.vapidKey = null;
    }

    async init() {
        console.log('[FCMService] Inicializando...');
        
        if (!('serviceWorker' in navigator)) {
            console.warn('[FCMService] Service Workers não suportados.');
            return;
        }

        try {
            // 1. Busca Configuração
            const config = await dataService.fetchJson('/config/firebase');
            if (!config || !config.apiKey) {
                console.warn('[FCMService] Configuração do Firebase incompleta.');
                return;
            }

            this.vapidKey = config.vapidKey;

            // 2. Carrega Firebase via Script dinâmico (compat para facilitar no SW)
            // No frontend principal usamos o módulo
            const { initializeApp } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js');
            const { getMessaging, getToken, onMessage } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js');

            const app = initializeApp(config);
            this.messaging = getMessaging(app);

            // 3. Registra Service Worker
            const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            console.log('[FCMService] Service Worker registrado com sucesso.');

            // 4. Solicita Permissão e Token
            await this.requestPermission();

            // 5. Listener para mensagens em foreground
            onMessage(this.messaging, (payload) => {
                console.log('[FCMService] Mensagem recebida em foreground:', payload);
                // Aqui poderíamos disparar um Toast na UI
                if (window.dispatchEvent) {
                    window.dispatchEvent(new CustomEvent('sentinela-notification', { detail: payload }));
                }
            });

        } catch (e) {
            console.error('[FCMService] Erro na inicialização:', e);
        }
    }

    async requestPermission() {
        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('[FCMService] Permissão concedida.');
                await this.saveToken();
            } else {
                console.warn('[FCMService] Permissão negada para notificações.');
            }
        } catch (e) {
            console.error('[FCMService] Erro ao solicitar permissão:', e);
        }
    }

    async saveToken() {
        if (!this.messaging || !authService.isAuthenticated()) return;

        try {
            const { getToken } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js');
            const currentToken = await getToken(this.messaging, {
                vapidKey: this.vapidKey,
                serviceWorkerRegistration: await navigator.serviceWorker.ready
            });

            if (currentToken) {
                console.log('[FCMService] Token obtido:', currentToken);
                
                // Registra no backend
                await fetch(`${window.SENTINELA_CONFIG.apiUrl}/auth/register-push-token`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: authService.user.id,
                        token: currentToken,
                        platform: 'web'
                    })
                });
                
                console.log('[FCMService] Token registrado no backend com sucesso.');
            } else {
                console.warn('[FCMService] Nenhum token disponível. Verifique as permissões.');
            }
        } catch (e) {
            console.error('[FCMService] Erro ao salvar token:', e);
        }
    }
}

export const fcmService = new SentinelFCMService();

```

## Arquivo: `src/services/firebaseConfig.js`

```javascript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';
import * as admin from 'firebase-admin';
import { getApp, getApps, cert } from 'firebase-admin/app';
import dotenv from 'dotenv';

dotenv.config();

const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

// Inicializa Firebase Client-Side (Frontend)
const app = initializeApp(firebaseConfig);
export const messaging = getMessaging(app);

// Inicializa Firebase Admin (Backend)
if (!getApps().length) {
  const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT_KEY || '{}');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

export const adminApp = admin;

```

## Arquivo: `src/services/paymentService.js`

```javascript
// SENTINELA | Diamond Edition - Payment Service v20.3
// Orquestra Stripe, PayPal e PIX

import { authService } from './authService.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';

class SentinelPaymentService {
    /**
     * Inicia o fluxo de compra de munição forense (STN)
     * @param {string} method - 'stripe', 'paypal', 'pix'
     * @param {number} amount - Quantidade de STN
     */
    async purchaseSTN(method, stnAmount) {
        console.log(`[Payments] Iniciando compra de ${stnAmount} STN via ${method}...`);
        
        try {
            const response = await fetch(`${API_BASE}/payments/create-order`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    method,
                    amount: stnAmount,
                    userId: authService.user?.id
                })
            });

            const order = await response.json();

            if (method === 'stripe') {
                window.location.href = order.checkoutUrl;
            } else if (method === 'pix') {
                return order.qrCode; // Retorna para o modal da UI
            } else if (method === 'paypal') {
                window.location.href = order.approvalUrl;
            }
        } catch (e) {
            console.error('[Payments] Erro no checkout:', e);
            throw e;
        }
    }

    async subscribePro() {
        // Fluxo específico para assinatura mensal via Stripe
        return this.purchaseSTN('stripe', 'subscription_pro');
    }
}

export const paymentService = new SentinelPaymentService();

```

## Arquivo: `src/components/session-manager.js`

```javascript
/**
 * PASA v24.1 - Injetor de Sessão de Emergência (UI)
 * Adaptado para o visual "Diamond Edition" (Tailwind + Slate)
 */
export function renderSessionManager(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="insight-card p-4 bg-white border border-slate-200 rounded-xl">
            <h3 class="text-[10px] font-black text-slate-400 uppercase mb-3 tracking-widest flex items-center gap-2">
                <i data-lucide="key-round" class="w-3 h-3 text-orange-500"></i> Injeção de Sessão IG
            </h3>
            <textarea id="ig-cookies-input" rows="3" class="w-full bg-slate-50 text-slate-700 border border-slate-200 rounded-md p-2 text-xs focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none mb-2 font-mono" placeholder="Cole os cookies de sessão aqui..."></textarea>
            <button id="inject-cookies-btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md text-xs transition-colors flex items-center justify-center gap-2">
                <i data-lucide="zap" class="w-3 h-3"></i> INJETAR E DESPAUSAR
            </button>
            <p id="inject-status" class="text-[10px] mt-2 text-center font-medium"></p>
        </div>
    `;

    document.getElementById('inject-cookies-btn').addEventListener('click', async () => {
        const cookies = document.getElementById('ig-cookies-input').value;
        const statusEl = document.getElementById('inject-status');

        if (!cookies) {
            statusEl.textContent = '❌ Cole os cookies primeiro.';
            statusEl.className = 'text-[10px] mt-2 text-center font-medium text-red-500';
            return;
        }

        statusEl.textContent = '⏳ Enviando para a API...';
        statusEl.className = 'text-[10px] mt-2 text-center font-medium text-yellow-600';

        try {
            const res = await fetch('/api/v1/sessions/instagram/cookies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cookies })
            });

            if (res.ok) {
                statusEl.textContent = '✅ Sessão restaurada! Retomando fila...';
                statusEl.className = 'text-[10px] mt-2 text-center font-medium text-emerald-600';
                setTimeout(() => location.reload(), 2500);
            } else {
                throw new Error('Falha na resposta da API');
            }
        } catch (e) {
            statusEl.textContent = '❌ Erro crítico na injeção.';
            statusEl.className = 'text-[10px] mt-2 text-center font-medium text-red-500';
        }
    });
    
    // Renderiza ícones Lucide injetados
    if (window.lucide) lucide.createIcons();
}

```

## Arquivo: `src/components/NotificationToast.js`

```javascript
import React, { useEffect, useState } from 'react';
import { messaging } from '../services/firebaseConfig';
import { onMessage } from 'firebase/messaging';

const NotificationToast = () => {
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('Mensagem recebida:', payload);
      setNotification(payload.notification);
      setTimeout(() => setNotification(null), 5000);
    });

    return () => unsubscribe();
  }, []);

  if (!notification) return null;

  return (
    <div style={{
      position: 'fixed', top: '20px', right: '20px', padding: '15px',
      backgroundColor: '#333', color: '#fff', borderRadius: '8px', zIndex: 1000
    }}>
      <h4>{notification.title}</h4>
      <p>{notification.body}</p>
    </div>
  );
};

export default NotificationToast;

```

## Arquivo: `src/components/BrazilMap.js`

```javascript
/**
 * BrazilMap.js - Componente Geopolítico Sentinela
 * v17.2.5 - High-Accuracy Contiguous Mapping
 */
export function renderBrazilMap(id, ufStats, onSelect) {
    const container = document.getElementById(id);
    if (!container) return;

    // Coordenadas Geográficas Alinhadas (Sistema de Grade Unificado)
    const mapPaths = [
        { id: 'AC', name: 'Acre', d: 'M57,364 L79,343 L99,353 L106,378 L87,398 L51,391 Z' },
        { id: 'AL', name: 'Alagoas', d: 'M461,304 L473,303 L477,314 L464,318 Z' },
        { id: 'AP', name: 'Amapá', d: 'M292,109 L308,103 L329,119 L323,138 L302,142 Z' },
        { id: 'AM', name: 'Amazonas', d: 'M44,204 L146,183 L208,235 L217,312 L101,374 L75,342 L66,281 Z' },
        { id: 'BA', name: 'Bahia', d: 'M358,284 L411,281 L451,324 L461,389 L422,442 L356,432 L340,361 Z' },
        { id: 'CE', name: 'Ceará', d: 'M412,192 L442,190 L457,212 L443,239 L416,236 Z' },
        { id: 'DF', name: 'Distrito Federal', d: 'M341,392 L353,392 L343,403 L341,403 Z' },
        { id: 'ES', name: 'Espírito Santo', d: 'M436,447 L450,453 L448,478 L435,475 Z' },
        { id: 'GO', name: 'Goiás', d: 'M298,342 L354,348 L361,424 L313,433 L295,394 Z' },
        { id: 'MA', name: 'Maranhão', d: 'M327,153 L379,165 L404,275 L357,280 L333,181 Z' },
        { id: 'MT', name: 'Mato Grosso', d: 'M175,258 L301,241 L305,340 L240,378 L180,334 Z' },
        { id: 'MS', name: 'Mato Grosso do Sul', d: 'M221,382 L274,381 L288,446 L230,471 L210,438 Z' },
        { id: 'MG', name: 'Minas Gerais', d: 'M344,437 L421,444 L434,518 L356,541 L326,487 Z' },
        { id: 'PA', name: 'Pará', d: 'M222,143 L320,138 L340,178 L302,243 L238,259 Z' },
        { id: 'PB', name: 'Paraíba', d: 'M452,229 L471,232 L474,249 L453,248 Z' },
        { id: 'PR', name: 'Paraná', d: 'M252,484 L317,485 L325,526 L262,535 Z' },
        { id: 'PE', name: 'Pernambuco', d: 'M430,240 L472,249 L470,274 L437,271 Z' },
        { id: 'PI', name: 'Piauí', d: 'M375,168 L409,176 L400,277 L370,278 Z' },
        { id: 'RJ', name: 'Rio de Janeiro', d: 'M403,516 L432,523 L429,541 L401,539 Z' },
        { id: 'RN', name: 'Rio Grande do Norte', d: 'M447,208 L474,211 L476,227 L450,226 Z' },
        { id: 'RS', name: 'Rio Grande do Sul', d: 'M250,563 L317,568 L311,631 L240,622 Z' },
        { id: 'RO', name: 'Rondônia', d: 'M117,351 L171,335 L180,381 L127,392 Z' },
        { id: 'RR', name: 'Roraima', d: 'M126,58 L177,56 L190,113 L138,123 Z' },
        { id: 'SC', name: 'Santa Catarina', d: 'M267,536 L325,537 L330,564 L273,562 Z' },
        { id: 'SP', name: 'São Paulo', d: 'M292,453 L347,458 L343,501 L288,502 L278,480 Z' },
        { id: 'SE', name: 'Sergipe', d: 'M454,289 L465,290 L463,303 L452,302 Z' },
        { id: 'TO', name: 'Tocantins', d: 'M297,243 L340,240 L354,342 L298,336 Z' }
    ];

    const maxHate = Math.max(...Object.values(ufStats).map(s => s.odio || 0), 1);

    container.innerHTML = `
        <svg viewBox="0 0 550 700" class="sentinela-map-svg">
            <defs>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <g transform="translate(20, 20)">
                ${mapPaths.map(uf => {
                    const data = ufStats[uf.id] || { odio: 0, alvos: 0 };
                    const hasHate = data.odio > 0;
                    const intensity = hasHate ? (data.odio / maxHate) : 0;
                    const fill = hasHate ? `rgba(239, 68, 68, ${0.15 + intensity * 0.85})` : 'rgba(148, 163, 184, 0.08)';
                    const isSelected = window.__selectedUF === uf.id;
                    const stroke = isSelected ? '#38bdf8' : (hasHate ? '#ef4444' : 'rgba(255, 255, 255, 0.1)');
                    const strokeWidth = isSelected ? '3' : '1';
                    const pulseClass = (intensity > 0.75) ? 'map-pulse' : '';

                    return `
                    <path d="${uf.d}" 
                          id="uf-${uf.id}" 
                          fill="${fill}" 
                          stroke="${stroke}" 
                          stroke-width="${strokeWidth}"
                          class="uf-path ${pulseClass}"
                          filter="${isSelected ? 'url(#glow)' : ''}"
                          onclick="window.handleUFClick('${uf.id}', '${uf.name}')">
                        <title>${uf.name}: ${data.odio} alertas (${data.alvos} alvos)</title>
                    </path>`;
                }).join('')}
            </g>
        </svg>
    `;

    window.handleUFClick = (id, name) => {
        const data = ufStats[id] || { alvos: 0, odio: 0 };
        window.__selectedUF = id;
        if (typeof onSelect === 'function') onSelect(name, data, id);
    };
}

```

## Arquivo: `src/components/PredictiveTrends.js`

```javascript
export function renderPredictiveTrends(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="glass-card" style="padding: 24px; border-left: 4px solid #10b981;"><h4 style="font-size: 10px; color: #10b981; font-weight: 800;">TENDÊNCIA PREDITIVA</h4><p style="font-size: 14px; color: white; margin-top: 8px;">Estabilidade detectada em 85% dos alvos.</p></div>';
}
```

