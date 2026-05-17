# Plano de Implementação: Migração Frontend (Next.js + FastAPI + Supabase)

## Overview
Transformar o amontoado de Vanilla JS em um frontend robusto e "Solenya-tight" usando Next.js 16 (App Router), Tailwind CSS v4, e Shadcn UI, coexistindo pacificamente com o backend Python (FastAPI) no Vercel e o banco de dados no Supabase.

## Scope Definition (CRITICAL)
### In Scope
- Setup de Next.js na raiz do projeto.
- Configuração de dependências Frontend (`package.json` unificado ou gerenciado separadamente).
- Migração visual: Componentização dos dashboards, painéis e gráficos usando Shadcn e Recharts baseados no `PROPOSTA.MD`.
- Estado: Substituir `state.js` por `Zustand` e injetar chamadas via `React Query`.
- Autenticação e Queries: Instalação e uso estrito de `@supabase/supabase-js` (abandonando a ideia do Prisma citada no protótipo).
- Roteamento Híbrido: Preservar o funcionamento do `vercel.json` para que a rota `/api/*` continue a chamar `api/index.py`.

### Out of Scope (DO NOT TOUCH)
- Qualquer alteração na lógica dos *Workers* Python, do ORM/Queries do Python ou nas rotas de `api/*.py`.
- Alteração no modelo do banco de dados (Supabase) ou re-escrita de SQL.
- Deploy fora do Vercel. 

## Current State Analysis
1. O repositório atual possui Python (`pyproject.toml`, `requirements.txt`) e Node/JS na raiz (`package.json`). 
2. A interface é gerada via `index.html` estático e manipulada pelo `src/core/app.js` renderizando literals de HTML.
3. O deploy Vercel usa o arquivo `vercel.json` para direcionar a rota `/api/(.*)` para `api/index.py`. O resto é servido como estático (arquivos da raiz).
4. Em um ambiente Next.js no Vercel, o Vercel CLI entende o `next build` e trata as pastas `api/` do Python de forma integrada com as rotas Next.js. O `/api` irá pro Python e o resto pro Frontend Next.js.

## Implementation Phases

### Phase 1: Expurgo Vanilla & Setup do Monólito Híbrido
- **Goal**: Limpar o lixo estático e instalar as fundações do Next.js sem quebrar o Vercel.
- **Steps**:
  1. [ ] Remover/renomear os arquivos estáticos legados: `index.html`, `local_dashboard.html`, e mover a pasta `src/core` para um arquivo `.legacy/`.
  2. [ ] Copiar/Mover o esqueleto do `proposta_frontend` para a raiz (ou configurar pasta `src/app`).
  3. [ ] Atualizar o `package.json` principal mesclando as dependências do `PROPOSTA.MD` (Next.js, Shadcn, React, Tailwind, Recharts). Remover qualquer referência a `Prisma`.
  4. [ ] Garantir que o `vercel.json` mantenha as functions python intactas.
- **Verification**: Rodar `npm run dev` e confirmar que a página inicial sobe. Acessar `/api/v1/monitor/status` e garantir que o FastAPI continua respondendo.

### Phase 2: Integração Supabase Nativa (The God Mode Data Layer)
- **Goal**: Refatorar o componente de banco para conectar diretamente via cliente do Supabase, descartando ferramentas mágicas inúteis.
- **Steps**:
  1. [ ] Instalar `@supabase/supabase-js` e configurar um client singleton no frontend em `src/lib/supabase.ts` (ou similar).
  2. [ ] Implementar a Autenticação usando as variáveis de ambiente (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
  3. [ ] Criar os hooks customizados com `TanStack React Query` para buscar `comentarios`, `candidatos`, `dossies` e `fila_coleta`.
- **Verification**: O frontend no painel do Next.js consegue logar e puxar a lista de comentários em JSON do banco.

### Phase 3: UI & Dashboards (Shadcn + Recharts)
- **Goal**: Construir a interface "War Room" profissional.
- **Steps**:
  1. [ ] Inicializar os componentes base do Shadcn: Card, Avatar, Badge, Tabs, Table.
  2. [ ] Construir o componente `<Dashboard />` recriando as métricas e KPI's.
  3. [ ] Migrar os gráficos temporais e de categorias usando `<LineChart>` e `<BarChart>` do Recharts baseados no hook de dados de Supabase (Phase 2).
  4. [ ] Implementar o feed de Alertas Críticos (Tabela/Feed contínuo) reaproveitando o estilo da prova de conceito do `PROPOSTA.MD`.
- **Verification**: Navegar pelo painel e verificar se a estilização de Tailwind v4/Shadcn aplicou corretamente com os dados dinâmicos do banco (nada de mock data).

### Phase 4: Sincronização de Estado Local e Ajustes Finais
- **Goal**: Garantir que as lógicas e painéis laterais funcionem fluídos usando Zustand.
- **Steps**:
  1. [ ] Criar um store Zustand (`useUIStore`) para o toggle dos sidebars, modo de exibição, pesquisa/filtros e página atual.
  2. [ ] Testar integração do Frontend com a auditoria dos comentários via RPC ou POST na rota `api/*` (Python).
  3. [ ] Remoção final de assets soltos da versão antiga e limpeza de dependências não utilizadas.
- **Verification**: Build local bem-sucedido (`npm run build`). Nenhuma quebra de layout. Nenhuma chamada de API retornando 404.