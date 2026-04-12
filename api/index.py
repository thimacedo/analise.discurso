from flask import Flask, render_template_string, jsonify
import os
import sys

# Adiciona o diretório raiz ao path para importar os módulos do pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ForenseNet | Análise de Discurso de Ódio</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --bg: #0f172a;
                --card-bg: #1e293b;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --accent: #f43f5e;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                line-height: 1.6;
                overflow-x: hidden;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
            }

            header {
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                background: radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            }

            .hero-content h1 {
                font-size: 4rem;
                font-weight: 800;
                margin-bottom: 1rem;
                letter-spacing: -0.02em;
                background: linear-gradient(to right, #fff, #94a3b8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-content p {
                font-size: 1.25rem;
                color: var(--text-muted);
                max-width: 600px;
                margin: 0 auto 2rem;
            }

            .badge {
                display: inline-block;
                padding: 0.5rem 1rem;
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 99px;
                color: var(--primary);
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 2rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .btn {
                display: inline-block;
                padding: 1rem 2.5rem;
                background-color: var(--primary);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
            }

            .btn:hover {
                background-color: var(--primary-dark);
                transform: translateY(-2px);
                box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.5);
            }

            .features {
                padding: 100px 0;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
            }

            .card {
                background: var(--card-bg);
                padding: 2.5rem;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                transition: transform 0.3s ease;
            }

            .card:hover {
                transform: translateY(-5px);
                border-color: rgba(99, 102, 241, 0.3);
            }

            .card h3 {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: var(--primary);
            }

            .card p {
                color: var(--text-muted);
            }

            .status-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-top: 2rem;
                font-size: 0.875rem;
                color: var(--text-muted);
            }

            .dot {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                box-shadow: 0 0 10px #10b981;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.4; }
                100% { opacity: 1; }
            }

            footer {
                padding: 4rem 0;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
                color: var(--text-muted);
                font-size: 0.875rem;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container hero-content">
                <span class="badge">Linguística Forense + Tecnologia Digital</span>
                <h1>ForenseNet v1.0</h1>
                <p>Plataforma avançada de monitoramento e análise de discurso de ódio em contextos políticos digitais.</p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <a href="/status" class="btn">Ver Status do Sistema</a>
                </div>
                <div class="status-indicator">
                    <div class="dot"></div>
                    <span>Pipeline operacional e pronto para análise</span>
                </div>
            </div>
        </header>

        <section class="features">
            <div class="container">
                <div class="grid">
                    <div class="card">
                        <h3>Coleta Automatizada</h3>
                        <p>Extração profunda de comentários e interações de perfis políticos via InstagramCollector.</p>
                    </div>
                    <div class="card">
                        <h3>Análise Linguística</h3>
                        <p>Processamento de linguagem natural (NLP) para identificação de padrões de ódio e preconceito.</p>
                    </div>
                    <div class="card">
                        <h3>Relatórios Periciais</h3>
                        <p>Geração de evidências estruturadas com visualizações dinâmicas e métricas temporais.</p>
                    </div>
                </div>
            </div>
        </section>

        <footer>
            <div class="container">
                <p>&copy; 2026 ForenseNet. Desenvolvido para pesquisa em análise do discurso e tecnologia.</p>
            </div>
        </footer>
    </body>
    </html>
    """
    return html_content

@app.route('/status')
def status():
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "modules": [
            "InstagramCollector",
            "CorpusBuilder",
            "HateSpeechClassifier",
            "DataMiner",
            "DataVisualizer"
        ],
        "environment": "Vercel Serverless"
    })

if __name__ == "__main__":
    app.run(debug=True)
