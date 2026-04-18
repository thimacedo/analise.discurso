# api/templates.py

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForenseNet v5.5 | Forensic OSINT Lab</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Lora:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --bg-pericial: #FDFCFB; --text-pericial: #111827; --accent-forensic: #1E3A8A; }
        body { font-family: 'Outfit', sans-serif; background-color: var(--bg-pericial); color: var(--text-pericial); overflow: hidden; }
        .evidence-text { font-family: 'Lora', serif; font-size: 1.1rem; line-height: 1.6; color: #1F2937; }
        .sidebar { background-color: #FFFFFF; border-right: 1px solid #F1F5F9; width: 300px; }
        .nav-button { display: flex; align-items: center; gap: 0.85rem; width: 100%; padding: 1rem 1.5rem; border-radius: 6px; font-weight: 600; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; transition: all 0.2s; }
        .nav-button.active { background-color: var(--accent-forensic); color: #FFFFFF; }
        .comment-scroll { max-height: 600px; overflow-y: auto; scrollbar-width: thin; }
        .post-preview { border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0; background: #F8FAFC; }
        .caption-text { font-family: 'Lora', serif; font-size: 0.9rem; line-height: 1.4; color: #64748B; }
        .osint-badge { font-size: 9px; font-weight: 800; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; }
        .osint-tag { background: #F1F5F9; color: #475569; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }
    </style>
</head>
<body class="antialiased">
    <div class="flex h-screen overflow-hidden">
        <aside class="sidebar p-10 flex flex-col flex-shrink-0">
            <div class="mb-14">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 bg-[#1E3A8A] flex items-center justify-center text-white rounded-lg shadow-xl shadow-blue-900/20"><i data-lucide="camera" class="w-7 h-7"></i></div>
                    <div>
                        <h1 class="text-2xl font-800 tracking-tighter uppercase leading-none italic">Forense<span class="text-blue-600">Net</span></h1>
                        <span class="text-[10px] font-800 text-slate-400 uppercase tracking-[0.3em]">VISUAL OSINT v5.5</span>
                    </div>
                </div>
            </div>
            <nav class="flex-1 space-y-2">
                <button onclick="switchView('overview')" id="nav-overview" class="nav-button active"><i data-lucide="layout-dashboard" class="w-4 h-4"></i> Dashboard</button>
                <button onclick="switchView('repository')" id="nav-repository" class="nav-button"><i data-lucide="layers" class="w-4 h-4"></i> Cadeia de Provas</button>
                <button onclick="switchView('intelligence')" id="nav-intelligence" class="nav-button"><i data-lucide="cpu" class="w-4 h-4"></i> IA Lab</button>
            </nav>
            <div class="mt-auto"><p id="last-update" class="text-[10px] font-mono font-bold text-slate-400 uppercase text-center">SYNC: --:--:--</p></div>
        </aside>

        <main class="flex-1 overflow-y-auto">
            <header class="h-24 px-12 border-b border-slate-100 bg-white/60 backdrop-blur-xl flex justify-between items-center sticky top-0 z-50">
                <div class="flex items-center gap-6 flex-1 max-w-2xl"><i data-lucide="search" class="w-6 h-6 text-slate-300"></i><input type="text" placeholder="FILTRAR POR HASH OU ALVO..." class="bg-transparent border-0 focus:ring-0 text-xs font-bold uppercase tracking-[0.2em] w-full"></div>
                <div class="flex items-center gap-10">
                    <button onclick="refreshAll()" class="p-3 hover:bg-slate-50 rounded-full transition-all text-gray-400 hover:text-blue-900"><i data-lucide="refresh-cw" class="w-5 h-5"></i></button>
                    <div class="w-12 h-12 bg-slate-900 text-white rounded-lg flex items-center justify-center font-800 shadow-lg italic text-xl">F</div>
                </div>
            </header>

            <div class="p-16 max-w-7xl mx-auto space-y-16">
                <!-- VISTA GERAL -->
                <div id="view-overview" class="view-content space-y-16">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-10 text-center">
                        <div class="flat-card bg-white border-b-4 border-b-blue-900"><span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Corpus Coletado</span><h2 id="kpi-total" class="text-5xl font-800 tracking-tighter italic">---</h2></div>
                        <div class="flat-card bg-white border-b-4 border-b-red-600"><span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Incidentes Identificados</span><h2 id="kpi-hate" class="text-5xl font-800 tracking-tighter text-red-600 italic">---</h2></div>
                        <div class="flat-card bg-white border-b-4 border-b-amber-500"><span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Nível de Hostilidade</span><h2 id="kpi-percent" class="text-5xl font-800 tracking-tighter text-amber-600">0.0%</h2></div>
                        <div class="flat-card bg-[#1E3A8A] text-white"><span class="text-[10px] font-800 text-blue-300 uppercase tracking-widest block mb-3">Integridade de Prova</span><h2 class="text-5xl font-800 tracking-tighter italic">99.9%</h2></div>
                    </div>
                </div>

                <!-- CADEIA DE PROVAS (VISUAL) -->
                <div id="view-repository" class="view-content hidden space-y-16 animate-in slide-in-from-bottom duration-500">
                    <div class="flex justify-between items-end border-b-2 border-slate-100 pb-10">
                        <div><h2 class="text-6xl font-800 tracking-tighter uppercase italic leading-none mb-3">Cadeia de <span class="text-blue-900 underline decoration-8 underline-offset-8">Contexto</span></h2><p class="text-slate-400 font-bold uppercase text-[11px] tracking-[0.3em]">Agrupamento pericial por postagem original e evidência visual.</p></div>
                        <button onclick="refreshAll()" class="px-12 py-5 bg-slate-900 text-white text-[10px] font-800 uppercase tracking-[0.4em] rounded-lg hover:bg-black transition-transform hover:scale-105 italic">Atualizar Dashboard</button>
                    </div>
                    <div id="evidence-container" class="space-y-24"></div>
                </div>
                
                <!-- SIMULADOR IA -->
                <div id="view-intelligence" class="view-content hidden max-w-5xl mx-auto space-y-16">
                     <div class="text-center space-y-4"><h2 class="text-8xl font-800 tracking-tighter uppercase italic leading-none">IA <span class="text-blue-900">Lab</span></h2><p class="text-slate-400 font-bold uppercase tracking-[0.5em] text-xs italic">Decomposição Semântica v5.5</p></div>
                    <div class="bg-white border-2 border-slate-100 p-20 space-y-12 shadow-2xl shadow-blue-900/5"><textarea id="ai-input" placeholder="INSIRA TEXTO PARA PERÍCIA..." class="w-full h-96 border-0 bg-slate-50 p-12 font-serif text-4xl italic focus:ring-1 focus:ring-blue-900 resize-none"></textarea><button onclick="simulateAI()" class="w-full bg-blue-900 text-white font-800 py-8 uppercase tracking-[0.5em] hover:bg-black transition-all">EXECUTAR ANÁLISE</button></div>
                </div>
            </div>
        </main>
    </div>

    <script>
        lucide.createIcons();
        const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
        const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.RMpgx8mDRrYRNfJ_GdOrsT5o8NkJiwBgW_J7CXSznWk";
        const HATE_KEYWORDS = ["macaco", "lixo", "nordestino", "puta", "viado", "ladrão", "corja", "morte", "senzala", "fuzilar", "cancer", "parasita", "escória", "fazer o l", "faz o l"];

        async function refreshAll() {
            document.getElementById('last-update').innerText = "SYNC: " + new Date().toLocaleTimeString('pt-BR');
            await loadStats();
            await loadComments();
        }

        function annotateText(text) {
            if(!text) return "";
            let annotated = text;
            HATE_KEYWORDS.forEach(word => {
                const regex = new RegExp(`\\\\b(${word})\\\\b`, 'gi');
                annotated = annotated.replace(regex, `<span class="highlight-hate" title="Dicionário Pericial: Gatilho Detectado">$1</span>`);
            });
            return annotated;
        }

        async function loadStats() {
            try {
                const headers = { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}`, "Prefer": "count=exact" };
                const resTotal = await fetch(`${SB_URL}/comentarios?select=id`, { headers });
                const total = parseInt(resTotal.headers.get("content-range")?.split("/")[1]) || 0;
                const resHate = await fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=id`, { headers });
                const hate = parseInt(resHate.headers.get("content-range")?.split("/")[1]) || 0;
                document.getElementById('kpi-total').innerText = total.toLocaleString();
                document.getElementById('kpi-hate').innerText = hate.toLocaleString();
                document.getElementById('kpi-percent').innerText = total > 0 ? `${((hate/total)*100).toFixed(1)}%` : "0.0%";
            } catch(e) { console.error(e); }
        }

        async function loadComments() {
            try {
                const res = await fetch(`${SB_URL}/comentarios?select=*&order=data_coleta.desc&limit=100`, { headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` } });
                const data = await res.json();
                const grouped = data.reduce((acc, c) => {
                    const key = c.post_url || 'unknown';
                    if (!acc[key]) acc[key] = { candidate: c.candidato_id, date: c.data_coleta, image: c.post_image, caption: c.post_caption, comments: [] };
                    acc[key].comments.push(c);
                    return acc;
                }, {});
                const container = document.getElementById('evidence-container');
                container.innerHTML = Object.entries(grouped).map(([postKey, group]) => {
                    const postUrl = postKey !== 'unknown' ? (postKey.startsWith('http') ? postKey : `https://www.instagram.com/p/${postKey}/`) : '#';
                    const hateCount = group.comments.filter(c => c.is_hate).length;
                    const hasHighRisk = hateCount > group.comments.length * 0.3;
                    return `
                    <div class="flex flex-col lg:flex-row gap-16 items-start animate-in fade-in duration-700">
                        <div class="w-full lg:w-96 flex-shrink-0 space-y-6">
                            <div class="post-preview shadow-2xl shadow-blue-900/10 relative group"><img src="${group.image || 'https://via.placeholder.com/400x500?text=PROVA+VISUAL'}" class="w-full h-auto object-cover grayscale group-hover:grayscale-0 transition-all duration-700"><div class="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded text-[9px] font-800 uppercase tracking-widest border border-slate-200">Instagram Evidence</div></div>
                            <div class="p-6 bg-white border border-slate-100 rounded-lg space-y-4"><div class="flex items-center gap-3"><div class="w-8 h-8 bg-blue-900 rounded flex items-center justify-center text-white text-[10px] font-bold uppercase italic">@</div><div class="text-[#1E3A8A] font-800 text-lg italic tracking-tighter">@${group.candidate}</div></div><p class="caption-text italic">"${group.caption ? group.caption.substring(0, 150) + '...' : 'Sem legenda disponível.'}"</p><a href="${postUrl}" target="_blank" class="flex items-center justify-center gap-2 w-full py-3 bg-slate-50 text-[9px] font-800 text-slate-400 uppercase tracking-[0.3em] rounded hover:bg-blue-900 hover:text-white transition-all italic">VER POST ORIGINAL</a></div>
                        </div>
                        <div class="flex-1 bg-white border border-slate-100 rounded-2xl p-12 relative overflow-hidden shadow-2xl shadow-slate-200/50">
                            ${hasHighRisk ? '<div class="absolute top-0 left-0 w-full h-2 bg-red-600"></div>' : ''}
                            <div class="flex justify-between items-center mb-12"><h4 class="text-xs font-800 uppercase tracking-[0.4em] text-slate-300 italic">Corpus do Incidente (${group.comments.length} amostras)</h4><span class="osint-badge ${hasHighRisk ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-900'} font-bold tracking-widest italic">${hasHighRisk ? 'ALTA TOXICIDADE' : 'FLUXO MONITORADO'}</span></div>
                            <div class="comment-scroll space-y-12 pr-6">
                                ${group.comments.map(c => `
                                    <div class="relative pl-8 border-l-2 border-slate-50 py-2 group">
                                        <div class="flex items-center justify-between mb-4"><div class="flex items-center gap-3"><div class="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-[8px] font-bold text-slate-400">👤</div><span class="text-[10px] font-bold text-slate-900 uppercase tracking-tighter">@${c.autor || 'ID-ANON'}</span></div><span class="osint-badge ${c.is_hate ? 'bg-red-600 text-white' : 'bg-emerald-100 text-emerald-700'} text-[8px] italic">${c.is_hate ? (c.categoria_ia || 'ÓDIO') : 'SEGURO'}</span></div>
                                        <div class="evidence-text italic text-slate-700 leading-relaxed transition-colors group-hover:text-black">"${annotateText(c.texto_bruto)}"</div>
                                        <div class="mt-6 flex items-center gap-6 text-[8px] font-bold text-slate-300 uppercase tracking-[0.2em]"><span>TS: ${new Date(c.data_coleta).toLocaleTimeString()}</span><span>ID: ${c.id.substring(0,12)}</span><span>CERT: AUTH-256</span></div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `}).join(''); lucide.createIcons(); } catch(e) { console.error(e); } }

        function switchView(viewId, updateHash = true) {
            document.querySelectorAll('.view-content').forEach(v => v.classList.add('hidden'));
            document.getElementById(`view-${viewId}`).classList.remove('hidden');
            document.querySelectorAll('.nav-button').forEach(n => n.classList.remove('active'));
            document.getElementById(`nav-${viewId}`).classList.add('active');
            if(updateHash) window.location.hash = viewId;
        }

        window.onload = () => {
            const initialView = window.location.hash.replace('#', '') || 'overview';
            switchView(initialView, false);
            refreshAll();
        };

        window.onhashchange = () => {
            const newView = window.location.hash.replace('#', '') || 'overview';
            switchView(newView, false);
        };

        setInterval(refreshAll, 60000);
    </script>
</body>
</html>
"""
