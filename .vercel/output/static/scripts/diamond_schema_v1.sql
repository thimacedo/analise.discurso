-- SENTINELA | Diamond Edition - Database Schema v1.0

-- 1. Tabela: metricas_diarias
CREATE TABLE IF NOT EXISTS public.metricas_diarias (
    id           uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    data         date NOT NULL,
    total_coletado       integer DEFAULT 0,
    total_processado     integer DEFAULT 0,
    total_hate           integer DEFAULT 0,
    total_neutro         integer DEFAULT 0,
    resiliencia          numeric(5,2) DEFAULT 100.00,
    pasa_breakdown       jsonb DEFAULT '{}',
    uf_breakdown         jsonb DEFAULT '{}',
    indices_coordenacao  numeric(5,2) DEFAULT 0.00,
    pico_hostilidade     boolean DEFAULT false,
    created_at           timestamptz DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(data)
);

ALTER TABLE public.metricas_diarias ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Anon pode ler metricas" ON public.metricas_diarias;
CREATE POLICY "Anon pode ler metricas" ON public.metricas_diarias FOR SELECT TO anon USING (true);
CREATE INDEX IF NOT EXISTS idx_metricas_diarias_data ON public.metricas_diarias (data DESC);

-- 2. Tabela: redes_coordenadas
CREATE TABLE IF NOT EXISTS public.redes_coordenadas (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    nome            text NOT NULL,
    status          text DEFAULT 'MONITORANDO' CHECK (status IN ('ATIVA', 'MONITORANDO', 'MAPEADA', 'DESATIVADA')),
    descricao       text,
    alvos_vinculados integer DEFAULT 0,
    eventos_count    integer DEFAULT 0,
    alcance_estimado text DEFAULT '0',
    cluster_labels   jsonb DEFAULT '[]',
    palavras_chave   jsonb DEFAULT '[]',
    severidade       integer DEFAULT 0 CHECK (severidade >= 0 AND severidade <= 100),
    primeira_deteccao timestamptz DEFAULT CURRENT_TIMESTAMP,
    ultima_atividade  timestamptz DEFAULT CURRENT_TIMESTAMP,
    created_at        timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at        timestamptz DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.redes_coordenadas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Anon pode ler redes" ON public.redes_coordenadas;
CREATE POLICY "Anon pode ler redes" ON public.redes_coordenadas FOR SELECT TO anon USING (true);

-- 3. Tabela: alertas_ativos
CREATE TABLE IF NOT EXISTS public.alertas_ativos (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    severidade      text NOT NULL CHECK (severidade IN ('CRITICAL', 'WARNING', 'INFO')),
    titulo          text NOT NULL,
    descricao       text,
    rede_id         uuid REFERENCES public.redes_coordenadas(id),
    candidato_ids   jsonb DEFAULT '[]',
    volume_eventos  integer DEFAULT 0,
    z_score         numeric(6,2) DEFAULT 0.00,
    uf_afetadas     jsonb DEFAULT '[]',
    status          text DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'RESOLVIDO', 'SUPRIMIDO')),
    expira_em       timestamptz,
    created_at      timestamptz DEFAULT CURRENT_TIMESTAMP,
    resolved_at     timestamptz
);

ALTER TABLE public.alertas_ativos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Anon pode ler alertas" ON public.alertas_ativos;
CREATE POLICY "Anon pode ler alertas" ON public.alertas_ativos FOR SELECT TO anon USING (true);
CREATE INDEX IF NOT EXISTS idx_alertas_severidade ON public.alertas_ativos (severidade, created_at DESC) WHERE status = 'ATIVO';

-- 4. Função RPC: upsert_metrica_diaria
CREATE OR REPLACE FUNCTION public.upsert_metrica_diaria(
    p_data date,
    p_total_coletado integer,
    p_total_hate integer,
    p_total_neutro integer,
    p_resiliencia numeric,
    p_pasa_breakdown jsonb,
    p_uf_breakdown jsonb
)
RETURNS void AS $$
BEGIN
    INSERT INTO public.metricas_diarias (data, total_coletado, total_hate, total_neutro, resiliencia, pasa_breakdown, uf_breakdown)
    VALUES (p_data, p_total_coletado, p_total_hate, p_total_neutro, p_resiliencia, p_pasa_breakdown, p_uf_breakdown)
    ON CONFLICT (data) DO UPDATE SET
        total_coletado = EXCLUDED.total_coletado,
        total_hate = EXCLUDED.total_hate,
        total_neutro = EXCLUDED.total_neutro,
        resiliencia = EXCLUDED.resiliencia,
        pasa_breakdown = EXCLUDED.pasa_breakdown,
        uf_breakdown = EXCLUDED.uf_breakdown;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. View: v_pasa_breakdown
CREATE OR REPLACE VIEW public.v_pasa_breakdown AS
SELECT
    categoria_ia,
    COUNT(*) AS total,
    ROUND(COUNT(*)::numeric / NULLIF(SUM(COUNT(*)) OVER(), 0) * 100, 1) AS percentual,
    AVG(likes) AS avg_engajamento,
    MAX(data_coleta) AS ultimo_evento
