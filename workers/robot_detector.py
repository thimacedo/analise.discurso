import sqlite3
import collections
import json

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"

def analyze_networks():
    print("🧠 [CROSS-ANALYSIS] Cruzando padroes de Bots com Discurso de Odio...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Busca perfis suspeitos e seus vereditos
    c.execute("""
        SELECT autor_username, COUNT(*) as volume, 
               SUM(CASE WHEN is_hate = 1 THEN 1 ELSE 0 END) as total_hate,
               GROUP_CONCAT(DISTINCT categoria_ia) as categorias
        FROM comentarios 
        WHERE autor_username NOT LIKE 'sentinela_%'
        GROUP BY autor_username
        HAVING volume > 1 OR total_hate > 0
        ORDER BY total_hate DESC, volume DESC
    """)
    rows = c.fetchall()
    
    network_data = []
    for r in rows:
        network_data.append({
            "username": r[0],
            "volume": r[1],
            "odio": r[2],
            "categorias": r[3],
            "score": round((r[2] / r[1]) * 100 if r[1] > 0 else 0, 1)
        })
    
    # Salva resultado para o frontend consumir via Supabase (Metadados)
    print(f"✅ Analise concluida: {len(network_data)} perfis na malha de interesse.")
    return network_data

if __name__ == '__main__':
    data = analyze_networks()
    # Simula o output para conferência
    for p in data[:5]:
        print(f"Perfil: @{p['username']} | Odio: {p['odio']} | Risco: {p['score']}%")
