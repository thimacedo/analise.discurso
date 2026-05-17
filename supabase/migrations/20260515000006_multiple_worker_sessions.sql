-- PASA v49.6: Permite múltiplas sessões por plataforma para suporte a fallback/rotação
-- Remove a restrição de chave primária na coluna plataforma e introduz um ID único

-- 1. Adiciona coluna ID se não existir
ALTER TABLE public.worker_sessions ADD COLUMN IF NOT EXISTS id UUID DEFAULT gen_random_uuid();

-- 2. Remove PK atual (plataforma)
ALTER TABLE public.worker_sessions DROP CONSTRAINT IF EXISTS worker_sessions_pkey;

-- 3. Define a nova PK no ID
ALTER TABLE public.worker_sessions ADD PRIMARY KEY (id);

-- 4. Adiciona constraint de unicidade no par (plataforma, cookies) para evitar duplicados idênticos
ALTER TABLE public.worker_sessions ADD CONSTRAINT worker_sessions_plataforma_cookies_key UNIQUE (plataforma, cookies);

-- 5. Index para performance de busca por plataforma
CREATE INDEX IF NOT EXISTS idx_worker_sessions_plataforma ON public.worker_sessions(plataforma);
