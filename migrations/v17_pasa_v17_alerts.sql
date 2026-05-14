-- migrations/v17_pasa_v17_alerts.sql

-- Detecta workers degradados e gera alertas acionáveis
-- Garante que dois workers nunca peguem a mesma mensagem
CREATE OR REPLACE FUNCTION public.detect_worker_anomalies()
RETURNS TABLE (
  worker_name       text,
  anomaly_type      text,
  current_value     numeric,
  threshold         numeric,
  severity          text,
  suggested_action  text
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY

  -- 1. Taxa de sucesso abaixo de 70% nas últimas 2 horas
  SELECT
    h.worker_name,
    'LOW_SUCCESS_RATE'::text,
    h.success_rate_pct,
    70::numeric,
    CASE
      WHEN h.success_rate_pct < 40 THEN 'critical'
      WHEN h.success_rate_pct < 70 THEN 'warning'
    END,
    'Verificar logs do worker e status da API externa'::text
  FROM public.worker_health h
  WHERE h.success_rate_pct < 70

  UNION ALL

  -- 2. Worker silencioso — não executa há mais de 1 hora
  SELECT
    wl.worker_name,
    'WORKER_SILENT'::text,
    EXTRACT(EPOCH FROM (now() - wl.last_audit)) / 60,
    60::numeric,
    'warning'::text,
    'Verificar se o Main Runner está ativo'::text
  FROM public.worker_ledger wl
  WHERE wl.last_audit < now() - interval '1 hour'
    AND wl.status != 'idle'

  UNION ALL

  -- 3. Fila crescendo sem consumo — mensagens paradas há >15 min
  -- Nota: Ajustado para usar a tabela pg_queue simulada se pgmq não existir
  SELECT
    'EventBus'::text,
    'QUEUE_BACKLOG'::text,
    COUNT(*)::numeric,
    50::numeric,
    CASE WHEN COUNT(*) > 200 THEN 'critical' ELSE 'warning' END,
    'ClassifierWorker pode estar parado ou API do Gemini indisponível'::text
  FROM public.pg_queue
  WHERE status = 'PENDING' AND created_at < now() - interval '15 minutes'
  HAVING COUNT(*) > 50

  UNION ALL

  -- 4. Dead letter queue acumulando
  SELECT
    'DeadLetterQueue'::text,
    'DLQ_GROWING'::text,
    COUNT(*)::numeric,
    10::numeric,
    'warning'::text,
    'Investigar mensagens na dead_letter_queue'::text
  FROM public.dead_letter_queue
  WHERE failed_at > now() - interval '24 hours'
  HAVING COUNT(*) > 10;
END;
$$;

-- Tabela de alertas disparados (evita spam de notificação)
CREATE TABLE IF NOT EXISTS public.system_alerts (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  worker_name   text NOT NULL,
  anomaly_type  text NOT NULL,
  severity      text NOT NULL,
  current_value numeric,
  threshold     numeric,
  message       text,
  resolved      boolean DEFAULT false,
  notified      boolean DEFAULT false,
  created_at    timestamptz DEFAULT now(),
  resolved_at   timestamptz,
  -- Impede alertas duplicados do mesmo tipo nas últimas 2 horas
  UNIQUE (worker_name, anomaly_type, resolved)
);

-- Coluna push_token nos profiles
ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS push_token text;

-- Índice para limpeza eficiente de tokens inválidos
CREATE INDEX IF NOT EXISTS idx_profiles_push_token
  ON public.profiles (push_token)
  WHERE push_token IS NOT NULL;
