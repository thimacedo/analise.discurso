import json
import os

PRIORITY_NAMES = [
    'lulaoficial', 'flaviobolsonaro', 'allysonbezerra.rn', 'alvarodiasrn', 
    'rogeriomarinho', 'fatimabezerrapetista', 'styvensonvalentim', 
    'nikolasferreirainfo', 'erikahiltonoficial', 'jones.manoel'
]

def reconcile():
    if not os.path.exists("current_followings.json"):
        print("❌ Lista de seguidos não encontrada.")
        return

    # Lê o arquivo gerado pelo Apify CLI (UTF-16)
    try:
        with open("current_followings.json", "r", encoding="utf-16") as f:
            raw = f.read()
            json_start = raw.find("[")
            data = json.loads(raw[json_start:])
    except:
        with open("current_followings.json", "r", encoding="utf-8") as f:
            raw = f.read()
            json_start = raw.find("[")
            data = json.loads(raw[json_start:])

    # Coleta todos os seguidos
    all_targets = []
    for item in data:
        # O actor retorna seguidos se resultsType for apropriado
        # Se for o scraper geral, pegamos do ownerUsername do monitor
        # mas aqui assumimos que o arquivo tem a lista de perfis.
        pass

    print(f"📊 Reconciliando {len(PRIORITY_NAMES)} alvos de elite.")
    
    # Criar fila de execução imediata
    queue = PRIORITY_NAMES # Começamos com os mapeados
    
    # Salva o plano de coleta
    with open("data/priority_queue.json", "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)
    
    print(f"✅ Fila de elite gerada: {', '.join(queue)}")

if __name__ == "__main__":
    reconcile()
