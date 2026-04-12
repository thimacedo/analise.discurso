from flask import Flask, render_template_string, jsonify, send_file
import pandas as pd
import requests
from io import StringIO
import os

app = Flask(__name__)

# HTML completo com PapaParse e função loadData corrigida
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Política com Lupa | Monitor de Discurso e Ódio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f4f7fc; color: #1e2a3e; line-height: 1.5; padding: 2rem 1.5rem; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 2rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 1rem; }
        .logo h1 { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #0f3b5c, #e67e22); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo p { font-size: 0.85rem; color: #5a6e7c; margin-top: 0.2rem; }
        .badge { background: #e2e8f0; padding: 0.3rem 1rem; border-radius: 30px; font-size: 0.8rem; font-weight: 500; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
        .card { background: white; border-radius: 24px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #e9edf2; }
        .card-title { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5a6e7c; margin-bottom: 0.75rem; }
        .card-number { font-size: 2.8rem; font-weight: 800; color: #0f3b5c; line-height: 1.2; }
        .insight-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1.8rem; margin-bottom: 2.5rem; }
        .insight-card { background: white; border-radius: 24px; padding: 1.5rem; border: 1px solid #e9edf2; }
        .insight-title { font-weight: 700; font-size: 1.2rem; margin-bottom: 1.2rem; border-left: 4px solid #e67e22; padding-left: 0.8rem; }
        canvas { max-height: 280px; width: 100%; }
        .term-list { list-style: none; }
        .term-list li { display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid #edf2f7; font-size: 0.9rem; }
        .comments-section { background: white; border-radius: 24px; padding: 1.5rem; margin-bottom: 2rem; border: 1px solid #e9edf2; }
        .comment-item { background: #f8fafc; padding: 1rem; border-radius: 16px; margin-bottom: 0.8rem; border-left: 3px solid #e67e22; }
        .comment-text { font-size: 0.9rem; margin-bottom: 0.3rem; }
        .comment-meta { font-size: 0.7rem; color: #7c8b9c; display: flex; gap: 1rem; align-items: center; }
        .badge-cat { background: #ffe8e0; color: #e67e22; padding: 0.2rem 0.6rem; border-radius: 20px; font-weight: 600; font-size: 0.7rem; }
        .footer { text-align: center; margin-top: 2rem; font-size: 0.75rem; color: #8ba0ae; border-top: 1px solid #e2e8f0; padding-top: 1.5rem; }
        @media (max-width: 700px) { .insight-row { grid-template-columns: 1fr; } body { padding: 1rem; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo"><h1>🔍 Política com Lupa</h1><p>Observatório independente de discurso e ódio nas eleições</p></div>
        <div class="badge" id="statusBadge">📡 Carregando...</div>
    </div>
    <div class="stats-grid">
        <div class="card"><div class="card-title">Total analisado</div><div class="card-number" id="totalCount">—</div></div>
        <div class="card"><div class="card-title">Discurso de ódio</div><div class="card-number" id="hateCount">—</div></div>
        <div class="card"><div class="card-title">Taxa de risco</div><div class="card-number" id="riskRate">—<span class="card-unit">%</span></div></div>
        <div class="card"><div class="card-title">Última atualização</div><div class="card-number" id="lastUpdate" style="font-size:1.1rem;">—</div></div>
    </div>
    <div class="insight-row">
        <div class="insight-card"><div class="insight-title">🗂️ Categorias de ódio</div><canvas id="categoryChart"></canvas></div>
        <div class="insight-card"><div class="insight-title">📌 Termos mais frequentes</div><ul class="term-list" id="termList"><li>Carregando...</li></ul></div>
    </div>
    <div class="comments-section"><h3>💬 Últimos comentários classificados como ódio</h3><div id="commentsList"></div></div>
    <div class="footer">Projeto independente | Coleta a cada 12h | Dados públicos do Instagram</div>
</div>
<script>
    const CSV_URL = "/dados_latest.csv";
    let categoryChart = null;
    const hateTerms = {
        'racismo': ['macaco', 'preto', 'crioulo', 'selvagem', 'negro', 'raça', 'inferior', 'escravo', 'primitivo', 'animal'],
        'homofobia': ['viado', 'bicha', 'gay', 'sapatão', 'bixa', 'veado', 'baitola', 'boiola'],
        'transfobia': ['traveco', 'travesti', 'transexual', 'transformado', 'aberração', 'mutante', 'anormal', 'doente'],
        'misoginia': ['puta', 'vadia', 'cadela', 'vagabunda', 'prostituta', 'piranha', 'safada', 'feminista', 'lugar de mulher', 'cozinha'],
        'xenofobia': ['nordestino', 'baiano', 'paraíba', 'cearense', 'norte', 'sertanejo', 'migrante', 'refugiado', 'invasor', 'sem terra']
    };
    function classifyText(text) {
        if (!text) return 'neutro';
        const lower = text.toLowerCase();
        for (const [cat, terms] of Object.entries(hateTerms)) {
            if (terms.some(t => lower.includes(t))) return cat;
        }
        return 'neutro';
    }
    function getTopTerms(texts, topN=15) {
        const stop = new Set(['de','a','o','que','e','do','da','em','um','para','com','não','uma','os','as','se','na','por','mais','dos','das','mas','ao','ele','como','seu','sua','meu','minha','você','pra','pro','tá','né','vai','ser','ter','aquele','aquela','isso','isto','aquilo','está','estão','era','aí','então','foi','são','tudo','muito','bem','vamos','tem','porque']);
        const freq = new Map();
        texts.forEach(t => {
            if (!t) return;
            t.toLowerCase().split(/\s+/).forEach(w => {
                w = w.replace(/[^\wáéíóúâêôãõç]/g,'');
                if (w.length<3 || stop.has(w)) return;
                freq.set(w, (freq.get(w)||0)+1);
            });
        });
        return Array.from(freq.entries()).sort((a,b)=>b[1]-a[1]).slice(0,topN);
    }
    async function loadData() {
        try {
            const res = await fetch(CSV_URL);
            if (!res.ok) throw new Error('CSV não encontrado');
            const text = await res.text();
            Papa.parse(text, {
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    const data = results.data;
                    const classified = data.map(row => ({ ...row, category: classifyText(row.texto) }));
                    const hate = classified.filter(c => c.category !== 'neutro');
                    document.getElementById('totalCount').innerText = data.length;
                    document.getElementById('hateCount').innerText = hate.length;
                    const rate = data.length ? (hate.length/data.length*100).toFixed(2) : 0;
                    document.getElementById('riskRate').innerHTML = rate+'<span class="card-unit">%</span>';
                    document.getElementById('lastUpdate').innerText = new Date().toLocaleString();
                    const catCount = {};
                    hate.forEach(c => catCount[c.category] = (catCount[c.category]||0)+1);
                    if (categoryChart) categoryChart.destroy();
                    const ctx = document.getElementById('categoryChart').getContext('2d');
                    categoryChart = new Chart(ctx, {
                        type: 'bar',
                        data: { labels: Object.keys(catCount), datasets: [{ label: 'Comentários', data: Object.values(catCount), backgroundColor: '#e67e22' }] }
                    });
                    const topTerms = getTopTerms(data.map(d=>d.texto));
                    const termList = document.getElementById('termList');
                    termList.innerHTML = '';
                    topTerms.forEach(([term, freq]) => {
                        const li = document.createElement('li');
                        li.innerHTML = `<span class="term">${term}</span><span class="freq">${freq}</span>`;
                        termList.appendChild(li);
                    });
                    const commentsDiv = document.getElementById('commentsList');
                    commentsDiv.innerHTML = '';
                    hate.slice(0,5).forEach(c => {
                        const div = document.createElement('div');
                        div.className = 'comment-item';
                        div.innerHTML = `<div class="comment-text">${escapeHtml(c.texto)}</div><div class="comment-meta"><span>@${c.autor_username||'anon'}</span><span class="badge-cat">${c.category}</span></div>`;
                        commentsDiv.appendChild(div);
                    });
                    document.getElementById('statusBadge').innerHTML = '📡 Dados carregados';
                }
            });
        } catch(e) {
            console.error(e);
            document.getElementById('statusBadge').innerHTML = '❌ Erro ao carregar';
        }
    }
    function escapeHtml(str) { return str ? str.replace(/[&<>]/g, function(m){return m==='&'?'&':m==='<'?'<':'>';}) : ''; }
    loadData();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# CORREÇÃO #4: usar send_file (evita memory leak)
@app.route('/dados_latest.csv')
def dados_csv():
    path = os.path.join(os.path.dirname(__file__), 'dados_latest.csv')
    if os.path.exists(path):
        return send_file(path, mimetype='text/csv')
    return "Arquivo não encontrado", 404

@app.route('/stats')
def stats():
    path = os.path.join(os.path.dirname(__file__), 'dados_latest.csv')
    if not os.path.exists(path):
        return jsonify({"error": "Arquivo de dados não encontrado"}), 404
    df = pd.read_csv(path)
    hate = df[df['categoria_odio'] != 'neutro']
    cat_counts = hate['categoria_odio'].value_counts().to_dict()
    return jsonify({
        'total': len(df),
        'hate': len(hate),
        'hate_rate': round(len(hate)/len(df)*100, 2) if len(df) else 0,
        'categories': cat_counts,
        'last_update': pd.Timestamp.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)