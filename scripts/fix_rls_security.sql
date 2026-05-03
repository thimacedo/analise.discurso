-- SENTINELA | Diamond Security - RLS Hardening v1.2
-- Blindagem completa baseada no relatório de auditoria (Tabelas e Views).

-- 1) Habilitar RLS nas tabelas principais e auditadas
ALTER TABLE public.candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comentarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.historico_monitoramento ENABLE ROW LEVEL SECURITY;

-- 2) Políticas de Leitura Pública (Dashboard)
-- Tabela: candidatos
DROP POLICY IF EXISTS "Acesso público para leitura de candidatos" ON public.candidatos;
CREATE POLICY "Acesso público para leitura de candidatos" ON public.candidatos 
FOR SELECT TO anon, authenticated USING (true);

-- Tabela: comentarios
DROP POLICY IF EXISTS "Acesso público para leitura de comentarios" ON public.comentarios;
CREATE POLICY "Acesso público para leitura de comentarios" ON public.comentarios 
FOR SELECT TO anon, authenticated USING (true);

-- Tabela: historico_monitoramento (Correção do erro rls_disabled_in_public)
DROP POLICY IF EXISTS "Acesso público para leitura do historico" ON public.historico_monitoramento;
CREATE POLICY "Acesso público para leitura do historico" ON public.historico_monitoramento 
FOR SELECT TO anon, authenticated USING (true);

-- 3) Segurança do Invoker em Views (Postgres 15+)
-- Corrige o erro security_definer_view, forçando as views a respeitarem o RLS das tabelas
ALTER VIEW IF EXISTS public.v_candidato_score SET (security_invoker = true);
ALTER VIEW IF EXISTS public.v_pasa_breakdown SET (security_invoker = true);
ALTER VIEW IF EXISTS public.dashboard_comentarios_classificacao SET (security_invoker = true);
ALTER VIEW IF EXISTS public.view_performance_perfis SET (security_invoker = true);
ALTER VIEW IF EXISTS public.dashboard_intel_agregada SET (security_invoker = true);

-- 4) Grants de API (PostgREST)
GRANT SELECT ON public.candidatos TO anon, authenticated;
GRANT SELECT ON public.comentarios TO anon, authenticated;
GRANT SELECT ON public.historico_monitoramento TO anon, authenticated;

-- 5) Log de Auditoria
COMMENT ON TABLE public.historico_monitoramento IS 'Blindagem v1.2: RLS habilitado e políticas de leitura pública configuradas.';
