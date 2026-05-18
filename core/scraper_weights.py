import json
import os

STATE_FILE = "scraper_weights.json"

def get_weights():
    if not os.path.exists(STATE_FILE):
        return {"json_api": 1.0, "browser": 1.0, "css_dom": 1.0}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def update_weight(method, success):
    weights = get_weights()
    if success:
        weights[method] *= 1.2 # Recompensa: aumenta probabilidade
    else:
        weights[method] *= 0.5 # Punição: reduz probabilidade
    with open(STATE_FILE, "w") as f:
        json.dump(weights, f)

def get_best_method():
    weights = get_weights()
    # Retorna o método com maior peso
    return max(weights, key=weights.get)
