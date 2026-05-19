-- 1. Tabelas e Índices para Performance e Idempotência
CREATE UNIQUE INDEX IF NOT EXISTS ux_comentarios_nat
  ON comentarios (candidato_id, post_shortcode, id_externo);

CREATE INDEX IF NOT EXISTS ix_comentarios_candidato ON comentarios(candidato_id);
CREATE INDEX IF NOT EXISTS ix_comentarios_shortcode ON comentarios(post_shortcode);
CREATE INDEX IF NOT EXISTS ix_comentarios_publicacao ON comentarios(data_publicacao DESC);

-- 2. Tabela de KPIs (Operacional)
CREATE TABLE IF NOT EXISTS kpi_runs (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ts timestamptz NOT NULL DEFAULT now(),
  tier_used int,
  alvo text,
  comentarios_coletados int,
  duracao_ms int,
  erro text
);

-- 3. Notificação para reload de schema do PostgREST
SELECT pg_notify('pgrst', 'reload schema');
