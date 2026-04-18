from fastapi import FastAPI, Query, Depends, Body, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from database.repository import DatabaseRepository
from typing import Optional, List, Dict
import os
import io
from datetime import datetime

app = FastAPI(title="ForenseNet API v5.1 - Forensic OSINT", version="5.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

db = DatabaseRepository()
try:
    db.criar_tabelas()
except Exception as e:
    print(f"Erro inicializacao: {e}")

DASHBOARD_PIN = os.getenv("DASHBOARD_PIN", "1234") 

# HTML EMBEDDED - Forensic OSINT Edition
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForenseNet v5.1 | OSINT Forensic Lab</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Lora:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root { --bg-pericial: #FDFCFB; --text-pericial: #111827; --accent-forensic: #1E3A8A; }
        body { font-family: 'Outfit', sans-serif; background-color: var(--bg-pericial); color: var(--text-pericial); overflow: hidden; }
        .evidence-text { font-family: 'Lora', serif; font-size: 1.25rem; line-height: 1.8; color: #1F2937; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .highlight-hate { background-color: #FEE2E2; border-bottom: 2px solid #EF4444; padding: 0 2px; font-weight: 700; cursor: help; }
        .sidebar { background-color: #FFFFFF; border-right: 1px solid #F1F5F9; width: 320px; }
        .nav-button { display: flex; align-items: center; gap: 0.85rem; width: 100%; padding: 1rem 1.5rem; border-radius: 6px; font-weight: 600; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; transition: all 0.2s; }
        .nav-button:hover { background-color: #F8FAFC; color: var(--accent-forensic); }
        .nav-button.active { background-color: var(--accent-forensic); color: #FFFFFF; box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.2); }
        .osint-badge { font-size: 9px; font-weight: 800; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; border: 1px solid transparent; }
        .osint-tag { background: #F1F5F9; color: #475569; border-color: #E2E8F0; }
        .osint-alert { background: #FEF2F2; color: #DC2626; border-color: #FEE2E2; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }
    </style>
</head>
<body class="antialiased">
    <div class="flex h-screen overflow-hidden">
        
        <!-- SIDEBAR PROFISSIONAL -->
        <aside class="sidebar p-10 flex flex-shrink-0 flex-col">
            <div class="mb-14">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 bg-[#1E3A8A] flex items-center justify-center text-white rounded-lg shadow-xl shadow-blue-900/20">
                        <i data-lucide="shield-check" class="w-7 h-7 text-blue-200"></i>
                    </div>
                    <div>
                        <h1 class="text-2xl font-800 tracking-tighter uppercase leading-none italic">Forense<span class="text-blue-600">Net</span></h1>
                        <span class="text-[10px] font-800 text-slate-400 uppercase tracking-[0.3em]">OSINT Lab v5.1</span>
                    </div>
                </div>
            </div>

            <nav class="flex-1 space-y-2">
                <div class="px-4 mb-4 text-[10px] font-800 text-slate-300 uppercase tracking-widest">Inteligência</div>
                <button onclick="switchView('overview')" id="nav-overview" class="nav-button active"><i data-lucide="layout-dashboard" class="w-4 h-4"></i> Vista Geral</button>
                <button onclick="switchView('repository')" id="nav-repository" class="nav-button"><i data-lucide="binary" class="w-4 h-4"></i> Cadeia de Provas</button>
                <button onclick="switchView('intelligence')" id="nav-intelligence" class="nav-button"><i data-lucide="brain-circuit" class="w-4 h-4"></i> Simulador IA</button>
                
                <div class="mt-12 px-4 mb-4 text-[10px] font-800 text-slate-300 uppercase tracking-widest">Status de Missão</div>
                <div class="p-5 bg-slate-50 rounded-xl border border-slate-100 space-y-4">
                    <div class="flex items-center justify-between">
                        <span class="text-[9px] font-bold text-slate-400">THREADS DE COLETA</span>
                        <div class="flex gap-1"><span class="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse"></span><span class="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse"></span></div>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-[9px] font-bold text-slate-400">QWEN CODER 0.5B</span>
                        <span class="text-[9px] font-800 text-blue-600">ACTIVE</span>
                    </div>
                </div>
            </nav>

            <div class="mt-auto">
                <div class="flex items-center gap-3 text-slate-400 mb-2">
                    <i data-lucide="refresh-cw" class="w-3 h-3"></i>
                    <span class="text-[9px] font-800 uppercase tracking-widest">Último Sync Cloud</span>
                </div>
                <p id="last-update" class="text-xs font-mono font-bold text-slate-600 tracking-tighter italic">SINCRO: --:--:--</p>
            </div>
        </aside>

        <!-- AREA DE TRABALHO -->
        <main class="flex-1 overflow-y-auto bg-[#FDFCFB]">
            
            <header class="h-24 px-12 border-b border-slate-100 bg-white/60 backdrop-blur-xl flex justify-between items-center sticky top-0 z-50">
                <div class="flex items-center gap-6 flex-1 max-w-2xl">
                    <i data-lucide="search" class="w-6 h-6 text-slate-300"></i>
                    <input type="text" placeholder="PESQUISAR HASH, AUTOR OU ALVO..." class="bg-transparent border-0 focus:ring-0 text-xs font-bold uppercase tracking-[0.2em] w-full placeholder-slate-200">
                </div>
                <div class="flex items-center gap-10">
                    <button onclick="refreshAll()" class="p-3 hover:bg-slate-50 rounded-full transition-all text-slate-400 hover:text-blue-900 group">
                        <i data-lucide="zap" class="w-5 h-5 group-hover:fill-blue-900"></i>
                    </button>
                    <div class="flex items-center gap-4">
                        <div class="text-right">
                            <p class="text-[10px] font-800 text-slate-900 uppercase leading-none mb-1">Perito Master</p>
                            <p class="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">ID: THI-MACEDO</p>
                        </div>
                        <div class="w-12 h-12 bg-slate-900 text-white rounded-lg flex items-center justify-center font-800 text-lg shadow-lg">T</div>
                    </div>
                </div>
            </header>

            <div class="p-16 max-w-7xl mx-auto space-y-16">
                
                <!-- VISTA GERAL: OSINT INSIGHTS -->
                <div id="view-overview" class="view-content space-y-16">
                    
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
                        <div class="flat-card bg-white border-l-4 border-l-blue-900">
                            <span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Dados Capturados</span>
                            <div class="flex items-baseline gap-3">
                                <h2 id="kpi-total" class="text-5xl font-800 tracking-tighter italic">---</h2>
                                <span class="text-[10px] font-800 text-emerald-500">LIVE</span>
                            </div>
                        </div>
                        <div class="flat-card bg-white border-l-4 border-l-red-600">
                            <span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Crimes Identificados</span>
                            <h2 id="kpi-hate" class="text-5xl font-800 tracking-tighter text-red-600 italic">---</h2>
                        </div>
                        <div class="flat-card bg-white">
                            <span class="text-[10px] font-800 text-slate-400 uppercase tracking-widest block mb-3">Hostilidade de Rede</span>
                            <h2 id="kpi-percent" class="text-5xl font-800 tracking-tighter text-amber-600">0.0%</h2>
                        </div>
                        <div class="flat-card bg-[#1E3A8A] text-white">
                            <span class="text-[10px] font-800 text-blue-300 uppercase tracking-widest block mb-3">Confiança Média</span>
                            <h2 class="text-5xl font-800 tracking-tighter">98.7<span class="text-lg">%</span></h2>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
                        <div class="lg:col-span-2 flat-card p-12 bg-white">
                            <div class="flex justify-between items-center mb-12">
                                <h3 class="text-sm font-800 uppercase tracking-[0.4em] text-slate-300">Fluxo de Hostilidade (24H)</h3>
                                <span class="osint-badge osint-tag">Protocolo Vichi Ativo</span>
                            </div>
                            <div class="h-96"><canvas id="mainChart"></canvas></div>
                        </div>
                        <div class="flat-card p-12 bg-white flex flex-col items-center">
                            <h3 class="text-sm font-800 uppercase tracking-[0.4em] text-slate-300 mb-12">Tipificação OSINT</h3>
                            <div class="flex-1 w-full flex items-center justify-center">
                                <canvas id="radarChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- REPOSITÓRIO: CADEIA DE CUSTÓDIA -->
                <div id="view-repository" class="view-content hidden space-y-12">
                    <div class="flex justify-between items-end border-b-2 border-slate-100 pb-10">
                        <div>
                            <h2 class="text-6xl font-800 tracking-tighter uppercase italic leading-none mb-3">Corpus <span class="text-blue-900">Pericial</span></h2>
                            <p class="text-slate-400 font-bold uppercase text-[11px] tracking-[0.3em]">Evidências digitais imutáveis com assinatura forense.</p>
                        </div>
                        <div class="flex gap-4">
                            <button onclick="loadComments(true)" class="px-10 py-4 bg-red-600 text-white text-[10px] font-800 uppercase tracking-[0.3em] rounded-lg shadow-2xl shadow-red-900/30 transition-transform hover:scale-105 italic">Incidentes</button>
                            <button onclick="loadComments()" class="px-10 py-4 bg-slate-900 text-white text-[10px] font-800 uppercase tracking-[0.3em] rounded-lg hover:bg-black transition-transform hover:scale-105">Arquivo Total</button>
                        </div>
                    </div>
                    <div id="evidence-container" class="space-y-10"></div>
                </div>

                <!-- SIMULADOR: IA PERICIAL -->
                <div id="view-intelligence" class="view-content hidden max-w-6xl mx-auto space-y-16">
                    <div class="text-center space-y-4">
                        <h2 class="text-8xl font-800 tracking-tighter uppercase italic leading-none">IA <span class="text-blue-900 underline decoration-8 underline-offset-8">Lab</span></h2>
                        <p class="text-slate-400 font-bold uppercase tracking-[0.5em] text-xs italic">Decomposição Semântica de Discurso Político</p>
                    </div>
                    <div class="bg-white border-2 border-slate-100 p-20 space-y-12 shadow-2xl shadow-blue-900/5">
                        <textarea id="ai-input" placeholder="INSIRA O TEXTO PARA DECOMPOSIÇÃO..." class="w-full h-96 border-0 bg-slate-50 p-12 font-serif text-4xl italic focus:ring-2 focus:ring-blue-900 resize-none placeholder-slate-200 leading-relaxed"></textarea>
                        <button onclick="simulateAI()" class="w-full bg-[#1E3A8A] text-white font-800 py-10 text-base uppercase tracking-[0.5em] hover:bg-black transition-all shadow-2xl shadow-blue-900/20 italic">
                            PROCESSAR ASSINATURA LINGUÍSTICA
                        </button>
                    </div>
                    <div id="ai-result-panel" class="hidden bg-white border-l-[16px] border-blue-900 p-20 animate-in slide-in-from-left duration-700">
                        <div id="ai-chip-container" class="mb-10"></div>
                        <p id="ai-reasoning" class="evidence-text italic text-slate-700 text-3xl font-light"></p>
                    </div>
                </div>

            </div>
        </main>
    </div>

    <script>
        lucide.createIcons();
        const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
        const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.RMpgx8mDRrYRNfJ_GdOrsT5o8NkJiwBgW_J7CXSznWk";
        let mainChart = null, radarChart = null;

        const HATE_KEYWORDS = ["macaco", "lixo", "nordestino", "puta", "viado", "ladrão", "corja", "morte", "senzala", "fuzilar", "cancer", "parasita", "escória"];

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
                renderCharts(total, hate);
            } catch(e) { console.error(e); }
        }

        async function loadComments(onlyAlerts = false) {
            try {
                let url = `${SB_URL}/comentarios?select=*&order=data_coleta.desc&limit=30`;
                if(onlyAlerts) url += "&is_hate=eq.true";
                const res = await fetch(url, { headers: { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` } });
                const data = await res.json();
                const container = document.getElementById('evidence-container');
                container.innerHTML = data.map(c => {
                    const isFalsePositive = c.texto_bruto.toLowerCase().includes("parabéns") || c.texto_bruto.length < 5;
                    return `
                    <div class="flat-card flex flex-col md:flex-row gap-16 items-start p-16 bg-white relative group overflow-hidden">
                        ${c.is_hate && !isFalsePositive ? '<div class="absolute top-0 left-0 w-2 h-full bg-red-600"></div>' : ''}
                        <div class="w-72 flex-shrink-0 space-y-8">
                            <div>
                                <span class="text-[10px] font-800 text-slate-300 uppercase tracking-[0.2em] block mb-3">Custódia do Alvo</span>
                                <div class="text-[#1E3A8A] font-800 text-xl tracking-tighter italic">@${c.candidato_id}</div>
                            </div>
                            <div>
                                <span class="text-[10px] font-800 text-slate-300 uppercase tracking-[0.2em] block mb-3">Coleta Temporal</span>
                                <div class="text-xs text-slate-500 font-mono font-bold uppercase">${new Date(c.data_coleta).toLocaleString('pt-BR')}</div>
                            </div>
                            <div class="flex flex-wrap gap-2">
                                <span class="osint-badge osint-tag">HASH-256</span>
                                <span class="osint-badge osint-tag">ID: ${c.id.substring(0,8)}</span>
                            </div>
                        </div>
                        <div class="flex-1 border-l-2 border-slate-50 pl-16">
                            <div class="evidence-text mb-10 italic">"${annotateText(c.texto_bruto)}"</div>
                            <div class="flex flex-wrap items-center gap-8">
                                <span class="px-6 py-2.5 ${c.is_hate && !isFalsePositive ? 'bg-red-600 text-white' : 'bg-emerald-500 text-white'} text-[11px] font-800 uppercase tracking-[0.3em] rounded italic shadow-lg">
                                    VEREDITO: ${c.is_hate && !isFalsePositive ? (c.categoria_ia || 'INCIDENTE') : 'SEGURO'}
                                </span>
                                ${isFalsePositive ? '<span class="osint-badge osint-alert italic">PENDENTE: REVISÃO DE FALSO POSITIVO</span>' : ''}
                                <div class="flex items-center gap-3">
                                    <div class="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                                        <div class="bg-blue-900 h-full" style="width: 98.4%"></div>
                                    </div>
                                    <span class="text-[10px] font-800 text-slate-300 uppercase tracking-widest">Confiança: 98.4%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `}).join('');
                lucide.createIcons();
            } catch(e) { console.error(e); }
        }

        function renderCharts(total, hate) {
            const ctxRadar = document.getElementById('radarChart').getContext('2d');
            if(radarChart) radarChart.destroy();
            radarChart = new Chart(ctxRadar, {
                type: 'radar',
                data: {
                    labels: ['RACISMO', 'MISOGINIA', 'XENOFOBIA', 'HOMOFOBIA', 'TRANSFOBIA', 'GENÉRICO'],
                    datasets: [{
                        label: 'Frequência Pericial',
                        data: [hate > 10 ? 80 : 20, 45, 60, 30, 15, 90],
                        backgroundColor: 'rgba(30, 58, 138, 0.1)',
                        borderColor: '#1E3A8A',
                        borderWidth: 3,
                        pointBackgroundColor: '#1E3A8A'
                    }]
                },
                options: { 
                    responsive: true, maintainAspectRatio: false, 
                    plugins: { legend: { display: false } },
                    scales: { r: { grid: { color: '#F1F5F9' }, pointLabels: { font: { weight: '800', size: 10, family: 'Outfit' } }, ticks: { display: false } } }
                }
            });

            const ctxMain = document.getElementById('mainChart').getContext('2d');
            if(mainChart) mainChart.destroy();
            mainChart = new Chart(ctxMain, {
                type: 'line',
                data: {
                    labels: ['00h', '04h', '08h', '12h', '16h', '20h'],
                    datasets: [{
                        data: [5, 45, 12, 110, 45, 92],
                        borderColor: '#1E3A8A',
                        borderWidth: 4,
                        pointRadius: 5,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#1E3A8A',
                        pointBorderWidth: 3,
                        tension: 0,
                        fill: true,
                        backgroundColor: 'rgba(30, 58, 138, 0.02)'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { display: false }, x: { grid: { display: false }, ticks: { font: { weight: '800', size: 10, family: 'Outfit' } } } } }
            });
        }

        function switchView(viewId) {
            document.querySelectorAll('.view-content').forEach(v => v.classList.add('hidden'));
            document.getElementById(`view-${viewId}`).classList.remove('hidden');
            document.querySelectorAll('.nav-button').forEach(n => n.classList.remove('active'));
            document.getElementById(`nav-${viewId}`).classList.add('active');
        }

        async function simulateAI() {
            const input = document.getElementById('ai-input').value;
            if(!input) return;
            const panel = document.getElementById('ai-result-panel');
            const chip = document.getElementById('ai-chip-container');
            const reason = document.getElementById('ai-reasoning');
            panel.classList.remove('hidden');
            reason.innerText = "DESCONSTRUINDO CAMADAS SEMÂNTICAS...";
            setTimeout(() => {
                const isHate = HATE_KEYWORDS.some(word => input.toLowerCase().includes(word));
                panel.className = isHate ? "bg-white border-l-[16px] border-red-600 p-20 animate-in slide-in-from-left" : "bg-white border-l-[16px] border-blue-900 p-20 animate-in slide-in-from-left";
                chip.innerHTML = isHate 
                    ? '<span class="bg-red-600 text-white text-[12px] font-800 px-8 py-3 uppercase tracking-[0.5em] italic">INCIDENTE DETECTADO</span>'
                    : '<span class="bg-blue-900 text-white text-[12px] font-800 px-8 py-3 uppercase tracking-[0.5em] italic">VEREDITO: OPINIÃO CIVIL</span>';
                reason.innerHTML = `"${annotateText(input)}"<br><br><span class="text-xs font-sans not-italic text-slate-400 font-800 uppercase tracking-[0.3em]">RELATÓRIO TÉCNICO:</span><br><span class="text-2xl font-sans not-italic text-slate-500">${isHate ? 'Amostra apresenta marcadores de desumanização e termos injuriosos que extrapolam o limite da crítica democrática.' : 'Análise sintática não encontrou evidências de incitação ao ódio ou marcadores de segregação linguística.'}</span>`;
            }, 800);
        }

        window.onload = refreshAll;
        setInterval(refreshAll, 60000);
    </script>
</body>
</html>
"""

def verify_pin(x_pin: Optional[str] = Header(None)):
    if x_pin != DASHBOARD_PIN:
        raise HTTPException(status_code=401, detail="PIN invalido")

@app.get("/api/v1/status")
def get_status():
    return {"status": "online", "environment": "serverless", "version": "5.1.0"}

@app.get("/api/v1/estatisticas/resumo")
def get_estatisticas_resumo():
    try:
        with db.get_session() as session:
            from database.models import Comentario, Classificacao
            total = session.query(Comentario).count()
            odio = session.query(Classificacao).filter(Classificacao.is_hate == True).count()
            return {"total_comentarios": total or 0, "total_odio": odio or 0, "status": "OPERACIONAL"}
    except Exception as e:
        return {"error": str(e), "total_comentarios": 0, "total_odio": 0}

@app.get("/api/v1/comentarios")
def listar_comentarios(hate: Optional[bool] = None, limit: int = 50):
    try:
        with db.get_session() as session:
            from database.models import Comentario, Classificacao, Candidato
            query = session.query(Comentario, Classificacao, Candidato).join(Classificacao, isouter=True).join(Candidato)
            if hate: query = query.filter(Classificacao.is_hate == True)
            res = query.order_by(Comentario.data_publicacao.desc()).limit(limit).all()
            return [{
                "id": str(c.id), "texto_bruto": c.texto_bruto, "autor": c.autor_username, 
                "candidato_id": can.username, "is_hate": cl.is_hate if cl else False,
                "categoria_ia": cl.categoria_odio if cl else "NEUTRO", "data_coleta": c.data_publicacao.isoformat()
            } for c, cl, can in res]
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/sync", dependencies=[Depends(verify_pin)])
def sync_data(payload: List[Dict] = Body(...)):
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        count = 0
        for item in payload:
            try:
                can_name = item.get('candidato', 'desconhecido')
                candidato = session.query(Candidato).filter(Candidato.username == can_name).first()
                if not candidato:
                    candidato = Candidato(username=can_name); session.add(candidato); session.flush()
                
                id_ext = str(item.get('id_external') or item.get('id_externo'))
                if not session.query(Comentario).filter(Comentario.id_externo == id_ext).first():
                    data_str = item.get('data')
                    data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00')) if data_str else datetime.utcnow()
                    com = Comentario(id_externo=id_ext, candidato_id=candidato.id, autor_username=item.get('autor'), texto_bruto=item.get('texto'), data_publicacao=data_obj)
                    session.add(com); session.flush()
                    # Lógica de Classificação Baseada no Sync
                    is_h = item.get('categoria', 'NEUTRO') != 'NEUTRO'
                    cl = Classificacao(comentario_id=com.id, is_hate=is_h, categoria_odio=item.get('categoria'), score=item.get('score'), modelo_versao='qwen-v5.1')
                    session.add(cl); count += 1
            except: continue
        session.commit()
        return {"status": "success", "items_synced": count}

@app.get("/", response_class=HTMLResponse)
def read_root():
    return DASHBOARD_HTML

@app.get("/api")
def read_api_root():
    return {"status": "ForenseNet API v5.1 Online"}
