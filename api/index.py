from flask import Flask, render_template_string, jsonify
import os
import sys

# Ajuste do path para o ambiente serverless
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Design System & UI HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ForenseNet | Inteligência em Discurso de Ódio</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #818cf8;
            --primary-dark: #6366f1;
            --secondary: #f43f5e;
            --glass: rgba(30, 41, 59, 0.7);
            --bg: #020617;
            --text: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 100% 100%, rgba(244, 63, 94, 0.1) 0%, transparent 50%);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }

        .navbar {
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-weight: 800;
            font-size: 1.5rem;
            background: linear-gradient(to right, #818cf8, #f43f5e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .container { max-width: 1200px; margin: 0 auto; padding: 4rem 2rem; }

        .hero { text-align: center; margin-bottom: 6rem; }
        
        .badge {
            display: inline-block;
            padding: 0.5rem 1.25rem;
            background: rgba(129, 140, 248, 0.1);
            border: 1px solid rgba(129, 140, 248, 0.2);
            border-radius: 99px;
            color: var(--primary);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 2rem;
        }

        h1 {
            font-size: clamp(2.5rem, 8vw, 5rem);
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            letter-spacing: -0.03em;
        }

        .hero p {
            font-size: 1.25rem;
            color: var(--text-muted);
            max-width: 700px;
            margin: 0 auto 3rem;
        }

        .btn-group { display: flex; gap: 1rem; justify-content: center; }

        .btn {
            padding: 1rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            border: none;
        }

        .btn-primary {
            background: var(--primary);
            color: #fff;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-3px);
            background: var(--primary-dark);
            box-shadow: 0 20px 30px -10px rgba(99, 102, 241, 0.5);
        }

        .btn-outline {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text);
        }

        .btn-outline:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 4rem;
        }

        .card {
            background: var(--glass);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 2.5rem;
            border-radius: 24px;
            transition: all 0.3s ease;
        }

        .card:hover { border-color: var(--primary); transform: scale(1.02); }

        .card-icon {
            width: 48px;
            height: 48px;
            background: rgba(129, 140, 248, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
            color: var(--primary);
            font-size: 1.5rem;
        }

        .card h3 { font-size: 1.5rem; margin-bottom: 1rem; }
        .card p { color: var(--text-muted); font-size: 1rem; }

        .warning-box {
            background: rgba(244, 63, 94, 0.05);
            border: 1px solid rgba(244, 63, 94, 0.2);
            padding: 1.5rem;
            border-radius: 16px;
            margin-top: 4rem;
            display: flex;
            align-items: flex-start;
            gap: 1rem;
        }

        .warning-box span { color: var(--secondary); font-weight: 700; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ForenseNet</div>
        <div class="nav-links">
            <a href="/status" class="btn btn-outline" style="padding: 0.5rem 1rem; font-size: 0.8rem;">API Status</a>
        </div>
    </nav>

    <div class="container">
        <section class="hero">
            <span class="badge">Vercel Serverless Ready</span>
            <h1>Análise Forense de Discurso.</h1>
            <p>Integração de metodologias linguísticas com inteligência computacional para identificação e monitoramento de ódio no debate político.</p>
            <div class="btn-group">
                <a href="#github" class="btn btn-primary">Documentação</a>
                <a href="/status" class="btn btn-outline">Monitorar Operação</a>
            </div>
        </section>

        <div class="grid">
            <div class="card">
                <div class="card-icon">📊</div>
                <h3>Linguística Digital</h3>
                <p>Processamento automatizado seguindo a metodologia pericial para detecção de marcadores discursivos.</p>
            </div>
            <div class="card">
                <div class="card-icon">🧠</div>
                <h3>Inteligência Híbrida</h3>
                <p>Uso combinado de modelos locais e LLMs (OpenAI/Claude) para alta precisão taxonômica.</p>
            </div>
            <div class="card">
                <div class="card-icon">🛡️</div>
                <h3>Proteção de Dados</h3>
                <p>Monitoramento ético focado em segurança digital e transparência democrática.</p>
            </div>
        </div>

        <div class="warning-box">
            <span>⚠️ Nota de Deployment:</span>
            <p style="color: var(--text-muted); font-size: 0.9rem;">
                Este ambiente Vercel atua como interface de consulta e dashboard. A coleta intensiva (Scraping) e processamento pesado de corpus devem ser executados em workers dedicados ou ambiente local devido a restrições de tempo de execução serverless.
            </p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status')
def status():
    return jsonify({
        "system": "ForenseNet",
        "runtime": "Vercel Serverless (Python 3.9+)",
        "status": "online",
        "api_endpoints": ["/status", "/"],
        "notice": "Long-running tasks (scraping/NLP) disabled in serverless mode."
    })

# Exportação do app para o Vercel
app_handler = app
if __name__ == "__main__":
    app.run(debug=True)