FROM public.comentarios
WHERE is_hate = true AND processado_ia = true
GROUP BY categoria_ia
ORDER BY total DESC;

GRANT SELECT ON public.v_pasa_breakdown TO anon;

-- 6. View: v_candidato_score
CREATE OR REPLACE VIEW public.v_candidato_score AS
SELECT
    c.username,
    c.nome_completo,
    c.cargo,
    c.estado,
    c.partido,
    c.sexo,
    c.raca,
    c.seguidores,
    c.comentarios_totales_count,
    c.comentarios_odio_count,
    c.posts_avaliados_count,
    c.status_monitoramento,
    ROUND(LEAST(100, (
        CASE
            WHEN c.comentarios_totales_count > 0
            THEN LEAST(40, (c.comentarios_odio_count::numeric / c.comentarios_totales_count) * 160)
            ELSE 0
        END +
        LEAST(30, (c.comentarios_odio_count::numeric / 200) * 30) +
        CASE
            WHEN c.comentarios_odio_count > 0
            THEN LEAST(30, (
                SELECT COALESCE(AVG(likes), 0)
                FROM public.comentarios cm
                WHERE cm.candidato_id = c.username AND cm.is_hate = true
            ) / 50 * 30)
            ELSE 0
        END
    )::numeric), 0) AS score_risco,
    CASE
        WHEN c.comentarios_totales_count > 0 AND (c.comentarios_odio_count::numeric / c.comentarios_totales_count) > 0.25 THEN 'CRITICO'
        WHEN c.comentarios_totales_count > 0 AND (c.comentarios_odio_count::numeric / c.comentarios_totales_count) > 0.15 THEN 'ELEVADO'
        WHEN c.comentarios_totales_count > 0 AND (c.comentarios_odio_count::numeric / c.comentarios_totales_count) > 0.08 THEN 'MONITORANDO'
        ELSE 'CONTROLADO'
    END AS nivel_risco,
    (
        SELECT MAX(cm.data_coleta)
        FROM public.comentarios cm
        WHERE cm.candidato_id = c.username
    ) AS ultima_atividade
FROM public.candidatos c
WHERE c.status_monitoramento = 'Ativo';

GRANT SELECT ON public.v_candidato_score TO anon;

-- 7. View Materializada: mv_agregacao_uf
CREATE MATERIALIZED VIEW IF NOT EXISTS public.mv_agregacao_uf AS
SELECT
    c.estado AS uf,
    COUNT(DISTINCT c.username) AS total_alvos,
    SUM(c.comentarios_totales_count) AS total_comentarios,
    SUM(c.comentarios_odio_count) AS total_hate,
    CASE
        WHEN SUM(c.comentarios_totales_count) > 0
        THEN ROUND(100 - ((SUM(c.comentarios_odio_count)::numeric / SUM(c.comentarios_totales_count)) * 100), 2)
        ELSE 100.00
    END AS resiliencia,
    CASE
        WHEN SUM(c.comentarios_totales_count) = 0 THEN 'CONTROLADO'
        WHEN SUM(c.comentarios_odio_count)::numeric / NULLIF(SUM(c.comentarios_totales_count), 0) > 0.25 THEN 'CRITICO'
        WHEN SUM(c.comentarios_odio_count)::numeric / NULLIF(SUM(c.comentarios_totales_count), 0) > 0.15 THEN 'ELEVADO'
        WHEN SUM(c.comentarios_odio_count)::numeric / NULLIF(SUM(c.comentarios_totales_count), 0) > 0.08 THEN 'MONITORANDO'
        ELSE 'CONTROLADO'
    END AS nivel_risco
FROM public.candidatos c
WHERE c.status_monitoramento = 'Ativo'
GROUP BY c.estado
ORDER BY total_hate DESC;

GRANT SELECT ON public.mv_agregacao_uf TO anon;

-- 8. Trigger: Atualização Automática de Counters
CREATE OR REPLACE FUNCTION public.update_candidato_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.candidatos
        SET comentarios_totales_count = COALESCE(comentarios_totales_count, 0) + 1,
            comentarios_odio_count = COALESCE(comentarios_odio_count, 0) + CASE WHEN NEW.is_hate THEN 1 ELSE 0 END,
            updated_at = CURRENT_TIMESTAMP
        WHERE username = NEW.candidato_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.is_hate != NEW.is_hate THEN
        UPDATE public.candidatos
        SET comentarios_odio_count = COALESCE(comentarios_odio_count, 0) + CASE WHEN NEW.is_hate THEN 1 ELSE -1 END,
            updated_at = CURRENT_TIMESTAMP
        WHERE username = NEW.candidato_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_update_counters ON public.comentarios;
CREATE TRIGGER trg_update_counters
AFTER INSERT OR UPDATE OF is_hate ON public.comentarios
FOR EACH ROW EXECUTE FUNCTION public.update_candidato_counters();
