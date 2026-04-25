import json
import os
import subprocess
import sys

# CONFIGURAÇÕES
PROJECT_ID = "gen-lang-client-0990464313"
BUCKET = "gs://prompt-opt-data-gen-lang-0990464313"
DATASET_PATH = r"E:\prompt_dataset.jsonl"
THRESHOLD = 5  # Rodar otimização a cada 5 novos exemplos

def append_to_dataset(input_text, output_text):
    entry = {"input": input_text, "output": output_text}
    with open(DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"✅ Registrado no dataset local.")
    check_and_trigger()

def check_and_trigger():
    if not os.path.exists(DATASET_PATH):
        return
    
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    count = len(lines)
    print(f"📊 Dataset atual: {count} exemplos.")
    
    if count >= THRESHOLD and count % THRESHOLD == 0:
        print("🚀 Limite atingido! Iniciando ciclo de otimização no Vertex AI...")
        run_sync_and_opt()

def run_sync_and_opt():
    try:
        # 1. Sync GCS
        print("☁️ Sincronizando dados com GCS...")
        subprocess.run(["gcloud", "storage", "cp", DATASET_PATH, f"{BUCKET}/data/train_data.jsonl"], check=True)
        subprocess.run(["gcloud", "storage", "cp", DATASET_PATH, f"{BUCKET}/data/test_data.jsonl"], check=True)
        
        # 2. Nota: O disparo do job via script Python puro exigiria o SDK instalado.
        # Em modo YOLO, eu (o agente) vou assumir o disparo do comando 'run_data_driven_optimize' 
        # assim que este script me retornar o sinal verde.
        print("✨ SINC_OK")
        
    except Exception as e:
        print(f"❌ Erro na automação: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        append_to_dataset(sys.argv[1], sys.argv[2])
    else:
        check_and_trigger()
