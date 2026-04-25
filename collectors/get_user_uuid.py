import httpx

def get_investigator_uuid():
    headers = {
        "apikey": "SUPABASE_KEY_PLACEHOLDER",
        "Authorization": "Bearer SUPABASE_KEY_PLACEHOLDER"
    }
    url = "https://vhamejkldzxbeibqeqpk.supabase.co/auth/v1/admin/users"
    
    try:
        response = httpx.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json().get("users", [])
            for u in users:
                print(f"INVESTIGADOR_UUID:{u['id']} | EMAIL:{u['email']}")
        else:
            print(f"❌ Erro ao acessar Auth: {response.text}")
    except Exception as e:
        print(f"❌ Falha: {e}")

if __name__ == "__main__":
    get_investigator_uuid()
