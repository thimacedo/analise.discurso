import httpx

def set_explicit_ownership():
    uuid = "66f853ed-c42b-43d4-bcc3-23f05b2c44e9"
    headers = {
        "apikey": "SUPABASE_KEY_PLACEHOLDER",
        "Authorization": "Bearer SUPABASE_KEY_PLACEHOLDER",
        "Content-Type": "application/json"
    }
    
    # 1. Candidatos
    url_cand = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1/candidatos?user_id=is.null"
    resp_cand = httpx.patch(url_cand, json={"user_id": uuid}, headers=headers)
    
    # 2. Comentarios
    url_com = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1/comentarios?user_id=is.null"
    resp_com = httpx.patch(url_com, json={"user_id": uuid}, headers=headers)
    
    if resp_cand.status_code in [200, 204] and resp_com.status_code in [200, 204]:
        print(f"✅ Propriedade vinculada com sucesso ao UUID: {uuid}")
    else:
        print(f"⚠️ Erro ao vincular: {resp_cand.text} {resp_com.text}")

if __name__ == "__main__":
    set_explicit_ownership()
