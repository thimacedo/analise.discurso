-- SENTINELA | Diamond Security - RLS Fix v1.0
-- Este script habilita o RLS e define políticas para acesso público e privado.

-- 1. Habilitar RLS nas tabelas principais
ALTER TABLE public.candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comentarios ENABLE ROW LEVEL SECURITY;

-- 2. Políticas para a tabela 'candidatos'
DROP POLICY IF EXISTS "Acesso público para leitura de candidatos" ON public.candidatos;
CREATE POLICY "Acesso público para leitura de candidatos" 
ON public.candidatos FOR SELECT 
USING (true); -- Dashboard público

-- 3. Políticas para a tabela 'comentarios'
DROP POLICY IF EXISTS "Acesso público para leitura de comentarios" ON public.comentarios;
CREATE POLICY "Acesso público para leitura de comentarios" 
ON public.comentarios FOR SELECT 
USING (true); -- Dashboard público

-- 4. Exemplo de Política Restrita (Dossiês Forenses)
-- Se criarmos uma tabela de 'dossies_restritos', a política seria:
-- CREATE POLICY "Apenas dono vê seus dossies" ON public.dossies
-- FOR SELECT USING (auth.uid() = user_id);

-- 5. Segurança do Invoker em Views (Postgres 15+)
-- Garante que Views respeitem as políticas de RLS das tabelas subjacentes
ALTER VIEW IF EXISTS public.v_candidato_score SET (security_invoker = true);
ALTER VIEW IF EXISTS public.v_pasa_breakdown SET (security_invoker = true);

-- 6. Log de Auditoria
COMMENT ON TABLE public.comentarios IS 'Tabela protegida por RLS. Acesso anônimo permitido apenas para leitura.';
