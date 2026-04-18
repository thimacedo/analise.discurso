import json
import os
import sqlite3
import time
from datetime import datetime
from instagram_collector import ForensicCollector

def run_batch_extraction(limit_percent=0.2):
    print(f"🚀 Iniciando extração em lote ({int(limit_percent*100)}% dos perfis)...")
    
    # 1. Carregar perfis
    with open("perfis_monitorados.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)
    
    total_to_scan = int(len(profiles) * limit_percent)
    targets = profiles[:total_to_scan]
    
    print(f"📈 Alvo: {total_to_scan} perfis de um total de {len(profiles)}.")
    
    collector = ForensicCollector()
    db_file = "odio_politica.db"
    
    success_count = 0
    total_comments = 0

    for profile in targets:
        username = profile["username"]
        print(f"\n📡 Coletando: @{username}...")
        
        try:
            # Coleta comentários dos 2 posts mais recentes de cada
            df = collector.monitor_multiple_candidates([username], posts_per_candidate=2)
            
            if not df.empty:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                for _, row in df.iterrows():
                    try:
                        cursor.execute("""
                            INSERT INTO comentarios (id_externo, candidato_id, post_id, autor_username, texto_bruto, data_coleta, data_publicacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(row['id']), 
                            username, 
                            str(row['post_id']), 
                            row['owner_username'], 
                            row['text'], 
                            datetime.now().isoformat(),
                            row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp'])
                        ))
                        total_comments += 1
                    except sqlite3.IntegrityError:
                        # Ignora duplicados (id_externo único)
                        continue
                
                conn.commit()
                conn.close()
                print(f"✅ Sucesso: {len(df)} comentários processados.")
                success_count += 1
            else:
                print(f"⚠️ Nenhum dado novo para @{username}.")
            
            # Pausa de segurança entre perfis para evitar 429
            print("⏳ Pausa de 15s para resfriamento...")
            time.sleep(15)
            
        except Exception as e:
            print(f"❌ Erro ao processar @{username}: {e}")
            time.sleep(30) # Pausa maior em caso de erro

    print(f"\n🏁 RELATÓRIO FINAL:")
    print(f"✅ Perfis Processados: {success_count}/{total_to_scan}")
    print(f"💬 Total de Comentários Salvos: {total_comments}")

if __name__ == "__main__":
    run_batch_extraction()
