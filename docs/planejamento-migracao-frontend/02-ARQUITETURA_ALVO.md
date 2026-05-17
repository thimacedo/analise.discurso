# Arquitetura Alvo (Frontend)

## 🧩 Componentes do Sistema

A nova arquitetura será dividida em camadas, adotando os padrões do **Next.js App Router**:

### 1. Camada de Apresentação (UI)
- **Shadcn UI + Tailwind CSS v4:** Todos os botões, cards, diálogos, tabelas e formulários seguirão a biblioteca Shadcn. Isso padroniza o sistema e oferece uma experiência "dashboard forense" sofisticada.
- **Gráficos (Recharts):** Gráficos de evolução temporal e distribuição de categorias serão migrados para Recharts, recebendo os dados injetados diretamente via propriedades do React.

### 2. Camada de Estado e Gerenciamento de Dados
- **Zustand:** Substituirá o atual objeto global `State` (`state.js`). Será usado para estados efêmeros de interface (ex: painéis laterais colapsados, modais ativos).
- **React Query (TanStack):** Cuidará da busca, cache, sincronização e atualização dos dados do banco.
- **Supabase Client (`@supabase/supabase-js`):** Embora a proposta inclua `Prisma`, para manter o alinhamento com a arquitetura atual (PASA) onde o **Supabase é a Fonte da Verdade**, a integração de dados permanecerá via cliente Supabase (SSR suportado). Isso evita o retrabalho de mapeamento de schemas via Prisma.

### 3. Roteamento e Autenticação
- **Next.js App Router (`src/app/`):** O dashboard principal passará a ser uma rota Next.js (ex: `app/dashboard/page.tsx`).
- **Autenticação:** Manteremos o Supabase Auth, que suporta facilmente Next.js usando o pacote `@supabase/ssr` para controle de sessão em cookies HTTP-only.

## ⚙️ Conflito de Integração (Vercel)
**Atenção:** Atualmente, a API Python (FastAPI) utiliza as rotas `api/*` no Vercel através de um `vercel.json`. O Next.js também é tradicionalmente implantado no Vercel no diretório raiz. A integração exigirá:
1. Uma configuração cuidadosa de reescrita (rewrites) no `next.config.ts` para que `/api/*` aponte para o backend FastAPI (ou garantir que o `vercel.json` encaminhe `api/*` para o Python e o restante para o Next.js buildado).