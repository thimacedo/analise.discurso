-- MIGRATION: Add re-perícia flag to candidatos table
-- Date: 2026-05-01

ALTER TABLE public.candidatos 
ADD COLUMN IF NOT EXISTS needs_re_pericia BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN public.candidatos.needs_re_pericia IS 'Sinaliza que o alvo deve ter todos os seus comentários re-processados pela IA.';
