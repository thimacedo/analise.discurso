from flask import Flask, render_template_string, jsonify
import os
import requests
import csv
from io import StringIO

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
        <title>ForenseNet | Monitor de Ódio</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;800&display=swap" rel="stylesheet">
        <style>
            :root { --p: #6366f1; --bg: #020617; }
            body { font-family: 'Outfit', sans-serif; background: var(--bg); color: white; padding: 40px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 900px; margin: 40px auto; }
            .card { background: #1e293b66; border: 1px solid #334155; padding: 30px; border-radius: 20px; }
            .val { font-size: 54px; font-weight: 800; color: var(--p); }
            .label { color: #94a3b8; text-transform: uppercase; font-size: 11px; letter-spacing: 2px; }
        </style>
    </head>
    <body>
        <h1 style="font-weight: 800; font-size: 38px">Forense<span style="color:var(--p)">Net</span></h1>
        <div class="grid">
            <div class="card"><div class="label">Total Analisado</div><div class="val" id="total">--</div></div>
            <div class="card"><div class="label">Discurso de Ódio</div><div class="val" id="odio" style="color:#f43f5e">--</div></div>
            <div class="card"><div class="label">Taxa de Risco</div><div class="val" id="rate">--</div></div>
        </div>
        <script>
            fetch('/api/stats').then(res => res.json()).then(data => {
                document.getElementById('total').innerText = data.total;
                document.getElementById('odio').innerText = data.hate;
                document.getElementById('rate').innerText = data.hate_rate + '%';
            });
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
        
        return jsonify({'total': total, 'hate': hate_count, 'hate_rate': rate})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
