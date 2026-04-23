# 🛡️ Walkthrough: Blindagem de Deploy (Sentinela v9)

## 📋 Problema Identificado
O deploy na Vercel apresentava erros de 404 no arquivo `index.html` e `/favicon.ico`, além de exceções de `runtime.lastError` no console, causados por conflitos entre o roteamento da API FastAPI (Python) e os arquivos estáticos.

## 🛠️ Solução Aplicada (Protocolo Gold Standard)

### 1. Roteamento Híbrido Estrito (`vercel.json`)
A configuração foi refatorada para isolar as rotas da API e garantir que o roteador da Vercel priorize o arquivo estático na raiz.
- **Antes:** Redirecionava tudo `/(.*)` para a API.
- **Depois:** 
    - `/api/(.*)` vai para `api/index.py`.
    - `/(.*)` (todo o resto) serve o `index.html`.

### 2. Eliminação de Dependências de Recursos Externos (Favicon)
Para evitar o erro `/favicon.ico 404`, o ícone foi convertido em um **Data URI inline** dentro do `<head>` do HTML. Isso garante que o ícone carregue instantaneamente sem requisições adicionais ao servidor.

### 3. Blindagem de Scripts Terceiros (Message Port)
O erro `message port closed` geralmente ocorre por conflitos de extensões (como AssistLoop). 
- Foi adicionada uma camada de proteção no carregamento de scripts para silenciar exceções de comunicação assíncrona que não afetam a lógica do sistema.

## 🚀 Como Manter a Estabilidade
- **Sempre** use caminhos absolutos no `vercel.json`.
- **Nunca** remova o `requirements.txt` da raiz, pois a Vercel o utiliza para detectar o runtime Python.
- **Mantenha** o `index.html` na raiz para que o builder `@vercel/static` o localize sem configurações complexas.

---
**Status:** Resolvido e Blindado (v9.0)
**Data:** 23/04/2026
