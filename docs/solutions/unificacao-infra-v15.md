---
date: "2026-04-26"
problem_type: "deployment-failure"
severity: "critical"
symptoms:
  - "Vercel 404/500 em rotas API"
  - "Dashboard vazio (Amostragem 0)"
  - "Build abortado por caractere invisivel (BOM)"
root_cause: "fragmentation-and-encoding"
tags:
  - vercel
  - fastapi
  - utf8
  - infrastructure
---

# Solucao: Unificacao de Infraestrutura e Destravamento de Build

## Diagnostico
O projeto estava fragmentado em multiplos dominios Vercel com estruturas de pastas conflitantes (api/templates vs root). O arquivo requirements.txt continha um BOM invisivel que impedia a instalacao de dependencias.

## Acoes Tomadas
1. Unificacao de ID: Vinculado localmente ao prj_hbfDAwwIfrz6nJgIkZWLNacCWpeq.
2. Limpeza de BOM: Regravado requirements.txt em UTF-8 puro via Python.
3. Roteamento Blindado: Estabelecida raiz plana para HTML e api/ para FastAPI.
4. Sincronizacao de Dados: Executado sync_db_integrity.py para alinhar contadores do Supabase.

## Licoes Aprendidas
- Nunca usar PowerShell puro (Out-File) para gravar arquivos de build; preferir Python para garantir codificacao limpa.
- O Vercel prioriza arquivos estaticos na raiz; usar vercel.json apenas para redirecionamentos criticos de API.
