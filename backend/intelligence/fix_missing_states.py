import httpx
import time

URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY"
h = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# MAPA DE CORREÇÃO CIRÚRGICA (Consolidado)
FIX_MAP = {
    "RN": ["subtenenteeliabe22", "vereador.vava.azevedo", "erikojacome", "marciamaia_", "divaneidebasilio", "comunicadorluizalmir", "vereadorchagascatarino", "robinsonfaria", "drkerginaldo", "rafaeladenilda", "vereadorleolima", "cabodeyvison", "annelagartixa", "profroberiopaulino", "vereadorafraniobezerra", "adjutodias", "coronelazevedo22", "joseagripinomaia", "vereadoreuricodajapao", "jaimecaladooficial", "vereadorgustavonegocio", "kelpslima", "carloseduardoe55", "henriqueeduardoalves", "rogerio.smarinho", "jacojacome", "antenorroberto65", "hermanomorais", "alexandremottacamara"],
    "PE": ["tulio.gadelha", "senadorhumberto", "jones.manoel"],
    "RJ": ["chico.alencar", "drcesarmaia", "pastorhenriquevieira", "instadabene"],
    "SP": ["depchinaglia", "depzarattini", "pedroponciosp", "padilhando", "luizaerundina", "thainarafaria13"],
    "MG": ["duda_salabert"],
    "PR": ["sargentofahur"],
    "GO": ["gusgayer"],
    "RS": ["marcelvanhattem", "manueladavila"]
}

def fix_all():
    print("🚀 Iniciando Fix Estabilizado de Estados...")
    count = 0
    for uf, usernames in FIX_MAP.items():
        for u in usernames:
            try:
                print(f"Fixing @{u} -> {uf}")
                r = httpx.patch(f"{URL}/candidatos?username=eq.{u}", headers=h, json={"estado": uf}, timeout=10.0)
                if r.status_code in [200, 204]:
                    count += 1
                else:
                    print(f"   ❌ Erro @{u}: {r.status_code}")
                time.sleep(0.5) # Intervalo de segurança
            except Exception as e:
                print(f"   ❌ Falha conexão @{u}: {str(e)}")
                time.sleep(2) # Espera maior em caso de erro
                
    print(f"\n✅ Sincronização concluída! {count} perfis reposicionados.")

if __name__ == "__main__":
    fix_all()
