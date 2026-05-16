-- PASA v46.2: Rastreabilidade temporal de Shadowban
ALTER TABLE public.candidatos
ADD COLUMN IF NOT EXISTS shadowban_detected_at TIMESTAMPTZ;
