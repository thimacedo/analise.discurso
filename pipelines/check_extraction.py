import json
import os
import pandas as pd
from instagram_collector import ForensicCollector

def check_extraction_process():
    print("🧐 Analisando processo de extração de comentários...")
    try:
        # 1. Carregar perfis mapeados
        output_file = "perfis_monitorados.json"
        if not os.path.exists(output_file):
            print(f"❌ Erro: {output_file} não encontrado.")
            return
            
        with open(output_file, "r", encoding="utf-8") as f:
            profiles = json.load(f)
        
        if not profiles:
            print("❌ Erro: Lista de perfis monitorados está vazia.")
            return

        target_username = profiles[0]["username"]
        print(f"🔍 Testando extração real para o primeiro perfil da lista: @{target_username}")
        
        collector = ForensicCollector()
        # Coleta apenas 1 post para teste rápido
        df = collector.monitor_multiple_candidates([target_username], posts_per_candidate=1)
        
        if not df.empty:
            print(f"✅ SUCESSO! Extraídos {len(df)} comentários de @{target_username}.")
            print("--- AMOSTRA DOS DADOS ---")
            print(df[["owner_username", "text"]].head(5).to_string(index=False))
            
            # Verificar se os comentários são "apropriados" (se têm conteúdo de texto)
            empty_comments = df[df["text"].str.strip() == ""].shape[0]
            if empty_comments > 0:
                print(f"⚠️ Alerta: Detectados {empty_comments} comentários vazios.")
            else:
                print("✨ Qualidade dos dados: Comentários contêm texto válido.")
        else:
            print(f"⚠️ Nenhum comentário extraído de @{target_username}. Motivos possíveis: Sem posts recentes, perfil privado ou restrição temporária.")

        # 2. Verificação de Armazenamento
        db_file = "odio_politica.db"
        if os.path.exists(db_file):
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM comments") # Ajustar se o nome da tabela for diferente
            count = cursor.fetchone()[0]
            print(f"📂 Banco de Dados: {db_file} contém {count} registros.")
            conn.close()
        else:
            print(f"⚠️ Banco de dados {db_file} não encontrado na raiz.")

    except Exception as e:
        print(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    check_extraction_process()
