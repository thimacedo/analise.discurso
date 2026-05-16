-- PASA v47: Coluna para rastrear se os Reels foram coletados
ALTER TABLE public.candidatos
ADD COLUMN IF NOT EXISTS reels_scraped BOOLEAN DEFAULT FALSE;
