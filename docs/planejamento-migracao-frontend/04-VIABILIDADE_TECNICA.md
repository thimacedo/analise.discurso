# Verificação de Viabilidade Técnica

## Análise de Componentes

### 1. Framework Base (Next.js 16 + React 19)
- **Status:** Altamente viável.
- **Justificativa:** O Next.js é a principal escolha de mercado atual. O fato do Vercel ser a plataforma de hospedagem da aplicação inteira facilita imensamente o deploy, pois o Vercel foi criado pela mesma empresa do Next.js, possuindo zero configurações manuais pesadas para o frontend (Zero-config deploy).

### 2. Estilização (Tailwind CSS v4 + Shadcn)
- **Status:** Totalmente viável.
- **Justificativa:** Atualmente, a aplicação já usa classes de utilitário do Tailwind no Vanilla JS. A migração para Shadcn será feita transpondo as classes já mapeadas no `app.js` (como `bg-danger-50`, `border-success-400`) diretamente para as Props do React ou variáveis da configuração do Tailwind, o que garante 100% de compatibilidade visual.

### 3. Banco de Dados e Conexão (Supabase)
- **Status:** Viável com ressalvas na Proposta.
- **Justificativa:** A proposta contida no arquivo tar referia a ferramentas como Prisma ORM. Recomenda-se descartar o Prisma para não quebrar a arquitetura de API existente (`FastAPI`) e a segurança do Supabase. Utilizar a stack do `@supabase/supabase-js` com React Client garante RLS (Row Level Security) transparente e menor verbosidade, reaproveitando os schemas atuais sem custos adicionais de infraestrutura.

### 4. Coexistência de Rotas (Next.js + FastAPI)
- **Status:** Requer atenção (Ponto Crítico).
- **Justificativa:** O Vercel lida com subpastas `/api` do repositório como Serverless Functions. Atualmente a API FastAPI deve estar rodando nela. Adicionar o App Router do Next.js precisará apenas que o arquivo `next.config.ts` inclua regras de `rewrites` garantindo que chamadas no frontend Next.js para `/api` caiam para o servidor de backend, se ele estiver contido no mesmo repositório (Monorepo), ou apenas tratar via CORS caso a API seja desmembrada. Esta é uma tarefa rotineira em monorepos.

## Veredito Final
✅ **VIABILIDADE TÉCNICA APROVADA.** 
A transição do legado Vanilla JS para o padrão imposto pelo `PROPOSTA.MD` eliminará dores de cabeça de manutenção a médio/longo prazo (ex.: bugs de reinjeção no DOM), padronizará o visual a níveis governamentais/corporativos estritos e melhorará as métricas TTI (Time to Interactive) sem forçar recriação de bancos de dados.