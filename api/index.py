from flask import Flask, render_template_string, jsonify
import os
import requests
import csv
from io import StringIO

app = Flask(__name__)

# Configuração Cloud
BUCKET_URL = f"https://{os.getenv('AWS_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com"

# Design System & UI HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForenseNet | Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #818cf8; --secondary: #f43f5e; --bg: #020617; --text: #f8fafc; }
        body { font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3rem; }
        .logo { font-weight: 800; font-size: 1.5rem; color: var(--primary); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }
        .stat-card { background: rgba(30, 41, 59, 0.7); padding: 2rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
        .stat-value { font-size: 2.5rem; font-weight: 800; color: var(--secondary); }
        .stat-label { color: #94a3b8; font-size: 0.9rem; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; }
        .viz-card { background: rgba(30, 41, 59, 0.7); padding: 1.5rem; border-radius: 20px; text-align: center; }
        .viz-card img { max-width: 100%; border-radius: 12px; margin-top: 1rem; }
        .btn { padding: 0.75rem 1.5rem; background: var(--primary); color: white; border-radius: 10px; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div class="logo">ForenseNet</div>
            <a href="#" class="btn" onclick="location.reload()">Atualizar Dados</a>
        </nav>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="val-total">--</div>
                <div class="stat-label">Comentários</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="val-hate">--</div>
                <div class="stat-label">Discurso de Ódio</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="val-risk">--</div>
                <div class="stat-label">Status de Risco</div>
            </div>
        </div>

        <div class="image-grid">
            <div class="viz-card">
                <h3>Nuvem de Termos</h3>
                <img src="{{ bucket_url }}/nuvem_geral.png" onerror="this.src='https://placehold.co/600x400/1e293b/6366f1?text=Aguardando+Dados'">
            </div>
            <div class="viz-card">
                <h3>Monitoramento 24h</h3>
                <img src="{{ bucket_url }}/categories.png" onerror="this.src='https://placehold.co/600x400/1e293b/f43f5e?text=Disponível+em+Breve'">
            </div>
        </div>
    </div>
    <script>
        async function load() {
            const r = await fetch('/api/stats');
            const d = await r.json();
            document.getElementById('val-total').innerText = d.total;
            document.getElementById('val-hate').innerText = d.hate + '%';
            document.getElementById('val-risk').innerText = d.risk;
        }
        load();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, bucket_url=BUCKET_URL)

@app.route('/api/stats')
def stats():
    try:
        csv_url = f"{BUCKET_URL}/corpus_classificado.csv"
        res = requests.get(csv_url, timeout=5)
        if res.status_code == 200:
            f = StringIO(res.text)
            reader = csv.DictReader(f)
            data = list(reader)
            total = len(data)
            hate_count = sum(1 for row in data if row.get('is_hate_speech', '').lower() == 'true' or row.get('is_hate_speech') == '1')
            hate_rate = round((hate_count / total) * 100, 1) if total > 0 else 0
            return jsonify({
                "total": total,
                "hate": hate_rate,
                "risk": "Controlado" if hate_rate < 5 else "Critico"
            })
    except: pass
    return jsonify({"total": 0, "hate": 0, "risk": "Sem dados"})

if __name__ == "__main__":
    app.run(debug=True)
