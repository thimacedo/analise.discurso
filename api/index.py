from flask import Flask, render_template_string, jsonify
import os
import csv
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

# URL pública dos dados no GitHub Raw (atualize com seu usuário e repositório)
DATA_URL = "https://raw.githubusercontent.com/thimacedo/analise.discurso/main/corpus_classificado_latest.csv"

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ForenseNet | Monitor de Discurso de Ódio</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;600;800&display=swap" rel="stylesheet">
        <style>
            :root { --p: #6366f1; --s: #f43f5e; --bg: #020617; --card: #1e293b66; }
            body { font-family: 'Outfit', sans-serif; background: var(--bg); color: #f8fafc; margin: 0; padding: 40px; }
            .container { max-width: 1100px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 20px; }
            .badge { background: #10b98122; color: #10b981; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid #10b98144; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 40px 0; }
            .card { background: var(--card); border: 1px solid #334155; padding: 30px; border-radius: 24px; backdrop-filter: blur(10px); }
            .val { font-family: 'JetBrains Mono', monospace; font-size: 54px; font-weight: 800; color: var(--p); margin: 10px 0; }
            .label { color: #94a3b8; text-transform: uppercase; font-size: 13px; letter-spacing: 2px; }
            footer { text-align: center; color: #475569; font-size: 12px; margin-top: 60px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1 style="margin:0; font-weight: 800; font-size: 32px">Forense<span style="color:var(--p)">Net</span></h1>
                    <p style="color:#64748b; margin: 5px 0 0">Monitoramento Linguístico-Forense Automático</p>
                </div>
                <div class="badge">SISTEMA ONLINE</div>
            </div>

            <div class="grid">
                <div class="card"><div class="label">Volume Analisado</div><div class="val" id="total">--</div></div>
                <div class="card"><div class="label">Casos de Ódio</div><div class="val" id="odio" style="color:var(--s)">--</div></div>
                <div class="card"><div class="label">Taxa de Risco</div><div class="val" id="rate">--</div></div>
            </div>
        </div>

        <footer>Metodologia Prof. Leonardo Vichi | Processamento via GitHub Actions | Front-end Vercel</footer>

        <script>
            fetch('/api/stats').then(res => res.json()).then(data => {
                document.getElementById('total').innerText = data.total || 0;
                document.getElementById('odio').innerText = data.hate || 0;
                document.getElementById('rate').innerText = (data.hate_rate || 0) + '%';
            });
        </script>
    </body>
    </html>
    """)

@app.route('/api/stats')
def stats():
    try:
        # Baixa dados diretamente do GitHub Raw
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        total = len(df)
        hate = df[df['categoria_odio'] != 'neutro']
        
        return jsonify({
            'total': total,
            'hate': len(hate),
            'hate_rate': round(len(hate)/total*100, 2),
            'categories': hate['categoria_odio'].value_counts().to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
