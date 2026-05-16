-- PASA v46: Coluna para rastreabilidade de Shadowban Suspeito
ALTER TABLE public.candidatos
ADD COLUMN IF NOT EXISTS shadowban_suspect BOOLEAN DEFAULT FALSE;
