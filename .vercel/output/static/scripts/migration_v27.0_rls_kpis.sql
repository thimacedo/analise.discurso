-- Migração v27.0: Blindagem RLS e Motor de KPIs Reais

-- 1. Ativação de RLS (Segurança Diamond)
ALTER TABLE public.candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comentarios ENABLE ROW LEVEL SECURITY;

-- Políticas de Acesso Público (Leitura)
DROP POLICY IF EXISTS "Acesso público leitura candidatos" ON public.candidatos;
CREATE POLICY "Acesso público leitura candidatos" ON public.candidatos FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "Acesso público leitura comentarios" ON public.comentarios;
CREATE POLICY "Acesso público leitura comentarios" ON public.comentarios FOR SELECT TO anon, authenticated USING (true);

-- 2. Função Consolidada de KPIs (Janela 24h)
CREATE OR REPLACE FUNCTION public.get_dashboard_kpis()
RETURNS TABLE (
    alvos bigint,
    alertas bigint,
    amostra bigint,
    resiliencia_pct numeric
) AS $$
BEGIN
    RETURN QUERY
    WITH base_comentarios AS (
        SELECT candidato_id, is_hate 
        FROM public.comentarios 
        WHERE data_coleta >= now() - interval '1 day'
    )
    SELECT 
        COUNT(DISTINCT candidato_id)::bigint as alvos,
        COUNT(*) FILTER (WHERE is_hate = true)::bigint as alertas,
        COUNT(*)::bigint as amostra,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE is_hate = false) / NULLIF(COUNT(*), 0), 
            2
        ) as resiliencia_pct
    FROM base_comentarios;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Nova Tabela de Auditoria de Alvos (Direcionamento do Ódio)
ALTER TABLE public.comentarios 
ADD COLUMN IF NOT EXISTS direcao_odio text DEFAULT 'DIRETO' 
CHECK (direcao_odio IN ('DIRETO', 'INDIRETO', 'TERCEIROS'));

COMMENT ON COLUMN public.comentarios.direcao_odio IS 'DIRETO: Contra o dono do perfil. INDIRETO: Contra outro alvo via este perfil.';
