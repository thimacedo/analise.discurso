-- SENTINELA | Diamond Security - RLS Hardening v1.1
-- Versão robusta com atribuição de papéis (anon, authenticated) e Grants explícitos.

-- 1) Habilitar RLS nas tabelas principais
ALTER TABLE public.candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comentarios ENABLE ROW LEVEL SECURITY;

-- 2) Políticas: Dashboard público (tanto anon quanto authenticated)
DROP POLICY IF EXISTS "Acesso público para leitura de candidatos" ON public.candidatos;
CREATE POLICY "Acesso público para leitura de candidatos"
  ON public.candidatos
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- 3) Políticas: Dashboard público (tanto anon quanto authenticated)
DROP POLICY IF EXISTS "Acesso público para leitura de comentarios" ON public.comentarios;
CREATE POLICY "Acesso público para leitura de comentarios"
  ON public.comentarios
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- 4) Segurança do Invoker em Views (Postgres 15+)
-- Garante que Views respeitem as políticas de RLS das tabelas subjacentes
ALTER VIEW IF EXISTS public.v_candidato_score SET (security_invoker = true);
ALTER VIEW IF EXISTS public.v_pasa_breakdown SET (security_invoker = true);

-- 5) Grants necessários para a API (PostgREST)
-- Sem estes grants, o Supabase pode retornar 401/403 mesmo com RLS liberado
GRANT SELECT ON public.candidatos  TO anon, authenticated;
GRANT SELECT ON public.comentarios TO anon, authenticated;

-- Log de Auditoria
COMMENT ON TABLE public.comentarios IS 'Tabela blindada v1.1. RLS e Grants configurados para anon/auth.';
