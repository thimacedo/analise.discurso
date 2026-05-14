from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import monitor

# A VARIAVEL ABAIXO PRECISA ESTAR SEM INDENTÇÃO (NADA DE ESPAÇO ANTES)
app = FastAPI(title="Sentinela Democrática API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, troque * pela URL do seu frontend no Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitor.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "Sentinela API v1"}
