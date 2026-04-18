import requests
import os
import json
from database.repository import DatabaseRepository
from database.models import Comentario, Classificacao, Candidato

def manual_push():
    print("🚀 Extraindo dados do banco local...")
    db = DatabaseRepository()
    session = db.get_session()
    
    # Busca comentários, classificações e candidatos (usando os modelos corretos)
    results = session.query(Comentario, Classificacao, Candidato)\
        .join(Classificacao, Comentario.id == Classificacao.comentario_id)\
        .join(Candidato, Comentario.candidato_id == Candidato.id)\
        .limit(200).all()
        
    payload = []
    for c, cl, can in results:
        payload.append({
            "id_externo": c.id_externo,
            "candidato": can.username,
            "autor": c.autor_username,
            "texto": c.texto_bruto,
            "data": c.data_publicacao.isoformat() if c.data_publicacao else None,
            "categoria": cl.categoria_odio,
            "score": cl.score
        })
    
    print(f"📦 Payload preparado com {len(payload)} itens.")
    
    headers = {
        'X-PIN': '1234',
        'Content-Type': 'application/json'
    }
    
    try:
        url = 'https://analise.discurso.git/api/v1/sync' # URL baseada no seu git, corrigindo para a real:
        url = 'https://analise-discurso.vercel.app/api/v1/sync'
        
        print(f"📡 Enviando para {url}...")
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"✅ Status: {r.status_code}")
        print(f"📩 Resposta: {r.text}")
    except Exception as e:
        print(f"❌ Erro no envio: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    manual_push()
