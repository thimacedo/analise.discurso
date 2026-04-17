# migrar_csv_para_db.py
import pandas as pd
import glob
import os
from database.repository import DatabaseRepository
from database.models import Comentario
from datetime import datetime

def migrar():
    # Garante que o script rode no diretório correto para o glob funcionar
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("="*60)
    print("🚚 MIGRANDO DADOS HISTÓRICOS (CSV -> SQLITE)")
    print("="*60)
    
    db = DatabaseRepository()
    db.criar_tabelas()
    
    # 1. Localizar arquivos de dados brutos
    arquivos_brutos = glob.glob("dados_brutos*.csv")
    print(f"📂 Encontrados {len(arquivos_brutos)} arquivos de dados brutos.")
    
    for arquivo in arquivos_brutos:
        print(f"📖 Processando {arquivo}...")
        try:
            df = pd.read_csv(arquivo)
            # Normalização de nomes de colunas
            df.columns = [c.lower() for c in df.columns]
            
            for _, row in df.iterrows():
                # Salva Candidato
                candidate_name = row.get('candidate', row.get('candidato', 'desconhecido'))
                candidato = db.salvar_candidato(candidate_name, {})
                
                # Salva Comentário
                db.salvar_comentario(candidato.id, {
                    'id_externo': str(row.get('id', row.get('id_externo', ''))),
                    'post_id': str(row.get('post_id', '')),
                    'autor_username': row.get('owner_username', row.get('autor_username', 'anonimo')),
                    'texto_bruto': row.get('text', row.get('texto_bruto', row.get('texto', ''))),
                    'data_publicacao': pd.to_datetime(row.get('timestamp', row.get('data_publicacao', datetime.now())))
                })
        except Exception as e:
            print(f"⚠️ Erro ao processar {arquivo}: {e}")

    # 2. Localizar arquivos classificados
    arquivos_classificados = glob.glob("corpus_classificado*.csv")
    if not arquivos_classificados and os.path.exists("corpus_classificado.csv"):
        arquivos_classificados = ["corpus_classificado.csv"]
        
    print(f"\n📂 Encontrados {len(arquivos_classificados)} arquivos classificados.")
    
    for arquivo in arquivos_classificados:
        print(f"📖 Processando classificações de {arquivo}...")
        try:
            df = pd.read_csv(arquivo)
            count = 0
            for _, row in df.iterrows():
                id_ext = str(row.get('id', row.get('id_externo')))
                
                session = db.get_session()
                try:
                    comentario = session.query(Comentario).filter(Comentario.id_externo == id_ext).first()
                    if comentario:
                        db.salvar_classificacao(comentario.id, {
                            'categoria_odio': row.get('category'),
                            'score': row.get('score'),
                            'confianca': row.get('confidence'),
                            'modelo_versao': 'legacy-migration'
                        })
                        count += 1
                finally:
                    session.close()
            print(f"✅ {count} classificações migradas de {arquivo}.")
        except Exception as e:
            print(f"⚠️ Erro ao processar classificações de {arquivo}: {e}")

    print("\n" + "="*60)
    print("✨ MIGRAÇÃO CONCLUÍDA")
    print("="*60)

if __name__ == "__main__":
    migrar()
