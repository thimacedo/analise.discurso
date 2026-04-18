# teste_completo_v2.py
import pandas as pd
from local_qwen_classifier import QwenLocalClassifier
from database.repository import DatabaseRepository
from database.models import Comentario, Classificacao
import os

def executar_teste():
    print("="*60)
    print("🧪 TESTE DE INTEGRAÇÃO - FORENSENET v2.1 (IA LOCAL)")
    print("="*60)

    # 1. Configurar Banco
    db = DatabaseRepository()
    db.criar_tabelas()
    execucao = db.iniciar_execucao()
    print("✅ Banco de dados inicializado.")

    # 2. Dados de Teste (Simulando Coleta)
    print("\n[1/3] Simulando coleta de dados...")
    test_data = [
        {
            "candidate": "candidato_teste",
            "id_externo": "test_001",
            "post_id": "post_A",
            "owner_username": "usuario_comum",
            "text": "Acho que as propostas de educação são boas.",
            "timestamp": "2026-04-17 10:00:00"
        },
        {
            "candidate": "candidato_teste",
            "id_externo": "test_002",
            "post_id": "post_A",
            "owner_username": "hater_radical",
            "text": "Esses políticos do norte são todos preguiçosos e não deveriam votar.",
            "timestamp": "2026-04-17 10:05:00"
        }
    ]
    raw_df = pd.DataFrame(test_data)
    
    # Salvar no Banco
    for _, row in raw_df.iterrows():
        cand = db.salvar_candidato(row['candidate'], {"partido": "TESTE"})
        db.salvar_comentario(cand.id, {
            'id_externo': row['id_externo'],
            'post_id': row['post_id'],
            'autor_username': row['owner_username'],
            'texto_bruto': row['text'],
            'data_publicacao': pd.to_datetime(row['timestamp'])
        })
    print(f"✅ {len(test_data)} comentários persistidos no DB.")

    # 3. Classificação Local (IA Qwen)
    print("\n[2/3] Acionando Qwen Local via Ollama...")
    classifier = QwenLocalClassifier()
    # No teste real, passamos o texto limpo, aqui passamos o bruto para simplificar
    classified_df = classifier.classify_batch(raw_df['text'].tolist())
    
    # Merge e Persistência das Classificações
    final_df = pd.concat([raw_df, classified_df], axis=1)
    
    print("\n[3/3] Vinculando classificações no Banco...")
    total_odio = 0
    for _, row in final_df.iterrows():
        session = db.get_session()
        try:
            comentario = session.query(Comentario).filter(Comentario.id_externo == row['id_externo']).first()
            if comentario:
                db.salvar_classificacao(comentario.id, {
                    'categoria_odio': row.get('category', 'NEUTRO'),
                    'score': float(row.get('score', 0.0)),
                    'confianca': float(row.get('confidence', 0.0)),
                    'modelo_versao': 'qwen-test-v2.1'
                })
                if row.get('is_hate'):
                    total_odio += 1
                    print(f"🚩 ÓDIO DETECTADO: [{row['category']}] -> {row['text'][:50]}...")
        finally:
            session.close()

    db.finalizar_execucao(execucao.id, "SUCESSO", len(test_data), len(test_data))
    
    print("\n" + "="*60)
    print("✨ TESTE CONCLUÍDO COM SUCESSO")
    print(f"📊 Total analisado: {len(test_data)}")
    print(f"🚩 Casos de ódio identificados: {total_odio}")
    print("="*60)

if __name__ == "__main__":
    executar_teste()
