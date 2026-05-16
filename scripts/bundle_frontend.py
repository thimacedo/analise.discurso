import os

files_to_bundle = [
    "index.html",
    "local_dashboard.html",
    "src/styles/main.css",
    "src/config.js",
    "src/core/app.js",
    "src/core/state.js",
    "src/core/ui.js",
    "src/core/auth.js",
    "src/core/payments.js",
    "src/core/workers_view.js",
    "src/core/workersUI.js",
    "src/services/apiService.js",
    "src/services/dataService.js",
    "src/services/authService.js",
    "src/services/fcmService.js",
    "src/services/firebaseConfig.js",
    "src/services/paymentService.js",
    "src/components/session-manager.js",
    "src/components/NotificationToast.js",
    "src/components/BrazilMap.js",
    "src/components/PredictiveTrends.js"
]

with open('frontend_context.md', 'w', encoding='utf-8') as outfile:
    outfile.write("# Contexto Completo do Frontend - Sentinela Democrática\n\n")
    outfile.write("Este arquivo contém o código fonte unificado de toda a camada Frontend (Vanilla JS, HTML e CSS).\n\n")
    for fpath in files_to_bundle:
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as infile:
                ext = fpath.split('.')[-1]
                if ext == 'js': ext = 'javascript'
                outfile.write(f"## Arquivo: `{fpath}`\n\n```{ext}\n")
                outfile.write(infile.read())
                outfile.write("\n```\n\n")
        else:
            outfile.write(f"## Arquivo: `{fpath}`\n\n> Aviso: Arquivo não encontrado no sistema.\n\n")

print("Arquivo frontend_context.md gerado com sucesso!")
