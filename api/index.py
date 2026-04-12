from flask import Flask, render_template_string, jsonify
import os
import requests
import csv
from io import StringIO
from collections import Counter

app = Flask(__name__)

# URL pública (RAW) dos dados no GitHub para visualização dinâmica
DATA_URL = "https://raw.githubusercontent.com/thimacedo/analise.discurso/main/api/dados_latest.csv"

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Política com Lupa | Monitor de Discurso e Ódio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #f4f7fc;
            color: #1e2a3e;
            line-height: 1.5;
            padding: 2rem 1.5rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1rem;
        }
        .logo h1 {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0f3b5c, #e67e22);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: -0.5px;
        }
        .logo p {
            font-size: 0.85rem;
            color: #5a6e7c;
            margin-top: 0.2rem;
        }
        .badge {
            background: #e2e8f0;
            padding: 0.3rem 1rem;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 500;
            color: #2c3e50;
        }

        /* cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }
        .card {
            background: white;
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            border: 1px solid #e9edf2;
            transition: all 0.2s;
        }
        .card:hover {
            border-color: #cbd5e1;
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        }
        .card-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            color: #5a6e7c;
            margin-bottom: 0.75rem;
        }
        .card-number {
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f3b5c;
            line-height: 1.2;
        }
        .card-unit {
            font-size: 1rem;
            font-weight: 400;
            color: #7f8c8d;
        }
        .risk-high {
            color: #e67e22;
        }

        /* gráfico + lista */
        .insight-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.8rem;
            margin-bottom: 2.5rem;
        }
        .insight-card {
            background: white;
            border-radius: 24px;
            padding: 1.5rem;
            border: 1px solid #e9edf2;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }
        .insight-title {
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-left: 4px solid #e67e22;
            padding-left: 0.8rem;
        }
        canvas {
            max-height: 280px;
            width: 100%;
        }
        .term-list {
            list-style: none;
        }
        .term-list li {
            display: flex;
            justify-content: space-between;
            padding: 0.6rem 0;
            border-bottom: 1px solid #edf2f7;
            font-size: 0.9rem;
        }
        .term-list .term {
            font-weight: 500;
        }
        .term-list .freq {
            color: #e67e22;
            font-weight: 600;
        }

        /* tabela de comentários */
        .comments-section {
            background: white;
            border-radius: 24px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid #e9edf2;
        }
        .comments-section h3 {
            margin-bottom: 1rem;
            font-weight: 700;
        }
        .comment-item {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 16px;
            margin-bottom: 0.8rem;
            border-left: 3px solid #e67e22;
        }
        .comment-text {
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
            color: #1e2a3e;
        }
        .comment-meta {
            font-size: 0.7rem;
            color: #7c8b9c;
            display: flex;
            gap: 1rem;
        }
        .badge-cat {
            background: #ffe8e0;
            color: #e67e22;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.7rem;
        }

        .footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.75rem;
            color: #8ba0ae;
            border-top: 1px solid #e2e8f0;
            padding-top: 1.5rem;
        }

        @media (max-width: 700px) {
            .insight-row {
                grid-template-columns: 1fr;
            }
            body {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">
            <h1>🔍 Política com Lupa</h1>
            <p>Observatório independente de discurso e ódio nas eleições</p>
        </div>
        <div class="badge">📊 Dados em tempo real</div>
    </div>

    <!-- cards dinâmicos -->
    <div class="stats-grid" id="statsGrid">
        <div class="card"><div class="card-title">Total analisado</div><div class="card-number" id="totalCount">—</div></div>
        <div class="card"><div class="card-title">Discurso de ódio</div><div class="card-number" id="hateCount">—</div></div>
        <div class="card"><div class="card-title">Taxa de risco</div><div class="card-number" id="riskRate">—<span class="card-unit">%</span></div></div>
        <div class="card"><div class="card-title">Última atualização</div><div class="card-number" id="lastUpdate" style="font-size:1.1rem;">—</div></div>
    </div>

    <!-- gráfico de categorias + top termos -->
    <div class="insight-row">
        <div class="insight-card">
            <div class="insight-title">🗂️ Categorias de ódio</div>
            <canvas id="categoryChart" width="400" height="250" style="max-height:250px"></canvas>
        </div>
        <div class="insight-card">
            <div class="insight-title">📌 Termos mais frequentes</div>
            <ul class="term-list" id="termList">
                <li><span class="term">carregando...</span><span class="freq"></span></li>
            </ul>
        </div>
    </div>

    <!-- últimos comentários com ódio (mock, mas você pode integrar com API depois) -->
    <div class="comments-section">
        <h3>💬 Últimos comentários classificados como ódio</h3>
        <div id="commentsList">
            <div class="comment-item"><div class="comment-text">Exemplo: “Esse candidato não merece nem o voto dos animais”</div><div class="comment-meta"><span>@usuario</span><span class="badge-cat">xenofobia</span></div></div>
            <div class="comment-item"><div class="comment-text">“Volta para o seu lugar, nordestino”</div><div class="comment-meta"><span>@fulano</span><span class="badge-cat">xenofobia</span></div></div>
            <div class="comment-item"><div class="comment-text">“Lugar de mulher é na cozinha, não na política”</div><div class="comment-meta"><span>@beltrano</span><span class="badge-cat">misoginia</span></div></div>
        </div>
        <p style="font-size:0.75rem; margin-top:0.8rem;">⚠️ Exemplos ilustrativos – integração com dados reais em breve.</p>
    </div>

    <div class="footer">
        Projeto independente de monitoramento do discurso político | Coleta realizada a cada 12h | Dados públicos do Instagram
    </div>
</div>

<script>
    let categoryChart = null;

    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) throw new Error('API indisponível');
            const data = await res.json();
            document.getElementById('totalCount').innerText = data.total || 0;
            document.getElementById('hateCount').innerText = data.hate || 0;
            const rate = data.hate_rate || 0;
            document.getElementById('riskRate').innerHTML = rate + '<span class="card-unit">%</span>';
            document.getElementById('lastUpdate').innerText = new Date().toLocaleString('pt-BR');

            // atualizar gráfico de categorias
            if (data.categories && typeof data.categories === 'object') {
                const labels = Object.keys(data.categories);
                const values = Object.values(data.categories);
                if (categoryChart) categoryChart.destroy();
                const ctx = document.getElementById('categoryChart').getContext('2d');
                categoryChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Comentários',
                            data: values,
                            backgroundColor: '#e67e22',
                            borderRadius: 8,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: { position: 'top' },
                        }
                    }
                });
            } else {
                // fallback mock para demonstração
                const mockCategories = {racismo: 12, homofobia: 8, misoginia: 5, xenofobia: 7};
                const labels = Object.keys(mockCategories);
                const values = Object.values(mockCategories);
                if (categoryChart) categoryChart.destroy();
                const ctx = document.getElementById('categoryChart').getContext('2d');
                categoryChart = new Chart(ctx, {
                    type: 'bar',
                    data: { labels: labels, datasets: [{ label: 'Comentários', data: values, backgroundColor: '#e67e22' }] }
                });
            }
        } catch (err) {
            console.error(err);
            document.getElementById('totalCount').innerText = 'Erro';
            document.getElementById('hateCount').innerText = '—';
            document.getElementById('riskRate').innerHTML = '—';
        }
    }

    // Para a lista de termos, se você tiver um endpoint /terms, use. Enquanto isso, mock.
    function loadTerms() {
        const termsMock = [
            { term: "vergonha", freq: 34 }, { term: "bandido", freq: 28 }, { term: "ladrão", freq: 22 },
            { term: "incompetente", freq: 19 }, { term: "corrupto", freq: 15 }
        ];
        const listEl = document.getElementById('termList');
        listEl.innerHTML = '';
        termsMock.forEach(t => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="term">${t.term}</span><span class="freq">${t.freq}</span>`;
            listEl.appendChild(li);
        });
    }

    loadStats();
    loadTerms();
    setInterval(loadStats, 60000); // atualiza a cada minuto (opcional)
</script>
</body>
</html>
    """)

@app.route('/api/stats')
def stats():
    try:
        # Busca os dados do GitHub Raw
        response = requests.get(DATA_URL, timeout=10)
        if response.status_code != 200:
            return jsonify({"total": 0, "hate": 0, "hate_rate": 0, "msg": "Aguardando GitHub Raw..."})
        
        f = StringIO(response.text)
        reader = csv.DictReader(f)
        data = list(reader)
        
        total = len(data)
        hate_count = sum(1 for row in data if row.get('categoria_odio') != 'neutro')
        rate = round((hate_count / total * 100), 1) if total > 0 else 0
        
        # Conta categorias
        categories = Counter()
        for row in data:
            cat = row.get('categoria_odio', 'neutro')
            if cat != 'neutro':
                categories[cat] += 1
        
        return jsonify({
            'total': total, 
            'hate': hate_count, 
            'hate_rate': rate,
            'categories': dict(categories)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)