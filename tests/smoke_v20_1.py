import sys
import os
sys.path.append(os.getcwd())

try:
    from core.normalizer import target_normalizer
    from core.firebase_alerter import send_alert_summary
    from core.firebase_init import admin_app
    
    print("🧪 [SMOKE] Iniciando Validação v20.1...")
    
    # 1. Teste Normalizador
    n = target_normalizer.normalize("Lula")
    print(f"Normalizador (Lula): {n}")
    if n != "lulaoficial":
        print("❌ FALHA: Normalizador não mapeou 'Lula' corretamente.")
        sys.exit(1)
    
    # 2. Teste Firebase
    print(f"Firebase Admin SDK: {'ATIVO' if admin_app else 'CONFIGURADO (Sem chave de serviço)'}")
    
    # 3. Teste Orquestrador (Import)
    import orquestrador
    print("Orquestrador: IMPORT OK")
    
    print("\n✅ [SMOKE] v20.1 validada com sucesso!")
except Exception as e:
    print(f"\n❌ [ERROR] Falha crítica no Smoke Test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
