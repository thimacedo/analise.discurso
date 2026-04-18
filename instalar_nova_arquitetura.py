#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd, description):
    print(f"\n⚙️  {description}")
    print(f"$ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso")
            return True
        else:
            print(f"⚠️  Aviso: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

print("=" * 70)
print("🚀 INSTALADOR AUTOMÁTICO - NOVA ARQUITETURA PROFISSIONAL")
print("=" * 70)

print("\n📋 Passo 1: Instalando novas dependências...")
run_command("pip install -r requirements-new.txt", "Instalar dependências")

print("\n📋 Passo 2: Verificando arquivo .env...")
if os.path.exists('.env'):
    print("✅ Arquivo .env já existe")
    with open('.env', 'r') as f:
        conteudo = f.read()
        
    if 'DATABASE_URL' not in conteudo:
        print("\n⚠️  Adicionando variáveis padrão no .env...")
        with open('.env', 'a') as f:
            f.write("\n\n# NOVA ARQUITETURA\n")
            f.write("DATABASE_URL=postgresql://postgres:postgres@localhost:5432/odio_politica\n")
            f.write("REDIS_URL=redis://localhost:6379/0\n")
        print("✅ Variáveis adicionadas")
else:
    print("⚠️  Criando arquivo .env padrão...")
    with open('.env', 'w') as f:
        f.write("# CONFIGURAÇÕES\n")
        f.write("COLETA_LIMITE_PERFIS=5\n")
        f.write("COLETA_POSTS_POR_PERFIL=2\n\n")
        f.write("# NOVA ARQUITETURA\n")
        f.write("DATABASE_URL=postgresql://postgres:postgres@localhost:5432/odio_politica\n")
        f.write("REDIS_URL=redis://localhost:6379/0\n")
    print("✅ Arquivo .env criado")

print("\n📋 Passo 3: Criando tabelas no banco de dados...")
try:
    from database.repository import DatabaseRepository
    db = DatabaseRepository()
    db.criar_tabelas()
    print("✅ Tabelas criadas com sucesso no PostgreSQL")
except Exception as e:
    print(f"⚠️  Não foi possível criar as tabelas: {e}")
    print("ℹ️  Isso é normal se o PostgreSQL ainda não está instalado ou rodando")

print("\n" + "=" * 70)
print("✅ INSTALAÇÃO CONCLUÍDA!")
print("=" * 70)
print("\nPróximos passos:")
print("1. Instale e inicie o PostgreSQL localmente")
print("2. Instale e inicie o Redis localmente")
print("3. Rode o pipeline normalmente: python orquestrador.py")
print("4. Rode a API: uvicorn api.main:app --reload")
print("5. Acesse: http://localhost:8000/docs")
print("\nArquitetura nova está pronta para uso! 🚀")