from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# A VARIAVEL ABAIXO PRECISA ESTAR SEM INDENTÇÃO (NADA DE ESPAÇO ANTES)
app = FastAPI(title="Sentinela Democrática API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, troque * pela URL do seu frontend no Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "Sentinela API v1"}

@app.get("/api/v1/alerts")
def get_alerts():
    # Aqui você vai conectar a lógica do dataService ou Supabase no futuro
    return {"alerts": [], "count": 0}
