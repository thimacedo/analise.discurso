
from core.supabase_service import supabase
import json

def inspect_database():
    tables = ['candidatos', 'fila_coleta', 'worker_sessions', 'worker_metrics', 'monitoramento_logs']
    print(f"{'Tabela':<20} | {'Registros':<10} | {'Ação Sugerida'}")
    print("-" * 50)
    
    for table in tables:
        try:
            res = supabase.table(table).select('*', count='exact').limit(3).execute()
            count = res.count if res.count is not None else 0
            
            action = "Manter"
            if table == 'fila_coleta' and count > 0:
                action = "Limpar (Pendências antigas)"
            elif table == 'worker_metrics' and count > 0:
                action = "Limpar (Métricas de teste)"
            elif table == 'monitoramento_logs' and count > 0:
                action = "Limpar (Logs de teste)"
                
            print(f"{table:<20} | {count:<10} | {action}")
            
            if count > 0:
                print(f"   Sample: {res.data[0] if res.data else 'None'}")
                
        except Exception as e:
            print(f"{table:<20} | {'ERRO':<10} | Tabela pode não existir")

if __name__ == "__main__":
    inspect_database()
