# Plano de Implementação: Migração Frontend (Next.js + FastAPI + Supabase)

## Overview
Transformar o amontoado de Vanilla JS em um frontend robusto e "Solenya-tight" usando Next.js 16 (App Router), Tailwind CSS v4, e Shadcn UI, coexistindo pacificamente com o backend Python (FastAPI) no Vercel e o banco de dados no Supabase.

## Scope Definition (CRITICAL)
### In Scope
- Setup de Next.js na raiz do projeto.
- Configuração de dependências Frontend (`package.json` unificado ou gerenciado separadamente).
- Migração visual: Componentização de TODAS as 7 abas do protótipo (War Room, Análise Forense, Alvos, Dossiês, Alertas, Rede e Fila de Coleta) usando Shadcn e Recharts.
- CSS/Estética Tática: Migrar os estilos globais (`globals.css`) que incluem as animações de scan line, glow pulses e corner brackets descritas no `worklog.md` do protótipo base.
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

### Phase 3: UI, Tematização Tática e as 7 Abas (Shadcn + Recharts)
- **Goal**: Construir a interface "War Room" profissional garantindo os 7 módulos do protótipo.
- **Steps**:
  1. [ ] Configurar a tematização tática global (`globals.css`) incluindo as animações de scan line, grids e "glow pulse" mapeadas no `worklog.md`.
  2. [ ] Inicializar os componentes base do Shadcn: Card, Avatar, Badge, Tabs, Table.
  3. [ ] Construir e rotear as 7 Abas principais: War Room, Análise Forense, Alvos, Dossiês, Alertas, Rede (Análise de Grafos) e Fila de Coleta.
  4. [ ] Migrar os gráficos temporais e de distribuição de categorias usando Recharts (Radar, Linha e Barras).
  5. [ ] Implementar o `CommentDetailModal` global para visualização profunda de comentários a partir de qualquer aba.
- **Verification**: Navegar pelas 7 abas do painel e verificar se a tematização e dados dinâmicos estão 100% integrados à "espinha dorsal" do `PROPOSTA.MD`.

### Phase 4: Sincronização de Estado Local e Ajustes Finais
- **Goal**: Garantir que as lógicas e painéis laterais funcionem fluídos usando Zustand.
- **Steps**:
  1. [ ] Criar um store Zustand (`useUIStore`) para o toggle dos sidebars, modo de exibição, pesquisa/filtros e página atual.
  2. [ ] Testar integração do Frontend com a auditoria dos comentários via RPC ou POST na rota `api/*` (Python).
  3. [ ] Remoção final de assets soltos da versão antiga e limpeza de dependências não utilizadas.
- **Verification**: Build local bem-sucedido (`npm run build`). Nenhuma quebra de layout. Nenhuma chamada de API retornando 404.