from flask import Flask, render_template_string, jsonify
import os
import requests
import csv
from io import StringIO

app = Flask(__name__)

# Configuração Cloud (Busca direto do S3 público)
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'forense-dados-publicos')
REGION = os.getenv('AWS_REGION', 'us-east-1')
CSV_URL = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/corpus_classificado_latest.csv"

@app.route('/')
def home():
    # Template simplificado que consome a API /api/stats
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ForenseNet | Monitor</title>
        <style>
            body { font-family: sans-serif; background: #0f172a; color: white; padding: 40px; }
            .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
            .card { background: #1e293b; padding: 20px; border-radius: 10px; text-align: center; }
            .val { font-size: 40px; font-weight: bold; color: #818cf8; }
        </style>
    </head>
    <body>
        <h1>📊 ForenseNet - Monitoramento em Tempo Real</h1>
        <div class="grid">
            <div class="card"><div class="val" id="total">--</div>Total Comentários</div>
            <div class="card"><div class="val" id="odio" style="color:#f43f5e">--</div>Discurso de Ódio</div>
            <div class="card"><div class="val" id="taxa">--</div>Taxa de Risco</div>
        </div>
        <script>
            fetch('/api/stats').then(res => res.json()).then(data => {
                document.getElementById('total').innerText = data.total;
                document.getElementById('odio').innerText = data.hate;
                document.getElementById('taxa').innerText = data.hate_rate + '%';
            });
        </script>
    </body>
    </html>
    """)

@app.route('/api/stats')
def stats():
    try:
        response = requests.get(CSV_URL, timeout=5)
        if response.status_code != 200:
            return jsonify({"total": 0, "hate": 0, "hate_rate": 0})
        
        f = StringIO(response.text)
        reader = csv.DictReader(f)
        data = list(reader)
        
        total = len(data)
        hate_count = sum(1 for row in data if row.get('categoria_odio') != 'neutro')
        rate = round((hate_count / total * 100), 2) if total > 0 else 0
        
        return jsonify({
            'total': total,
            'hate': hate_count,
            'hate_rate': rate
        })
    except Exception:
        return jsonify({"total": "Erro", "hate": "S3", "hate_rate": "Offline"})

if __name__ == "__main__":
    app.run(debug=True)
