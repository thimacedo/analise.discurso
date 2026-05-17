# Cronograma e Fases da Migração

## Fase 1: Setup da Nova Infraestrutura (Dias 1-2)
1. Extrair os componentes base da pasta `proposta_frontend` para a raiz do repositório ou um diretório como `frontend/`.
2. Configurar o arquivo `next.config.ts` com as variáveis de ambiente necessárias e configurar o roteamento (rewrites) para garantir que chamadas à `/api` sejam direcionadas ao backend FastAPI existente.
3. Inicializar e testar Shadcn UI (`npx shadcn-ui@latest init`).
4. Instalar pacote oficial do Supabase para SSR (`@supabase/ssr`).

## Fase 2: Autenticação e Camada de Dados (Dias 3-4)
1. Transferir o fluxo atual de `auth.js` e `supabase.js` para Server Actions ou API Routes do Next.js (protegendo a aplicação via middleware).
2. Adicionar provedores React Query (`QueryClientProvider`) na raiz do App Router.
3. Recriar as funções de extração de dados contidas no atual `app.js` (como `fetchComments`, `fetchKPIs`, etc.) como *hooks* customizados (ex: `useComments()`) e queries do React Query.

## Fase 3: Migração de Componentes Visuais (Dias 5-8)
1. **Cards e Alertas:** Substituir a renderização de strings de HTML (como `renderCommentCard()`) por componentes React (`<CommentCard />`) implementados com Shadcn (Card, Avatar, Badge).
2. **KPIs:** Substituir o grid manual de KPIs por instâncias do componente `<Card>` estilizados via Tailwind.
3. **Gráficos e Estatísticas:** Incorporar Recharts baseando-se no `PROPOSTA.MD`, montando gráficos de barra e rosca iterando sobre os dados do React Query.
4. **Filtros e Paginação:** Adicionar Zustand para controlar o estado da UI (`view`, `searchTerm`, `pagination`).

## Fase 4: Desativação do Vanilla JS (Dia 9)
1. Ajustar os roteamentos no Vercel (garantir que `next build` seja o novo comando de build principal do frontend).
2. Remover pastas antigas: apagar `/public/core`, o antigo `index.html` e demais dependências Vanilla legadas.
3. Testar o fluxo fim a fim (War Room local -> Banco de Dados -> Novo Frontend React).